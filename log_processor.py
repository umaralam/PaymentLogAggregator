import logging
import socket
from tlog_parser import TlogParser
from outfile_writer import FileWriter


class PROCESSOR:
    def __init__(self, initializedPath_object, outputDirectory_object,\
                    validation_object, oarm_uid, config):
        
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.oarm_uid = oarm_uid
        self.config = config
        
        #for dumping data as json
        self.payment_data_dict_list = []
        self.payment_data_dict = {"PAYMENT_TRANS_DATA": ""}
        
        #griff and packs tlog dictionary
        self.griff_tlog_dict = {}
        self.packs_tlog_dict = {}
        self.griff_ext_hit_tlog_dict = {}
        self.packs_ext_hit_tlog_dict = {}
        
        self.prism_ctid = []
        self.prism_tomcat_tlog_dict = {}
        self.prism_daemon_tlog_dict = {}
    
    def process(self):
        tlogParser_object = TlogParser(self.initializedPath_object, self.validation_object, self.config,\
                                        self.payment_data_dict_list, self.payment_data_dict,\
                                        self.griff_tlog_dict, self.packs_tlog_dict,\
                                        self.griff_ext_hit_tlog_dict, self.packs_ext_hit_tlog_dict,\
                                        self.prism_ctid, self.prism_tomcat_tlog_dict, self.prism_daemon_tlog_dict)
        
        hostname = socket.gethostname()
        for pname in self.config[hostname]:
            
            if pname == 'GRIFF':
                # tlogParser_object.parse_tlog("GRIFF")
                try:
                    if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"]:
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogParser_object.parse_tlog("GRIFF"):
                        # if tlogParser_object.parse_tomcat_tlog("GRIFF"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
            elif pname == 'PACKS':
                try:
                    if self.initializedPath_object.packs_tomcat_log_path_dict["packs_PACKS_T_LOG_APPENDER.FILE_log"]:
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogParser_object.parse_tlog("PACKS"):
                        # if tlogParser_object.parse_tomcat_tlog("PACKS"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
            elif pname == 'PRISM':
                try:
                    if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_tlog_path"]:
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogParser_object.parse_tlog("PRISM_TOMCAT"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
                try:
                    if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_tlog_path"]:
                        logging.debug('%s daemon tlog path exists', pname)
                        if tlogParser_object.parse_tlog("PRISM_DEAMON"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
                try:
                    if self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_tlog_path"]:
                        logging.debug('%s smsd tlog path exists', pname)
                        if tlogParser_object.parse_tlog("PRISM_SMSD"):
                            pass
                except KeyError as error:
                    logging.exception(error)
            
        outfile_writer = FileWriter()
        if self.payment_data_dict_list:
            self.payment_data_dict["PAYMENT_TRANS_DATA"] = self.payment_data_dict_list
            outfile_writer.write_json_tlog_data(self.payment_data_dict)
        
        # json_object = json.dumps(self.payment_tlog_dict)
        
        # logging.info('tlogs: %s', str(self.griff_tlog_dict["PACKS"]).replace("'", '"'))
        # logging.info('json tlog data: %s',json.dumps(self.payment_tlog_dict))
        