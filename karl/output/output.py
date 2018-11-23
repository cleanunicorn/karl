from abc import ABC, abstractclassmethod
from mythril.analysis.report import Report


class OutputInterface(ABC):
    def __init__(self):
        super().__init__()

    @abstractclassmethod
    def send(self, report: Report, contract_address=""):
        pass
