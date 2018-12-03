class SandboxBaseException(Exception):
    pass


class BlockNumberInvalidException(SandboxBaseException):
    """Invalid specified block number"""


class ContractInvalidException(SandboxBaseException):
    """Invalid contract address"""


class ReportInvalidException(SandboxBaseException):
    """Invalid report specified"""


class RPCInvalidException(SandboxBaseException):
    """Invalid rpc endpoint specified"""
