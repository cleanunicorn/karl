import argparse
import sys
from karl.output.stdout import Stdout
from karl.output.posturl import Posturl
from karl.karl import Karl


def main():
    parser = argparse.ArgumentParser(
        description="Smart contract monitor using Mythril to find exploits"
    )

    rpc = parser.add_argument_group("RPC options")
    rpc.add_argument(
        "--rpc",
        help="Custom RPC settings",
        metavar="HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}",
    )
    rpc.add_argument(
        "--rpctls", type=bool, default=False, help="RPC connection over TLS"
    )

    output = parser.add_argument_group("Output")
    output.add_argument(
        "--output",
        help="Where to send results",
        default="stdout",
        metavar="Can be one of: stdout, posturl",
    )
    output.add_argument("--posturl", help="Send results to a RESTful url")

    args = parser.parse_args()

    output_destination = None
    if args.output == "stdout":
        output_destination = Stdout()
    else:
        if args.output == "posturl":
            if args.posturl is None:
                print(
                    "No posturl specified. Set a destination with --posturl http://server:port/destination/url"
                )
                sys.exit()
            else:
                output_destination = Posturl(url=args.posturl)

    if output_destination is None:
        print("Must pick an output destination with --output")
        sys.exit()

    try:
        # Start Karl
        karl = Karl(rpc=args.rpc, rpctls=args.rpctls, output=output_destination)
        karl.run(forever=True)
    except Exception as e:
        print("[CLI] Exception:", e)


if __name__ == "__main__":
    main()
