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
        
        #prism required parameters
        self.task_type = ""
        self.stck_sub_type = ""
        self.input_tag = ""
    
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
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None, None, None)
                        
                            elif pname == "PACKS" and tlog_dict:
                                pass
                                            
                        elif self.log_mode == "all":
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None, None, None)
            else:
                if pname == "PRISM_TOMCAT":
                    thread_list = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
                elif pname == "PRISM_DEAMON":
                    thread_list = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
                for thread in thread_list:    
                    logging.info('thread in tlog header: %s', tlog_header_data_dict[thread])
                    # for tlog_dict in tlog_header_data_dict[thread]:
                    if self.log_mode == "error":
                        if self.check_for_issue_in_prism_tlog(
                                                                tlog_header_data_dict[thread],PrismTasks, PrismTlogErrorTag,
                                                                PrismTlogLowBalTag, PrismTlogRetryTag,
                                                                PrismTlogNHFTag, PrismTlogHandlerExp,
                                                                PrismTlogAwaitPushTag, PrismTlogAwaitPushTimeOutTag
                                                            ):
                            if self.stck_sub_type:
                                daemonLogProcessor_object.process_daemon_log(pname, thread, None, self.task_type, self.stck_sub_type, self.input_tag)
                            else:
                                daemonLogProcessor_object.process_daemon_log(pname, thread, None, self.task_type, tlog_header_data_dict[thread]["SUB_TYPE"], self.input_tag)
                                    
                    elif self.log_mode == "all":
                        if self.stck_sub_type:
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"], None, self.task_type, self.stck_sub_type, self.input_tag)
                        else:
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"], None, self.task_type, tlog_dict["SUB_TYPE"], self.input_tag)
                                
        except KeyError as error:
            logging.exception(error)
    
    def check_for_issue_in_prism_tlog(self, tlog_dict, prism_tasks, *args):
        #issue validation against input_tags
        
        for prism_input_tags in args:
            for status in prism_input_tags:
                # logging.info('status input: %s', tlog_dict["FLOW_TASKS"])
                for task in tlog_dict["FLOW_TASKS"]:
                    if status.value in task:
                        self.input_tag = status.value
                        for ptask in prism_tasks:
                            if ptask.name == status.name:
                                if status.name == "SUB_TYPE_CHECK":
                                    self.stck_sub_type = 'A'
                                # logging.info('ptask value: %s', ptask.value)
                                self.task_type = ptask.value
                                return True
        return False
    
    def reinitialize_constructor_parameters(self):
        self.task_type = ""
            
        