import logging
import json
import sys
from karl.sandbox.exceptions import (
    BlockNumberInvalidException,
    ContractInvalidException,
    ReportInvalidException,
    RPCInvalidException,
)
from karl.sandbox.vulnerability import Vulnerability
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
        exploits = []

        hacker = Web3.toChecksumAddress(Ganache.accounts[9])
        feeder = Web3.toChecksumAddress(Ganache.accounts[8])

        # Parse report and generate vulnerability list
        vulns = []
        for i in range(0, len(self.report.issues)):
            issue = self.report.sorted_issues()[i]

            if "withdraw its balance" in issue["description"]:
                vuln_type = "KILL_AND_WITHDRAW"
                description = (
                    "Looks line anyone can kill this contract and steal its balance."
                )
            elif "withdraw ETH" in issue["description"]:
                vuln_type = "ETHER_THEFT"
                description = "Looks like anyone can withdraw ETH from this contract."
            else:
                vuln_type = "KILL_ONLY"
                description = "Anybody can accidentally kill this contract."

            transactions = issue["tx_sequence"]

            # Build formatted transaction list
            transaction_list = []
            for i in range(0, len(transactions["steps"])):
                t = transactions["steps"][i]
                tx = {
                    "from": hacker,
                    "to": self.contract_address,
                    # If a transaction has an argument that points
                    # to the hacker replace that
                    "data": t["input"].replace(
                        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", hacker[2:]
                    ),
                    "value": int(t["value"], 16),
                }
                transaction_list.append(tx)

            vulns.append(
                Vulnerability(
                    kind=vuln_type,
                    description=description,
                    transactions=transaction_list,
                )
            )

        # Test each vulnerability
        for i, v in enumerate(vulns):
            self.logger.debug(v)

            # Set up new forked chain
            self.logger.debug("Forking chain at block {}".format(self.block_number))
            ganache = Ganache(
                internal_port=9545, rpc=self.rpc, verbosity=self.verbosity
            )
            w3 = Web3(HTTPProvider(ganache.internal_rpc))
            initial_balance = w3.eth.getBalance(hacker)

            # Force feed ether
            """
            pragma solidity 0.5.1;

            contract SelfDestructor {
                constructor(address payable _receiver) public payable {
                    selfdestruct(_receiver);
                }
            }
            """
            self.logger.debug("Feeding eth to contract")
            tx_feed_args = {
                "from": feeder,
                "data": "0x6080604052604051602080604c833981018060405260208110156021"
                "57600080fd5b81019080805190602001909291905050508073"
                "ffffffffffffffffffffffffffffffffffffffff16fffe"
                # Add the address of the contract that is force fed
                + str(24 * "0") + self.contract_address[2:].lower(),
                # Feed with 1 ETH
                "value": 10 ** 18,
            }
            self.logger.debug("Transaction = {}".format(tx_feed_args))
            tx_feed_hash = w3.eth.sendTransaction(tx_feed_args)
            tx_feed_receipt = w3.eth.waitForTransactionReceipt(tx_feed_hash, timeout=10)
            self.logger.debug("Fed ether in receipt = {}".format(tx_feed_receipt))

            # Sending transactions to chain
            for tx in v.transactions:
                self.logger.debug("Sending transaction")
                self.logger.debug("Transaction = {}".format(tx))
                try:
                    tx_hash = w3.eth.sendTransaction(tx)
                    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
                    self.logger.debug("Receipt = {}".format(tx_receipt))
                except Exception as e:
                    self.logger.error(
                        "Exception raised while exploiting the contract: %s\n%s",
                        e,
                        sys.exc_info()[2],
                    )

            final_balance = w3.eth.getBalance(hacker)
            if final_balance > initial_balance:
                print("Confirmed vulnerability!")
                print(
                    "Initial balance = {}, final balance = {}".format(
                        initial_balance, final_balance
                    )
                )
                v.confirmed = True
                print(v)
                exploits.append(self.report.sorted_issues()[i])
            else:
                print("Doesn't have more ether after exploit")

            # Stop forked chain
            self.logger.debug("Stopping forked chain")
            ganache.stop()

        return exploits
