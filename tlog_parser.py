import logging
import socket
from tlog import Tlog
class TlogParser:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, validation_object, config,\
                    payment_data_dict_list, payment_data_dict,\
                    griff_tlog_dict, packs_tlog_dict,\
                    griff_ext_hit_tlog_dict, packs_ext_hit_tlog_dict,\
                    prism_ctid, prism_tomcat_tlog_dict, prism_daemon_tlog_dict):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.config = config
        self.payment_data_dict_list = payment_data_dict_list
        self.payment_data_dict = payment_data_dict
        self.griff_tlog_dict = griff_tlog_dict
        self.packs_tlog_dict = packs_tlog_dict
        self.griff_ext_hit_tlog_dict = griff_ext_hit_tlog_dict
        self.packs_ext_hit_tlog_dict = packs_ext_hit_tlog_dict
        
        self.prism_ctid = prism_ctid
        self.prism_tomcat_tlog_dict = prism_tomcat_tlog_dict
        self.prism_daemon_tlog_dict = prism_daemon_tlog_dict
        
    def parse_tlog(self, pname):
        
        #tlog object
        tlog_object = Tlog(self.initializedPath_object, self.validation_object,\
                            self.payment_data_dict_list, self.payment_data_dict, self.config,\
                            self.griff_tlog_dict, self.packs_tlog_dict,\
                            self.griff_ext_hit_tlog_dict, self.packs_ext_hit_tlog_dict,\
                            self.prism_ctid, self.prism_tomcat_tlog_dict, self.prism_daemon_tlog_dict)
        
        # tlog_object.get_tlog(pname)
        
        # ctid_msisdn_data, tlog_dict = tlog_object.get_tomcat_tlog(pname)
        
        if pname == "GRIFF":
            #fetching griff access and tlog
            self.griff_tlog_dict = tlog_object.get_tlog(pname)
            # logging.info('griff tlog dict: %s', self.griff_tlog_dict)
            try:
                if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TPTLOGAppender_log"]:
                    logging.debug('%s tomcat external hit tlog path exists', pname)
                    
                    #fetching griff external hit tlog
                    self.griff_ext_hit_tlog_dict = tlog_object.get_tlog("GRIFF_EXTHIT")
                    # logging.info('griff ext tlog dict: %s', self.griff_ext_hit_tlog_dict)
                    
                    for ctid in self.griff_ext_hit_tlog_dict["GRIFF_EXT_HIT_TLOG"][f"{self.validation_object.fmsisdn}"]:
                        self.prism_ctid.append(ctid)
            except KeyError as error:
                logging.exception(error)
        
        # elif pname == "GRIFF_EXTHIT":
        #     pass
        
        elif pname == "PACKS":
            #fetching packs access and tlog
            self.packs_tlog_dict = tlog_object.get_tlog(pname)
            # logging.info('packs tlog dict: %s', self.packs_tlog_dict)
            try:
                if self.initializedPath_object.packs_tomcat_log_path_dict["packs_EXTERNAL_HITS_APPENDER.FILE_log"]:
                    logging.debug('%s tomcat external hit tlog path exists', pname)
                    
                    #fetching packs external hit tlog
                    self.packs_ext_hit_tlog_dict = tlog_object.get_tlog("PACKS_EXTHIT")
                    # logging.info('packs ext tlog dict: %s', self.packs_ext_hit_tlog_dict)
                    
                    for ctid in self.packs_ext_hit_tlog_dict["PACKS_EXT_HIT_TLOG"][f"{self.validation_object.fmsisdn}"]:
                        if ctid in self.prism_ctid:
                            logging.info('ctid present in prism ctid')
                        else:
                            self.prism_ctid.append(ctid)
            
            except KeyError as error:
                logging.exception(error)
                    
        # elif pname == "PACKS_EXTHIT":
        #     pass
        
            
        elif pname == "PRISM_TOMCAT":
            # logging.info('prism ctid: %s', self.prism_ctid)
            tlog_object.get_tlog(pname)
    
        elif pname == "PRISM_DEAMON":
            tlog_object.get_tlog(pname)
            
        elif pname == "PRISM_SMSD":
            tlog_object.get_tlog(pname)
            