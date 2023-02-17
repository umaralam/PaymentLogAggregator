import logging
from pathlib import Path
import shutil
import socket
from process_daemon_log import DaemonLogProcessor

class TlogParser:
    """
        Tlog parser class
        for parsing tlog for any issue
    """
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, log_mode, oarm_uid):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.log_mode = log_mode
        self.oarm_uid = oarm_uid
    
    def parse_tlog(self, pname, ctid_map, ctid_tlog_header_data_dict):
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object,\
                                                        self.validation_object, self.oarm_uid)
        #processing tlog based on different key in the tlog        
        try:
            for ctid in ctid_map:
                for tlog_dict in ctid_tlog_header_data_dict[ctid]:
                    if self.log_mode == "error":
                        if pname == "GRIFF" and tlog_dict:
                            out = str(tlog_dict["OUT"]).split(",")
                            logging.info('griff out: %s', out)
                            msg = "CG is not available"
    
                            logging.info('status value: %s', out[2].strip())
                            if out[0] != "OUT=200" and msg not in out[2].strip():        
                                #fetch daemon log
                                logging.info('issue thread: %s', tlog_dict["THREAD_NAME"])
                                daemonLogProcessor_object.process_daemon_log(pname, ctid, tlog_dict["THREAD_NAME"])
                    
                    elif pname == "PACKS":
                        pass
                                        
                    elif self.log_mode == "all":
                        daemonLogProcessor_object.process_daemon_log(pname, ctid, tlog_dict["THREAD_NAME"])
                    
        except KeyError as error:
            logging.exception(error)
            
        