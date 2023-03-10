import logging
import re
import signal
import subprocess
from log_files import LogFileFinder
from collections import defaultdict
from tlog_parser import TlogParser
from input_tags import DaiusActivityType


class Tlog:
    """
    tlog mapping class
    for creating tlog data mapping based on ctid, 
    access log data included
    """
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, log_mode,\
                    payment_data_dict_list, payment_data_dict, config, onmopay_tlog_dict,\
                    onmopay_cg_redirection_tlog_dict, onmopay_request_counter_tlog_dict,\
                    onmopay_paycore_plog_dict, griff_tlog_dict,\
                    packs_tlog_dict, griff_ext_hit_tlog_dict, packs_ext_hit_tlog_dict,\
                    prism_ctid, prism_tomcat_tlog_dict, prism_daemon_tlog_dict, prism_daemon_tlog_thread_dict,\
                    prism_tomcat_tlog_thread_dict, prism_tomcat_handler_generic_http_req_resp_dict,\
                    prism_daemon_handler_generic_http_req_resp_dict, prism_tomcat_handler_generic_soap_req_resp_dict,\
                    prism_daemon_handler_generic_soap_req_resp_dict, prism_tomcat_request_log_dict,\
                    prism_daemon_request_log_dict, prism_tomcat_callbackV2_log_dict, prism_daemon_callbackV2_log_dict,\
                    prism_tomcat_perf_log_dict, prism_daemon_perf_log_dict, prism_smsd_tlog_dict, oarm_uid):
        
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.log_mode = log_mode
        self.tlog_files = []
        self.backup_tlog_files = []
        self.access_files = []
        
        #ctid msisdn mapping for griff and packs
        self.ctid_msisdn_map_dict = {}
        # self.ctid_map_dict = {}
        
        self.tlog_record = []
        self.access_record = []
        self.is_backup_file = False
        
        #ctid containing files list
        self.tlog_files_with_ctid_msisdn = []
        self.tlog_backup_files_with_ctid_msisdn = []
        
        #tlog header mapping parameters
        self.tlog_dict = defaultdict(list)
        self.ctid_data_dict = defaultdict(list)
        self.msisdn_data_dict = {}
        self.ctid_access_data_dict = defaultdict(list)
        self.msisdn_access_data_dict = defaultdict(list)
        # self.msisdn_sms_data_dict = defaultdict(list)
        self.msisdn_sms_data_list = []
        
        #Is for both tlog and external tlog
        # self.griff_ctid_msisdn_data_list = []
        # self.packs_ctid_msisdn_data_list = []
        
        #for external hits
        # self.griff_ctid_data_list = []
        # self.packs_ctid_data_list = []
        
        #header data mapped tlogs
        self.onmopay_access_log_dict = {}
        self.griff_access_log_dict = {}
        self.packs_access_log_dict = {}
        self.prism_access_log_dict = {}
        
        #log processor initialization parameter
        self.payment_data_dict_list = payment_data_dict_list
        self.payment_data_dict = payment_data_dict
        self.config = config
        
        self.onmopay_tlog_dict = onmopay_tlog_dict
        self.onmopay_cg_redirection_tlog_dict = onmopay_cg_redirection_tlog_dict
        self.onmopay_request_counter_tlog_dict = onmopay_request_counter_tlog_dict
        self.onmopay_paycore_plog_dict = onmopay_paycore_plog_dict
        
        self.griff_tlog_dict = griff_tlog_dict
        self.griff_ext_hit_tlog_dict = griff_ext_hit_tlog_dict
        
        self.packs_tlog_dict = packs_tlog_dict
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
        self.oarm_uid = oarm_uid
        self.is_success_access_hit = True
    
    def get_tlog(self, pname):
        """
        calling path finder method
        """
        
        logfile_object = LogFileFinder(self.initializedPath_object, self.validation_object, self.config)

        if pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION":
            self.constructor_parameter_reinitialize()
            self.constructor_ctid_msisdn_paramter_reinitialization()
            
        elif pname == "GRIFF" or pname == "PACKS":
            self.constructor_parameter_reinitialize()
            self.constructor_ctid_msisdn_paramter_reinitialization()
            
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
            self.constructor_parameter_reinitialize()
            self.constructor_ctid_msisdn_paramter_reinitialization()
        
        elif pname == "ONMOPAY_REQUEST_COUNTER" or pname == "ONMOPAY_PAYCORE_PERF_LOG"\
            or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT"\
            or pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP"\
            or pname == "PRISM_DAEMON_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP"\
            or pname == "PRISM_TOMCAT_PERF_LOG" or pname == "PRISM_DAEMON_PERF_LOG"\
            or pname == "PRISM_SMSD":
            
            self.constructor_parameter_reinitialize()
        
        self.tlog_files = logfile_object.get_tlog_files(pname)
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
            self.backup_tlog_files = logfile_object.get_tlog_backup_files(pname)
            
        # logging.info('tlog files: %s', self.tlog_files)
        # logging.info('backup tlog files: %s', self.backup_tlog_files)
        
        if self.tlog_files:
            if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT"\
                or pname == "PACKS_EXTHIT" or pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION"\
                or pname == "ONMOPAY_REQUEST_COUNTER" or pname == "ONMOPAY_PAYCORE_PERF_LOG":
                for file in self.tlog_files:
                    # function call
                    self.msisdn_ctid_map(pname, file, self.is_backup_file)
                    
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                # function call
                self.ctid_based_tlog_fetch(pname, self.tlog_files, False)
            
            elif pname == "PRISM_SMSD":
                # function call
                self.msisdn_based_sms_tlog_fetch(pname, self.tlog_files)
                
            
            elif pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP"\
                    or pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP"\
                    or pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP"\
                    or pname == "PRISM_DAEMON_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP"\
                    or pname == "PRISM_TOMCAT_PERF_LOG" or pname == "PRISM_DAEMON_PERF_LOG":
                # function call
                self.thread_based_prism_handler_req_resp_fetch(pname, self.tlog_files)
            
        if self.backup_tlog_files:
            self.is_backup_file = True
            
            for file in self.backup_tlog_files:
                #function call
                self.msisdn_ctid_map(pname, file, self.is_backup_file)
            
        if pname == "GRIFF":
            if self.initializedPath_object.griff_tomcat_log_path_dict["griff_tomcat_access_path"]:
                logging.debug('griff tomcat access path exists.')
                self.access_files = logfile_object.get_tomcat_access_files(pname)
            
            if self.access_files:
                self.ctid_based_accesslog_fetch(pname, self.access_files)
            
        elif pname == "PACKS":
            if self.initializedPath_object.packs_tomcat_log_path_dict["packs_tomcat_access_path"]:
                logging.debug('packs tomcat access path exists.')
                self.access_files = logfile_object.get_tomcat_access_files(pname)
            
            if self.access_files:
                self.ctid_based_accesslog_fetch(pname, self.access_files)
                
        elif pname == "PRISM_TOMCAT":
            if self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_access_path"]:
                logging.debug('prism tomcat access path exists.')
                self.access_files = logfile_object.get_tomcat_access_files(pname)
            
            if self.access_files:
                self.msisdn_based_accesslog_fetch(pname, self.access_files)
        
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT"\
            or pname == "PACKS_EXTHIT" or pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION"\
            or pname == "ONMOPAY_REQUEST_COUNTER" or pname == "ONMOPAY_PAYCORE_PERF_LOG":
            if self.ctid_msisdn_map_dict and (self.tlog_files_with_ctid_msisdn\
                                            or self.tlog_backup_files_with_ctid_msisdn):
                if self.tlog_files_with_ctid_msisdn:
                    self.ctid_based_tlog_fetch(pname, self.tlog_files_with_ctid_msisdn, False)
                if self.tlog_backup_files_with_ctid_msisdn:
                    self.ctid_based_tlog_fetch(pname, self.tlog_backup_files_with_ctid_msisdn, True)
        
        logging.info('tlog record: %s', self.tlog_record)
        if self.tlog_record:
            data_list = []
            for data in self.tlog_record:
                logging.info('data in tlog: %s', data)
                for record in str(data).splitlines():
                    if record not in data_list:
                        data_list.append(record)
            
            if pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP"\
                    or pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP"\
                    or pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP"\
                    or pname == "PRISM_DAEMON_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP":
                    
                    self.prism_handler_req_resp_header_map(pname, data_list)
                    
            elif pname == "PRISM_TOMCAT_PERF_LOG" or pname == "PRISM_DAEMON_PERF_LOG":
                self.perf_data_mapping(pname, data_list)
            elif pname == "PRISM_SMSD":
                self.sms_data_header_mapping(pname, data_list)
            elif pname == "ONMOPAY_CG_REDIRECTION" or pname == "ONMOPAY_PAYCORE_PERF_LOG":
                self.onmopay_data_mapping(pname, data_list)
            else:
                self.tlog_record_header_mapping(pname, data_list)
        
        if pname == "ONMOPAY" and self.onmopay_tlog_dict:
            # outfile_writer.write_json_tlog_data(self.griff_tlog_dict)
            return self.onmopay_tlog_dict
        
        elif pname == "GRIFF" and self.griff_tlog_dict:
            # outfile_writer.write_json_tlog_data(self.griff_tlog_dict)
            return self.griff_tlog_dict
        
        elif pname == "PACKS" and self.packs_tlog_dict:
            # outfile_writer.write_json_tlog_data(self.packs_tlog_dict)
            return self.packs_tlog_dict
        
        elif pname == "GRIFF_EXTHIT" and self.griff_ext_hit_tlog_dict:
            # outfile_writer.write_json_tlog_data(self.griff_ext_hit_tlog_dict)
            return self.griff_ext_hit_tlog_dict
        
        elif pname == "PACKS_EXTHIT" and self.packs_ext_hit_tlog_dict:
            # outfile_writer.write_json_tlog_data(self.packs_ext_hit_tlog_dict)
            return self.packs_ext_hit_tlog_dict
        
        elif pname == "PRISM_TOMCAT":
            return self.prism_tomcat_tlog_dict
        
        elif pname == "PRISM_DEAMON":
            return self.prism_daemon_tlog_dict
        
    
    def msisdn_ctid_map(self, pname, file, is_backup_file):
        
        if is_backup_file:
            if pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 2,12", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 5,4", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
            
            elif pname == "GRIFF_EXTHIT":
                # logging.info('griff ext backup file: %s', file)
                ctid_data = subprocess.check_output(f"zcat {file} | cut -d ',' -f 3 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    skip_string = ['#product=griff','#source=external_hits', 'THREAD_NAME', '#version=1.0.0']
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        if row != "" and row not in skip_string:
                            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                                if str(row).replace('"', '') == ctid:
                                    # logging.info('back ctid: %s and row: %s', ctid, row)
                                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                
            elif pname == "PACKS_EXTHIT":
                ctid_data = subprocess.check_output(f"zcat {file} | cut -d ',' -f 3 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        if row != "" and row != "APPID":
                            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                                if str(row).replace('"', '') == ctid:
                                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                
        else:
            if pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION":
                if pname == "ONMOPAY":
                    ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 3,4", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                elif pname == "ONMOPAY_CG_REDIRECTION":
                    ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 5,6", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                    
                if ctid_mdn_data:
                    self.tlog_files_with_ctid_msisdn.append(file)
            
            elif pname == "ONMOPAY_REQUEST_COUNTER":
                ctid_data = subprocess.check_output(f"cat {file} | cut -d ',' -f 2 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    skip_string = ['SessionId']
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        if row != "" and row not in skip_string:
                            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                                if str(row).replace('"', '') == ctid:
                                    # logging.info('normal ctid: %s and row: %s', ctid, row)
                                    self.tlog_files_with_ctid_msisdn.append(file)
            
            elif pname == "ONMOPAY_PAYCORE_PERF_LOG":
                ctid_data = subprocess.check_output(f"cat {file} | cut -d '|' -f 2 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                            if str(row).replace('"', '') == ctid:
                                logging.info('normal ctid: %s and row: %s', ctid, row)
                                self.tlog_files_with_ctid_msisdn.append(file)
            
            elif pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 2,12", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 5,4", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_files_with_ctid_msisdn.append(file)
            
            elif pname == "GRIFF_EXTHIT":
                ctid_data = subprocess.check_output(f"cat {file} | cut -d ',' -f 3 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    skip_string = ['#product=griff','#source=external_hits', 'THREAD_NAME', '#version=1.0.0']
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        if row != "" and row not in skip_string:
                            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                                if str(row).replace('"', '') == ctid:
                                    # logging.info('normal ctid: %s and row: %s', ctid, row)
                                    self.tlog_files_with_ctid_msisdn.append(file)
            
            elif pname == "PACKS_EXTHIT":
                ctid_data = subprocess.check_output(f"cat {file} | cut -d ',' -f 3 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_data:
                    ctid_data_splitted = ctid_data.split('\n')
                    for row in ctid_data_splitted:
                        if row != "" and row != "APPID":
                            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                                if str(row).replace('"', '') == ctid:
                                    self.tlog_files_with_ctid_msisdn.append(file)
                
        if pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION":
            ctid_msisdn_data = []
            ctid_msisdn_data = ctid_mdn_data.split('\n')
        
        elif pname == "GRIFF":
            ctid_msisdn_data = []
            ctid_msisdn_data = ctid_mdn_data.split('\n')
            # for row in ctid_msisdn_data:
            #     if row != "":
            #         self.griff_ctid_msisdn_data_list.append(row)
            
        elif pname == "PACKS":
            ctid_msisdn_data = ctid_mdn_data.split('\n')
            logging.info('packs ctid msisdn data: %s', ctid_msisdn_data)
            # for row in ctid_msisdn_data:
            #     if row != "":
            #         self.packs_ctid_msisdn_data_list.append(row)
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION":
            for row in ctid_msisdn_data:
                if row != "":
                    if pname == "ONMOPAY":
                        ctid, msisdn = tuple(row.replace('"', '').split(","))
                    elif pname == "ONMOPAY_CG_REDIRECTION":
                        ctid, msisdn = tuple(row.replace('"', '').split(","))
                    elif pname == "GRIFF":
                        ctid, msisdn = tuple(row.replace('"', '').split(","))
                    elif pname == "PACKS":
                        ctid, msisdn = tuple(row.replace('"', '').split(","))
                    try:
                        if ctid not in self.ctid_msisdn_map_dict[msisdn]:
                            # append the new ctid to the existing array of msisdn
                            self.ctid_msisdn_map_dict[msisdn].append(ctid)
                            # logging.info('map: %s', self.ctid_msisdn_map_dict)
                    except KeyError as ex:
                        # create a new array of msisdn
                        self.ctid_msisdn_map_dict[msisdn] = [ctid]
                        
            logging.info('map: %s', self.ctid_msisdn_map_dict)
    
    def ctid_based_tlog_fetch(self, pname, files, is_backup_files):
        try:
            if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT"\
                or pname == "PACKS_EXTHIT" or pname == "ONMOPAY" or pname == "ONMOPAY_CG_REDIRECTION"\
                or pname == "ONMOPAY_REQUEST_COUNTER" or pname == "ONMOPAY_PAYCORE_PERF_LOG":
                temp_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
                
                for ctid in temp_map:
                    if is_backup_files:
                        for file in files:
                            try:
                                data = subprocess.check_output(f"zcat {file} | grep -a {ctid}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                                self.tlog_record.append(data)
                            except Exception as ex:
                                logging.info(ex)
                    else:
                        for file in files:
                            try:
                                data = subprocess.check_output(f"cat {file} | grep -a {ctid}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                                self.tlog_record.append(data)
                            except Exception as ex:
                                logging.info(ex)
                                
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
                # temp_map = self.prism_ctid  //support not available for now
                msisdn = self.validation_object.fmsisdn

                if is_backup_files:
                    for file in files:
                        try:
                            data = subprocess.check_output(f"zcat {file} | grep -a {msisdn}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                            self.tlog_record.append(data)
                        except Exception as ex:
                            logging.info(ex)
                else:
                    for file in files:
                        try:
                            data = subprocess.check_output(f"cat {file} | grep -a {msisdn}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                            self.tlog_record.append(data)
                        except Exception as ex:
                            logging.info(ex)
        except Exception as ex:
            logging.info(ex)
    
    def thread_based_prism_handler_req_resp_fetch(self, pname, files):
        if pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP"\
            or pname == "PRISM_TOMCAT_PERF_LOG":
                
            threads = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
            
        elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_DAEMON_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP"\
            or pname == "PRISM_DAEMON_PERF_LOG":
                
            threads = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
        
        for thread in threads:
            try:
                for file in files:
                    try:
                        data = subprocess.check_output(f"cat {file} | grep -a {thread}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                        self.tlog_record.append(data)
                    except Exception as ex:
                        logging.info(ex)
            except Exception as ex:
                logging.info(ex)
          
    def tlog_record_header_mapping(self, pname, data_list):
        #GRIFF tlog header mapping and call to tlog parser class
        tlogParser_object = TlogParser(self.initializedPath_object, self.outputDirectory_object,\
                                        self.validation_object, self.log_mode, self.oarm_uid,\
                                        self.prism_daemon_tlog_thread_dict, self.prism_tomcat_tlog_thread_dict)
        if pname == "ONMOPAY":
            header = [
                        "TIMESTAMP","StoreID","SessionID","UserID","AuthenticationMechanism","RemoteIP",\
                        "UserAgent","DeviceIndex","CampaignSource","CampaignMedium","CampaignID","CampaignSessionID",\
                        "ActivityType","Operator","CampaignIdentifier","Referrer","RequestOrigin","NetWorkType",\
                        "Mode","AntiFraudScore","AntiFraudThreatFlags","BillingOption","X_Forwarded_For",\
                        "X_Requested_With","ErrorCode","IsUserIDEncrypted","QualityCheckScore"
                    ]
        
        elif pname == "ONMOPAY_REQUEST_COUNTER":
            header = [
                        "Timestamp","SessionId","ActionName","ServiceId","Operator","Partner","Hostname",\
                        "FinalAction","AdditionalData","PerformanceLog"
                    ]
        
        elif pname == "GRIFF":
            header = [
                        "TIMESTAMP","CTID","HOST","X_FORWARDED_FOR","THREAD_NAME","TOTAL_TIME","GRIFF_TIME",\
                        "EXT_TIME","STORENAME","SUB_CODE","GRIFF_ACTION","MSISDN","OLDMSISDN","UID","OLDUID",\
                        "OPERATOR","CIRCLE","PACK_TYPE","APPID","PACKID","OLDPACKID","SESSIONID","U","USERNAME",\
                        "PASSWORD","CPNAME","TPS_VALID","OUT","CONTENTID","CONTENTTYPE","CONTENTINFO","MODE",\
                        "BYPASSLIMIT","OMREVPOS","ISPPD","PACK_DISPLAY_CUSTOM_PAGE","UNIT","ACTION","EXP_DATE",\
                        "CBCK_PRISM_STATUS","EVENTKEY","AMOUNT","APP_PACKS_COLLECTION","MNP","CG","PACKS",\
                        "PRISM","SHORTURL","TONEPLAYER","RBT","CBCK","SMS","SRVKEY","CHARGE_TYPE","TRANS_TIME",\
                        "SBNID","SCID","USERINFO","HEADERS","TRAP_STATUS","NETWORK-TYPE","CGREFID","TRX_DATA",\
                        "PACKS_DATA"
                    ]
            
        elif pname == "PACKS":
            header = [
                        "PackTLogCreatedTimeStamp","THREAD_NAME","API_NAME","CTID","REQ_MSISDN","REQ_APPID",\
                        "REQ_PACKID","REQ_OPERATOR","REQ_CIRCLE","SEL_OPERATOR","SEL_CIRCLE","REQ_ACTION",\
                        "REQ_USERINFO","RES_USERINFO","REQ_AMOUNT","REQ_SERVICEKEY","REQ_EVENTKEY",\
                        "REQ_ALL_PARAMS","BILLING_SERVICE_KEY","BILLING_URL_TEMPLATE","BILLING_URL_CALLED",\
                        "BILLING_REQ_TIME_START","BILLING_REQ_TIME_END","BILLING_AMOUNT","BILLING_RES_STATUS",\
                        "BILLING_RES_MESSAGE","CREDITS_BEFORE","CREDITS_AFTER","APP_NAME","PACK_NAME","SUB_TYPE",\
                        "BILLING_MODE","BILLING_TYPE","CALLBACK_REGISTERED","RET_APPS","RET_PACKS","RET_STATUS",\
                        "RET_ERROR_REASON","SEL_APPIDs","SEL_PACKIDs","SUBSCRIBER_ID","SUBS_STATUS_BEFORE",\
                        "SUBS_STATUS_AFTER","REQ_ACTION_MODE","REQ_NEW_MSISDN","PACK_LEVEL_FILTER",\
                        "APP_LEVEL_FILTER","COMMON_PARAM_FILTER","CHARGE_KEY","SOURCE_IP","GRIFF_RESPONSE",\
                        "THIRD_PARTIES","TOTAL_TIMETAKEN","PACKS_TIMETAKEN","EXT_TIMETAKEN","TRAP_STATUS"
                    ]
        
        elif pname == "GRIFF_EXTHIT":
            header = [
                        "TIMESTAMP","THREAD_NAME","CTID","STORENAME","EXTNAME","APINAME","HTTPMETHOD",\
                        "HTTPSTATUSCODE","TIMETAKEN","PROXYHOST","PROXYPORT","URL","REQHEADERS","RQEPARAMS",\
                        "REQBODY","RESPONSE"
                    ]
        
        elif pname == "PACKS_EXTHIT":
            header = [
                        "TIMESTAMP","THREAD_NAME","CTID","APPID","PACKID","APINAME","EXTNAME","HTTPMETHOD",\
                        "HTTPSTATUSCODE","TIMETAKEN","PROXYHOST","PROXYPORT","URL","REQHEADERS","RQEPARAMS",\
                        "REQBODY","RESPONSE","RESPONSEHEADERS"
                    ]
        
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
        
            header = [
                        "TIMESTAMP","THREAD","SITE_ID","MSISDN","SUB_TYPE","SBN_ID/EVT_ID","SRV_KEYWORD",\
                        "CHARGE_TYPE","PARENT_KEYWORD","AMOUNT","MODE","USER","REQUEST_DATE","INVOICE_DATE",\
                        "EXPIRY_DATE","RETRY_COUNT","CYCLE_STATUS","GRACE_COUNT","GRACE_RETRY_COUNT",\
                        "NEW_SRV_KEYWORD","INFER_SUB_STATUS","CHARGE_KEYWORD","TRIGGER_ID","PACK_KEY",\
                        "PARENT_ID","APP_NAME","SITE_NAME","REN_COUNT","FLOW_TASKS","CONTENT_ID","CAMPAIGN_ID",\
                        "TOTAL_CHG_AMNT","RECO","TASK_TYPE","TASK_STATUS","PAYMENT_STATUS","CHARGE_SCHEDULE",\
                        "NEXT_BILL_DATE"
                    ]
        
        elif pname == "PRISM_SMSD":
            header = [
                        "TIMESTAMP","THREAD","SITE_ID","MSISDN","SRNO","SRVCODE","MSG","HANDLER",\
                        "STATUS","REMARKS","TIME_TAKEN","SMS_INFO"
                    ]
        
        logging.info('process name: %s', pname)
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT"\
            or pname == "PACKS_EXTHIT" or pname == "ONMOPAY" or pname == "ONMOPAY_REQUEST_COUNTER":
            ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
             
            for ctid in ctid_map:
                for data in data_list:
                    splitted_data = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', data)
                    
                    if pname == "ONMOPAY":
                        if ctid == splitted_data[2].replace('"', '').strip():
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
            
                            if data_dict["ActivityType"]:
                                for activity in DaiusActivityType:
                                    if activity.value == data_dict["ActivityType"]:
                                        data_dict["ActivityType"] = f'{data_dict["ActivityType"]} ({activity.name})'
                            self.ctid_data_dict[ctid].append(data_dict)
                        
                    elif pname == "ONMOPAY_REQUEST_COUNTER":
                        if ctid == splitted_data[1].replace('"', '').strip():
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[ctid].append(data_dict)
                    
                    elif pname == "GRIFF":
                        if ctid == splitted_data[1].replace('"', '').strip():
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[ctid].append(data_dict)
                
                    elif pname == "PACKS":
                        if ctid == splitted_data[3].replace('"', ''):
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[ctid].append(data_dict)
                                
                    
                    elif pname == "GRIFF_EXTHIT":
                        if ctid == str(splitted_data[2]).replace('"', ''):
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[str(ctid).replace('"', '')].append(data_dict)
                    
                    elif pname == "PACKS_EXTHIT":
                        if ctid == str(splitted_data[2]).replace('"', ''):
                            logging.info('packs ext ctid: %s', ctid)
                            data_dict = {}
                            for index, element in enumerate(splitted_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[str(ctid).replace('"', '')].append(data_dict)
                            logging.info('keys: %s', self.ctid_data_dict.keys())
            
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
            # ctid_map = self.validation_object.fmsisdn
            # logging.info('prism data ctid: %s', ctid_map)
            logging.info('data list prism: %s', data_list)
            for data in data_list:
                splitted_data = str(data).split("|")
                logging.info('splitted data: %s', splitted_data)
                # if ctid in data:
                data_dict = {}
                flow_tasks_element = []
                index_count = 28
                # logging.info('splitted data length: %s', len(splitted_data))
                for index, element in enumerate(splitted_data):
                    if index <= 27:
                        data_dict[header[index]] = element.replace('"', '').replace("'", '"').strip().rstrip(":")
                    elif index <= len(splitted_data) - 6:
                        flow_tasks_element.append(element.replace('"', '').replace("'", '"').strip())
                        data_dict[header[index_count]] = flow_tasks_element
                        
                    elif index <= len(splitted_data) - 2:
                        index_count += 1
                        data_dict[header[index_count]] = element.replace('"', '').replace("'", '"').strip()
                    
                    elif index == len(splitted_data) - 1:
                        # logging.info('index: %s', index)
                        try:
                            for i, td in enumerate(element.split("=")[1].split("]")[0].split(",")):
                                index_count += 1
                                data_dict[header[index_count]] = td.replace('"', '').replace("'", '"').strip()
                            # data_dict[header[len(header) - 1]] = f"{ctid}"
                        except IndexError as error:
                            logging.exception(error)
                    
                    # logging.info('index_: %s', index)
                    # elif index == len(splitted_data):
                
                # if ctid in data_dict["CTID"]: //support not available for now
                self.msisdn_data_dict[data_dict["THREAD"]] = data_dict
        
        
        if pname == "PRISM_TOMCAT":
            logging.info('msisdn data dict: %s', self.msisdn_data_dict)
            for thread, data in self.msisdn_data_dict.items():
                self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"].append(thread)
                logging.info('prism tomcat thread: %s', self.prism_tomcat_tlog_thread_dict)
        
        elif pname == "PRISM_DEAMON":
            for thread, data in self.msisdn_data_dict.items():
                self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"].append(thread)
                logging.info('prism daemon thread: %s', self.prism_daemon_tlog_thread_dict)
                    
                        
        if pname == "ONMOPAY":
            self.onmopay_tlog_dict = {"ONMOPAY_DMCONSUMER_DAIUS_ACTIVITY": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.onmopay_tlog_dict)
            logging.info('onmopay tlogs: %s', str(self.onmopay_tlog_dict).replace("'", '"'))
        
        elif pname == "ONMOPAY_REQUEST_COUNTER":
            self.onmopay_request_counter_tlog_dict = {"ONMOPAY_PAYCORE_REQUEST_COUNTER": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.onmopay_request_counter_tlog_dict)
            logging.info('onmopay paycore request counter tlogs: %s', str(self.onmopay_request_counter_tlog_dict))
        
        elif pname == "GRIFF":
            # self.griff_tlog_dict = {"GRIFF_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.griff_tlog_dict = {"GRIFF_TLOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.griff_tlog_dict)
            logging.info('griff tlogs: %s', str(self.griff_tlog_dict).replace("'", '"'))
        
        elif pname == "GRIFF_EXTHIT":
            # self.griff_ext_hit_tlog_dict = {"GRIFF_EXT_HIT_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.griff_ext_hit_tlog_dict = {"GRIFF_EXT_HIT_TLOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.griff_ext_hit_tlog_dict)
            logging.info('griff ext tlogs: %s', str(self.griff_ext_hit_tlog_dict))
            
        elif pname == "PACKS":
            # self.packs_tlog_dict = {"PACKS_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.packs_tlog_dict = {"PACKS_TLOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.packs_tlog_dict)
            logging.info('packs tlogs: %s', str(self.packs_tlog_dict).replace("'", '"'))
        
        elif pname == "PACKS_EXTHIT":
            # self.packs_ext_hit_tlog_dict = {"PACKS_EXT_HIT_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            logging.info('packs ctid data ext: %s', self.ctid_data_dict)
            self.packs_ext_hit_tlog_dict = {"PACKS_EXT_HIT_TLOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.packs_ext_hit_tlog_dict)
            logging.info('packs ext tlogs: %s', str(self.packs_ext_hit_tlog_dict).replace("'", '"'))
        
        elif pname == "PRISM_TOMCAT":
            # self.prism_tomcat_tlog_dict = {"PRISM_REALTIME_BILLING_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_tlog_dict = {"PRISM_TOMCAT_BILLING_TLOG": dict(self.msisdn_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_tlog_dict)
            logging.info('prism realtime billing tlogs: %s', str(self.prism_tomcat_tlog_dict).replace("'", '"'))
        
        elif pname == "PRISM_DEAMON":
            self.prism_daemon_tlog_dict = {"PRISM_DAEMON_TLOG": dict(self.msisdn_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_tlog_dict)
            logging.info('prism billing tlogs: %s', str(self.prism_daemon_tlog_dict).replace("'", '"'))
        
        # parse tlog for error
        if pname == "ONMOPAY":
            if self.ctid_data_dict:
                ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
                tlogParser_object.parse_tlog(pname, self.ctid_data_dict, ctid_map)
        
        # parse tlog for error
        if pname == "GRIFF" or pname == "PACKS":
            if self.ctid_data_dict:
                ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
                tlogParser_object.parse_tlog(pname, self.ctid_data_dict, ctid_map)
            
        # parse tlog for error
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
            if self.msisdn_data_dict:
                tlogParser_object.parse_tlog(pname, self.msisdn_data_dict)
        
    def prism_handler_req_resp_header_map(self, pname, data_list):
        # prism tomcat and daemon handler request response mapping
        
        if pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
            
            header = [
                        "TIMESTAMP","THREAD_ID","TASK_TYPE","URL","REQUEST","RESPONSE","TIME_TAKEN"
                    ]
        
        elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
            
            header = [
                        "TIMESTAMP","THREAD_ID","TASK_TYPE","URL","REQUEST_XML","RESPONSE_XML","TIME_TAKEN"
                    ]
        elif pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_DAEMON_REQ_RESP":
            
            header = [
                        "TIMESTAMP","THREAD","REQTYPE","URL","ENTITY_DATA","PARAMTERS","RESPONSE_CODE",\
                        "RESPONSE_TIME(sec)","RESPONSE"
                    ]
            
        elif pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP":
            
            header = [
                        "TIMESTAMP","THREAD","URL","RESPONSE","CODE","RETRY_COUNT"
                    ]
        
        if pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_TOMCAT_REQ_RESP" or pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP":
            
            threads = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
            
        elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP"\
            or pname == "PRISM_DAEMON_REQ_RESP" or pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP":
                
            threads = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
            
        for thread in threads:
            for data in data_list:
                splitted_data = str(data).split("|")
                # splitted_data = re.split(r'\|(?=[^|])(?:[^|]*\([^)]+\))*[^|]*', data)
                # splitted_data = re.split(r'\|(?=(?:[^<]*<[^>]*>)*[^>]*$)', data)
                if thread == splitted_data[1].replace('"', '').strip():
                    logging.info('splitted data: %s', splitted_data)
                    
                    data_dict = {}
                    
                    try:
                        for index, element in enumerate(splitted_data):
                            
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"').strip().rstrip(":")
                        self.ctid_data_dict[thread].append(data_dict)
                    except IndexError as error:
                        logging.exception(error)
            logging.info('prism gen req resp data dict: %s', self.ctid_data_dict)
    
        if pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP":
            # self.prism_tomcat_handler_generic_http_req_resp_dict = {"PRISM_TOMCAT_GENERIC_HTTP_HANDLER_REQ_RESP": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_handler_generic_http_req_resp_dict = {"PRISM_TOMCAT_GENERIC_HTTP_HANDLER_REQ_RESP": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_handler_generic_http_req_resp_dict)
            logging.info('prism tomcat generic http req-resp: %s', str(self.prism_tomcat_handler_generic_http_req_resp_dict).replace("'", '"'))
        
        elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP":
            # self.prism_tomcat_handler_generic_soap_req_resp_dict = {"PRISM_TOMCAT_GENERIC_SOAP_HANDLER_REQ_RESP": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_handler_generic_soap_req_resp_dict = {"PRISM_TOMCAT_GENERIC_SOAP_HANDLER_REQ_RESP": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_handler_generic_soap_req_resp_dict)
            logging.info('prism tomcat generic soap req-resp: %s', str(self.prism_tomcat_handler_generic_soap_req_resp_dict).replace("'", '"'))
        
        elif pname == "PRISM_TOMCAT_REQ_RESP":
            # self.prism_tomcat_request_log_dict = {"PRISM_TOMCAT_REQUEST_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_request_log_dict = {"PRISM_TOMCAT_REQUEST_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_request_log_dict)
            logging.info('prism tomcat request log: %s', str(self.prism_tomcat_request_log_dict).replace("'", '"'))
        
        elif pname == "PRISM_TOMCAT_CALLBACK_V2_REQ_RESP":
            # self.prism_tomcat_callbackV2_log_dict = {"PRISM_TOMCAT_CALLBACK_V2_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_callbackV2_log_dict = {"PRISM_TOMCAT_CALLBACK_V2_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_callbackV2_log_dict)
            logging.info('prism tomcat callbackV2 log: %s', str(self.prism_tomcat_callbackV2_log_dict).replace("'", '"'))
        
        elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
            # self.prism_daemon_handler_generic_http_req_resp_dict = {"PRISM_DAEMON_GENERIC_HTTP_HANDLER_REQ_RESP": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_daemon_handler_generic_http_req_resp_dict = {"PRISM_DAEMON_GENERIC_HTTP_HANDLER_REQ_RESP": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_handler_generic_http_req_resp_dict)
            logging.info('prism daemon generic http req-resp: %s', str(self.prism_daemon_handler_generic_http_req_resp_dict).replace("'", '"'))
        
        elif pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
            # self.prism_daemon_handler_generic_soap_req_resp_dict = {"PRISM_DAEMON_GENERIC_SOAP_HANDLER_REQ_RESP": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_daemon_handler_generic_soap_req_resp_dict = {"PRISM_DAEMON_GENERIC_SOAP_HANDLER_REQ_RESP": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_handler_generic_soap_req_resp_dict)
            logging.info('prism daemon generic soap req-resp: %s', str(self.prism_daemon_handler_generic_soap_req_resp_dict).replace("'", '"'))
        
        elif pname == "PRISM_DAEMON_REQ_RESP":
            # self.prism_daemon_request_log_dict = {"PRISM_DAEMON_REQUEST_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_daemon_request_log_dict = {"PRISM_DAEMON_REQUEST_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_request_log_dict)
            logging.info('prism daemon request log: %s', str(self.prism_daemon_request_log_dict).replace("'", '"'))
        
        elif pname == "PRISM_DAEMON_CALLBACK_V2_REQ_RESP":
            # self.prism_daemon_callbackV2_log_dict = {"PRISM_DAEMON_CALLBACK_V2_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_daemon_callbackV2_log_dict = {"PRISM_DAEMON_CALLBACK_V2_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_callbackV2_log_dict)
            logging.info('prism daemon generic soap req-resp: %s', str(self.prism_daemon_callbackV2_log_dict).replace("'", '"'))
   
   
    def sms_data_header_mapping(self, pname, data_list):
        #sms tlog header map
        tlogParser_object = TlogParser(self.initializedPath_object, self.outputDirectory_object,\
                                        self.validation_object, self.log_mode, self.oarm_uid,\
                                        self.prism_daemon_tlog_thread_dict, self.prism_tomcat_tlog_thread_dict)
        if pname == "PRISM_SMSD":
            
            header = [
                        "TIMESTAMP","THREAD","SITE_ID","MSISDN","SRNO","SRVCODE","MSG","HANDLER","STATUS","REMARKS","TIME_TAKEN","SMS_INFO"
                    ]
     
            for data in data_list:
                splitted_data = str(data).split("|")
                # splitted_data = re.split(r'\|(?=[^|])(?:[^|]*\([^)]+\))*[^|]*', data)
                # splitted_data = re.split(r'\|(?=(?:[^<]*<[^>]*>)*[^>]*$)', data)
                
                logging.info('splitted data: %s', splitted_data)
                
                data_dict = {}
                
                try:
                    for index, element in enumerate(splitted_data):
                        
                            data_dict[header[index]] = element.replace('"', '').replace("'", '"').strip().rstrip(":")
                    # self.msisdn_sms_data_dict[f"{self.validation_object.fmsisdn}"].append(data_dict)
                    self.msisdn_sms_data_list.append(data_dict)
                except IndexError as error:
                    logging.exception(error)
            logging.info('sms tlog data dict: %s', self.msisdn_sms_data_list)
    
        if pname == "PRISM_SMSD":
            # self.prism_smsd_tlog_dict = {"PRISM_SMSD_TLOG": dict(self.msisdn_sms_data_dict)}
            self.prism_smsd_tlog_dict = {"PRISM_SMSD_TLOG": self.msisdn_sms_data_list}
            self.payment_data_dict_list.append(self.prism_smsd_tlog_dict)
            logging.info('prism sms tlog: %s', str(self.prism_smsd_tlog_dict).replace("'", '"'))
        
        # parse tlog for error
        if self.prism_smsd_tlog_dict:
            tlogParser_object.parse_tlog(pname, self.prism_smsd_tlog_dict)
        
    def ctid_based_accesslog_fetch(self, pname, files):
        #access data for griff and packs        
        if pname == "GRIFF" or pname == "PACKS" or pname == "PRISM_TOMCAT":
            if pname == "GRIFF" or pname == "PACKS":
                ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
            # elif pname == "PRISM_TOMCAT":
            #     ctid_map = self.prism_ctid
            logging.info('access ctid list: %s', ctid_map)
            for ctid in ctid_map:
                self.constructor_access_paramter_reinitialize()
                for file in files:
                    try:
                        data = subprocess.check_output(f"cat {file} | grep -a {ctid}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                        self.access_record.append(data)
                        
                        if self.access_record:
                            logging.info('%s access record: %s', pname, self.access_record)
                            data_list = []
                            for data in self.access_record:
                                logging.info('data in access log: %s', data)
                                for record in str(data).splitlines():
                                    if record:
                                        logging.info('access rec: %s', record)
                                        data_list.append(record)
                        self.ctid_access_data_dict[f"{ctid}"].append(data_list)
                    except Exception as ex:
                        logging.info(ex)
                        
        
        if self.ctid_access_data_dict:
            self.access_data_mapping(pname)
            
    def msisdn_based_accesslog_fetch(self, pname, files):
        #keeping prism out of ctid flow
        if pname == "PRISM_TOMCAT":
            mdn = self.validation_object.fmsisdn

        self.constructor_access_paramter_reinitialize()
        for file in files:
            try:
                data = subprocess.check_output(f"cat {file} | grep -a {mdn}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                self.access_record.append(data)
                
                if self.access_record:
                    logging.info('%s access record: %s', pname, self.access_record)
                    data_list = []
                    for data in self.access_record:
                        logging.info('data in access log: %s', data)
                        for record in str(data).splitlines():
                            if record:
                                logging.info('access rec: %s', record)
                                data_list.append(record)
                self.msisdn_access_data_dict[f"{mdn}"].append(data_list)
            except Exception as ex:
                logging.info(ex)
                        
        
        if self.msisdn_access_data_dict:
            self.access_data_mapping(pname)

    def onmopay_data_mapping(self, pname, data_list):
        #csv data without header
             
        if pname == "ONMOPAY_CG_REDIRECTION":
            ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
            for ctid in ctid_map:
                for data in data_list:
                    if ctid == str(data).split(",")[4]:
                        self.ctid_data_dict[ctid].append(data)
            self.onmopay_cg_redirection_tlog_dict = {"ONMOPAY_PAYCORE_CG_REDIRECTION": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.onmopay_cg_redirection_tlog_dict)
        
        elif pname == "ONMOPAY_PAYCORE_PERF_LOG":
            ctid_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
            for ctid in ctid_map:
                for data in data_list:
                    if ctid == str(data).split("|")[1]:
                        self.ctid_data_dict[ctid].append(data)
            self.onmopay_paycore_plog_dict = {"ONMOPAY_PAYCORE_PERF_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.onmopay_paycore_plog_dict)
            
    
    def access_data_mapping(self, pname):
        
        logging.info('ctid based access data dict: %s', self.ctid_access_data_dict)
        
        if pname == "GRIFF":
            # self.griff_access_log_dict = {"GRIFF_ACCESS_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_access_data_dict)}}
            self.griff_access_log_dict = {"GRIFF_ACCESS_LOG": dict(self.ctid_access_data_dict)}
            self.payment_data_dict_list.append(self.griff_access_log_dict)
            logging.info('griff access logs: %s', self.griff_access_log_dict)
    
        elif pname == "PACKS":
            self.packs_access_log_dict = {"PACKS_ACCESS_LOG": dict(self.ctid_access_data_dict)}
            self.payment_data_dict_list.append(self.packs_access_log_dict)
            logging.info('packs access logs: %s', self.packs_access_log_dict)
        
        elif pname == "PRISM_TOMCAT":
            # self.prism_access_log_dict = {"PRISM_ACCESS_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_access_data_dict)}}
            self.prism_access_log_dict = {"PRISM_ACCESS_LOG": dict(self.msisdn_access_data_dict)}
            self.payment_data_dict_list.append(self.prism_access_log_dict)
            logging.info('prism access logs: %s', self.prism_access_log_dict)
        
        # if pname == "PRISM_TOMCAT":
        #     tlogParser_object = TlogParser(self.initializedPath_object, self.outputDirectory_object,\
        #                                 self.validation_object, self.log_mode, self.oarm_uid,\
        #                                 self.prism_daemon_tlog_thread_dict, self.prism_tomcat_tlog_thread_dict)
        #     if self.msisdn_access_data_dict:
        #         tlogParser_object.parse_accessLog("PRISM_TOMCAT_ACCESS", self.msisdn_access_data_dict)
            
    def perf_data_mapping(self, pname, data_list):
        #perf log mapping
        if pname == "PRISM_TOMCAT_PERF_LOG":
            threads = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
        elif pname == "PRISM_DAEMON_PERF_LOG":
            threads = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
        
        for thread in threads:
            for data in data_list:
                if thread in data:
                    self.ctid_data_dict[thread].append(data)
                
        if pname == "PRISM_TOMCAT_PERF_LOG":
            # self.prism_tomcat_perf_log_dict = {"PRISM_TOMCAT_PERF_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.prism_tomcat_perf_log_dict = {"PRISM_TOMCAT_PERF_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_tomcat_perf_log_dict)
            logging.info('prism tomcat perf log: %s', self.prism_tomcat_perf_log_dict)
    
        elif pname == "PRISM_DAEMON_PERF_LOG":
            self.prism_daemon_perf_log_dict = {"PRISM_DAEMON_PERF_LOG": dict(self.ctid_data_dict)}
            self.payment_data_dict_list.append(self.prism_daemon_perf_log_dict)
            logging.info('prism daemon perf log: %s', self.prism_daemon_perf_log_dict)
    
    def msisdn_based_sms_tlog_fetch(self, pname, files):    
        for file in files:
            try:
                data = subprocess.check_output(f"cat {file} | grep -a {self.validation_object.fmsisdn}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                self.tlog_record.append(data)
            except Exception as ex:
                logging.info(ex)

                            
    def constructor_parameter_reinitialize(self):
        self.tlog_files = []
        self.backup_tlog_files = []
        self.access_files = []
        self.tlog_record = []
        self.access_record = []
        self.is_backup_file = False
        self.tlog_files_with_ctid_msisdn = []
        self.tlog_backup_files_with_ctid_msisdn = []
        # self.tlog_dict = defaultdict()
        self.ctid_data_dict = defaultdict(list)
        self.ctid_access_data_dict = defaultdict(list)
        
    def constructor_ctid_msisdn_paramter_reinitialization(self):
        self.ctid_msisdn_map_dict = {}
        
    def constructor_access_paramter_reinitialize(self):
        self.access_record = []
            