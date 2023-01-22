import logging
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
        
    def parse_tomcat_tlog(self, pname):
        
        #tlog object
        tlog_object = Tlog(self.initializedPath_object, self.validation_object)
        
        ctid_msisdn_data, tlog_dict = tlog_object.get_tomcat_tlog(pname)
        
        
        if pname == "GRIFF":
            for row in ctid_msisdn_data:
                ctid, msisdn = tuple(row.replace('"', '').split(","))
                logging.info('griff ctid: %s data= %s', ctid, tlog_dict["GRIFF"]["GRIFF_TLOG"][f"{msisdn}"][f"{ctid}"])
        
        elif pname == "PACKS":
            for row in ctid_msisdn_data:
                msisdn, ctid = tuple(row.replace('"', '').split(","))
                try:              
                    logging.info('packs ctid: %s data= %s', ctid, tlog_dict["PACKS"]["PACKS_TLOG"][f"{msisdn}"][f"{ctid}"])
                except KeyError as ex:
                    logging.info('key not present: %s', ex)