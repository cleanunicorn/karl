import argparse
from mythril.mythril import Mythril
from karl.karl import Karl


def main():
    parser = argparse.ArgumentParser(
        description="Smart contract monitor using Mythril to find exploits"
    )

    rpc = parser.add_argument_group("RPC options")
    rpc.add_argument(
        "--rpc",
        help="Custom RPC settings",
        metavar="HOST:PORT / ganache / infura-[network_name]",
    )
    rpc.add_argument(
        "--rpctls", type=bool, default=False, help="RPC connection over TLS"
    )

    args = parser.parse_args()

    try:
        myth = Mythril(
            onchain_storage_access=True,
            enable_online_lookup=True
        )
        myth.set_api_rpc(rpc=args.rpc, rpctls=args.rpctls)

        karl = Karl(
            mythril=myth,
        )

        karl.run()

    except Exception as e:
        print("Exception ", e)


if __name__ == "__main__":
    main()
