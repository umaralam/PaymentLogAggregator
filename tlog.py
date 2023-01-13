import csv
import logging
from log_files import LogFileFinder

class Tlog:
    """
    tlog mapping class
    """
    def __init__(self, initializedPath_object, validation_object):
        
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
    
    def get_griff_tomcat_tlog(self):
        """
        calling path finder method
        """
        tlog_record = []
        logfile_object = LogFileFinder(self.initializedPath_object, self.validation_object)
        tlog_files = list(logfile_object.tomcat_griff_tlog_files())
        logging.info('tlog files: %s', tlog_files)
        # if tlog_files != None:
        #     for file in tlog_files:
        #         with open(file, "r") as file_in:
        #             data = [line for line in csv.reader(file_in, lineterminator = '\n')]
        #             logging.info('data: %s', data)
        
        backup_tlog_files = list(logfile_object.tomcat_griff_tlog_backup_files())
        logging.info('backup tlog files: %s', backup_tlog_files)
        