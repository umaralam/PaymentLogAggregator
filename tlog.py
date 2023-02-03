import csv
import logging
import re
import signal
import subprocess
from log_files import LogFileFinder
from collections import defaultdict


class Tlog:
    """
    tlog mapping class
    """
    def __init__(self, initializedPath_object, validation_object,\
                    payment_data_dict_list, payment_data_dict, config,\
                    griff_tlog_dict, packs_tlog_dict,\
                    griff_ext_hit_tlog_dict, packs_ext_hit_tlog_dict,\
                    prism_ctid):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
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
        self.ctid_access_data_dict = defaultdict(list)
        
        #Is for both tlog and external tlog
        self.griff_ctid_msisdn_data_list = []
        self.packs_ctid_msisdn_data_list = []
        
        #for external hits
        # self.griff_ctid_data_list = []
        # self.packs_ctid_data_list = []
        
        #header data mapped tlogs
        self.griff_access_log_dict = {}
        self.packs_access_log_dict = {}
        
        #log processor initialization parameter
        self.payment_data_dict_list = payment_data_dict_list
        self.payment_data_dict = payment_data_dict
        self.config = config
        self.griff_tlog_dict = griff_tlog_dict
        self.packs_tlog_dict = packs_tlog_dict
        self.griff_ext_hit_tlog_dict = griff_ext_hit_tlog_dict
        self.packs_ext_hit_tlog_dict = packs_ext_hit_tlog_dict
        
        self.prism_ctid = prism_ctid
    
    def get_tlog(self, pname):
        """
        calling path finder method
        """
        
        logfile_object = LogFileFinder(self.initializedPath_object, self.validation_object, self.config)

        if pname == "GRIFF" or pname == "PACKS":
            self.constructor_parameter_reinitialize()
            self.constructor_ctid_msisdn_paramter_reinitialization()
            
        elif pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
            self.constructor_parameter_reinitialize()
        
        self.tlog_files = logfile_object.get_tlog_files(pname)
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
            self.backup_tlog_files = logfile_object.get_tlog_backup_files(pname)
            
        # logging.info('tlog files: %s', self.tlog_files)
        # logging.info('backup tlog files: %s', self.backup_tlog_files)
        
        if self.tlog_files:
            if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
                for file in self.tlog_files:
                    #function call
                    self.msisdn_ctid_map(pname, file, self.is_backup_file)
                    
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
                self.ctid_based_tlog_fetch(pname, self.tlog_files, False)
            
        if self.backup_tlog_files:
            self.is_backup_file = True
            
            for file in self.backup_tlog_files:
                #function call
                self.msisdn_ctid_map(pname, file, self.is_backup_file)
            
        if pname == "GRIFF":
            if self.initializedPath_object.griff_tomcat_log_path_dict["griff_tomcat_access_path"]:
                logging.debug('griff tomcat access path exists.')
                self.access_files = logfile_object.get_tomcat_access_files(pname)
        
        elif pname == "PACKS":
            if self.initializedPath_object.packs_tomcat_log_path_dict["packs_tomcat_access_path"]:
                logging.debug('packs tomcat access path exists.')
                self.access_files = logfile_object.get_tomcat_access_files(pname)
        
        if self.access_files:
            self.ctid_based_accesslog_fetch(pname, self.access_files)
            
        if self.ctid_msisdn_map_dict and (self.tlog_files_with_ctid_msisdn or self.tlog_backup_files_with_ctid_msisdn):
            if self.tlog_files_with_ctid_msisdn:
                self.ctid_based_tlog_fetch(pname, self.tlog_files_with_ctid_msisdn, False)
            if self.tlog_backup_files_with_ctid_msisdn:
                self.ctid_based_tlog_fetch(pname, self.tlog_backup_files_with_ctid_msisdn, True)
        
        if self.tlog_record:
            logging.info('tlog record: %s', self.tlog_record)
            data_list = []
            for data in self.tlog_record:
                logging.info('data in tlog: %s', data)
                for record in str(data).splitlines():
                    if record not in data_list:
                        data_list.append(record)
                    
            self.tlog_record_header_mapping(pname, self.is_backup_file, data_list)
            # logging.info('data list: %s', data_list)
        
        if pname == "GRIFF" and self.griff_tlog_dict:
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
    
    def msisdn_ctid_map(self, pname, file, is_backup_file):
        
        if is_backup_file:
            if pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 5,4 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
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
            if pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    self.tlog_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 5,4 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
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
                
        if pname == "GRIFF":
            ctid_msisdn_data = ctid_mdn_data.split('\n')
            for row in ctid_msisdn_data:
                if row != "":
                    self.griff_ctid_msisdn_data_list.append(row)
            
        elif pname == "PACKS":
            ctid_msisdn_data = ctid_mdn_data.split('\n')
            logging.info('packs ctid msisdn data: %s', ctid_msisdn_data)
            for row in ctid_msisdn_data:
                if row != "":
                    self.packs_ctid_msisdn_data_list.append(row)
        
        if pname == "GRIFF" or pname == "PACKS":
            for row in ctid_msisdn_data:
                if row != "":
                    if pname == "GRIFF":
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
            if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
                temp_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
                
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
                temp_map = self.prism_ctid

                # logging.info('temp map ee: %s', temp_map)
                
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
        except Exception as ex:
            logging.info(ex)
            
    def tlog_record_header_mapping(self, pname, is_backup, data_list):
        
        #GRIFF tlog header mapping
        if pname == "GRIFF":
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
                        "PackTLogCreatedTimeStamp","THREAD_NAME","API_NAME","CTID","REQ_MSISDN","REQ_APPID","REQ_PACKID",\
                        "REQ_OPERATOR","REQ_CIRCLE","SEL_OPERATOR","SEL_CIRCLE","REQ_ACTION","REQ_USERINFO","RES_USERINFO",\
                        "REQ_AMOUNT","REQ_SERVICEKEY","REQ_EVENTKEY","REQ_ALL_PARAMS","BILLING_SERVICE_KEY","BILLING_URL_TEMPLATE",\
                        "BILLING_URL_CALLED","BILLING_REQ_TIME_START","BILLING_REQ_TIME_END","BILLING_AMOUNT","BILLING_RES_STATUS",\
                        "BILLING_RES_MESSAGE","CREDITS_BEFORE","CREDITS_AFTER","APP_NAME","PACK_NAME","SUB_TYPE","BILLING_MODE",\
                        "BILLING_TYPE","CALLBACK_REGISTERED","RET_APPS","RET_PACKS","RET_STATUS","RET_ERROR_REASON","SEL_APPIDs",\
                        "SEL_PACKIDs","SUBSCRIBER_ID","SUBS_STATUS_BEFORE","SUBS_STATUS_AFTER","REQ_ACTION_MODE","REQ_NEW_MSISDN",\
                        "PACK_LEVEL_FILTER","APP_LEVEL_FILTER","COMMON_PARAM_FILTER","CHARGE_KEY","SOURCE_IP","GRIFF_RESPONSE",\
                        "THIRD_PARTIES","TOTAL_TIMETAKEN","PACKS_TIMETAKEN","EXT_TIMETAKEN","TRAP_STATUS"
                    ]
        
        elif pname == "GRIFF_EXTHIT":
            header = [
                        "TIMESTAMP","THREAD_NAME","CTID","STORENAME","EXTNAME","APINAME","HTTPMETHOD","HTTPSTATUSCODE","TIMETAKEN",\
                        "PROXYHOST","PROXYPORT","URL","REQHEADERS","RQEPARAMS","REQBODY","RESPONSE"
                    ]
        
        elif pname == "PACKS_EXTHIT":
            header = [
                        "TIMESTAMP","THREAD_NAME","CTID","APPID","PACKID","APINAME","EXTNAME","HTTPMETHOD","HTTPSTATUSCODE",\
                        "TIMETAKEN","PROXYHOST","PROXYPORT","URL","REQHEADERS","RQEPARAMS","REQBODY","RESPONSE","RESPONSEHEADERS"
                    ]
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
            temp_map = self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]
            
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
            temp_map = self.prism_ctid
            
        for ctid in temp_map:
            if pname == "GRIFF" or pname == "PACKS" or pname == "GRIFF_EXTHIT" or pname == "PACKS_EXTHIT":
                for data in data_list:
                    splited_data = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', data)
                    
                    if pname == "GRIFF":
                        if ctid == splited_data[1].replace('"', '').strip():
                            data_dict = {}
                            for index, element in enumerate(splited_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[ctid].append(data_dict)
                
                    elif pname == "PACKS":
                        if ctid == splited_data[3].replace('"', ''):
                            data_dict = {}
                            for index, element in enumerate(splited_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[ctid].append(data_dict)
                                
                    
                    elif pname == "GRIFF_EXTHIT":
                        if ctid == str(splited_data[2]).replace('"', ''):
                            data_dict = {}
                            for index, element in enumerate(splited_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[str(ctid).replace('"', '')].append(data_dict)
                    
                    elif pname == "PACKS_EXTHIT":
                        if ctid == str(splited_data[2]).replace('"', ''):
                            data_dict = {}
                            for index, element in enumerate(splited_data):
                                data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                            self.ctid_data_dict[str(ctid).replace('"', '')].append(data_dict)
            
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
                pass
                        
        # logging.info('ctid data dict: %s', self.ctid_data_dict)
        if pname == "GRIFF":
            self.griff_tlog_dict = {"GRIFF_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.payment_data_dict_list.append(self.griff_tlog_dict)
            logging.info('griff tlogs: %s', str(self.griff_tlog_dict).replace("'", '"'))
        
        elif pname == "GRIFF_EXTHIT":
            self.griff_ext_hit_tlog_dict = {"GRIFF_EXT_HIT_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.payment_data_dict_list.append(self.griff_ext_hit_tlog_dict)
            logging.info('griff ext tlogs: %s', str(self.griff_ext_hit_tlog_dict))
            
        elif pname == "PACKS":
            self.packs_tlog_dict = {"PACKS_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.payment_data_dict_list.append(self.packs_tlog_dict)
            logging.info('packs tlogs: %s', str(self.packs_tlog_dict).replace("'", '"'))
        
        elif pname == "PACKS_EXTHIT":
            self.packs_ext_hit_tlog_dict = {"PACKS_EXT_HIT_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}
            self.payment_data_dict_list.append(self.packs_ext_hit_tlog_dict)
            logging.info('packs ext tlogs: %s', str(self.packs_ext_hit_tlog_dict).replace("'", '"'))
            
        
        # logging.info('json tlog data: %s',json.dumps(self.payment_tlog_dict))
            
    
    def ctid_based_accesslog_fetch(self, pname, files):
        if pname == "GRIFF":
            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                self.constructor_access_paramter_reinitialize()
                for file in files:
                    try:
                        data = subprocess.check_output(f"cat {file} | grep -a {ctid}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                        self.access_record.append(data)
                        
                        if self.access_record:
                            logging.info('griff access record: %s', self.access_record)
                            data_list = []
                            for data in self.access_record:
                                logging.info('data in tlog: %s', data)
                                for record in str(data).splitlines():
                                    if record:
                                        logging.info('access rec: %s', record)
                                        data_list.append(record)
                                # calling access data map function
                        self.ctid_access_data_dict[f"{ctid}"].append(data_list)
                    except Exception as ex:
                        logging.info(ex)
                        
        elif pname == "PACKS":
            for file in files:
                try:
                    data = subprocess.check_output(f"cat {file} | grep -a {self.validation_object.fmsisdn}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                    self.access_record.append(data)
                    
                    if self.access_record:
                        # logging.info('packs access record: %s', self.access_record)
                        self.ctid_access_data_dict[f"{self.validation_object.fmsisdn}"].append(self.access_record)
                except Exception as ex:
                    logging.info(ex)
        
        if self.ctid_access_data_dict:
            self.access_data_mapping(pname)
            
    
    def access_data_mapping(self, pname):
        
        logging.info('ctid based access data dict: %s', self.ctid_access_data_dict)
        
        if pname == "GRIFF":
            # self.griff_access_log_dict = {"GRIFF_ACCESS_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_access_data_dict)}}
            self.griff_access_log_dict = {"GRIFF_ACCESS_LOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_access_data_dict)}}
            self.payment_data_dict_list.append(self.griff_access_log_dict)
            logging.info('griff access logs: %s', self.griff_access_log_dict)
    
        elif pname == "PACKS":
            self.packs_access_log_dict = {"PACKS_ACCESS_LOG": dict(self.ctid_access_data_dict)}
            self.payment_data_dict_list.append(self.packs_access_log_dict)
            logging.info('packs access logs: %s', self.packs_access_log_dict)
            
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
            