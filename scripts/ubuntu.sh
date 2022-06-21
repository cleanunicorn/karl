#!/bin/bash

apt update
apt upgrade
apt install -y python3 python3-pip libssl-dev 
pip3 install maturin

pip3 install -e .
karl --help

# Start Ganache locally, catch all errors and discard them because ganache isn't a requirement for Karl to work
./ganache &>/dev/null &

# You'll have to create an account on Infura for this, but it's free to use their APIs
# Replace with your given API URL
rpcurl=https://mainnet.infura.io/
karl --rpc $rpcurl --block=15003900