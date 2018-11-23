class OutputBaseException(Exception):
    pass


class PostURLBaseException(OutputBaseException):
    pass


class PostURLInvalidURL(PostURLBaseException):
    pass
