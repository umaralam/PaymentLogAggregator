from enum import Enum


class logMode(Enum):
    IS_DEBUG_DATA = "txn"
    IS_DEBUG_ALL = "all"
    IS_DEBUG_ERROR = "error"