# Karl

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![CircleCI](https://circleci.com/gh/cleanunicorn/karl/tree/master.svg?style=shield)](https://circleci.com/gh/cleanunicorn/karl)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/53bb3ba0ed50447698e775edd397baa7)](https://www.codacy.com/app/lucadanielcostin/karl)
[![PyPI](https://img.shields.io/pypi/v/karl.svg)](https://pypi.org/project/karl/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=cleanunicorn_karl&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=cleanunicorn_karl)

A monitor for smart contracts that checks for security vulnerabilities

## Install

Get latest version of Karl.

```console
$ pip install --user karl
```

Install [Ganache](https://truffleframework.com/ganache) with [npm](https://www.npmjs.com/get-npm) if you want Karl to clone the blockchain and reduce false positives.

```console
$ npm i -g ganache-cli
```

## Demo

[![asciicast](https://asciinema.org/a/222983.svg)](https://asciinema.org/a/222983)

### Description
Karl will allow you to monitor a blockchain for vulnerable smart contracts that are being deployed.

It connects to the blockchain, monitors for new blocks and runs `mythril` for every new smart contract deployed.

The output can be displayed in the console, saved in files in a folder or POSTed to a URL.

Output can be:

- **stdout** just posting the results to standard output
- **folder** create a file for each vulnerable contract in a folder
- **posturl** POST the results to an http endpoint

### Help message

```console
$ karl --help
usage: karl.py [-h]
               [--rpc HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}]
               [--rpctls RPCTLS] [--block NUMBER]
               [--output Can be one of: stdout, posturl, folder]
               [--posturl POSTURL] [--folder-output FOLDER_OUTPUT] [--verbose]

Smart contract monitor using Mythril to find exploits

optional arguments:
  -h, --help            show this help message and exit

RPC options:
  --rpc HOST:PORT / ganache / infura-{mainnet, rinkeby, kovan, ropsten}
                        Custom RPC settings
  --rpctls RPCTLS       RPC connection over TLS
  --block NUMBER        Start from this block, otherwise start from latest

Output:
  --output Can be one of: stdout, posturl, folder
                        Where to send results
  --posturl POSTURL     Send results to a RESTful url [when using `--output
                        posturl`]
  --folder-output FOLDER_OUTPUT
                        Save files to this folder [when using `--output
                        folder`]

Verbosity:
  --verbose, -v         Set verbosity level
```

Mythril modules enabled

- ether_thief
- suicide

## Examples

### Running against the **mainnet**

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

### Running against **ganache** with **stdout** enabled

```console
$ karl --rpc ganache --output=stdout
INFO:mythril.mythril:Using RPC settings: ('localhost', 8545, False)
INFO:mythril.analysis.modules.suicide:Suicide module: Analyzing suicide instruction
POSSIBLE VULNERABILITY!
Initial balance = 100000000000000000000, final balance = 100999999999999985722

Type = VulnerabilityType.KILL_AND_WITHDRAW
Description = Looks line anyone can kill this contract and steal its balance.
Transactions = [{'from': '0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e', 'to': '0x2F2B2FE9C08d39b1F1C22940a9850e2851F40f99', 'data': '0xcbf0b0c0bebebebebebebebebebebebe1dF62f291b2E969fB0849d99D9Ce41e2F137006e', 'value': 0}]
```

### Running against **ganache** with **posturl** enabled

```console
$ karl --rpc ganache --output=posturl --posturl=http://localhost:8080
Posturl initialized
Running
Scraping block 5
Analyzing 0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70
```

And it will send this to the listening service

```console
$ nc -l 8080
POST / HTTP/1.1
Accept-Encoding: identity
Content-Type: application/x-www-form-urlencoded
Content-Length: 725
Host: localhost:8080
User-Agent: Python-urllib/3.7
Connection: close

{
    "error": null,
    "issues": [{
        "address": 722,
        "contract": "0x4b8e80acaE3F0db32e5d35925EfaA97D477dBb70",
        "debug": "Transaction Sequence: {'1': {'calldata': '0x56885cd8', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}, '4': {'calldata': '0x6c343ffe', 'call_value': '0x0', 'caller': '0xaaaaaaaabbbbbbbbbcccccccddddddddeeeeeeee'}}",
        "description": "Arbitrary senders other than the contract creator can withdraw ETH from the contract account without previously having sent an equivalent amount of ETH to it. This is likely to be a vulnerability.",
        "function": "withdrawfunds()",
        "max_gas_used": 1749,
        "min_gas_used": 1138,
        "swc-id": "105",
        "title": "Ether thief",
        "type": "Warning"
    }],
    "success": true
}
```

## Running against the **mainnet** with **folder** output enabled

```console
$ karl --rpc infura-mainnet --output folder
```

## Troubleshooting

### OpenSSL

If you get this error

```error
  #include <openssl/aes.h>
          ^~~~~~~~~~~~~~~
compilation terminated.
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

You must install the openssl source code libraries

#### Ubuntu

```console
$ sudo apt-get install libssl-dev
```

## Credits

This tool is inspired by [Bernhard's](https://github.com/b-mueller/) initial prototyping and it heavily uses his project [Myth](https://github.com/ConsenSys/mythril-classic).
