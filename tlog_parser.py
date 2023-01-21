import socket
from tlog import Tlog
class TlogParser:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, validation_object, config):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.config = config
        # self.payment_tlog_dict = payment_tlog_dict
        
    def parse_tomcat_tlog(self, pname):
        
        tlog_object = Tlog(self.initializedPath_object, self.validation_object)
        
        tlog_object.get_tomcat_tlog(pname)
            # elif pname == "PACKS":
            #     tlog_object.get_tomcat_tlog("PACKS")
            # elif pname == "PRISMD":
            #     tlog_object.get_tomcat_tlog("PRISMD")