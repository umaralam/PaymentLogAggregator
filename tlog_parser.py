from tlog import Tlog
class TlogParser:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, input_date):
        
        self.initializedPath_object = initializedPath_object
        self.input_date = input_date
        
    def parse_griff_tomcat(self, validation_object):
        
        tlog_object = Tlog(self.initializedPath_object, self.input_date)
        
        if tlog_object.get_griff_tomcat_tlog(validation_object):
            pass