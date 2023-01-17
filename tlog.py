import csv
import logging
from queue import Empty
import signal
import subprocess
from log_files import LogFileFinder
import re

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
        self.griff_tlog_record = []
        self.is_backup_file = False
        self.griff_tlog_dict = {}
    
    def get_griff_tomcat_tlog(self):
        """
        calling path finder method
        """
        logfile_object = LogFileFinder(self.initializedPath_object, self.validation_object)
        self.tlog_files = logfile_object.tomcat_griff_tlog_files()
        self.backup_tlog_files = logfile_object.tomcat_griff_tlog_backup_files()
        
        logging.info('tlog files: %s', self.tlog_files)
        logging.info('backup tlog files: %s', self.backup_tlog_files)
        
        if self.tlog_files:
            for file in self.tlog_files:
                #function call
                self.msisdn_ctid_map(file, self.is_backup_file)
        
        if self.backup_tlog_files:
            self.is_backup_file = True
            
            for file in self.backup_tlog_files:
                #function call
                self.msisdn_ctid_map(file, self.is_backup_file)
        
        if self.ctid_msisdn_map_dict:
            logging.info('msisdn-ctid map: %s', self.ctid_msisdn_map_dict)
            self.ctid_based_tlog_fetch()
        
        if self.griff_tlog_record:
            logging.info('griff tlog record: %s', self.griff_tlog_record)
                
                
        # if tlog_files != None:
        #     for file in tlog_files:
        #         with open(file, "r") as file_in:
        #             data = [line for line in csv.reader(file_in, lineterminator = '\n')]
        #             logging.info('data: %s', data)
    
    def msisdn_ctid_map(self, file, is_backup_file):
        
        if is_backup_file:
            ctid_mdn_map_list = subprocess.check_output(f"zcat {file} | grep -a {self.validation_object.fmsisdn} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
        else:
            ctid_mdn_map_list = subprocess.check_output(f"grep -a {self.validation_object.fmsisdn} {file} | cut -d ',' -f 2,12 | sort -u", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                
        ctid_msisdn_map_list = ctid_mdn_map_list.split('\n')
        for record in ctid_msisdn_map_list:
            if record != "":
                ctid, msisdn = tuple(record.replace('"', '').split(","))
                try:
                    if msisdn in self.ctid_msisdn_map_dict[msisdn]:
                    # append the new ctid to the existing array of msisdn
                        self.ctid_msisdn_map_dict[msisdn].append(ctid)
                except KeyError as ex:
                    # create a new array of msisdn
                    self.ctid_msisdn_map_dict[msisdn] = [ctid]
    
    def ctid_based_tlog_fetch(self):
        try:   
            for ctid in self.ctid_msisdn_map_dict[self.validation_object.fmsisdn]:
                logging.info('ctid is: %s', ctid)
                for file in self.tlog_files:
                    with open(file, "r") as tlog_file:
                        logging.info('tlog file: %s', file)
                        reader = csv.reader(tlog_file)
                        for row in reader:
                            try:
                                if row[1] == ctid:
                                    logging.info('row data in reader: %s', row)
                                    self.griff_tlog_record.append(row)
                            except Exception as ex:
                                logging.info("Ignoring header data")
        except Exception as ex:
            logging.info(ex)
            
    def tlog_record_header_mapping(self):
        for ntlog, data in enumerate(self.griff_tlog_record):
                    tlog_data = data.split("|")
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
                            
                    ntlog_dict = f'dict_{ntlog}'
                    self.dictionary_of_tlogs[f'{ntlog_dict}'] = {}
                    for counter, tlog_header in enumerate(header):
                        try:
                            self.dictionary_of_tlogs[ntlog_dict][tlog_header] = self.data_in_tlog(tlog_data, counter)
                        except IndexError as ex:
                            logging.info('Header data did not match')
                            
    def data_in_tlog(self, data, index):
        """
        Returns data in tlog.
        """
        try:
            return data[index]
        except IndexError as ex:
            raise
        