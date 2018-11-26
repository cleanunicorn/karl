# Karl

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CircleCI](https://circleci.com/gh/cleanunicorn/karl/tree/master.svg?style=shield)](https://circleci.com/gh/cleanunicorn/karl) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/53bb3ba0ed50447698e775edd397baa7)](https://www.codacy.com/app/lucadanielcostin/karl)
[![PyPI](https://img.shields.io/pypi/v/karl.svg)](https://pypi.org/project/karl/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A monitor for smart contracts that checks for security vulnerabilities

## Install

```console
$ pip install --user karl
```

Will make `karl` available in your shell.

### Description
Karl will allow you to monitor a blockchain for vulnerable smart contracts that are being deployed.

It connects to the blockchain, monitors for new blocks and runs `mythril` for every new smart contract deployed.

The output can be displayed in the console or POSTed to a URL.

### Help message

```console
$ karl --help
usage: karl [-h]
            [--rpc HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}]
            [--rpctls RPCTLS] [--output Can be one of: stdout, posturl]
            [--posturl POSTURL]

Smart contract monitor using Mythril to find exploits

optional arguments:
  -h, --help            show this help message and exit

RPC options:
  --rpc HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}
                        Custom RPC settings
  --rpctls RPCTLS       RPC connection over TLS

Output:
  --output Can be one of: stdout, posturl
                        Where to send results
  --posturl POSTURL     Send results to a RESTful url
```

Mythril modules enabled
  - ether_thief
  - suicide

## Examples

### Running against the main net

```console
$ karl --rpc infura-mainnet --rpctls true      
Stdout initialized
Running
Scraping block 6745471
Scraping block 6745472
Scraping block 6745473
Analyzing 0xf8c065bB1DafC99eE5476a2b675FAC4a036a4B07
Scraping block 6745474
Analyzing 0xC9e044D76f211E84bA651b30BBA86758ca8017c7
Scraping block 6745475
Scraping block 6745476
Scraping block 6745477
Analyzing 0x19427b8FD32dfEc78393517Da416bC5C583E6065
```

### Running against ganache with standard output enabled
```console
$ karl --rpc ganache --output=stdout
Stdout initialized
Running
Scraping block 5
Analyzing 0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70
Found 1 issues for 0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70
==== Ether thief ====
SWC ID: 105
Type: Warning
Contract: 0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70
Function name: withdrawfunds()
PC address: 722
Estimated Gas Usage: 1138 - 1749
Arbitrary senders other than the contract creator can withdraw ETH from the contract account without previously having sent an equivalent amount of ETH to it. This is likely to be a vulnerability.
--------------------
--------------------
DEBUGGING INFORMATION:

Transaction Sequence: {'1': {'calldata': '0x56885cd8', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}, '4': {'calldata': '0x6c343ffe', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}}
```

### Running against ganache with posturl enabled

```console
$ karl --rpc ganache --output=posturl --posturl=http://localhost:8080
Posturl initialized
Running
Scraping block 5
Analyzing 0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70
```

And it will send this to the listening service

```
POST / HTTP/1.1
Accept-Encoding: identity
Content-Type: application/x-www-form-urlencoded
Content-Length: 725
Host: localhost:8080
User-Agent: Python-urllib/3.7
Connection: close

{"error": null, "issues": [{"address": 722, "contract": "0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70", "debug": "Transaction Sequence: {'1': {'calldata': '0x56885cd8', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}, '4': {'calldata': '0x6c343ffe', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}}", "description": "Arbitrary senders other than the contract creator can withdraw ETH from the contract account without previously having sent an equivalent amount of ETH to it. This is likely to be a vulnerability.", "function": "withdrawfunds()", "max_gas_used": 1749, "min_gas_used": 1138, "swc-id": "105", "title": "Ether thief", "type": "Warning"}], "success": true}
```
