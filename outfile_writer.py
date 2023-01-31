from collections import defaultdict
import json
import os

class FileWriter:
        
    def write_json_tlog_data(self, payment_data_dict):
        
        # Check if the file exists  
        if os.path.exists("payment_data.json"):
            with open("payment_data.json", "a") as outfile:
                json.dump(payment_data_dict, outfile, indent=4)
        else:
            # Open a JSON file for writing
            with open("payment_data.json", "w") as outfile:
                json.dump(payment_data_dict, outfile, indent=4)