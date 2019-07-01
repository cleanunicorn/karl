from abc import ABC, abstractclassmethod
from mythril.analysis.report import Report


class OutputInterface(ABC):
    def __init__(self):
        super().__init__()

    @abstractclassmethod
    def report(self, report: Report, contract_address=""):
        pass

    @abstractclassmethod
    def vulnerable(self, exploits=None, contract_address=None):
        pass
