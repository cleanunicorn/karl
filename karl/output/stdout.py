import logging
from karl.output.output import OutputInterface


class Stdout(OutputInterface):
    def __init__(self, verbosity=logging.NOTSET):
        self.logger = logging.getLogger("Stdout")
        self.logger.setLevel(verbosity)
        self.logger.debug("Stdout enabled")

    def send(self, report=dict(), contract_address=""):
        self.logger.debug(
            "Found {} issues for {}".format(len(report.issues), contract_address)
        )
        self.logger.info(report.as_text())
