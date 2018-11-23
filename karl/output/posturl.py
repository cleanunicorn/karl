import logging
import sys
from urllib import request
from karl.output.output import OutputInterface
from mythril.analysis.report import Report
from karl.output.exceptions import PostURLInvalidURL


class PostURL(OutputInterface):
    def __init__(self, url=None, verbosity=logging.NOTSET):
        if url.startswith("file:/"):
            raise PostURLInvalidURL("Cannot post results to file:/ locations")
        self.url = url
        self.logger = logging.getLogger("PostURL")
        self.logger.setLevel(verbosity)
        self.logger.debug("PostURL enabled, sending to {url}".format(url=self.url))

    def send(self, report: Report, contract_address=""):
        try:
            req = request.Request(
                url=self.url, data=bytes(report.as_json(), "utf-8"), method="POST"
            )
            with request.urlopen(req) as f:
                self.logger.debug(f.read().decode("utf-8"))
        except Exception as e:
            self.logger.error("Exception: %s\n%s", e, sys.exc_info()[2])
