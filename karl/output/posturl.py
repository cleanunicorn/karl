from urllib import request
from karl.output.output import OutputInterface
from mythril.analysis.report import Report


class PostURL(OutputInterface):
    url = None

    def __init__(self, url=None):
        print("PostURL initialized")
        self.url = url

    def send(self, report: Report, contract_address=""):
        try:
            req = request.Request(
                url=self.url, data=bytes(report.as_json(), "utf-8"), method="POST"
            )
            with request.urlopen(req) as f:
                print(f.read().decode("utf-8"))
        except Exception as e:
            print("[POSTURL] Exception:", e)
