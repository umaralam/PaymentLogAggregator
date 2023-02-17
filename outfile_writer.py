import json
import logging
import os
from pathlib import Path
import re
import shutil
import socket
from zipfile import ZipFile
import zipfile
from input_tags import Griff_St_SString, Griff_En_SString
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
    
    def write_complete_thread_log(self, pname, ctid, tlog_thread, record):
        #write complete thread log
        if pname == "GRIFF":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_griff")                
            thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_griff.log"
        elif pname == "PACKS":
            process_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_packs")                
            thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_packs.log"

        try:
            with open(thread_outfile, "w") as write_file:
                write_file.writelines(record)
                self.write_trimmed_thread_log(pname, process_folder, ctid, tlog_thread, thread_outfile)               
        except FileNotFoundError as error:
            logging.info('file not found to write.')
                
    def write_trimmed_thread_log(self, pname, process_folder, ctid, tlog_thread, thread_outfile):
        if pname == "GRIFF":
            # start_of_serach_string = "Processor Called"
            # end_of_serach_string = "Request completed"
            trimmed_thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_trimmed_griff.log"
            
        elif pname == "PACKS":
            # start_of_serach_string = ""
            # end_of_serach_string = "Request completed"
            trimmed_thread_outfile = f"{process_folder}/{ctid}_{tlog_thread}_trimmed_packs.log"
            
        #set initial index based on start of search string
        for start_of_serach_string in Griff_St_SString:
            try:
                with open(thread_outfile, "r") as outFile:
                    if pname == "GRIFF":
                        for i, line in enumerate(outFile):
                            # if re.search(r"{}".format(str(start_of_serach_string.value)), line):
                            if re.search(start_of_serach_string.value, line, re.DOTALL):
                                logging.info('st search: %s', start_of_serach_string.value)
                                self.set_initial_index(i)
                                break
            except FileNotFoundError as error:
                logging.info(error)
        
        #set final index based on end of search string
        try:
            with open(thread_outfile, "r") as outFile:
                if pname == "GRIFF":
                    for end_of_serach_string in Griff_En_SString:
                        logging.info('en search: %s', end_of_serach_string.value)
                        for i, line in enumerate(outFile):
                            if re.search(r"{}".format(str(end_of_serach_string.value)), line):
                                self.set_final_index(i)
                                break
        except FileNotFoundError as error:
            logging.info(error)
        
        # try:
        #     output = subprocess.check_output(['wc', '-l', thread_outfile]).decode().strip()
        #     self.set_final_index(int(output.split()[0]))
        # except subprocess.CalledProcessError as error:
        #     logging.info(error)
            
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
    
    def set_final_index(self, final_index):
        """
        Setting initial index from
        """
        self.__final_index = final_index
                
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