import time
import re
import logging
import sys
from mythril.mythril import Mythril
from web3 import Web3
from karl.exceptions import RPCError


logging.basicConfig(level=logging.INFO)


class Karl:
    """
    Karl main interface class.
    """

    def __init__(
        self,
        rpc=None,
        rpctls=False,
        block_number=None,
        output=None,
        verbosity=logging.NOTSET,
    ):
        """
            Initialize Karl with the received parameters
        """
        if rpc is None:
            raise (
                RPCError("Must provide a valid --rpc connection to an Ethereum node")
            )

        # Ethereum node to connect to
        self.rpc = rpc
        self.rpc_tls = rpctls
        # Send results to this output (could be stdout or restful url)
        self.output = output
        self.logger = logging.getLogger("Karl")
        self.logger.setLevel(verbosity)

        # Init web3 client
        web3_rpc = None
        if rpc == "ganache":
            web3_rpc = "http://127.0.0.1:8545"
        else:
            infura_network = (
                rpc.split("infura-")[1] if rpc.startswith("infura-") else None
            )
            if infura_network in ["mainnet", "rinkeby", "kovan", "ropsten"]:
                web3_rpc = "https://{net}.infura.io".format(net=infura_network)
            else:
                try:
                    host, port = rpc.split(":")
                    if rpctls:
                        web3_rpc = "https://{host}:{port}".format(host=host, port=port)
                    else:
                        web3_rpc = "http://{host}:{port}".format(host=host, port=port)
                except ValueError:
                    raise RPCError(
                        "Invalid RPC argument provided '{}', use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                            rpc
                        )
                    )
        if web3_rpc is None:
            raise RPCError(
                "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                    rpc
                )
            )
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc, request_kwargs={"timeout": 60}))
        if self.web3 is None:
            raise RPCError(
                "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                    rpc
                )
            )

        self.block_number = block_number or self.web3.eth.blockNumber

    def run(self, forever=True):
        self.logger.info("Starting scraping process")

        # TODO: Refactor try-except statements
        try:
            while forever:
                block = self.web3.eth.getBlock(
                    self.block_number, full_transactions=True
                )

                # If new block is not yet mined sleep and retry
                if block is None:
                    time.sleep(1)
                    continue

                self.logger.info(
                    "Processing block {block}".format(block=block.get("number"))
                )

                # Next block to scrape
                self.block_number += 1

                # For each transaction get the newly created accounts
                for t in block.get("transactions", []):
                    # If there is no to defined or to is reported as address(0x0) a new contract is created
                    if t.get("to", "0x0") != "0x0":
                        continue
                    try:
                        receipt = self.web3.eth.getTransactionReceipt(t["hash"])
                        address = str(receipt["contractAddress"])
                        report = self._run_mythril(contract_address=address)

                        issues_num = len(report.issues)
                        if issues_num:
                            self.logger.info("Found %s issue(s)", issues_num)
                            self.output.send(report=report, contract_address=address)
                        else:
                            self.logger.info("No issues found")
                    except Exception as e:
                        self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])
        except Exception as e:
            self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])

    def _run_mythril(self, contract_address=None):
        myth = Mythril(onchain_storage_access=True, enable_online_lookup=True)
        myth.set_api_rpc(rpc=self.rpc, rpctls=self.rpc_tls)

        self.logger.info("Analyzing %s", contract_address)
        myth.load_from_address(contract_address)
        self.logger.debug("Running Mythril")
        return myth.fire_lasers(
            strategy="dfs",
            modules=["ether_thief", "suicide"],
            address=contract_address,
            execution_timeout=45,
            create_timeout=10,
            max_depth=22,
            transaction_count=2,
            verbose_report=True,
        )
