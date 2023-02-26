#!/usr/local/bin/python3
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import socket
import sys
from input_validation import InputValidation
from process_initializer import Initializer
from outfile_writer import FileWriter

class Main:

    def init(self):
        logging.basicConfig(filename='aggregator.log', filemode='w', format='[%(asctime)s,%(msecs)d]%(pathname)s:(%(lineno)d)-%(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
        
        start = datetime.now()
        logging.debug('start of execution time: %s', start)
        
        num_argv = len(sys.argv)
        uid = sys.argv[len(sys.argv) - 1]
        hostname = socket.gethostname()
        outputDirectory_object = Path('out')
        outputDirectory_object.mkdir(exist_ok=True)
        
        validation_object = InputValidation(num_argv, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        validation_object.validate_argument()
        
        fileWriter_object = FileWriter(outputDirectory_object, uid)
        
        if os.path.exists('modified_log4j2.xml'):
            logging.info('removing old modified_log4j2.xml')
            os.remove('modified_log4j2.xml')
        
        if os.path.exists('modified_nlog.config'):
            logging.info('removing old modified_nlog.config')
            os.remove('modified_nlog.config')
        
        if os.path.exists(f'out/{hostname}_paymentTransactionData.json'):
            logging.info(f'out/{hostname}_paymentTransactionData.json')
            os.remove(f'out/{hostname}_paymentTransactionData.json')
        
        if validation_object.is_input_valid:
            data = Path(f"{hostname}.json").read_text()
            config = json.loads(data)
            
            if config:
                logging.info('\n')
                logging.info('Log aggregation for automation started')
                logging.info("*******************************************")
                
                try:
                    validation_object.validate_msisdn()
                    validation_object.validate_date()
                except Exception as error:
                    logging.exception(error)
                
                logging.info('\n')
                
                if validation_object.is_input_valid:
                    initializer_object = Initializer(hostname, outputDirectory_object, config, validation_object, validation_object.log_mode, uid)
                    initializer_object.initialize_process()
            
        else:
            logging.error('Invalid number of argument passed, should be "4" Please refer to the syntax.')
            logging.error('Hence log fetch could not happen.')
            
            
        logging.info('Log aggregation finished.')
        logging.info("**********************************")
        
        end = datetime.now()
        logging.debug('end of execution time: %s', end)
            
        duration = end.timestamp() - start.timestamp()
        logging.debug('Total time taken %s', duration)
        
        #move log to out folder and zip the out folder
        fileWriter_object.log_mover()
        fileWriter_object.zipped_outfile()
        
        
if __name__ == '__main__':
    main_object = Main()
    main_object.init()