from distutils.core import setup
import os

setup(
    name="karl",
    version="0.2",
    packages=["karl"],
    license="MIT",
    author="Daniel Luca",
    author_email="daniel.luca@mythril.ai",
    long_description=read_file("README.md") if os.path.isfile("README.md") else "",
    long_description_content_type="text/markdown",
    credits="Bernhardt Muller",
)
