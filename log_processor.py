from collections import defaultdict
import logging
import os
import shutil
import socket
from tlog_processor import TlogProcessor
from outfile_writer import FileWriter


class PROCESSOR:
    def __init__(self, initializedPath_object, outputDirectory_object,\
                    validation_object, log_mode, oarm_uid, config):
        
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.log_mode = log_mode
        self.oarm_uid = oarm_uid
        self.config = config
        
        #for dumping data as json
        self.payment_data_dict_list = []
        self.payment_data_dict = {"PAYMENT_TRANSACTION_DATA": {}}
        # self.payment_transaction_data = defaultdict(list)
        # self.payment_data_dict = defaultdict(list)
        # self.payment_data_dict = {"PAYMENT_TRANSACTION_DATA": {"{}".format(validation_object.fmsisdn) : ""}}
        
        #onmopay, griff, packs and prism tlog dictionary
        self.onmopay_tlog_dict = {}
        self.onmopay_cg_redirection_tlog_dict = {}
        self.onmopay_request_counter_tlog_dict = {}
        self.onmopay_paycore_plog_dict = {}
        self.griff_tlog_dict = {}
        self.packs_tlog_dict = {}
        self.griff_ext_hit_tlog_dict = {}
        self.packs_ext_hit_tlog_dict = {}
        self.prism_tomcat_tlog_dict = {}
        self.prism_daemon_tlog_dict = {}
        self.prism_smsd_tlog_dict = {}
        
        self.prism_ctid = []
        self.prism_daemon_tlog_thread_dict = defaultdict(list)
        self.prism_tomcat_tlog_thread_dict = defaultdict(list)
        self.prism_tomcat_handler_generic_http_req_resp_dict = {}
        self.prism_daemon_handler_generic_http_req_resp_dict = {}
        self.prism_tomcat_handler_generic_soap_req_resp_dict = {}
        self.prism_daemon_handler_generic_soap_req_resp_dict = {}
        self.prism_tomcat_request_log_dict = {}
        self.prism_daemon_request_log_dict = {}
        self.prism_tomcat_callbackV2_log_dict = {}
        self.prism_daemon_callbackV2_log_dict = {}
        self.prism_tomcat_perf_log_dict = {}
        self.prism_daemon_perf_log_dict = {}
        self.stop_prism_process = False
        self.hostname = socket.gethostname()
    
    def process(self):
        tlogProcessor_object = TlogProcessor(self.initializedPath_object, self.outputDirectory_object,\
                                        self.validation_object, self.log_mode, self.config,\
                                        self.payment_data_dict_list, self.payment_data_dict, self.onmopay_tlog_dict,\
                                        self.onmopay_cg_redirection_tlog_dict, self.onmopay_request_counter_tlog_dict,\
                                        self.onmopay_paycore_plog_dict, self.griff_tlog_dict, self.packs_tlog_dict,\
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
                                        self.prism_smsd_tlog_dict, self.oarm_uid)
        
        
        for pname in self.config[self.hostname]:
            if pname == "ONMOPAY":
                # folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_onmopay")
                folder = os.path.join(self.outputDirectory_object, '{}_issue_onmopay'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                try:
                    if self.initializedPath_object.onmopay_consumer_log_path_dict["onmopay_consumer_NovaLogFileAppender_log"]:                
                        logging.debug('%s onmopay consumer log path exists', pname)
                        if tlogProcessor_object.process_tlog("ONMOPAY"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
            elif pname == 'GRIFF':
                # folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_griff")
                folder = os.path.join(self.outputDirectory_object, '{}_issue_griff'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                try:
                    if self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"]:                
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogProcessor_object.process_tlog("GRIFF"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
            elif pname == 'PACKS':
                # folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_packs")
                folder = os.path.join(self.outputDirectory_object, '{}_issue_packs'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                try:
                    if self.initializedPath_object.packs_tomcat_log_path_dict["packs_PACKS_T_LOG_APPENDER.FILE_log"]:
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogProcessor_object.process_tlog("PACKS"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
            elif pname == 'PRISM':
                folder = os.path.join(self.outputDirectory_object, '{}_issue_prism_tomcat'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                folder = os.path.join(self.outputDirectory_object, '{}_issue_prism_daemon'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                folder = os.path.join(self.outputDirectory_object, '{}_issue_prism_smsd'.format(self.hostname))
                self.remove_old_process_folder(pname, folder)
                
                try:
                    if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_tlog_path"]:
                        logging.debug('%s tomcat tlog path exists', pname)
                        if tlogProcessor_object.process_tlog("PRISM_TOMCAT"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
                try:
                    if self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_tlog_path"]:
                        logging.debug('%s daemon tlog path exists', pname)
                        if tlogProcessor_object.process_tlog("PRISM_DEAMON"):
                            pass
                except KeyError as error:
                    logging.exception(error)
                
                try:
                    if self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_tlog_path"]:
                        logging.debug('%s smsd tlog path exists', pname)
                        if tlogProcessor_object.process_tlog("PRISM_SMSD"):
                            pass
                except KeyError as error:
                    logging.exception(error)
            
        
        fileWriter_object = FileWriter(self.outputDirectory_object, self.oarm_uid)
        
        if self.payment_data_dict_list:
            
            self.payment_data_dict["PAYMENT_TRANSACTION_DATA"]["{}".format(self.validation_object.fmsisdn)] = self.payment_data_dict_list
            
            if self.log_mode == "txn" or self.log_mode == "error" or self.log_mode == "all":
                fileWriter_object.write_json_tlog_data(self.payment_data_dict)
                
    def remove_old_process_folder(self, pname, folder):
            #removing process folder if already exists
            logging.info('out directory already exists. Hence removing the old files of %s if exists.', self.hostname)
            if os.path.exists(folder):
                shutil.rmtree(folder)
            else:
                logging.info('%s out folder does not exists:', pname)