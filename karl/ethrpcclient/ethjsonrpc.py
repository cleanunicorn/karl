"""This module contains a basic Ethereum RPC client.

It was changed to allow Infura connections.

This code is adapted from: https://github.com/ConsenSys/mythril
"""
import json
import logging

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError

from mythril.ethereum.interface.rpc.base_client import BaseClient
from mythril.ethereum.interface.rpc.exceptions import (
    BadJsonError,
    BadResponseError,
    BadStatusCodeError,
    ConnectionError,
)

log = logging.getLogger(__name__)

MAX_RETRIES = 3
JSON_MEDIA_TYPE = "application/json"


class EthJsonRpc(BaseClient):
    """Ethereum JSON-RPC client class."""

    def __init__(self, url=None):
        """

        :param url:
        """
        self.url = url
        self.session = requests.Session()
        self.session.mount(self.url, HTTPAdapter(max_retries=MAX_RETRIES))

    def _call(self, method, params=None, _id=1):
        """

        :param method:
        :param params:
        :param _id:
        :return:
        """
        params = params or []
        data = {"jsonrpc": "2.0", "method": method, "params": params, "id": _id}
        headers = {"Content-Type": JSON_MEDIA_TYPE}
        log.debug("rpc send: %s" % json.dumps(data))
        try:
            r = self.session.post(self.url, headers=headers, data=json.dumps(data))
        except RequestsConnectionError:
            raise ConnectionError
        if r.status_code / 100 != 2:
            raise BadStatusCodeError(r.status_code)
        try:
            response = r.json()
            log.debug("rpc response: %s" % response)
        except ValueError:
            raise BadJsonError(r.text)
        try:
            return response["result"]
        except KeyError:
            raise BadResponseError(response)

    def close(self):
        """Close the RPC client's session."""
        self.session.close()
