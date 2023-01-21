import csv
import logging
import re
import signal
import subprocess
from log_files import LogFileFinder
from collections import defaultdict
import json

class Tlog:
    """
    tlog mapping class
    """
    def __init__(self, initializedPath_object, validation_object):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.tlog_files = []
        self.backup_tlog_files = []
        self.ctid_msisdn_map_dict = {}
        self.tlog_record = []
        self.is_backup_file = False
        self.tlog_files_with_ctid_msisdn = []
        self.tlog_backup_files_with_ctid_msisdn = []
        self.tlog_dict = defaultdict(list)
        self.ctid_data_dict = defaultdict(list)
        self.griff_tlog_dict = {}
        self.packs_tlog_dict = {}
    
    def get_tomcat_tlog(self, pname):
        """
        calling path finder method
        """
        logfile_object = LogFileFinder(self.initializedPath_object, self.validation_object)
        # if pname == "GRIFF":
        #     #Re-initializing constructor paramters
        self.constructor_parameter_reinitialize()
        
        self.tlog_files = logfile_object.get_tomcat_tlog_files(pname)
        self.backup_tlog_files = logfile_object.get_tomcat_tlog_backup_files(pname)
            
        logging.info('tlog files: %s', self.tlog_files)
        logging.info('backup tlog files: %s', self.backup_tlog_files)
        
        if self.tlog_files:
            for file in self.tlog_files:
                #function call
                self.msisdn_ctid_map(pname, file, self.is_backup_file)
        
        if self.backup_tlog_files:
            self.is_backup_file = True
            
            for file in self.backup_tlog_files:
                #function call
                self.msisdn_ctid_map(pname, file, self.is_backup_file)
        
        if self.ctid_msisdn_map_dict and (self.tlog_files_with_ctid_msisdn or self.tlog_backup_files_with_ctid_msisdn):
            logging.info('msisdn-ctid map: %s', self.ctid_msisdn_map_dict)
            logging.info('tlog files with ctid-msisdn: %s',self.tlog_files_with_ctid_msisdn)
            logging.info('backup tlog files with ctid-msisdn: %s',self.tlog_backup_files_with_ctid_msisdn)
            
            if self.tlog_files_with_ctid_msisdn:
                self.ctid_based_tlog_fetch(pname, self.tlog_files_with_ctid_msisdn, False)
            if self.tlog_backup_files_with_ctid_msisdn:
                self.ctid_based_tlog_fetch(pname, self.tlog_backup_files_with_ctid_msisdn, True)
        
        if self.tlog_record:
            # splited_tlog_record = str(self.griff_tlog_record).split("\n")
            data_list = []
            for data in self.tlog_record:
                for record in str(data).splitlines():
                    data_list.append(record)
            # logging.info('data list: %s', data_list)
                
            self.tlog_record_header_mapping(pname, data_list)
            self.counter = 0
                
        # if self.griff_tlog_dict:
        #     logging.info('tlog header data: %s', self.griff_tlog_dict)
    
    def msisdn_ctid_map(self, pname, file, is_backup_file):
        
        if is_backup_file:
            if pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    logging.info('dated file: %s', file)
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 51,4 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    logging.info('dated file: %s', file)
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                
        else:
            if pname == "GRIFF":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    logging.info('dated backup file: %s', file)
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                    
            elif pname == "PACKS":
                ctid_mdn_data = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 51,4 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                if ctid_mdn_data:
                    logging.info('dated backup file: %s', file)
                    self.tlog_backup_files_with_ctid_msisdn.append(file)
                
        
        ctid_msisdn_data = ctid_mdn_data.split('\n')
        # logging.info('ctid-msisdn string data: %s', ctid_msisdn_data)
        for row in ctid_msisdn_data:
            if row != "":
                if pname == "GRIFF":
                    ctid, msisdn = tuple(row.replace('"', '').split(","))
                elif pname == "PACKS":
                    msisdn, ctid = tuple(row.replace('"', '').split(","))
                try:
                    if ctid not in self.ctid_msisdn_map_dict[msisdn]:
                        logging.info('ctid in ctid-msisdn map dict: %s', ctid)
                    # append the new ctid to the existing array of msisdn
                        self.ctid_msisdn_map_dict[msisdn].append(ctid)
                        logging.info('map: %s', self.ctid_msisdn_map_dict)
                except KeyError as ex:
                    logging.info('ctid in ctid-msisdn map dict: %s', ctid)
                    # create a new array of msisdn
                    self.ctid_msisdn_map_dict[msisdn] = [ctid]
                    
        logging.info('map: %s', self.ctid_msisdn_map_dict)
    
    def ctid_based_tlog_fetch(self, pname, files, is_backup_files):
        try:   
            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                # logging.info('ctid is: %s', ctid)
                if is_backup_files:
                    for file in files:
                        # logging.info('ctid: %s and tlog file fetch: %s', ctid, file)
                        try:
                            data = subprocess.check_output(f"zcat {file} | grep -a {ctid}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                            self.tlog_record.append(data)
                        except Exception as ex:
                            logging.info(ex)
                else:
                    for file in files:
                        with open(file, "r") as tlog_file:
                            reader = csv.reader(tlog_file)

                            for row in reader:
                                try:
                                    if pname == "GRIFF":
                                        if row[1] == ctid:       
                                            logging.info('row data in reader: %s', row)
                                            self.tlog_record.append(row)
                                            
                                    elif pname == "PACKS":
                                        if row[51] == ctid:
                                            logging.info('row data in reader: %s', row)
                                            self.tlog_record.append(row)
                                except Exception as ex:
                                    logging.info("Ignoring header data")
        except Exception as ex:
            logging.info(ex)
            
    def tlog_record_header_mapping(self, pname, data_list):
        
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
                        "PackTLogCreatedTimeStamp","THREAD_NAME","API_NAME","REQ_MSISDN","REQ_APPID","REQ_PACKID",\
                        "REQ_OPERATOR","REQ_CIRCLE","SEL_OPERATOR","SEL_CIRCLE","REQ_ACTION","REQ_USERINFO","RES_USERINFO",\
                        "REQ_AMOUNT","REQ_SERVICEKEY","REQ_EVENTKEY","REQ_ALL_PARAMS","BILLING_SERVICE_KEY","BILLING_URL_TEMPLATE",\
                        "BILLING_URL_CALLED","BILLING_REQ_TIME_START","BILLING_REQ_TIME_END","BILLING_AMOUNT","BILLING_RES_STATUS",\
                        "BILLING_RES_MESSAGE","CREDITS_BEFORE","CREDITS_AFTER","APP_NAME","PACK_NAME","SUB_TYPE","BILLING_MODE",\
                        "BILLING_TYPE","CALLBACK_REGISTERED","RET_APPS","RET_PACKS","RET_STATUS","RET_ERROR_REASON","SEL_APPIDs",\
                        "SEL_PACKIDs","SUBSCRIBER_ID","SUBS_STATUS_BEFORE","SUBS_STATUS_AFTER","REQ_ACTION_MODE","REQ_NEW_MSISDN",\
                        "PACK_LEVEL_FILTER","APP_LEVEL_FILTER","COMMON_PARAM_FILTER","CHARGE_KEY","SOURCE_IP","GRIFF_RESPONSE",\
                        "CTID","THIRD_PARTIES","TOTAL_TIMETAKEN","PACKS_TIMETAKEN","EXT_TIMETAKEN","TRAP_STATUS"
                    ]
            
        for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
            for data in data_list:
                splited_data = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', data)
                # logging.info('splitted data: %s', splited_data[50])
                if pname == "GRIFF":
                    if ctid == splited_data[1].replace('"', ''):
                        data_dict = {}
                        for index, element in enumerate(splited_data):
                            data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                        self.ctid_data_dict[ctid].append(data_dict)
                elif pname == "PACKS":
                    if ctid == splited_data[50].replace('"', ''):
                        data_dict = {}
                        for index, element in enumerate(splited_data):
                            data_dict[header[index]] = element.replace('"', '').replace("'", '"')
                        self.ctid_data_dict[ctid].append(data_dict)
                        
        if pname == "GRIFF":
            self.griff_tlog_dict = {"GRIFF": {"GRIFF_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}}
            logging.info('griff tlogs: %s', str(self.griff_tlog_dict).replace("'", '"'))
            
        elif pname == "PACKS":
            self.packs_tlog_dict = {"PACKS": {"PACKS_TLOG": {f"{self.validation_object.fmsisdn}": dict(self.ctid_data_dict)}}}
        
        logging.info('packs tlogs: %s', str(self.packs_tlog_dict).replace("'", '"'))
        # logging.info('json tlog data: %s',json.dumps(self.payment_tlog_dict))
            
        
    def constructor_parameter_reinitialize(self):
        self.tlog_files = []
        self.backup_tlog_files = []
        self.ctid_msisdn_map_dict = {}
        self.tlog_record = []
        self.is_backup_file = False
        self.tlog_files_with_ctid_msisdn = []
        self.tlog_backup_files_with_ctid_msisdn = []
        # self.tlog_dict = defaultdict()
        self.ctid_data_dict = defaultdict(list)
        

        
        