import logging
from pathlib import Path
import shutil
import socket
from process_daemon_log import DaemonLogProcessor
from input_tags import PrismTlogErrorTag, PrismTlogLowBalTag, PrismTlogRetryTag,\
    PrismTlogHandlerExp, PrismTlogNHFTag, PrismTlogAwaitPushTag, PrismTlogAwaitPushTimeOutTag,\
    PrismTlogSmsTag, PrismTasks

class TlogParser:
    """
        Tlog parser class
        for parsing tlog for any issue
    """
    def __init__(self, initializedPath_object, outputDirectory_object, validation_object, log_mode, oarm_uid,\
                    prism_daemon_tlog_thread_dict, prism_tomcat_tlog_thread_dict):
        
        self.initializedPath_object = initializedPath_object
        self.outputDirectory_object = outputDirectory_object
        self.validation_object = validation_object
        self.log_mode = log_mode
        self.oarm_uid = oarm_uid
        self.prism_daemon_tlog_thread_dict = prism_daemon_tlog_thread_dict
        self.prism_tomcat_tlog_thread_dict = prism_tomcat_tlog_thread_dict
        self.task_type = ""
    
    def parse_tlog(self, pname, tlog_header_data_dict, ctid_map=None):
        """
            tlog parser method
        """
        self.reinitialize_constructor_parameters()
        
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object,\
                                                        self.validation_object, self.oarm_uid)
        #processing tlog based on different key in the tlog        
        try:
            if ctid_map != None:
                for ctid in ctid_map:
                    for tlog_dict in tlog_header_data_dict[ctid]:
                        if self.log_mode == "error":
                            if pname == "GRIFF" and tlog_dict:
                                out = str(tlog_dict["OUT"]).split(",")
                                logging.info('griff out: %s', out)
                                msg = "CG is not available"
        
                                logging.info('status value: %s', out[2].strip())
                                if out[0] != "OUT=200" and msg not in out[2].strip():        
                                    #fetch daemon log
                                    logging.info('issue thread: %s', tlog_dict["THREAD_NAME"])
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None)
                        
                            elif pname == "PACKS" and tlog_dict:
                                pass
                                            
                        elif self.log_mode == "all":
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None)
            else:
                if pname == "PRISM_TOMCAT":
                    thread_list = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
                elif pname == "PRISM_DEAMON":
                    thread_list = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
                
                for thread in thread_list:    
                    for tlog_dict in tlog_header_data_dict[thread]:
                        if self.log_mode == "error":
                            if self.check_for_issue_in_prism_tlog(
                                                                    tlog_dict,PrismTasks, PrismTlogErrorTag,
                                                                    PrismTlogLowBalTag, PrismTlogRetryTag,
                                                                    PrismTlogNHFTag, PrismTlogHandlerExp,
                                                                    PrismTlogAwaitPushTag, PrismTlogAwaitPushTimeOutTag
                                                                ):
                                daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"], None, self.task_type)
                                            
                        elif self.log_mode == "all":
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"])
       
        except KeyError as error:
            logging.exception(error)
    
    def check_for_issue_in_prism_tlog(self, tlog_dict, tasks, *args):
        #issue validation against input_tags
        
        for prism_input_tags in args:
            for status in prism_input_tags:
                if status.value in tlog_dict["FLOW_TASKS"]:
                    logging.info('issue thread: %s', tlog_dict["THREAD"])
                    for task in tasks:
                        if task.name == status.name:
                            self.task_type = task.value
                            return True
        return False
    
    def reinitialize_constructor_parameters(self):
        self.task_type = ""
            
        