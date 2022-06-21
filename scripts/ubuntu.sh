#!/bin/bash

apt update
apt upgrade
apt install -y python3 python3-pip libssl-dev 
pip3 install maturin

pip3 install -e .
karl --help

karl --rpc https://mainnet.infura.io/ --block=9003035