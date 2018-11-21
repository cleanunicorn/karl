from abc import ABC, abstractclassmethod


class OutputInterface(ABC):
    def __init__(self):
        super().__init__()

    @abstractclassmethod
    def send(self, report=dict(), contract_address=""):
        pass
