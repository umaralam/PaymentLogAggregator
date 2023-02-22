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
        
        self.hostname = socket.gethostname()
        
        #out folder parameters
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
        
        #call to remove previously executed process folders
        if pname == "GRIFF":
            folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_griff")
            self.remove_old_process_folder(pname, folder)
        elif pname == "PACKS":
            folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_packs")
            self.remove_old_process_folder(pname, folder)
        elif pname == "PRISM_TOMCAT":
            folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_tomcat")
            self.remove_old_process_folder(pname, folder)
        elif pname == "PRISM_DEAMON":
            folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_daemon")
            self.remove_old_process_folder(pname, folder)
        elif pname == "PRISM_SMSD":
            folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_smsd")
            self.remove_old_process_folder(pname, folder)
        
        #Daemon log processor object
        daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object,\
                                                        self.validation_object, self.oarm_uid)
        #processing tlog based on different key in the tlog       
        try:
            if (pname == "GRIFF" or pname == "PACKS") and ctid_map != None:
                for ctid in ctid_map:
                    for tlog_dict in tlog_header_data_dict[ctid]:
                        if self.log_mode == "error":
                            if pname == "GRIFF" and tlog_dict:
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
            
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                if pname == "PRISM_TOMCAT":
                    thread_list = self.prism_tomcat_tlog_thread_dict["PRISM_TOMCAT_THREAD"]
                elif pname == "PRISM_DEAMON":
                    thread_list = self.prism_daemon_tlog_thread_dict["PRISM_DEAMON_THREAD"]
                for thread in thread_list:
                    logging.info('thread in tlog header: %s', tlog_header_data_dict[thread])
                    # for tlog_dict in tlog_header_data_dict[thread]:
                    if self.log_mode == "error":
                        if self.check_for_issue_in_prism_tlog(
                                                                pname, folder, tlog_header_data_dict[thread],
                                                                PrismTasks, PrismTlogErrorTag,
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
            
            elif pname == "PRISM_SMSD":
                if self.log_mode == "error":
                    for sms_tlog in tlog_header_data_dict["PRISM_SMSD_TLOG"]:
                        logging.info('sms tlog list: %s', sms_tlog)
                        for status in PrismTlogSmsTag:
                            if status.value == sms_tlog["STATUS"]:
                                #issue thread found so create smsd folder for the 1st time
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
                                # logging.info('ptask value: %s', ptask.value)
                                self.task_type = ptask.value
                                return True
        return False
    
    # def parse_accessLog(self, pname, accesslog_dict):
    #     if pname == "PRISM_TOMCAT_ACCESS":
    #         folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_tomcat_access")
    #         self.remove_old_process_folder(pname, folder)
            
    #         #Daemon log processor object
    #         daemonLogProcessor_object = DaemonLogProcessor(self.initializedPath_object, self.outputDirectory_object,\
    #                                                     self.validation_object, self.oarm_uid)
    #         if self.log_mode == "error":
    #             for access_log in accesslog_dict[f"{self.validation_object.fmsisdn}"]:
    #                 for acc_log in access_log:
    #                     http_status_code = str(acc_log).split(" ")[-2]
    #                     logging.info('%s http status code is: %s', pname, http_status_code)
    #                     if http_status_code != "200":
    #                         #access hit response is not 200, hence parsing tomcat log
    #                         if not self.prism_tomcat_access_out_folder:
    #                             self.create_process_folder(pname, folder)
    #                         daemonLogProcessor_object.process_daemon_log(pname, self.validation_object.fmsisdn, None, None, None, None)
                               
    def create_process_folder(self, pname, folder):
        """
            creating process folder
        """
        try:
            folder.mkdir(parents=True, exist_ok=False)
            self.set_process_out_folder(pname, True)
        except FileExistsError as error:
            logging.info(error)
            folder.mkdir(parents=True)
            self.set_process_out_folder(pname, True)
    
    def remove_old_process_folder(self, pname, folder):
        #removing process folder if already exists
        try:
            logging.info('out directory already exists. Hence removing the old files of %s if exists.', self.hostname)
            shutil.rmtree(folder)
        except FileNotFoundError as error:
            logging.info('%s out folder does not exists: %s', pname, error)
    
    def set_process_out_folder(self, pname, is_true):
        if pname == "GRIFF":
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
            
        