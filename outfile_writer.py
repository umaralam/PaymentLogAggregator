import json
import logging
import os
from pathlib import Path
import shutil
import socket
from zipfile import ZipFile
import zipfile

class FileWriter:
    
    def __init__(self, outputDirectory_object, oarm_uid):
        self.outputDirectory_object = outputDirectory_object
        self.oarm_uid = oarm_uid
        self.hostname = socket.gethostname()
        
    def write_json_tlog_data(self, payment_data_dict):
        
        # Check if the file exists  
        # if os.path.exists("payment_data.json"):
        #     with open("payment_data.json", "a") as outfile:
        #         json.dump(payment_data_dict, outfile, indent=4)
        # else:
            # Open a JSON file for writing
        with open(f"{self.outputDirectory_object}/{self.hostname}_paymentTransactionData.json", "w") as outfile:
            json.dump(payment_data_dict, outfile, indent=4)
    
    def write_complete_thread_log(self, pname, tlog_thread, record):
        if pname == "GRIFF":
            griff_folder = Path(f"{self.outputDirectory_object}/{self.hostname}_griff")
                
            thread_outfile = f"{griff_folder}/griff.log"
            new_line = '\n'
            # if os.path.isfile(thread_outfile) and os.path.getsize(thread_outfile) != 0:
            #     os.remove(thread_outfile)
            
            try:    
                with open(thread_outfile, "a") as write_file:
                    write_file.writelines(tlog_thread)
                    write_file.writelines(f"{new_line}========================================{new_line}")
                    write_file.writelines(record)
                    write_file.writelines(new_line)
                    
                
            except FileNotFoundError as error:
                logging.info('file not found to write.')
                
    def zipped_outfile(self):
        #zipping the out folder
        out_zipFile = Path(f"{self.oarm_uid}_{self.hostname}_outfile.zip")
        with ZipFile(out_zipFile, "a", compression=zipfile.ZIP_DEFLATED) as zip:
            for path in Path(self.outputDirectory_object).rglob(f"{self.hostname}_*"):
                zip.write(path)
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