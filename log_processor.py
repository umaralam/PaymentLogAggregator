from collections import defaultdict
import json
import logging
import socket
from tlog_parser import TlogParser


class PROCESSOR:
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, oarm_uid, config):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.oarm_uid = oarm_uid
        self.config = config
        
        # self.payment_tlog_dict = {}
        
    
    def process(self):
        tlogParser_object = TlogParser(self.initializedPath_object, self.validation_object, self.config)
        
        hostname = socket.gethostname()
        for pname in self.config[hostname]:
            if pname == "GRIFF" and self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"]:
                logging.debug('griff tomcat tlog path exists.')
                if tlogParser_object.parse_tomcat_tlog(pname):
                    pass
            elif pname == "PACKS" and self.initializedPath_object.packs_tomcat_log_path_dict["packs_PACKS_T_LOG_APPENDER.FILE_log"]:
                logging.debug('packs tomcat tlog path exists.')
                if tlogParser_object.parse_tomcat_tlog(pname):
                    pass
            else:
                pass
        
        # json_object = json.dumps(self.payment_tlog_dict)
        
        # logging.info('tlogs: %s', str(self.griff_tlog_dict["PACKS"]).replace("'", '"'))
        # logging.info('json tlog data: %s',json.dumps(self.payment_tlog_dict))
        