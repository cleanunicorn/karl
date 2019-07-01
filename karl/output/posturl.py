import logging
import sys
import json
from urllib import request
from karl.output.output import OutputInterface
from mythril.analysis.report import Report
from karl.output.exceptions import PostURLInvalidURL


class PostURL(OutputInterface):
    def __init__(self, url=None, verbosity=logging.INFO):
        if url.startswith("file:/"):
            raise PostURLInvalidURL("Cannot post results to file:/ locations")
        self.url = url
        self.logger = logging.getLogger("PostURL")
        self.logger.setLevel(verbosity)
        self.logger.debug("PostURL enabled, sending to {url}".format(url=self.url))

    def report(self, report: Report, contract_address=""):
        try:
            req = request.Request(
                url=self.url, data=bytes(report.as_json(), "utf-8"), method="POST"
            )
            with request.urlopen(req) as f:
                self.logger.debug(f.read().decode("utf-8"))
        except Exception as e:
            self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])

    def vulnerable(self, exploits, contract_address):
        self.logger.debug(
            "Found {} exploits for {}.".format(len(exploits), contract_address)
        )

        try:
            req = request.Request(
                url=self.url,
                data=bytes(json.dumps(exploits, indent=4, sort_keys=True), "utf-8"),
                method="POST",
            )
            with request.urlopen(req) as f:
                self.logger.debug(f.read().decode("utf-8"))
        except Exception as e:
            self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])
