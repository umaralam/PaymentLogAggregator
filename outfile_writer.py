import json
import logging
import os
from pathlib import Path
import re
import shutil
import socket
from zipfile import ZipFile
import zipfile
from input_tags import Griff_St_SString, Griff_En_SString, Packs_St_SString, Packs_En_SString, Prism_St_SString, Prism_En_SString
# import subprocess

class FileWriter:
    
    def __init__(self, outputDirectory_object, oarm_uid):
        self.outputDirectory_object = outputDirectory_object
        self.oarm_uid = oarm_uid
        self.hostname = socket.gethostname()
        self.__initial_index = 0
        self.__final_index = 0 
        
    def write_json_tlog_data(self, payment_data_dict):
        #dumping payment transaction data
        with open(f"{self.outputDirectory_object}/{self.hostname}_paymentTransactionData.json", "w") as outfile:
            json.dump(payment_data_dict, outfile, indent=4)
    
    def write_complete_thread_log(self, pname, tlog_thread, record, ctid, task_type, sub_type, input_tag):
        #write complete thread log
        if pname == "ONMOPAY":
            error_code = tlog_thread
            RequestOrigin = task_type
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_onmopay")
            thread_outfile = f"{process_folder}/{ctid}_paycore.log"
        
        elif pname == "GRIFF":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_griff")                
            thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_griff.log"
        
        elif pname == "PACKS":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_packs")                
            thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_packs.log"
        
        elif pname == "PRISM_TOMCAT":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_tomcat")                
            thread_outfile = f"{process_folder}/{task_type}_{tlog_thread}_prism_tomcat.log"
        
        elif pname == "PRISM_DEAMON":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_daemon")                
            thread_outfile = f"{process_folder}/{task_type}_{tlog_thread}_prism_daemon.log"
        
        elif pname == "PRISM_SMSD":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_issue_prism_smsd")                
            thread_outfile = f"{process_folder}/{tlog_thread}_prism_smsd.log"
            
        try:
            with open(thread_outfile, "w") as write_file:
                write_file.writelines(record)
                if pname == "GRIFF" or pname == "PACKS" or pname == "ONMOPAY":
                    if pname == "ONMOPAY":
                        self.write_trimmed_thread_log(pname, process_folder, error_code, thread_outfile, ctid, RequestOrigin, sub_type, input_tag)
                    else:
                        self.write_trimmed_thread_log(pname, process_folder, tlog_thread, thread_outfile, ctid, task_type, sub_type, input_tag)
                        
                elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                    self.write_trimmed_thread_log(pname, process_folder, tlog_thread, thread_outfile, ctid, task_type, sub_type, input_tag)
                    
        except FileNotFoundError as error:
            logging.info(error)
                
    def write_trimmed_thread_log(self, pname, process_folder, tlog_thread, thread_outfile, ctid, task_type, sub_type, input_tag):
        if pname == "ONMOPAY":
            error_code = tlog_thread
            RequestOrigin = task_type
            logging.info('request origin: %s', RequestOrigin)
            trimmed_thread_outfile = f"{process_folder}/{ctid}_trimmed_paycore.log"
            
        elif pname == "GRIFF":
            trimmed_thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_trimmed_griff.log"
            
        elif pname == "PACKS":
            trimmed_thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_trimmed_packs.log"
        
        elif pname == "PRISM_TOMCAT":
            trimmed_thread_outfile = f"{process_folder}/{task_type}_{tlog_thread}_trimmed_prism_tomcat.log"
        
        elif pname == "PRISM_DEAMON":
            trimmed_thread_outfile = f"{process_folder}/{task_type}_{tlog_thread}_trimmed_prism_daemon.log"
        
        try:   
            if pname == "GRIFF" or pname == "PACKS" or pname == "ONMOPAY":
                #set final index based on start of search string
                if pname == "ONMOPAY":
                    with open(thread_outfile, "r") as outFile:
                        for i, line in enumerate(outFile):
                            if re.search(r"{}".format(error_code), line):
                                self.set_final_index(i + 10)
                                if self.get_final_index() != 0:
                                    self.set_initial_index(self.get_final_index() - 50)
                                break
                            
                #set initial index based on start of search string
                if pname == "GRIFF":
                    for gf_start_serach_string in Griff_St_SString:
                        with open(thread_outfile, "r") as outFile:
                            for i, line in enumerate(outFile):
                                if re.search(gf_start_serach_string.value, line, re.DOTALL):
                                    self.set_initial_index(i)
                                    break
                elif pname == "PACKS":
                    for pk_start_serach_string in Packs_St_SString:
                        with open(thread_outfile, "r") as outFile:
                            for i, line in enumerate(outFile):
                                if re.search(pk_start_serach_string.value, line, re.DOTALL):
                                    self.set_initial_index(i)
                                    break
                
                    
                #set final index based on end of search string
                if pname == "GRIFF":
                    for gf_end_serach_string in Griff_En_SString:
                        with open(thread_outfile, "r") as outFile:
                            for i, line in enumerate(outFile):
                                if re.search(r"{}".format(str(gf_end_serach_string.value)), line):
                                    self.set_final_index(i)
                                    break
                elif pname == "PACKS":
                    for pk_end_serach_string in Packs_En_SString:
                        with open(thread_outfile, "r") as outFile:
                            for i, line in enumerate(outFile):
                                if re.search(r"{}".format(str(pk_end_serach_string.value)), line):
                                    self.set_final_index(i)
                                    break
            
            elif pname == "PRISM_TOMCAT" or pname == "PRISM_DEAMON":
                #set initial index based on start of search string
                for sm_start_serach_string in Prism_St_SString:
                    logging.info('st search: %s', str(sm_start_serach_string.value).format(task_type, sub_type))
                    sm_start_serach_string = str(sm_start_serach_string.value).format(task_type, sub_type)
                    with open(thread_outfile, "r") as outFile:
                        for i, line in enumerate(outFile):
                            if re.search(sm_start_serach_string, line, re.DOTALL):
                                self.set_initial_index(i)
                                break
                
                #set final index based on end of search string
                for sm_end_serach_string in Prism_En_SString:
                    logging.info('en search: %s', str(sm_end_serach_string.value).format(input_tag))
                    sm_end_serach_string = str(sm_end_serach_string.value).format(input_tag)
                    with open(thread_outfile, "r") as outFile:
                        for i, line in enumerate(outFile):
                            if re.search(sm_end_serach_string, line, re.DOTALL):
                                self.set_final_index(i)
                                break
                

        except FileNotFoundError as error:
            logging.info(error)
            
        logging.info('initial_index: %s and final_index: %s', self.__initial_index, self.__final_index)
        #write trim log
        if self.__initial_index != self.__final_index != 0:
            with open(thread_outfile, "r") as read_file:
                for i, line in enumerate(read_file):
                    if self.__initial_index <= i < self.__final_index + 1:
                        with open(trimmed_thread_outfile, "a") as write_file:
                            write_file.writelines(line)

    
    def set_initial_index(self, initial_index):
        """
        Setting initial index from
        """
        self.__initial_index = initial_index
    
    def get_initial_index(self):
        """
        getting initial index from
        """
        return self.__initial_index
    
    def set_final_index(self, final_index):
        """
        Setting initial index from
        """
        self.__final_index = final_index
    
    def get_final_index(self):
        """
        getting initial index from
        """
        return self.__final_index
                
    def zipped_outfile(self):
        #zipping the out folder
        out_zipFile = Path(f"{self.oarm_uid}_{self.hostname}_outfile.zip")
        
        with ZipFile(out_zipFile, "a", compression=zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(self.outputDirectory_object):
                for file in files:
                    zip.write(os.path.join(root, file))
        print(f"OARM_OUTPUT_FILENAME|{Path(out_zipFile).absolute()}")
        
        
    def log_mover(self):
        #move log_aggregator.log from current directory to respective directory.
        log = f'{self.outputDirectory_object}/{self.hostname}_aggregator.log'
        
        if Path('aggregator.log').exists():
            try:
                if os.path.isfile(log):
                    logging.info('aggregator.log file already exists. Hence removing and copying it.')
                    os.remove(log)
                shutil.move('aggregator.log', log)
            except Exception as error:
                logging.info(error)