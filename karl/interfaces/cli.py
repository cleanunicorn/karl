import argparse
import re
from mythril.mythril import Mythril
from karl.karl import Karl
from web3 import Web3


def main():
    parser = argparse.ArgumentParser(
        description="Smart contract monitor using Mythril to find exploits"
    )

    rpc = parser.add_argument_group("RPC options")
    rpc.add_argument(
        "--rpc",
        help="Custom RPC settings",
        metavar="HOST:PORT / ganache / infura-[mainnet, rinkeby, kovan, ropsten]",
    )
    rpc.add_argument(
        "--rpctls", type=bool, default=False, help="RPC connection over TLS"
    )

    args = parser.parse_args()

    try:
        # Start Karl
        karl = Karl(rpc=args.rpc, rpctls=args.rpctls)
        karl.run(forever=True)
    except Exception as e:
        print("[CLI] Exception:", e)


if __name__ == "__main__":
    main()
