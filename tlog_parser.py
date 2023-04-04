import json
import logging
import os
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
        
        self.hostname = socket.gethostname()
        
        #out folder parameters
        self.onmopay_out_folder = False
        self.griff_out_folder = False
        self.packs_out_folder = False
        self.prism_tomcat_out_folder = False
        self.prism_daemon_out_folder = False
        self.prism_smsd_out_folder = False
        self.prism_tomcat_access_out_folder = False
        
        #prism required parameters
        self.task_type = ""
        self.stck_sub_type = ""
        self.input_tag = ""
    
    def parse_tlog(self, pname, tlog_header_data_dict, ctid_map=None):
        """
            tlog parser method
        """
        self.reinitialize_constructor_parameters()
        folder = ""
        
        if pname == "ONMOPAY":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_onmopay".format(self.hostname))
        elif pname == "GRIFF":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_griff".format(self.hostname))
        elif pname == "PACKS":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_packs".format(self.hostname))
        elif pname == "PRISM_TOMCAT":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_prism_tomcat".format(self.hostname))
        elif pname == "PRISM_DEAMON":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_prism_daemon".format(self.hostname))
        elif pname == "PRISM_SMSD":
            folder = os.path.join(self.outputDirectory_object, "{}_issue_prism_smsd".format(self.hostname))
        
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object,\
                                                        self.validation_object, self.oarm_uid)
        #processing tlog based on different key in the tlog        
        try:
            if (pname == "GRIFF" or pname == "PACKS" or pname == "ONMOPAY") and ctid_map != None:
                for ctid in ctid_map:
                    for tlog_dict in tlog_header_data_dict[ctid]:
                        # logging.info('tlog dict onmo: %s', tlog_dict)

                        if self.log_mode == "error":
                            if pname == "ONMOPAY":
                                #empty check
                                if tlog_dict["ErrorCode"]:
                                    #issue thread found so create process folder for the 1st time
                                    if not self.onmopay_out_folder:
                                        self.create_process_folder(pname, folder)
                                    #fetch daemon log
                                    logging.info('%s is having an issue: %s', tlog_dict["SessionID"], tlog_dict["ErrorCode"])
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["ErrorCode"], ctid, tlog_dict["RequestOrigin"], None, None)
                                    
                            elif pname == "GRIFF" and tlog_dict:
                                out = str(tlog_dict["OUT"]).split(",")
                                logging.info('griff out: %s', out)
                                msg = "CG is not available"
        
                                logging.info('status value: %s', out[2].strip())
                                if out[0] != "OUT=200" and msg not in out[2].strip():
                                    
                                    #issue thread found so create griff folder for the 1st time
                                    if not self.griff_out_folder:
                                        self.create_process_folder(pname, folder)      
                                    
                                    #fetch daemon log
                                    logging.info('issue thread: %s', tlog_dict["THREAD_NAME"])
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None, None, None)
                        
                            elif pname == "PACKS" and tlog_dict:
                                if (tlog_dict["BILLING_RES_STATUS"] == "ERROR" 
                                        or (tlog_dict["BILLING_RES_STATUS"] == "" and tlog_dict["RET_STATUS"] == "FAILURE")
                                        or (tlog_dict["RET_STATUS"] == "SUCCESS" and tlog_dict["RET_ERROR_REASON"] != "")
                                    ):
                                    #issue thread found so create griff folder for the 1st time
                                    if not self.packs_out_folder:
                                        self.create_process_folder(pname, folder)      
                                    
                                    #fetch daemon log
                                    logging.info('issue thread: %s', tlog_dict["THREAD_NAME"])
                                    daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None, None, None)
                                
                                      
                                
                        elif self.log_mode == "all":
                            #issue thread found so create griff folder for the 1st time
                            if not self.griff_out_folder:
                                self.create_process_folder(pname, folder)
                                 
                            daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD_NAME"], ctid, None, None, None)
                    else:
                        if self.log_mode == "error":
                            if pname == "ONMOPAY":
                                for tlog_dict in tlog_header_data_dict[ctid]:
                                #will be checking for error csv
                                    daemonLogProcessor_object.process_daemon_log(pname, None, ctid, tlog_dict["RequestOrigin"], None, None)
            
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                thread_list = []
                if pname == "PRISM_TOMCAT":
                    thread_list = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
                elif pname == "PRISM_DEAMON":
                    thread_list = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
                for thread in thread_list:
                    for key, value in dict(tlog_header_data_dict).items():       
                        # logging.info('tlog key: %s value: %s', key, value['THREAD'])
        
                        if self.log_mode == "error" and thread == value['THREAD']:
                            if self.check_for_issue_in_prism_tlog(
                                                                    pname, folder, value,
                                                                    PrismTasks, PrismTlogErrorTag,
                                                                    PrismTlogLowBalTag, PrismTlogRetryTag,
                                                                    PrismTlogNHFTag, PrismTlogHandlerExp,
                                                                    PrismTlogAwaitPushTag, PrismTlogAwaitPushTimeOutTag
                                                                ):
                                if self.stck_sub_type:
                                    daemonLogProcessor_object.process_daemon_log(pname, thread, None, self.task_type, self.stck_sub_type, self.input_tag)
                                else:
                                    logging.info('reached thread: %s', thread)
                                    daemonLogProcessor_object.process_daemon_log(pname, thread, None, self.task_type, tlog_header_data_dict[thread]["SUB_TYPE"], self.input_tag)
                                    
                    # elif self.log_mode == "all":
                    #     if self.stck_sub_type:
                    #         daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"], None, self.task_type, self.stck_sub_type, self.input_tag)
                    #     else:
                    #         daemonLogProcessor_object.process_daemon_log(pname, tlog_dict["THREAD"], None, self.task_type, tlog_dict["SUB_TYPE"], self.input_tag)
            
            elif pname == "PRISM_SMSD":
                if self.log_mode == "error":
                    for sms_tlog in tlog_header_data_dict["PRISM_SMSD_TLOG"]:
                        # logging.info('sms tlog list: %s', sms_tlog)
                        for status in PrismTlogSmsTag:
                            if status.value == sms_tlog["STATUS"]:
                                if not self.prism_smsd_out_folder:
                                    self.create_process_folder(pname, folder)
                                daemonLogProcessor_object.process_daemon_log(pname, sms_tlog["THREAD"], None, None, None, None)
                            
                     
        except KeyError as error:
            logging.exception(error)
    
    def check_for_issue_in_prism_tlog(self, pname, folder, tlog_dict, prism_tasks, *args):
        #issue validation against input_tags
        for prism_input_tags in args:
            for status in prism_input_tags:
                for task in tlog_dict["FLOW_TASKS"]:
                    if status.value in task:
                        #issue thread found hence going to create prism process folder for the 1st time
                        if pname == "PRISM_TOMCAT":
                            if not self.prism_tomcat_out_folder:
                                self.create_process_folder(pname, folder)
                        elif pname == "PRISM_DEAMON":
                            if not self.prism_daemon_out_folder:
                                self.create_process_folder(pname, folder)
                        
                        #substitution parameters
                        self.input_tag = status.value
                        for ptask in prism_tasks:
                            if ptask.name == status.name:
                                if status.name == "SUB_TYPE_CHECK":
                                    self.stck_sub_type = 'A'
                                self.task_type = ptask.value
                                return True
        return False
                               
    def create_process_folder(self, pname, folder):
        """
            creating process folder
        """
        try:
            # folder.mkdir(parents=True, exist_ok=False)
            if not os.path.exists(folder):
                os.mkdir(folder)
            self.set_process_out_folder(pname, True)
        except os.error as error:
            logging.info(error)
            os.mkdir(folder)
            # folder.mkdir(parents=True)
            
            self.set_process_out_folder(pname, True)
    
    def set_process_out_folder(self, pname, is_true):
        if pname == "ONMOPAY":
            self.onmopay_out_folder = is_true
        elif pname == "GRIFF":
            self.griff_out_folder = is_true
        elif pname == "PACKS":
            self.packs_out_folder = is_true
        elif pname == "PRISM_TOMCAT":
            self.prism_tomcat_out_folder = is_true
        elif pname == "PRISM_TOMCAT_ACCESS":
            self.prism_tomcat_access_out_folder = is_true
        elif pname == "PRISM_DEAMON":
            self.prism_daemon_out_folder = is_true
        elif pname == "PRISM_SMSD":
            self.prism_smsd_out_folder = is_true
            
    def reinitialize_constructor_parameters(self):
        self.task_type = ""
            
        