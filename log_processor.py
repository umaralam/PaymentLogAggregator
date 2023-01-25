import logging
import socket
from tlog_parser import TlogParser
from outfile_writer import FileWriter


class PROCESSOR:
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, oarm_uid, config):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.oarm_uid = oarm_uid
        self.config = config
        
        #for dumping data as json
        self.payment_data_dict_list = []
        self.payment_data_dict = {"PAYMENT_TRANS_DATA": ""}
        
    
    def process(self):
        tlogParser_object = TlogParser(
                                        self.initializedPath_object, self.validation_object, self.config,\
                                        self.payment_data_dict_list, self.payment_data_dict
                                    )
        
        hostname = socket.gethostname()
        for pname in self.config[hostname]:
            
            if pname == "GRIFF":
                if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"]:
                    logging.debug('griff tomcat tlog path exists.')
                    if tlogParser_object.parse_tomcat_tlog("GRIFF"):
                        pass
                    
                if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TPTLOGAppender_log"]:
                    logging.debug('griff tomcat external hit tlog path exists.')
                    if tlogParser_object.parse_tomcat_tlog("GRIFF_EXTHIT"):
                        pass
                
            elif pname == "PACKS":
                if self.initializedPath_object.packs_tomcat_log_path_dict["packs_PACKS_T_LOG_APPENDER.FILE_log"]:
                    logging.debug('packs tomcat tlog path exists.')
                    if tlogParser_object.parse_tomcat_tlog("PACKS"):
                        pass
                    
                if self.initializedPath_object.packs_tomcat_log_path_dict["packs_EXTERNAL_HITS_APPENDER.FILE_log"]:
                    logging.debug('packs tomcat external hit tlog path exists.')
                    if tlogParser_object.parse_tomcat_tlog("PACKS_EXTHIT"):
                        pass
                
            else:
                pass
            
        outfile_writer = FileWriter()
        if self.payment_data_dict_list:
            logging.info('reached here')
            self.payment_data_dict["PAYMENT_TRANS_DATA"] = self.payment_data_dict_list
            outfile_writer.write_json_tlog_data(self.payment_data_dict)
        
        # json_object = json.dumps(self.payment_tlog_dict)
        
        # logging.info('tlogs: %s', str(self.griff_tlog_dict["PACKS"]).replace("'", '"'))
        # logging.info('json tlog data: %s',json.dumps(self.payment_tlog_dict))
        