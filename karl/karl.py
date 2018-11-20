class Karl:
    """
    Karl main interface class.
    """

    mythril = None

    def __init__(self,
        mythril=None
    ):
        """
            Provide the initialized Mythril object
        """
        if mythril is None:
            print("Error, no mythril")

        self.mythril = mythril

    def run(self):
        address = "0xa0af62406d044e45cb9cb5eb0a04340d7395738d"
        self.mythril.load_from_address(address)
        report = self.mythril.fire_lasers(
            strategy='dfs',
            modules=['ether_thief', 'suicide'],
            address=address,
            execution_timeout=45,
            create_timeout=10,
            max_depth=22,
            transaction_count=2,
            verbose_report=True,
        )

        print("Found {} issues".format(len(report.issues)))
        print(report.as_json())
