import time
import re
from mythril.mythril import Mythril
from web3 import Web3


class Karl:
    """
    Karl main interface class.
    """

    def __init__(self, rpc=None, rpctls=False, blockNumber=None, output=None):
        """
            Initialize Karl with the received parameters
        """
        if rpc is None:
            raise (
                Exception("Must provide a valid --rpc connection to an Ethereum node")
            )

        # Ethereum node to connect to
        self.rpc = rpc
        self.rpctls = rpctls
        # Send results to this output (could be stdout or restful url)
        self.output = output
        # What block number to start from
        self.blockNumber = None

        # Init web3 client
        web3rpc = None
        if rpc == "ganache":
            web3rpc = "http://127.0.0.1:8545"
        else:
            m = re.match(r"infura-(.*)", rpc)
            if m and m.group(1) in ["mainnet", "rinkeby", "kovan", "ropsten"]:
                web3rpc = "https://" + m.group(1) + ".infura.io"
            else:
                try:
                    host, port = rpc.split(":")
                    if rpctls:
                        web3rpc = "https://" + host + ":" + port
                    else:
                        web3rpc = "http://" + host + ":" + port
                except ValueError:
                    raise Exception(
                        "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                            rpc
                        )
                    )
        if web3rpc is None:
            raise Exception(
                "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                    rpc
                )
            )
        self.web3 = Web3(Web3.HTTPProvider(web3rpc, request_kwargs={"timeout": 60}))
        if self.web3 is None:
            raise (Exception("Must provide a valid web3 initialized interface"))

        if blockNumber is None:
            self.blockNumber = self.web3.eth.blockNumber

    def run(self, forever=True):
        print("Running")

        if forever:
            try:
                while True:
                    block = self.web3.eth.getBlock(
                        self.blockNumber, full_transactions=True
                    )

                    # If new block is not yet mined sleep and retry
                    if block is None:
                        time.sleep(5)
                        continue

                    # print(block)
                    print("Scraping block {}".format(block["number"]))

                    # Next block to scrape
                    self.blockNumber += 1

                    # For each transaction get the newly created accounts
                    for t in block["transactions"]:
                        if (not t["to"]) or (t["to"] == "0x0"):
                            try:
                                myth = Mythril(
                                    onchain_storage_access=True,
                                    enable_online_lookup=True,
                                )
                                myth.set_api_rpc(rpc=self.rpc, rpctls=self.rpctls)

                                receipt = self.web3.eth.getTransactionReceipt(t["hash"])
                                address = str(receipt["contractAddress"])
                                print("Analyzing {}".format(address))
                                myth.load_from_address(address)
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
                                if len(report.issues):
                                    self.output.send(
                                        report=report, contract_address=address
                                    )
                            except Exception as e:
                                print("[Karl] Exception:", e)
            except Exception as e:
                print("[Karl] Exception:", e)
