import logging
import json
from karl.sandbox.exceptions import (
    BlockNumberInvalidException,
    ContractInvalidException,
    ReportInvalidException,
    RPCInvalidException,
)
from karl.sandbox.vulnerability import Vulnerability, VulnerabilityType
from karl.sandbox.ganache import Ganache
from web3 import Web3, HTTPProvider


class Sandbox:
    def __init__(
        self,
        block_number=None,
        contract_address=None,
        report=None,
        rpc=None,
        verbosity=logging.NOTSET,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(verbosity)
        self.verbosity = verbosity

        if rpc is None:
            raise (RPCInvalidException)
        self.rpc = rpc

        if block_number is None:
            raise (BlockNumberInvalidException)
        self.block_number = block_number

        if contract_address is None:
            raise (ContractInvalidException)
        self.contract_address = contract_address

        if report is None:
            raise (ReportInvalidException)
        self.report = report

    def check_exploitability(self):
        exploitable = False

        # Parse report and generate vulnerability list
        vulns = []
        for i in range(0, len(self.report.issues)):
            issue = self.report.sorted_issues()[i]

            if "withdraw its balance" in issue["description"]:
                vuln_type = VulnerabilityType.KILL_AND_WITHDRAW
                description = (
                    "Looks line anyone can kill this contract and steal its balance."
                )
            elif "withdraw ETH" in issue["description"]:
                vuln_type = VulnerabilityType.ETHER_THEFT
                description = "Looks like anyone can withdraw ETH from this contract."
            else:
                vuln_type = VulnerabilityType.KILL_ONLY
                description = "Anybody can accidentally kill this contract."

            tx = issue["debug"].replace("\n", " ").replace("'", '"')
            transactions = json.loads(tx)

            # Build formatted transaction list
            transaction_list = []
            for _, t in transactions.items():
                hacker = Web3.toChecksumAddress(Ganache.accounts[0])

                tx = {
                    "from": hacker,
                    "to": self.contract_address,
                    # If a transaction has an argument that points
                    # to the hacker replace that
                    "data": t["calldata"].replace(
                        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", hacker[2:]
                    ),
                    "value": int(t["call_value"], 16),
                }
                transaction_list.append(tx)

            vulns.append(
                Vulnerability(
                    type=vuln_type,
                    description=description,
                    transactions=transaction_list,
                )
            )

        # Test each vulnerability
        for v in range(0, len(vulns)):
            self.logger.debug(vulns[v])

            # Set up new forked chain
            self.logger.debug("Forking chain at block {}".format(self.block_number))
            ganache = Ganache(
                block_number=self.block_number, rpc=self.rpc, verbosity=self.verbosity
            )
            w3 = Web3(HTTPProvider(ganache.internal_rpc))
            hacker = Web3.toChecksumAddress(ganache.accounts[0])
            initial_balance = w3.eth.getBalance(hacker)

            # Sending transactions to chain
            for tx in vulns[v].transactions:
                self.logger.debug("Sending transaction")
                self.logger.debug("Transaction = {}".format(tx))
                tx_hash = w3.eth.sendTransaction(tx)
                tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
                self.logger.debug("Receipt = {}".format(tx_receipt))

            final_balance = w3.eth.getBalance(hacker)
            if final_balance > initial_balance:
                print("POSSIBLE VULNERABILITY!")
                print(
                    "Initial balance = {}, final balance = {}".format(
                        initial_balance, final_balance
                    )
                )
                print(vulns[v])
                exploitable = True
            else:
                print("Doesn't have more ether after exploit")

            # Stop forked chain
            self.logger.debug("Stopping forked chain")
            ganache.stop()

        return exploitable
