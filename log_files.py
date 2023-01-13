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
      
        self.s_date = datetime.strptime(datetime.strftime(self.start_date, "%Y%m%d"), "%Y%m%d")
        self.e_date = datetime.strptime(datetime.strftime(self.end_date, "%Y%m%d"), "%Y%m%d")
    
    def tomcat_griff_tlog_files(self):
        tlog_files = []
        input_date = []
        griff_tlog_dir = ""
        
        
        #current tlog file
        tlog_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"])
        
        splitted_tlog_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_log'])\
                                .split("/")[0:-1]
        for i in range(1, len(splitted_tlog_path)):
            griff_tlog_dir += f"/{splitted_tlog_path[i]}"
                
        path = Path(rf"{griff_tlog_dir}")
        
        #method call to date range list
        input_date = self.date_range_list(self.s_date, self.e_date)
        logging.info('date list: %s', input_date)
        
        for date in input_date:
            logging.info('date: %s', date)
            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
            logging.info('input date formatted: %s', input_date_formatted)
            
            
            #input dated file in the tlog directory
            dated_tlog_files = [p for p in path.glob(f"griffTLog-{input_date_formatted}-*.csv")]
                
            if bool(dated_tlog_files):
                for files in dated_tlog_files:
                    tlog_files.append(str(files))
            
        return tlog_files    
    
    def tomcat_griff_tlog_backup_files(self):
        tlog_backup_files = []
        griff_tlog_backup_dir = ""
        
        
        splitted_tlog_backup_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_backup_log'])\
                                .split("/")[0:-1]
        for i in range(1, len(splitted_tlog_backup_path)):
            griff_tlog_backup_dir += f"/{splitted_tlog_backup_path[i]}"
        
        path = Path(rf"{griff_tlog_backup_dir}")
        
        #method call to date range list
        input_date = self.date_range_list(self.s_date, self.e_date)
        
        for date in input_date:
            input_date_formatted = datetime.strftime(date, "%Y-%m-%d")
                    
            #input dated file in the backup directory
            dated_tlog_backup_files = [p for p in path.glob(f"griffTLog-{input_date_formatted}-*.zip")]
            
            if bool(dated_tlog_backup_files):
                for files in dated_tlog_backup_files:
                    tlog_backup_files.append(str(files))
                    
        return tlog_backup_files
    
    def date_range_list(self, start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += timedelta(days=1)
        return date_list