import logging
import socket
from tlog import Tlog
class TlogParser:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, validation_object, config, payment_data_dict_list, payment_data_dict):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.config = config
        self.payment_data_dict_list = payment_data_dict_list
        self.payment_data_dict = payment_data_dict   
        
    def parse_tlog(self, pname):
        
        #tlog object
        tlog_object = Tlog(self.initializedPath_object, self.validation_object, self.payment_data_dict_list, self.payment_data_dict, self.config)
        
        tlog_object.get_tlog(pname)
        
        # ctid_msisdn_data, tlog_dict = tlog_object.get_tomcat_tlog(pname)
        
        if pname == "GRIFF":
            pass
            # for row in ctid_msisdn_data:
            #     ctid, msisdn = tuple(row.replace('"', '').split(","))
            #     logging.info('griff ctid: %s data= %s', ctid, tlog_dict["GRIFF"]["GRIFF_TLOG"][f"{msisdn}"][f"{ctid}"])
        
        elif pname == "GRIFF_EXTHIT":
            pass
        
        elif pname == "PACKS":
            pass
            # for row in ctid_msisdn_data:
            #     msisdn, ctid = tuple(row.replace('"', '').split(","))
            #     try:              
            #         logging.info('packs ctid: %s data= %s', ctid, tlog_dict["PACKS"]["PACKS_TLOG"][f"{msisdn}"][f"{ctid}"])
            #     except KeyError as ex:
            #         logging.info('key not present: %s', ex)
                    
        elif pname == "PACKS_EXTHIT":
            pass
        elif pname == "PRISM_TOMCAT":
            pass
        elif pname == "PRISM_DEAMON":
            pass
        elif pname == "PRISM_SMSD":
            pass