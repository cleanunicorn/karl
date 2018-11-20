import argparse
from mythril.mythril import Mythril

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
        "--rpctls",
        type=bool,
        default=False,
        help="RPC connection over TLS"
    )

    args = parser.parse_args()

if __name__ == "__main__":
    main()