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
        # Initialize Mythril
        myth = Mythril(onchain_storage_access=True, enable_online_lookup=True)
        myth.set_api_rpc(rpc=args.rpc, rpctls=args.rpctls)

        # Initialize Web3 client
        web3rpc = None
        if args.rpc == "ganache":
            web3rpc = "http://127.0.0.1:8545"
        else:
            m = re.match(r"infura-(.*)", args.rpc)
            if m and m.group(1) in ["mainnet", "rinkeby", "kovan", "ropsten"]:
                web3rpc = "https://" + m.group(1) + ".infura.io"
            else:
                try:
                    host, port = args.rpc.split(":")
                    if args.rpctls:
                        web3rpc = "https://" + host + ":" + port
                    else:
                        web3rpc = "http://" + host + ":" + port
                except ValueError:
                    raise Exception(
                        "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                            args.rpc
                        )
                    )

        if web3rpc is None:
            raise Exception(
                "Invalid RPC argument provided {}, use 'ganache', 'infura-[mainnet, rinkeby, kovan, ropsten]' or HOST:PORT".format(
                    args.rpc
                )
            )

        web3 = Web3(Web3.HTTPProvider(web3rpc, request_kwargs={"timeout": 60}))

        karl = Karl(mythril=myth, web3=web3)

        karl.run()

    except Exception as e:
        print("[CLI] Exception:", e)


if __name__ == "__main__":
    main()
