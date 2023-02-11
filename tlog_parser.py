import logging
from process_daemon_log import DaemonLogProcessor

class TlogParser:
    """
        Tlog parser class
        for parsing tlog for any issue
    """
    def __init__(self, initializedPath_object, validation_object):
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
    
    def parse_tlog(self, pname, ctid_map, ctid_tlog_header_data_dict):
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.validation_object)
        #processing tlog based on different key in the tlog        
        try:
            for ctid in ctid_map:
                for tlog_dict in ctid_tlog_header_data_dict[ctid]:
                    if pname == "GRIFF":
                        out = str(tlog_dict["OUT"]).split(",")
                        for status in out:
                            if status == "OUT=400" and tlog_dict["GRIFF_ACTION"] != "cgconsentinfo":
                                logging.info('griff out: %s', out)
                                logging.info('tlog parser tlog dict: %s', tlog_dict)
                                
                                #fetch griff daemon log
                                daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"])
                    
        except KeyError as error:
            logging.exception(error)
            
        