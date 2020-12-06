class NekoException(Exception):
    """ Base exception class for nekoslife.py """

    pass


class WaifuException(Exception):
    """ Base exception class for waifupics.py """

    pass


class NothingFound(NekoException):
    """ API did not return anything """

    pass


class EmptyArgument(NekoException):
    """ When an argument is not defined """

    pass


class InvalidArgument(NekoException):
    """ Invalid argument given """

    pass
