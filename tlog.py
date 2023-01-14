import csv
import logging
from queue import Empty
import signal
import subprocess
from log_files import LogFileFinder

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
        self.is_backup_file = False
    
    def get_griff_tomcat_tlog(self):
        """
        calling path finder method
        """
        tlog_record = []
        
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
                if msisdn in self.ctid_msisdn_map_dict:
                    # append the new ctid to the existing array of msisdn
                    self.ctid_msisdn_map_dict[msisdn].append(ctid)
                else:
                    # create a new array of msisdn
                    self.ctid_msisdn_map_dict[msisdn] = [ctid]
        