import time
import logging
import sys

from mythril.mythril import MythrilAnalyzer
from mythril.mythril import MythrilDisassembler
from mythril.ethereum.interface.rpc.client import EthJsonRpc

from web3 import Web3
from karl.exceptions import RPCError
from karl.sandbox.sandbox import Sandbox
from karl.sandbox.exceptions import SandboxBaseException


logging.basicConfig(level=logging.INFO)


class Karl:
    """
    Karl main interface class.
    """

    def __init__(
        self,
        rpc=None,
        rpc_tls=False,
        block_number=None,
        output=None,
        sandbox=True,
        verbosity=logging.INFO,
        timeout=600,
        tx_count=3,
        modules=["ether_thief", "selfdestruct"],
        onchain_storage=False,
        max_vm_depth=32,
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
        # Send results to this output (could be stdout or restful url)
        self.output = output

        # Sandbox options
        self.sandbox = sandbox

        # Scan options
        self.timeout = timeout
        self.tx_count = tx_count
        self.modules = modules
        self.onchain_storage = onchain_storage
        self.max_vm_depth = max_vm_depth

        # ! hack to stop mythril logging
        logging.getLogger("mythril").setLevel(logging.CRITICAL)

        # Set logging verbosity
        self.logger = logging.getLogger("Karl")
        self.logger.setLevel(verbosity)

        # Init web3 client
        web3_rpc = None
        eth_host = None
        eth_port = None
        eth_tls = rpc_tls
        if rpc == "ganache":
            web3_rpc = "http://127.0.0.1:8545"
            eth_host = "127.0.0.1"
            eth_port = "8545"
        else:
            infura_network = (
                rpc.split("infura-")[1] if rpc.startswith("infura-") else None
            )
            if infura_network in ["mainnet", "rinkeby", "kovan", "ropsten"]:
                web3_rpc = "https://{net}.infura.io".format(net=infura_network)
                eth_host = "{net}.infura.io".format(net=infura_network)
                eth_port = "443"
                eth_tls = True
            else:
                try:
                    host, port = rpc.split(":")
                    eth_host = host
                    eth_port = port
                    if rpc_tls:
                        web3_rpc = "https://{host}:{port}".format(host=host, port=port)
                    else:
                        web3_rpc = "http://{host}:{port}".format(host=host, port=port)
                except ValueError:
                    raise RPCError(
                        "Invalid RPC argument provided '{}', use "
                        "'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' "
                        "or HOST:PORT".format(rpc)
                    )
        if web3_rpc is None:
            raise RPCError(
                "Invalid RPC argument provided {}, use "
                "'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' "
                "or HOST:PORT".format(rpc)
            )
        self.web3_rpc = web3_rpc
        self.eth_host = eth_host
        self.eth_port = int(eth_port)
        self.rpc_tls = eth_tls
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc, request_kwargs={"timeout": 60}))
        if self.web3 is None:
            raise RPCError(
                "Invalid RPC argument provided {}, use "
                "'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' "
                "or HOST:PORT".format(rpc)
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
                    # If there is no to defined, or to is reported as address(0x0)
                    # a new contract was created
                    if (t["to"] is not None) and (t["to"] != "0x0"):
                        continue
                    try:
                        receipt = self.web3.eth.getTransactionReceipt(t["hash"])
                        if (receipt is None) or (
                            receipt.get("contractAddress", None) is None
                        ):
                            self.logger.error(
                                "Receipt invalid for hash = {}".format(t["hash"].hex())
                            )
                            self.logger.error(receipt)
                            continue
                        address = str(receipt.get("contractAddress", None))
                        report = self._run_mythril(contract_address=address)

                        issues_num = len(report.issues)
                        if issues_num:
                            self.logger.info("Found %s issue(s)", issues_num)
                            self.output.report(report=report, contract_address=address)

                            if self.sandbox:
                                self.logger.info("Firing up sandbox tester")
                                exploits = self._run_sandbox(
                                    block_number=block.get("number", None),
                                    contract_address=address,
                                    report=report,
                                    rpc=self.web3_rpc,
                                )
                                if len(exploits) > 0:
                                    self.output.vulnerable(
                                        exploits=exploits, contract_address=address
                                    )
                                else:
                                    pass
                        else:
                            self.logger.info("No issues found")
                    except Exception as e:
                        self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])
        except Exception as e:
            self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])

    def _run_mythril(self, contract_address=None):
        eth_json_rpc = EthJsonRpc(
            host=self.eth_host, port=self.eth_port, tls=self.rpc_tls
        )

        disassembler = MythrilDisassembler(
            eth=eth_json_rpc,
            solc_version=None,
            solc_args=None,
            enable_online_lookup=True,
        )

        disassembler.load_from_address(contract_address)

        analyzer = MythrilAnalyzer(
            strategy="bfs",
            onchain_storage_access=self.onchain_storage,
            disassembler=disassembler,
            address=contract_address,
            execution_timeout=self.timeout,
            max_depth=self.max_vm_depth,
            create_timeout=10,
        )

        self.logger.info("Analyzing %s", contract_address)
        self.logger.debug("Running Mythril")

        return analyzer.fire_lasers(
            modules=self.modules, transaction_count=self.tx_count
        )

    def _run_sandbox(
        self, block_number=None, contract_address=None, report=None, rpc=None
    ):
        try:
            sandbox = Sandbox(
                block_number=block_number,
                contract_address=contract_address,
                report=report,
                rpc=rpc,
                verbosity=self.logger.level,
            )
        except SandboxBaseException as e:
            self.logger.error(e)

        return sandbox.check_exploitability()
