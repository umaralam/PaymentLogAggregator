from datetime import datetime
import logging
from pathlib import Path

class LogFileFinder:
    """
    log file finder class
    """
    def __init__(self, initializedPath_object, input_date):
    
        self.initializedPath_object = initializedPath_object
        self.input_date = input_date
        self.input_date_formatted = datetime.strftime(datetime.strptime(self.input_date, "%Y%m%d"), "%Y-%m-%d")
    
    def tomcat_griff_tlog_files(self):
        tlog_files = []
        griff_tlog_dir = ""
        
        #current tlog file
        tlog_files.append(self.initializedPath_object.griff_tomcat_log_path_dict["griff_TLOG_log"])
        
        splitted_tlog_path = str(self.initializedPath_object.griff_tomcat_log_path_dict['griff_TLOG_log'])\
                                .split("/")[0:-1]
        for i in range(1, len(splitted_tlog_path)):
            griff_tlog_dir += f"/{splitted_tlog_path[i]}"
                
        path = Path(rf"{griff_tlog_dir}")
        
        #input dated file in the tlog directory
        dated_tlog_files = [p for p in path.glob(f"griffTLog-{self.input_date_formatted}-*.csv")]
            
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
                
        #input dated file in the backup directory
        dated_tlog_backup_files = [p for p in path.glob(f"griffTLog-{self.input_date_formatted}-*.zip")]
        
        if bool(dated_tlog_backup_files):
            for files in dated_tlog_backup_files:
                tlog_backup_files.append(str(files))
                
        return tlog_backup_files