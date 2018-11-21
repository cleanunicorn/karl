from karl.output.output import OutputInterface


class Stdout(OutputInterface):
    def __init__(self):
        print("Stdout initialized")

    def send(self, report=dict(), contract_address=""):
        print("Found {} issues for {}".format(len(report.issues), contract_address))
        print(report.as_json())
