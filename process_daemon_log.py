from datetime import datetime, timedelta
import logging
import os
import shutil
import signal
import socket
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
        self.csv_files = []
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
        self.error_code = ""
        self.is_error_in_csv = False
        
        self.hostname = socket.gethostname()
        self.onmopay_out_folder = False
        
    def process_daemon_log(self, pname, tlog_thread, ctid, task_type, sub_type, input_tag):
        #creating out file writter object for writting log to out file
        fileWriter_object = FileWriter(self.outputDirectory_object, self.oarm_uid)
        RequestOrigin = task_type
        
        if pname == "GRIFF" or pname == "PACKS" or pname == "ONMOPAY":
            if pname == "ONMOPAY":
                self.error_code = tlog_thread
            #msisdn processing main file
            try:
                self.reinitialize_constructor_parameter()
                if pname == "ONMOPAY":
                    try:
                        if self.error_code:
                            self.is_log_file = True
                            self.dated_log_files(pname)
                        else:
                            self.check_error_in_csv(pname, ctid)
                        # logging.info('paycore log file: %s', self.log_files)
                    except KeyError as error:
                        logging.info(error)
                if pname == "GRIFF":
                    self.log_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"])
                if pname == "PACKS":
                    self.log_files.append(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"])
                
                if pname == "ONMOPAY":
                    if self.error_code or self.is_error_in_csv:
                        self.fetch_daemon_log(ctid, self.log_files)
                else:
                    self.fetch_daemon_log(tlog_thread, self.log_files)
                    
                if self.issue_record:
                    if pname == "ONMOPAY":
                        fileWriter_object.write_complete_thread_log(pname, self.error_code, self.issue_record, ctid, RequestOrigin, None, None)
                    else:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, ctid, None, None, None)
                else:
                    if pname == "ONMOPAY":
                        logging.info('%s not found in debug log', ctid)
                    else:
                        logging.info('%s not found in debug log', tlog_thread)
                              
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
                    self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_TEST_{}_log".format(self.validation_object.fmsisdn)])
                elif pname == "PRISM_DEAMON":
                    self.log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_TEST_{}_log".format(self.validation_object.fmsisdn)])
                
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
                
        # elif pname == "PRISM_TOMCAT_ACCESS":
        #     #prism/tomcat log processing
        #     try:
        #         if not self.issue_record:
        #             self.reinitialize_constructor_parameter()
                
        #             self.log_files.append(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_PRISM_log"])
                    
        #             self.fetch_daemon_log(tlog_thread, self.log_files) 
                    
        #             if self.issue_record:
        #                 fileWriter_object.write_complete_thread_log(pname, tlog_thread, self.issue_record, None, task_type, sub_type, input_tag)
        #     except KeyError as error:
        #         logging.info(error)
    
    def dated_log_files(self, pname):
        try:            
            #method call to date range list
            self.input_date = self.date_range_list(self.s_date, self.e_date)
            
            for date in self.input_date:
                input_date_formatted = datetime.strftime(date, "%Y-%m-%d")

                if self.is_msisdn_file:
                    if pname == "GRIFF":
                        self.log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    if pname == "PACKS":
                        self.log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    
                elif self.is_msisdn_backup_file:
                    if pname == "GRIFF":
                        self.backup_log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
            
                    elif pname == "PACKS":
                        self.backup_log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                
                elif self.is_log_file:
                    if pname == "ONMOPAY":
                        self.log_files.append(str(self.initializedPath_object.onmopay_paycore_log_path_dict["onmopay_paycore_allfile_log"]).replace("${shortdate}", "{}".format(input_date_formatted)))
                        self.log_files.append(str(self.initializedPath_object.onmopay_paycore_log_path_dict["onmopay_paycore_serviceSpecificFile_log"]).replace("${shortdate}", "{}".format(input_date_formatted)).replace("${aspnet-item:variable=ServiceId}", "*"))
                                
                    elif pname == "GRIFF":
                        self.log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"]).replace(".log", "-{}*.log".format(input_date_formatted)))
                    elif pname == "PACKS":
                        self.log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_log"]).replace(".log", "-{}*.log".format(input_date_formatted)))
                
                elif self.is_backup_file:
                    if pname == "GRIFF":
                        self.backup_log_files.append(str(self.initializedPath_object.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    
                    elif pname == "PACKS":
                        self.backup_log_files.append(str(self.initializedPath_object.packs_tomcat_log_path_dict["packs_APPENDER_PACKS.FILE_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    
                    elif pname == "PRISM_TOMCAT":
                        self.backup_log_files.append(str(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_PRISM_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))

                    elif pname == "PRISM_DEAMON":
                        self.backup_log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_PRISM_backup_log"].replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    
                    elif pname == "PRISM_SMSD":
                        self.backup_log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_PRISM_backup_log"].replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                
                elif self.is_backup_root_file:
                    if pname == "PRISM_TOMCAT":
                        self.backup_log_files.append(str(self.initializedPath_object.prism_tomcat_log_path_dict["prism_tomcat_ROOT_backup_log"]).replace("yyyy-MM-dd", "{}".format(input_date_formatted)))

                    elif pname == "PRISM_DEAMON":
                        self.backup_log_files.append(self.initializedPath_object.prism_daemon_log_path_dict["prism_daemon_ROOT_backup_log"].replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                    
                    elif pname == "PRISM_SMSD":
                        self.backup_log_files.append(self.initializedPath_object.prism_smsd_log_path_dict["prism_smsd_ROOT_backup_log"].replace("yyyy-MM-dd", "{}".format(input_date_formatted)))
                
        except KeyError as error:
            logging.info(error)
    
    def check_error_in_csv(self, pname, ctid):
        #check if sessionId present in error csv file
        try:            
            #method call to date range list
            self.input_date = self.date_range_list(self.s_date, self.e_date)
            
            for date in self.input_date:
                input_date_formatted = datetime.strftime(date, "%Y%m%d")
                self.csv_files.append(str(self.initializedPath_object.onmopay_paycore_log_path_dict["onmopay_paycore_errorCSV-file_log"]).replace("${date:format=yyyyMMdd}", "{}".format(input_date_formatted)))
            
            if self.csv_files:
                for file in self.csv_files:
                    try:
                        # logging.info('tlog thread is: %s and log_file is: %s', ctid, file)
                        ctid_log = subprocess.check_output("grep -a {} {}".format(ctid, file), shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                        
                        if ctid_log:
                            folder = os.path.join(self.outputDirectory_object, "{}_issue_onmopay".format(self.hostname))
                            if not self.onmopay_out_folder:
                                self.create_process_folder(pname, folder)
                            splitted_record = str(ctid_log).split(",")
                            logging.info('splitted record=%s', splitted_record[11])
                            self.error_code = splitted_record[11]
                            self.is_error_in_csv = True
                            logging.info('error code=%s', self.error_code)
                            break
                    except subprocess.CalledProcessError as error:
                        logging.info('eigther %s does not exists or %s could not be found', file, ctid)
                        logging.info(error)
            
            for date in self.input_date:
                input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                self.log_files.append(str(self.initializedPath_object.onmopay_paycore_log_path_dict["onmopay_paycore_allfile_log"]).replace("${shortdate}", "{}".format(input_date_formatted)))
                self.log_files.append(str(self.initializedPath_object.onmopay_paycore_log_path_dict["onmopay_paycore_serviceSpecificFile_log"]).replace("${shortdate}", "{}".format(input_date_formatted)).replace("${aspnet-item:variable=ServiceId}", "*"))
        except KeyError as error:
            logging.info(error)
        
    def fetch_daemon_log(self, tlog_thread, log_files):
        #check file for the recod for the given thread
        for file in log_files:
            try:
                # logging.info('tlog thread is: %s and log_file is: %s', tlog_thread, file)
                
                if self.is_msisdn_backup_file or self.is_backup_file or self.is_backup_root_file:
                    thread_log = subprocess.check_output("zcat {0} | grep -a {1}".format(file, tlog_thread), shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                else:
                    thread_log = subprocess.check_output("grep -a {0} {1}".format(tlog_thread, file), shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                
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
    
    def create_process_folder(self, pname, folder):
        """
            creating process folder
        """
        if os.path.exists(folder):
            # delete the existing folder
            shutil.rmtree(folder)

        # create a new folder
        os.makedirs(folder)
            
    def set_process_out_folder(self, is_true):
        self.onmopay_out_folder = is_true
            
    def reinitialize_constructor_parameter(self):
        self.input_date = []
        self.log_files = []
        self.backup_log_files = []
        self.csv_files = []
        self.issue_record = ""
        self.error_code = ""
        self.is_msisdn_file = False
        self.is_msisdn_backup_file = False
        self.is_backup_file = False
        self.is_log_file = False
        self.is_backup_root_file = False
        self.is_error_in_csv = False
        
        