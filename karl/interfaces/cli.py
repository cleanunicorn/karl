import argparse
import sys
import logging
from karl.version import __version__
from karl.output.stdout import Stdout
from karl.output.posturl import PostURL
from karl.output.folder import Folder
from karl.karl import Karl


def main():
    parser = argparse.ArgumentParser(
        description="Smart contract monitor using Mythril to find exploits"
    )

    # Ethereum node
    rpc = parser.add_argument_group("RPC options")
    rpc.add_argument(
        "--rpc",
        help="Custom RPC settings",
        metavar="HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}",
    )
    rpc.add_argument(
        "--rpc_tls", type=bool, default=False, help="RPC connection over TLS"
    )
    rpc.add_argument(
        "--block",
        type=int,
        help="Start from this block, otherwise start from latest",
        metavar="NUMBER",
    )

    # Output
    output = parser.add_argument_group("Output")
    output.add_argument(
        "--output",
        help="Where to send results",
        default="stdout",
        metavar="Can be one of: stdout, posturl, folder",
    )
    output.add_argument(
        "--posturl",
        help="Send results to a RESTful url [when using `--output posturl`]",
    )
    output.add_argument(
        "--folder-output",
        help="Save files to this folder [when using `--output folder`]",
    )

    # Sandbox
    sandbox_options = parser.add_argument_group("Sandbox")
    sandbox_options.add_argument(
        "--sandbox",
        help="Test found transactions in a Ganache sandbox",
        default=False,
        type=str2bool,
    )

    # Verbosity
    verbosity = parser.add_argument_group("Verbosity")
    verbosity.add_argument(
        "--verbose", "-v", action="count", help="Set verbose", default=4
    )

    # Version
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    # Parse cli args
    args = parser.parse_args()

    # Set verbosity
    verbosity_default = logging.NOTSET
    verbosity_levels = {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG,
    }
    verbose = (
        len(verbosity_levels)
        if args.verbose is not None and args.verbose > len(verbosity_levels)
        else args.verbose
    )

    output_destination = None
    if args.output == "stdout":
        output_destination = Stdout(
            verbosity=verbosity_levels.get(verbose, verbosity_default)
        )
    elif args.output == "posturl":
        if args.posturl is None:
            print(
                "No posturl specified. Set a destination with --posturl http://server:port/destination/url"
            )
            sys.exit()
        else:
            output_destination = PostURL(
                url=args.posturl,
                verbosity=verbosity_levels.get(verbose, verbosity_default),
            )
    elif args.output == "folder":
        output_destination = Folder(
            folder_path=args.folder_output,
            verbosity=verbosity_levels.get(verbose, verbosity_default),
        )

    if output_destination is None:
        print("Must pick an output destination with --output")
        sys.exit()

    # Start Karl
    try:
        karl = Karl(
            rpc=args.rpc,
            rpc_tls=args.rpc_tls,
            output=output_destination,
            verbosity=verbosity_levels.get(verbose, verbosity_default),
            block_number=args.block,
            sandbox=args.sandbox,
        )
        karl.run(forever=True)
    except Exception as e:
        print("[CLI] Exception:", e)


def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


if __name__ == "__main__":
    main()
