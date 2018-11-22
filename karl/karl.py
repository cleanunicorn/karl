import time
import re
import logging
import sys

from mythril.mythril import Mythril
from web3 import Web3


logging.basicConfig(level=logging.INFO)


class Karl:
    """
    Karl main interface class.
    """

    def __init__(self, rpc=None, rpctls=False, block_number=None, output=None):
        """
            Initialize Karl with the received parameters
        """
        if rpc is None:
            raise (
                Exception("Must provide a valid --rpc connection to an Ethereum node")
            )

        # Ethereum node to connect to
        self.rpc = rpc
        self.rpc_tls = rpctls
        # Send results to this output (could be stdout or restful url)
        self.output = output
        self.logger = logging.getLogger("Karl")

        # Init web3 client
        web3_rpc = None
        if rpc == "ganache":
            web3_rpc = "http://127.0.0.1:8545"
        else:
            m = re.match(r"infura-(.*)", rpc)
            if m and m.group(1) in ["mainnet", "rinkeby", "kovan", "ropsten"]:
                web3_rpc = "https://" + m.group(1) + ".infura.io"
            else:
                try:
                    host, port = rpc.split(":")
                    if rpctls:
                        web3_rpc = "https://" + host + ":" + port
                    else:
                        web3_rpc = "http://" + host + ":" + port
                except ValueError:
                    raise Exception(
                        "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                            rpc
                        )
                    )
        if web3_rpc is None:
            raise Exception(
                "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                    rpc
                )
            )
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc, request_kwargs={"timeout": 60}))
        if self.web3 is None:
            raise (Exception("Must provide a valid web3 initialized interface"))

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
                    time.sleep(5)
                    continue

                self.logger.info("Scraping block %s", block["number"])

                # Next block to scrape
                self.block_number += 1

                # For each transaction get the newly created accounts
                for t in block["transactions"]:
                    if t["to"] and t["to"] != "0x0":
                        continue
                    try:
                        myth = Mythril(
                            onchain_storage_access=True,
                            enable_online_lookup=True,
                        )
                        myth.set_api_rpc(rpc=self.rpc, rpctls=self.rpc_tls)

                        receipt = self.web3.eth.getTransactionReceipt(t["hash"])
                        address = str(receipt["contractAddress"])
                        self.logger.info("Analyzing %s", address)
                        myth.load_from_address(address)
                        self.logger.info("Executing Mythril")
                        report = myth.fire_lasers(
                            strategy="dfs",
                            modules=["ether_thief", "suicide"],
                            address=address,
                            execution_timeout=45,
                            create_timeout=10,
                            max_depth=22,
                            transaction_count=2,
                            verbose_report=True,
                        )

                        issues_num = len(report.issues)
                        if issues_num:
                            self.logger.info("Found %s issues", issues_num)
                            self.output.send(
                                report=report, contract_address=address
                            )
                    except Exception as e:
                        self.logger.error("[Karl] Exception: %s\n%s", e, sys.exc_info()[2])
        except Exception as e:
            self.logger.error("[Karl] Exception: %s\n%s", e, sys.exc_info()[2])
