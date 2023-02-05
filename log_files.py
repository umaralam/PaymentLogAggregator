from datetime import datetime, timedelta
import logging
from pathlib import Path
import socket

class LogFileFinder:
    """
    log file finder class
    """
    def __init__(self, initializedPath_object, validation_object, config):
    
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.config = config
        
        self.start_date = validation_object.start_date
        self.end_date = validation_object.end_date
        
        self.access_log_files = []
        
        self.tlog_files = []
        self.tlog_dir = ""
        
        self.tlog_backup_files = []
        self.tlog_backup_dir = ""
      
        self.input_date = []
        
        self.s_date = datetime.strptime(datetime.strftime(self.start_date, "%Y%m%d"), "%Y%m%d")
        self.e_date = datetime.strptime(datetime.strftime(self.end_date, "%Y%m%d"), "%Y%m%d")
    
    def get_tlog_files(self, pname):
        
        #re-initializing constructor parameters
        self.constructor_paramter_reinitialize()
        
        if pname == "GRIFF":
            #current tlog file
            self.tlog_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"])
            
            splitted_tlog_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_log'])\
                                    .split("/")[0:-1]
            for i in range(1, len(splitted_tlog_path)):
                self.tlog_dir += f"/{splitted_tlog_path[i]}"

        
        elif pname == "PACKS":
            #current tlog file
            self.tlog_files.append(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_log'])
            
            splitted_tlog_path = str(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_log'])\
                                    .split("/")[0:-1]
            for i in range(1, len(splitted_tlog_path)):
                self.tlog_dir += f"/{splitted_tlog_path[i]}"
        
            
        elif pname == "GRIFF_EXTHIT":
            #current ext hit file
            self.tlog_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_TPTLOGAppender_log"])
        
        elif pname == "PACKS_EXTHIT":
            #current ext hit file
            self.tlog_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_EXTERNAL_HITS_APPENDER.FILE_log"])
        
        elif pname == "PRISM_TOMCAT":
            #current tlog file
            self.tlog_files.append(f'{self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_tlog_path"]}/TLOG_BILLING_REALTIME_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_tlog_path"]
        
        elif pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP":
            #current generic http req-resp tlog files
            self.tlog_files.append(f'{self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_http_handler_req_resp_path"]}/TLOG_REQUEST_RESPONSE_GENERIC_HTTP_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_http_handler_req_resp_path"]
        
        elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP":
            #current generic soap req-resp tlog files
            self.tlog_files.append(f'{self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_soap_handler_req_resp_path"]}/TLOG_REQUEST_RESPONSE_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_generic_soap_handler_req_resp_path"]
        
        elif pname == "PRISM_DEAMON":
            #current tlog file
            self.tlog_files.append(f'{self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_tlog_path"]}/TLOG_BILLING_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_tlog_path"]
        
        elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
            #current generic http req-resp tlog files
            self.tlog_files.append(f'{self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_http_handler_req_resp_path"]}/TLOG_REQUEST_RESPONSE_GENERIC_HTTP_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_http_handler_req_resp_path"]
        
        elif pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
            #current generic soap req-resp tlog files
            self.tlog_files.append(f'{self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_soap_handler_req_resp_path"]}/TLOG_REQUEST_RESPONSE_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_generic_soap_handler_req_resp_path"]
        
        elif pname == "PRISM_SMSD":
            #current tlog file
            self.tlog_files.append(f'{self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_tlog_path"]}/TLOG_SMS_*.tmp')
            self.tlog_dir = self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_tlog_path"]
        
        
        #process file for if pname == "GRIFF" or pname == "PACKS"
        if pname == "GRIFF" or pname == "PACKS" or pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON"\
                or pname == "PRISM_SMSD" or pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or\
                pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or\
                pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
            
            path = Path(rf"{self.tlog_dir}")
            
            #method call to date range list
            self.input_date = self.date_range_list(self.s_date, self.e_date)
            
            for date in self.input_date:
                # logging.info('search date is: %s', datetime.strftime(date, "%Y-%m-%d"))
                if pname == "GRIFF" or pname == "PACKS":
                    
                    input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                
                elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD" or\
                        pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP" or\
                        pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP" or pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":           
                    
                    input_date_formatted = datetime.strftime(date, "%Y%m%d")
                
                #input dated file in the tlog directory
                if pname == "GRIFF":
                    dated_tlog_files = [p for p in path.glob(f"griffTLog-{input_date_formatted}-*.csv")]
                elif pname == "PACKS":
                    dated_tlog_files = [p for p in path.glob(f"packTlog-{input_date_formatted}-*.csv")]
                elif pname == "PRISM_TOMCAT":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_BILLING_REALTIME_{input_date_formatted}_*..log")]
                elif pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log")]
                elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log")]
                elif pname == "PRISM_DEAMON":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_BILLING_{input_date_formatted}_*..log")]
                elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log")]
                elif pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log")]
                elif pname == "PRISM_SMSD":
                    dated_tlog_files = [p for p in path.glob(f"TLOG_SMS_{input_date_formatted}_*..log")]
                    
                if bool(dated_tlog_files):
                    if pname == "GRIFF":
                        logging.info(f"griffTLog-{input_date_formatted}-*.csv file present")
                    elif pname == "PACKS":
                        logging.info(f"packTlog-{input_date_formatted}-*.csv file present")
                    elif pname == "PRISM_TOMCAT":
                        logging.info(f"TLOG_BILLING_REALTIME_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_DEAMON":
                        logging.info(f"TLOG_BILLING_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log file present")
                    elif pname == "PRISM_SMSD":
                        logging.info(f"TLOG_SMS_{input_date_formatted}_*..log file present")
                        
                    for files in dated_tlog_files:
                        self.tlog_files.append(str(files))
                    logging.info('tlog files ex: %s', self.tlog_files)
                else:
                    if pname == "GRIFF":
                        logging.info(f"griffTLog-{input_date_formatted}-*.csv file not present" )
                    elif pname == "PACKS":
                        logging.info(f"packTlog-{input_date_formatted}-*.csv file not present" )
                    elif pname == "PRISM_TOMCAT":
                        logging.info(f"TLOG_BILLING_REALTIME_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_TOMCAT_GENERIC_HTTP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_TOMCAT_GENERIC_SOAP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_DEAMON":
                        logging.info(f"TLOG_BILLING_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_DAEMON_GENERIC_HTTP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_GENERIC_HTTP_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_DAEMON_GENERIC_SOAP_REQ_RESP":
                        logging.info(f"TLOG_REQUEST_RESPONSE_{input_date_formatted}_*..log file not present")
                    elif pname == "PRISM_SMSD":
                        logging.info(f"TLOG_SMS_{input_date_formatted}_*..log file not present")
        
        return self.tlog_files
    
    def get_tlog_backup_files(self, pname):
        #re-initializing constructor parameters
        self.constructor_paramter_reinitialize()
        
        if pname == "GRIFF":    
            #getting backup tlog files directory
            splitted_tlog_backup_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_backup_log'])\
                                    .split("/")[0:-1]
        elif pname == "PACKS":
            #getting backup tlog files directory
            splitted_tlog_backup_path = str(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_backup_log'])\
                                .split("/")[0:-1]
            
        elif pname == "GRIFF_EXTHIT":
            #getting backup tlog files directory
            splitted_tlog_backup_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TPTLOGAppender_backup_log'])\
                                    .split("/")[0:-1]
            
        elif pname == "PACKS_EXTHIT":
            #getting backup tlog files directory
            splitted_tlog_backup_path = str(self.initializedPath_object.packs_tomcat_log_path_dict['packs_EXTERNAL_HITS_APPENDER.FILE_backup_log'])\
                                .split("/")[0:-1]
                                
        for i in range(1, len(splitted_tlog_backup_path)):
            self.tlog_backup_dir += f"/{splitted_tlog_backup_path[i]}"
                        
        path = Path(rf"{self.tlog_backup_dir}")
        
        #method call to date range list
        input_date = self.date_range_list(self.s_date, self.e_date)
        
        for date in input_date:
            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                    
            #input dated file in the backup directory
            if pname == "GRIFF":
                dated_tlog_backup_files = [p for p in path.glob(f"griffTLog-{input_date_formatted}-*.zip")]
            elif pname == "PACKS":
                dated_tlog_backup_files = [p for p in path.glob(f"packTlog-{input_date_formatted}-*.zip")]
            elif pname == "GRIFF_EXTHIT":
                dated_tlog_backup_files = [p for p in path.glob(f"exthits-{input_date_formatted}-*.zip")]
            elif pname == "PACKS_EXTHIT":
                dated_tlog_backup_files = [p for p in path.glob(f"External_Hits-{input_date_formatted}-*.zip")]
                
            
            if bool(dated_tlog_backup_files):
                if pname == "GRIFF":
                    logging.info(f"griffTLog-{input_date_formatted}-*.zip file present")
                elif pname == "PACKS":
                    logging.info(f"packTlog-{input_date_formatted}-*.zip file present")
                elif pname == "GRIFF_EXTHIT":
                    logging.info(f"exthits-{input_date_formatted}-*.zip file present")
                elif pname == "PACKS_EXTHIT":
                    logging.info(f"External_Hits-{input_date_formatted}-*.zip file present")
                
                    
                for files in dated_tlog_backup_files:
                    self.tlog_backup_files.append(str(files))
                    
        return self.tlog_backup_files
    
    def get_tomcat_access_files(self, pname):
        #re-initializing constructor parameters
        self.constructor_paramter_reinitialize()
        
        hostname = socket.gethostname()
        
        try:
            if pname == "GRIFF":
                access_log_prefix = self.config[hostname]["GRIFF"]["GRIFF_TOMCAT"]["ACCESS_LOG_PREFIX"]
                access_log_suffix = self.config[hostname]["GRIFF"]["GRIFF_TOMCAT"]["ACCESS_LOG_SUFFIX"]
                access_log_path = self.initializedPath_object.griff_tomcat_log_path_dict["griff_tomcat_access_path"]
            
            elif pname == "PACKS":
                access_log_prefix = self.config[hostname]["PACKS"]["PACKS_TOMCAT"]["ACCESS_LOG_PREFIX"]
                access_log_suffix = self.config[hostname]["PACKS"]["PACKS_TOMCAT"]["ACCESS_LOG_SUFFIX"]
                access_log_path = self.initializedPath_object.packs_tomcat_log_path_dict["packs_tomcat_access_path"]
            
            elif pname == "PRISM_TOMCAT":
                access_log_prefix = self.config[hostname]["PRISM"]["PRISM_TOMCAT"]["ACCESS_LOG_PREFIX"]
                access_log_suffix = self.config[hostname]["PRISM"]["PRISM_TOMCAT"]["ACCESS_LOG_SUFFIX"]
                access_log_path = self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_access_path"]
        
        except KeyError as ex:
            logging.info('key error: %s', ex)
                
        path = Path(rf"{access_log_path}")
        
        #method call to date range list
        self.input_date = self.date_range_list(self.s_date, self.e_date)
        
        for date in self.input_date:
            # logging.info('search date is: %s', datetime.strftime(date, "%Y-%m-%d"))
            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")            
            
            #input dated access file in the access log path
            
            dated_access_files = [p for p in path.glob(f"{access_log_prefix}.{input_date_formatted}{access_log_suffix}")]
                        
            if bool(dated_access_files):
                logging.info(f"{access_log_prefix}.{input_date_formatted}{access_log_suffix} file present")        
    
            for files in dated_access_files:
                    self.access_log_files.append(str(files))
        
        return self.access_log_files
                    
    def date_range_list(self, start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += timedelta(days=1)
        return date_list
    
    
    def constructor_paramter_reinitialize(self):
        self.access_log_files = []
        self.tlog_files = []
        self.input_date = []
        self.tlog_dir = ""
        self.tlog_backup_files = []
        self.tlog_backup_dir = ""