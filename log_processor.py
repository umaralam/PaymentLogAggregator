import logging
from tlog_parser import TlogParser


class PROCESSOR:
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, oarm_uid):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.oarm_uid = oarm_uid
        
    
    def process(self):
        tlogParser_object = TlogParser(self.initializedPath_object, self.validation_object)
        
        if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"]:
            logging.debug('griff tomcat tlog path exists.')
            if tlogParser_object.parse_griff_tomcat():
                pass
        else:
            pass
        if self.initializedPath_object.packs_tomcat_log_path_dict["packs_PACKS_T_LOG_APPENDER.FILE_log"]:
            pass
        else:
            pass
        