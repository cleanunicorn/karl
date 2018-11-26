from setuptools import setup, find_packages
import os


def read_file(fname):
    """
    return file contents
    :param fname: path relative to setup.py
    :return: file contents
    """
    with open(os.path.join(os.path.dirname(__file__), fname), "r") as fd:
        return fd.read()


setup(
    name="karl",
    version="0.2.8",
    license="MIT",
    author="Daniel Luca",
    author_email="daniel.luca@consensys.net",
    long_description=read_file("Readme.md") if os.path.isfile("Readme.md") else "",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=read_file("requirements.txt").split("\n"),
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["karl=karl.interfaces.cli:main"]},
    credits=["Bernhard Mueller <bernhard.mueller@mithril.ai>"],
)
