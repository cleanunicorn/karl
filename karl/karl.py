class Karl:
    """
    Karl main interface class.
    """

    mythril = None
    web3 = None
    blockNumber = None

    def __init__(self,
        mythril=None,
        web3=None,
        blockNumber=None,
    ):
        """
            Provide the initialized Mythril object
        """
        if mythril is None:
            raise(Exception("Must provide a valid Mythril initialized interface"))

        if web3 is None:
            raise (Exception("Must provide a valid web3 initialized interface"))
            
        if blockNumber is None:
            self.blockNumber = web3.eth.blockNumber

        self.mythril = mythril
        self.web3 = web3

    def run(self):
        print("Running")

        try:
            block = self.web3.eth.getBlock(
                self.blockNumber,
                full_transactions=True,
            )
            print(block)
            # address = "0x74FC6891EF3c2B4D22F594FDD9DeA5c9F1a123a9"
            # self.mythril.load_from_address(address)
            # report = self.mythril.fire_lasers(
            #     strategy='dfs',
            #     modules=['ether_thief', 'suicide'],
            #     address=address,
            #     execution_timeout=45,
            #     create_timeout=10,
            #     max_depth=22,
            #     transaction_count=2,
            #     verbose_report=True,
            # )

            # print("Found {} issues".format(len(report.issues)))
            # print(report.as_json())
        except Exception as e:
            print("[Karl] Exception:", e)