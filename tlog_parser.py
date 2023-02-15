import logging
from process_daemon_log import DaemonLogProcessor

class TlogParser:
    """
        Tlog parser class
        for parsing tlog for any issue
    """
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, log_mode):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.log_mode = log_mode
    
    def parse_tlog(self, pname, ctid_map, ctid_tlog_header_data_dict):
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object, self.validation_object)
        #processing tlog based on different key in the tlog        
        try:
            for ctid in ctid_map:
                for tlog_dict in ctid_tlog_header_data_dict[ctid]:
                    if self.log_mode == "error":
                        if pname == "GRIFF" and tlog_dict:
                            out = str(tlog_dict["OUT"]).split(",")
                            logging.info('griff out: %s', out)
                            msg = "CG is not available"
                            for status in out:
                                if status == "OUT=400" and tlog_dict["GRIFF_ACTION"] != "cgconsentinfo":        
                                    #fetch griff daemon log
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"])
                                        
                    elif self.log_mode == "all":
                        daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"])
                    
        except KeyError as error:
            logging.exception(error)
            
        