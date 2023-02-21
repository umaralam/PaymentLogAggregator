from datetime import datetime, timedelta
import logging
import signal
import subprocess
from outfile_writer import FileWriter

class DaemonLogProcessor:
    """
        Daemon log processor class
        fetching daemon log for the issue threads in the tlogs
    """
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, oarm_uid):
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.oarm_uid = oarm_uid
        
        self.log_files = []
        self.backup_log_files = []
        
        self.start_date = validation_object.start_date
        self.end_date = validation_object.end_date
        
        self.input_date = []
        self.is_msisdn_backup_file = False
        self.is_msisdn_file = False
        self.is_backup_file = False
        self.is_log_file = False
        self.is_backup_root_file = False
        
        self.s_date = datetime.strptime(datetime.strftime(self.start_date, "%Y%m%d"), "%Y%m%d")
        self.e_date = datetime.strptime(datetime.strftime(self.end_date, "%Y%m%d"), "%Y%m%d")
        self.issue_record = ""
        
    def process_daemon_log(self, pname, tlog_thread, ctid, task_type, sub_type, input_tag):
        #creating out file writter object for writting log to out file
        fileWriter_object = FileWriter(self.outputDirectory_object, self.oarm_uid)
        
        if pname == "GRIFF" or pname == "PACKS":
            #msisdn processing main file
            try:
                self.reinitialize_constructor_parameter()
                
                if pname == "GRIFF":
                    self.log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"])
                if pname == "PACKS":
                    self.log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"])
                
                self.fetch_daemon_log(tlog_thread, self.log_files) 
                
                if self.issue_record:
                    fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
            except KeyError as error:
                logging.info(error)
            
            #msisdn dated file processing
            try:
                if not self.issue_record:                    
                    self.reinitialize_constructor_parameter()
                    self.is_msisdn_file = True
                    
                    self.dated_log_files(pname)
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
            except KeyError as error:
                logging.info(error)
            
            #msisdn dated backup files processing
            try:
                if not self.issue_record:
                    self.reinitialize_constructor_parameter()
                    self.is_msisdn_backup_file = True
                    self.dated_log_files(pname)
                    
                    if self.backup_log_files:
                        self.fetch_daemon_log(tlog_thread, self.backup_log_files)
                    
                        if self.issue_record:
                            fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
            except KeyError as error:
                logging.info(error)
            
            #main log file processing
            try:
                if not self.issue_record:
                    
                    self.reinitialize_constructor_parameter()
                                      
                    if pname == "GRIFF":
                        self.log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"])
                    elif pname == "PACKS":
                        self.log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_log"])

                    self.fetch_daemon_log(tlog_thread, self.log_files)
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
            except KeyError as error:
                logging.info(error)
            
            #main log dated file processing
            try:
                if not self.issue_record:
                    
                    self.reinitialize_constructor_parameter()
                    self.is_log_file = True
                    self.dated_log_files(pname)
                    
                    self.fetch_daemon_log(tlog_thread, self.log_files)
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)        
            except KeyError as error:
                logging.info(error)
            
            #main log dated file processing
            try:
                if not self.issue_record:                    
                    
                    self.reinitialize_constructor_parameter()
                    self.is_backup_file = True
                    self.dated_log_files(pname)
                    
                    if self.backup_log_files:
                        self.fetch_daemon_log(tlog_thread, self.backup_log_files)
                    
                        if self.issue_record:
                            fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
            except KeyError as error:
                logging.info(error)
                
        elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON" or pname == "PRISM_SMSD":
            #msisdn log processing
            try:
                self.reinitialize_constructor_parameter()
                
                if pname == "PRISM_TOMCAT":
                    self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict[f"prism_tomcat_TEST_{self.validation_object.fmsisdn}_log"])
                elif pname == "PRISM_DEAMON":
                    self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict[f"prism_daemon_TEST_{self.validation_object.fmsisdn}_log"])
                
                self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                if self.issue_record:
                    fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
            
            #queue id 99 processing
            try:
                if not self.issue_record:
                    self.reinitialize_constructor_parameter()
                        
                    if pname == "PRISM_TOMCAT":
                        self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_PROCESSOR_99_log"])
                    elif pname == "PRISM_DEAMON":
                        self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_PROCESSOR_99_log"])
                    elif pname == "PRISM_SMSD":
                        self.log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_PROCESSOR_99_log"])
                        
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
            
            #prism/tomcat log processing
            try:
                if not self.issue_record:
                    self.reinitialize_constructor_parameter()
                    
                    if pname == "PRISM_TOMCAT":
                        self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_PRISM_log"])
                    elif pname == "PRISM_DEAMON":
                        self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_PRISM_log"])
                    elif pname == "PRISM_SMSD":
                        self.log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_PRISM_log"])
                    
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
            
            #prism/tomcat root log processing
            try:
                if not self.issue_record:
                    self.reinitialize_constructor_parameter()
                    
                    if pname == "PRISM_TOMCAT":
                        self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_ROOT_log"])
                    elif pname == "PRISM_DEAMON":
                        self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_ROOT_log"])
                    elif pname == "PRISM_SMSD":
                        self.log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_ROOT_log"])
                    
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
            
            #prism/tomcat log backup dated file processing
            try:
                if not self.issue_record:
                    
                    self.reinitialize_constructor_parameter()
                    self.is_backup_file = True
                    self.dated_log_files(pname)
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
            
            #prism/tomcat root log backup dated file processing
            try:
                if not self.issue_record:
                    
                    self.reinitialize_constructor_parameter()
                    self.is_backup_root_file = True
                    self.dated_log_files(pname)
                    self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
                    if self.issue_record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
            except KeyError as error:
                logging.info(error)
    
    def dated_log_files(self, pname):
        try:            
            #method call to date range list
            self.input_date = self.date_range_list(self.s_date, self.e_date)
            
            for date in self.input_date:
                input_date_formatted = datetime.strftime(date, "%Y-%m-%d")

                if self.is_msisdn_file:
                    if pname == "GRIFF":
                        self.log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    if pname == "PACKS":
                        self.log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                elif self.is_msisdn_backup_file:
                    if pname == "GRIFF":
                        self.backup_log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
            
                    elif pname == "PACKS":
                        self.backup_log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                
                elif self.is_log_file:
                    if pname == "GRIFF":
                        self.log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"]).replace(".log", f"-{input_date_formatted}*.log"))
                    elif pname == "PACKS":
                        self.log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_log"]).replace(".log", f"-{input_date_formatted}*.log"))
                
                elif self.is_backup_file:
                    if pname == "GRIFF":
                        self.backup_log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                    elif pname == "PACKS":
                        self.backup_log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                    elif pname == "PRISM_TOMCAT":
                        self.backup_log_files.append(str(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_PRISM_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))

                    elif pname == "PRISM_DEAMON":
                        self.backup_log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_PRISM_backup_log"].replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                    elif pname == "PRISM_SMSD":
                        self.backup_log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_PRISM_backup_log"].replace("yyyy-MM-dd", f"{input_date_formatted}"))
                
                elif self.is_backup_root_file:
                    if pname == "PRISM_TOMCAT":
                        self.backup_log_files.append(str(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_ROOT_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))

                    elif pname == "PRISM_DEAMON":
                        self.backup_log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_ROOT_backup_log"].replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                    elif pname == "PRISM_SMSD":
                        self.backup_log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_ROOT_backup_log"].replace("yyyy-MM-dd", f"{input_date_formatted}"))
                
        except KeyError as error:
            logging.info(error)
        
    def fetch_daemon_log(self, tlog_thread, log_files):
        #check file for the recod for the given thread
        for file in log_files:
            try:
                logging.info('tlog thread is: %s and log_file is: %s', tlog_thread, file)
                
                if self.is_msisdn_backup_file or self.is_backup_file or self.is_backup_root_file:
                    thread_log = subprocess.check_output(f"zcat {file} | grep -a {tlog_thread}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                else:
                    thread_log = subprocess.check_output(f"grep -a {tlog_thread} {file}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                
                record = [data for data in thread_log]
                if record:
                    self.issue_record = record
        
            except subprocess.CalledProcessError as error:
                logging.info('eigther %s does not exists or %s could not be found', file, tlog_thread)
                logging.info(error)
    
    def date_range_list(self, start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += timedelta(days=1)
        return date_list
    
    def reinitialize_constructor_parameter(self):
        self.input_date = []
        self.log_files = []
        self.backup_log_files = []
        self.issue_record = ""
        self.is_msisdn_file = False
        self.is_msisdn_backup_file = False
        self.is_backup_file = False
        self.is_log_file = False
        self.is_backup_root_file = False
        
        