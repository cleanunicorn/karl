# SandboxBaseException
class SandboxBaseException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class BlockNumberInvalidException(SandboxBaseException):
    """Invalid specified block number"""

    def __init__(self):
        super().__init__("Invalid specified block number")


class ContractInvalidException(SandboxBaseException):
    """Invalid contract address"""

    def __init__(self):
        super().__init__("Invalid contract address")


class ReportInvalidException(SandboxBaseException):
    """Invalid report specified"""

    def __init__(self):
        super().__init__("Invalid report specified")


class RPCInvalidException(SandboxBaseException):
    """Invalid rpc endpoint specified"""

    def __init__(self):
        super().__init__("Invalid rpc endpoint specified")
