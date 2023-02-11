import logging
import socket
from tlog import Tlog
class TlogProcessor:
    """
    Parse the tlog for various conditions
    """
    def __init__(self, initializedPath_object, validation_object, config,\
                    payment_data_dict_list, payment_data_dict,\
                    griff_tlog_dict, packs_tlog_dict,\
                    griff_ext_hit_tlog_dict, packs_ext_hit_tlog_dict,\
                    prism_ctid, prism_tomcat_tlog_dict, prism_daemon_tlog_dict,\
                    prism_daemon_tlog_thread_dict, prism_tomcat_tlog_thread_dict,\
                    prism_tomcat_handler_generic_http_req_resp_dict,\
                    prism_daemon_handler_generic_http_req_resp_dict,\
                    prism_tomcat_handler_generic_soap_req_resp_dict,\
                    prism_daemon_handler_generic_soap_req_resp_dict,\
                    prism_tomcat_request_log_dict, prism_daemon_request_log_dict,\
                    prism_tomcat_callbackV2_log_dict, prism_daemon_callbackV2_log_dict,\
                    prism_tomcat_perf_log_dict, prism_daemon_perf_log_dict,\
                    prism_smsd_tlog_dict):
        
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
        self.prism_daemon_tlog_thread_dict = prism_daemon_tlog_thread_dict
        self.prism_tomcat_tlog_thread_dict = prism_tomcat_tlog_thread_dict
        
        self.prism_tomcat_handler_generic_http_req_resp_dict = prism_tomcat_handler_generic_http_req_resp_dict
        self.prism_daemon_handler_generic_http_req_resp_dict = prism_daemon_handler_generic_http_req_resp_dict
        self.prism_tomcat_handler_generic_soap_req_resp_dict = prism_tomcat_handler_generic_soap_req_resp_dict
        self.prism_daemon_handler_generic_soap_req_resp_dict = prism_daemon_handler_generic_soap_req_resp_dict
        
        self.prism_tomcat_request_log_dict = prism_tomcat_request_log_dict
        self.prism_daemon_request_log_dict = prism_daemon_request_log_dict
        self.prism_tomcat_callbackV2_log_dict = prism_tomcat_callbackV2_log_dict
        self.prism_daemon_callbackV2_log_dict = prism_daemon_callbackV2_log_dict
        self.prism_tomcat_perf_log_dict = prism_tomcat_perf_log_dict
        self.prism_daemon_perf_log_dict = prism_daemon_perf_log_dict
        
        self.prism_smsd_tlog_dict = prism_smsd_tlog_dict
        
    def process_tlog(self, pname):
        
        #tlog object
        tlog_object = Tlog(self.initializedPath_object, self.validation_object,\
                            self.payment_data_dict_list, self.payment_data_dict, self.config,\
                            self.griff_tlog_dict, self.packs_tlog_dict,\
                            self.griff_ext_hit_tlog_dict, self.packs_ext_hit_tlog_dict,\
                            self.prism_ctid, self.prism_tomcat_tlog_dict, self.prism_daemon_tlog_dict,\
                            self.prism_daemon_tlog_thread_dict, self.prism_tomcat_tlog_thread_dict,\
                            self.prism_tomcat_handler_generic_http_req_resp_dict,\
                            self.prism_daemon_handler_generic_http_req_resp_dict,\
                            self.prism_tomcat_handler_generic_soap_req_resp_dict,\
                            self.prism_daemon_handler_generic_soap_req_resp_dict,\
                            self.prism_tomcat_request_log_dict, self.prism_daemon_request_log_dict,\
                            self.prism_tomcat_callbackV2_log_dict, self.prism_daemon_callbackV2_log_dict,\
                            self.prism_tomcat_perf_log_dict, self.prism_daemon_perf_log_dict,\
                            self.prism_smsd_tlog_dict)
        
        # tlog_object.get_tlog(pname)
        
        # ctid_msisdn_data, tlog_dict = tlog_object.get_tomcat_tlog(pname)
        
        if pname == "GRIFF":
            #fetching griff access and tlog
            # tlog_object.get_tlog(pname)
            self.griff_tlog_dict = tlog_object.get_tlog(pname)
            # logging.info('griff tlog dict: %s', self.griff_tlog_dict)
            try:
                if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TPTLOGAppender_log"]:
                    logging.debug('%s tomcat external hit tlog path exists', pname)
                    
                    #fetching griff external hit tlog
                    # tlog_object.get_tlog("GRIFF_EXTHIT")
                    try:
                        self.griff_ext_hit_tlog_dict = tlog_object.get_tlog("GRIFF_EXTHIT")
                        # logging.info('griff ext tlog dict: %s', self.griff_ext_hit_tlog_dict)
                        
                        for ctid in self.griff_ext_hit_tlog_dict["GRIFF_EXT_HIT_TLOG"][f"{self.validation_object.fmsisdn}"]:
                            self.prism_ctid.append(ctid)
                            logging.info('ctid present in prism ctid: %s', self.prism_ctid)
                    except TypeError as error:
                        logging.exception(error)
            except KeyError as error:
                logging.exception(error)
        
        # elif pname == "GRIFF_EXTHIT":
        #     pass
        
        elif pname == "PACKS":
            #fetching packs access and tlog
            # tlog_object.get_tlog(pname)
            self.packs_tlog_dict = tlog_object.get_tlog(pname)
            # logging.info('packs tlog dict: %s', self.packs_tlog_dict)
            try:
                if self.initializedPath_object.packs_tomcat_log_path_dict["packs_EXTERNAL_HITS_APPENDER.FILE_log"]:
                    logging.debug('%s tomcat external hit tlog path exists', pname)
                    
                    #fetching packs external hit tlog
                    # tlog_object.get_tlog("PACKS_EXTHIT")
                    self.packs_ext_hit_tlog_dict = tlog_object.get_tlog("PACKS_EXTHIT")
                    # logging.info('packs ext tlog dict: %s', self.packs_ext_hit_tlog_dict)
                    
                    try:
                        for ctid in self.packs_ext_hit_tlog_dict["PACKS_EXT_HIT_TLOG"][f"{self.validation_object.fmsisdn}"]:
                            if ctid in self.prism_ctid:
                                logging.info('ctid present in prism ctid: %s', self.prism_ctid)
                            else:
                                self.prism_ctid.append(ctid)
                    except TypeError as error:
                        logging.exception(error)
            
            except KeyError as error:
                logging.exception(error)
                    
        # elif pname == "PACKS_EXTHIT":
        #     pass
        
            
        elif pname == "PRISM_TOMCAT":
            # fetching prism tomcat access and tlog
            self.prism_tomcat_tlog_dict = tlog_object.get_tlog(pname)
            
            #fetching prism tomcat generic http handler request response
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_http_handler_req_resp_path"]:
                tlog_object.get_tlog("PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP")
            
            #fetching prism tomcat generic soap handler request response
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_soap_handler_req_resp_path"]:
                tlog_object.get_tlog("PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP")
            
            #fetching prism tomcat request response and event callback v2 included
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_req_resp_path"]:
                tlog_object.get_tlog("PRISM_TOMCAT_REQ_RESP")
            
            #fetching prism tomcat callback v2 request response
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_callbackV2_req_resp_path"]:
                tlog_object.get_tlog("PRISM_TOMCAT_CALLBACK_V2_REQ_RESP")
            
            #fetching prism tomcat perf log
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_perf_log_path"]:
                tlog_object.get_tlog("PRISM_TOMCAT_PERF_LOG")
                
        elif pname == "PRISM_DEAMON":
            # fetching prism daemon tlog
            tlog_object.get_tlog(pname)
            
            #fetching prism daemon generic http handler request response
            if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_http_handler_req_resp_path"]:
                tlog_object.get_tlog("PRISM_DAEMON_GENERIC_HTTP_REQ_RESP")
            
            #fetching prism daemon generic soap handler request response
            if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_soap_handler_req_resp_path"]:
                tlog_object.get_tlog("PRISM_DAEMON_GENERIC_SOAP_REQ_RESP")
            
            #fetching prism daemon request response and event callback v2 included
            if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_req_resp_path"]:
                tlog_object.get_tlog("PRISM_DAEMON_REQ_RESP")
            
            #fetching prism daemon callback v2 request response
            if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_callbackV2_req_resp_path"]:
                tlog_object.get_tlog("PRISM_DAEMON_CALLBACK_V2_REQ_RESP")
            
            #fetching prism daemon perf log
            if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_perf_log_path"]:
                tlog_object.get_tlog("PRISM_DAEMON_PERF_LOG")
        
        elif pname == "PRISM_SMSD":
            tlog_object.get_tlog(pname)
            