from enum import Enum


class logMode(Enum):
    IS_DEBUG_DATA = "txn"
    IS_DEBUG_ALL = "all"
    IS_DEBUG_ERROR = "error"

class Griff_St_SString(Enum):
    #griff search string to get initial index
    search_string_1 = "Processor Called"
    search_string_2 = "Calling packs api with parameter operatorName"

class Griff_En_SString(Enum):
    search_string_1 = "Request completed"

class Packs_St_SString(Enum):
    search_string_1 = "Processor Called"