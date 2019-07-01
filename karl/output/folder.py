import logging
import json

from karl.output.output import OutputInterface


class Folder(OutputInterface):
    def __init__(self, folder_path=None, verbosity=logging.INFO):
        if folder_path is None:
            folder_path = "./"

        self.folder_path = folder_path
        self.logger = logging.getLogger("Folder")
        self.logger.setLevel(verbosity)
        self.logger.debug(
            "Folder enabled, saving output to {path}".format(path=self.folder_path)
        )

    def report(self, report=dict(), contract_address=""):
        self.logger.debug(
            "Found {} issues for {}".format(len(report.issues), contract_address)
        )

        file_path = "{path}/{filename}.txt".format(
            path=self.folder_path, filename=contract_address
        )
        with open(file_path, "w") as f:
            f.write(report.as_text())

    def vulnerable(self, exploits, contract_address):
        self.logger.debug(
            "Found {} exploits for {}.".format(len(exploits), contract_address)
        )

        file_path = "{path}/{filename}-exploits.json".format(
            path=self.folder_path, filename=contract_address
        )
        with open(file_path, "w") as f:
            f.write(json.dumps(exploits, indent=4, sort_keys=True))
