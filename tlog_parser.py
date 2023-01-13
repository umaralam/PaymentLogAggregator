from tlog import Tlog
class TlogParser:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, validation_object):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        
    def parse_griff_tomcat(self):
        
        tlog_object = Tlog(self.initializedPath_object, self.validation_object)
        
        if tlog_object.get_griff_tomcat_tlog():
            pass