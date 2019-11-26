from setuptools import setup, find_packages
from karl.version import __version__
from setuptools.command.install import install
import sys
import os
import shutil
import pathlib
import atexit


def read_file(fname):
    """
    return file contents
    :param fname: path relative to setup.py
    :return: file contents
    """
    with open(os.path.join(os.path.dirname(__file__), fname), "r") as fd:
        return fd.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")

        if tag != __version__:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, __version__
            )
            sys.exit(info)


def copySignatures():
    """Check if signatures.db is already installed and copy it in the home dir if not."""
    mythril_path = os.path.join(pathlib.Path.home(), ".mythril")
    signatures_path = os.path.join(mythril_path, "signatures.db")
    if not os.path.exists(mythril_path):
        print("Mythril db folder does not exist, creating...")
        try:
            os.mkdir(mythril_path)
        except OSError:
            print("Could not create Mythril db folder")
            print("Manually create ~/.mythril/signatures.db")

    if not os.path.exists(signatures_path):
        print("Signatures does not exist, creating...")
        try:
            shutil.copyfile("./signatures/signatures.db", signatures_path)
        except Exception as e:
            print(sys.exc_info()[0])
            print(type(e))  # the exception instance
            print(e.args)  # arguments stored in .args
            print(e)

            print(
                "Could not copy signatures.db file to {signatures_dest}".format(
                    signatures_dest=signatures_path
                )
            )
            print("Manually create ~/.mythril/signatures.db")


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def __init__(self, *args, **kwargs):
        super(PostInstallCommand, self).__init__(*args, **kwargs)
        atexit.register(copySignatures)


setup(
    name="karl",
    version=__version__,
    license="MIT",
    author="Daniel Luca",
    author_email="daniel.luca@consensys.net",
    long_description=read_file("Readme.md") if os.path.isfile("Readme.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    package_data={"karl": ["signatures/signatures.db"]},
    include_package_data=True,
    install_requires=read_file("requirements.txt").split("\n"),
    entry_points={"console_scripts": ["karl=karl.interfaces.cli:main"]},
    credits=["Bernhard Mueller <bernhard.mueller@mithril.ai>"],
    cmdclass={
        "verify": VerifyVersionCommand,
        "install": PostInstallCommand,
    },
)
