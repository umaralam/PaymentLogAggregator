from datetime import datetime, timedelta
import logging
from pathlib import Path
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
        self.log_dir = ""
        self.backup_log_dir = ""
        self.log_files = []
        self.backup_log_files = []
        
        self.start_date = validation_object.start_date
        self.end_date = validation_object.end_date
        
        self.input_date = []
        self.is_backup_file = False
        
        self.s_date = datetime.strptime(datetime.strftime(self.start_date, "%Y%m%d"), "%Y%m%d")
        self.e_date = datetime.strptime(datetime.strftime(self.end_date, "%Y%m%d"), "%Y%m%d")
        
    def process_daemon_log(self, pname, tlog_thread, ctid, task_type, sub_type, input_tag):
        #creating out file writter object for writting log to out file
        fileWriter_object = FileWriter(self.outputDirectory_object, self.oarm_uid)
    
        self.reinitialize_constructor_parameter()
        try:
            if pname == "GRIFF":
                self.log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"])
            elif pname == "PACKS":
                self.log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"])
            elif pname == "PRISM_TOMCAT":
                self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict[f"prism_tomcat_TEST_{self.validation_object.fmsisdn}_log"])
            elif pname == "PRISM_DEAMON":
                self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict[f"prism_daemon_TEST_{self.validation_object.fmsisdn}_log"])
            
            record = self.fetch_daemon_log(tlog_thread, self.log_files)
                
            if record:
                if pname == "GRIFF" or pname == "PACKS":
                    fileWriter_object.write_complete_thread_log(pname, tlog_thread, record, ctid, None, None, None)
                elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                    fileWriter_object.write_complete_thread_log(pname, tlog_thread, record, None, task_type, sub_type, input_tag)
            else:
                if pname == "GRIFF" or pname == "PACKS":
                    logging.info('%s msisdn debug log does not exists, hence checking msisdn backup debug log', pname)
                    self.set_is_backup_file(True)
                    
                    #method call to date range list
                    self.input_date = self.date_range_list(self.s_date, self.e_date)
                    
                    for date in self.input_date:
                        if pname == "GRIFF" or pname == "PACKS":
                            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                    
                            if pname == "GRIFF":
                                self.backup_log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                            elif pname == "PACKS":
                                self.backup_log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", f"{input_date_formatted}"))
                    
                    record = self.fetch_daemon_log(tlog_thread, self.backup_log_files)
                    
                    if record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, record, ctid, None, None, None)
                    else:
                        logging.info('%s msisdn debug log could not be found for the %s', pname, tlog_thread)
        
        except KeyError as error:
            logging.info(error)
            logging.info('%s msisdn debug log does not exists, hence checking the %s main and backup logs', pname, pname)
            self.reinitialize_constructor_parameter()
            
            if pname == "GRIFF":
                #main log file
                self.log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"])
                splitted_log_path = str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"])\
                                    .split("/")[0:-1]
            elif pname == "PACKS":
                #main log file
                self.log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_log"])
            
                splitted_log_path = str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_log"])\
                                    .split("/")[0:-1]
            
            for i in range(1, len(splitted_log_path)):
                self.log_dir += f"/{splitted_log_path[i]}"
                
            path = Path(rf"{self.log_dir}")
            
            #method call to date range list
            self.input_date = self.date_range_list(self.s_date, self.e_date)
            
            for date in self.input_date:
                if pname == "GRIFF" or pname == "PACKS":
                    input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                
                #dated log files
                if pname == "GRIFF":
                    dated_log_files = [p for p in path.glob(f"griff-{input_date_formatted}.log")]
                elif pname == "PACKS":
                    dated_log_files = [p for p in path.glob(f"packs-{input_date_formatted}.log")]
            
                if bool(dated_log_files):
                    for files in dated_log_files:
                        self.log_files.append(str(files))
                    
            logging.info('log files: %s', self.log_files)
            record = self.fetch_daemon_log(tlog_thread, self.log_files)
            
            if record:
                fileWriter_object.write_complete_thread_log(pname, tlog_thread, record, ctid, None, None, None)
            else:
                logging.info('Eigther debug log files does not exists in the current log path\
                             or thread could not be found. Going to check backup path.')
                self.set_is_backup_file(True)
                
                if pname == "GRIFF":
                    #main backup log file
                    self.backup_log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_backup_log"])
                    splitted_backup_log_path = str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_backup_log"])\
                                        .split("/")[0:-1]
                    
                elif pname == "PACKS":
                    #main backup log file
                    self.backup_log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_backup_log"])
                
                    splitted_backup_log_path = str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_backup_log"])\
                                        .split("/")[0:-1]
                    
                for i in range(1, len(splitted_backup_log_path)):
                    self.backup_log_dir += f"/{splitted_backup_log_path[i]}"
                    
                path = Path(rf"{self.backup_log_dir}")
                
                #method call to date range list
                # self.input_date = self.date_range_list(self.s_date, self.e_date)
                
                for date in self.input_date:
                    if pname == "GRIFF" or pname == "PACKS":
                        input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                    
                    #dated log files
                    if pname == "GRIFF":
                        dated_backup_log_files = [p for p in path.glob(f"griff-{input_date_formatted}-*.zip")]
                    elif pname == "PACKS":
                        dated_backup_log_files = [p for p in path.glob(f"packs-{input_date_formatted}-*.zip")]
                
                    if bool(dated_backup_log_files):
                        for files in dated_backup_log_files:
                            self.backup_log_files.append(str(files))
                        
                logging.info('backup log files: %s', self.log_files)
                record = self.fetch_daemon_log(tlog_thread, self.backup_log_files)
                
                if record:
                    fileWriter_object.write_complete_thread_log(pname, tlog_thread, record, ctid, None, None, None)
                else:
                    logging.info('%s debug log could not be found for the %s', pname, tlog_thread)
                
    def fetch_daemon_log(self, tlog_thread, log_files):
        #check file for the recod for the given thread
        for file in log_files:
            try:
                logging.info('tlog thread is: %s and log_file is: %s', tlog_thread, file)
                
                if self.is_backup_file:
                    thread_log = subprocess.check_output(f"zcat {file} | grep -a {tlog_thread}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                else:
                    thread_log = subprocess.check_output(f"grep -a {tlog_thread} {file}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                
                record = [data for data in thread_log]
                if record:
                    return record
        
            except subprocess.CalledProcessError as error:
                logging.info('eigther %s does not exists or %s could not be found', file, tlog_thread)
                logging.info(error)
                logging.info('we are checking other log paths as well')
    
    def date_range_list(self, start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += timedelta(days=1)
        return date_list
    
    def set_is_backup_file(self, is_backup):
        self.is_backup_file = is_backup
    
    def reinitialize_constructor_parameter(self):
        self.is_backup_file = False
        self.input_date = []
        self.log_files = []
        self.backup_log_files = []
        self.log_dir = ""
        self.backup_log_dir = ""
        