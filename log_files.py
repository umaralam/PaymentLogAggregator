from datetime import datetime, timedelta
import logging
from pathlib import Path

class LogFileFinder:
    """
    log file finder class
    """
    def __init__(self, initializedPath_object, validation_object):
    
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        self.start_date = validation_object.start_date
        self.end_date = validation_object.end_date
        
        self.tlog_files = []
        self.input_date = []
        self.tlog_dir = ""
        
        self.tlog_backup_files = []
        self.tlog_backup_dir = ""
      
        self.s_date = datetime.strptime(datetime.strftime(self.start_date, "%Y%m%d"), "%Y%m%d")
        self.e_date = datetime.strptime(datetime.strftime(self.end_date, "%Y%m%d"), "%Y%m%d")
    
    def get_tomcat_tlog_files(self, pname):
        if pname == "GRIFF":
            #re-initializing constructor parameters
            self.constructor_paramter_reinitialize()
            #current tlog file
            self.tlog_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"])
            
            splitted_tlog_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_log'])\
                                    .split("/")[0:-1]
            for i in range(1, len(splitted_tlog_path)):
                self.tlog_dir += f"/{splitted_tlog_path[i]}"
        
        elif pname == "PACKS":
            self.constructor_paramter_reinitialize()
            #current tlog file
            self.tlog_files.append(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_log'])
            
            splitted_tlog_path = str(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_log'])\
                                    .split("/")[0:-1]
            for i in range(1, len(splitted_tlog_path)):
                self.tlog_dir += f"/{splitted_tlog_path[i]}"
                
        path = Path(rf"{self.tlog_dir}")
        
        #method call to date range list
        self.input_date = self.date_range_list(self.s_date, self.e_date)
        
        for date in self.input_date:
            # logging.info('search date is: %s', datetime.strftime(date, "%Y-%m-%d"))
            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")            
            
            #input dated file in the tlog directory
            if pname == "GRIFF":
                dated_tlog_files = [p for p in path.glob(f"griffTLog-{input_date_formatted}-*.csv")]
            elif pname == "PACKS":
                dated_tlog_files = [p for p in path.glob(f"packTlog-{input_date_formatted}-*.csv")]
                
            if bool(dated_tlog_files):
                if pname == "GRIFF":
                    logging.info(f"griffTLog-{input_date_formatted}-*.csv file present" )
                elif pname == "PACKS":
                    logging.info(f"packTlog-{input_date_formatted}-*.csv file present" )
                    
                for files in dated_tlog_files:
                    self.tlog_files.append(str(files))
            else:
                if pname == "GRIFF":
                    logging.info(f"griffTLog-{input_date_formatted}-*.csv file not present" )
                elif pname == "PACKS":
                    logging.info(f"packTlog-{input_date_formatted}-*.csv file not present" )
            
        return self.tlog_files
    
    def get_tomcat_tlog_backup_files(self, pname):
        if pname == "GRIFF":
            #re-initializing constructor parameters
            self.constructor_paramter_reinitialize()
            
            #getting backup tlog files
            splitted_tlog_backup_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_backup_log'])\
                                    .split("/")[0:-1]
            for i in range(1, len(splitted_tlog_backup_path)):
                self.tlog_backup_dir += f"/{splitted_tlog_backup_path[i]}"
                
        elif pname == "PACKS":
            #re-initializing constructor parameters
            self.constructor_paramter_reinitialize()
            
            splitted_tlog_backup_path = str(self.initializedPath_object.packs_tomcat_log_path_dict['packs_PACKS_T_LOG_APPENDER.FILE_backup_log'])\
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
            
            if bool(dated_tlog_backup_files):
                if pname == "GRIFF":
                    logging.info(f"griffTLog-{input_date_formatted}-*.zip file present")
                elif pname == "PACKS":
                    logging.info(f"packTlog-{input_date_formatted}-*.zip file present")
                    
                for files in dated_tlog_backup_files:
                    self.tlog_backup_files.append(str(files))
                    
        return self.tlog_backup_files
    
    def date_range_list(self, start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += timedelta(days=1)
        return date_list
    
    def constructor_paramter_reinitialize(self):
        self.tlog_files = []
        self.input_date = []
        self.tlog_dir = ""
        self.tlog_backup_files = []
        self.tlog_backup_dir = ""