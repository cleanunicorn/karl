import logging
import json

from karl.output.output import OutputInterface


class Stdout(OutputInterface):
    def __init__(self, verbosity=logging.INFO):
        self.logger = logging.getLogger("Stdout")
        self.logger.setLevel(verbosity)
        self.logger.debug("Stdout enabled")

    def report(self, report, contract_address=""):
        self.logger.debug(
            "Found {} issues for {}.".format(len(report.issues), contract_address)
        )
        self.logger.info(report.as_text())

    def vulnerable(self, exploits, contract_address=""):
        self.logger.debug(
            "Found {} exploits for {}.".format(len(exploits), contract_address)
        )

        self.logger.info(json.dumps(exploits, indent=4, sort_keys=True))
