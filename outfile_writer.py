from collections import defaultdict
import json
import logging
import os

class FileWriter:
    
    def __init__(self, outputDirectory_object):
        self.outputDirectory_object = outputDirectory_object
        
    def write_json_tlog_data(self, payment_data_dict):
        
        # Check if the file exists  
        # if os.path.exists("payment_data.json"):
        #     with open("payment_data.json", "a") as outfile:
        #         json.dump(payment_data_dict, outfile, indent=4)
        # else:
            # Open a JSON file for writing
        with open(f"{self.outputDirectory_object}/payment_data.json", "w") as outfile:
            json.dump(payment_data_dict, outfile, indent=4)
    
    def write_complete_thread_log(self, pname, tlog_thread, record):
        if pname == "GRIFF":
            thread_outfile = f"{self.outputDirectory_object}/griff.log"
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