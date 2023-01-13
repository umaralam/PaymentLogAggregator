#!/usr/local/bin/python3
from datetime import datetime, timedelta
import json
import logging
import os
from pathlib import Path
import socket
import sys
from path_initializer import LogPathFinder
from input_validation import InputValidation
from log_processor import PROCESSOR


class Main:

    def init(self):
        logging.basicConfig(filename='log_aggregator.log', filemode='w', format='[%(asctime)s,%(msecs)d]%(pathname)s:(%(lineno)d)-%(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
        
        start = datetime.now()
        logging.debug('start of execution time: %s', start)
        
        num_argv = len(sys.argv)
        logging.debug('Number of arguments passed is %s', num_argv - 1)
        
        if num_argv == 4:
            logging.debug('Arguments passed are - msisdn:%s and search date:%s', sys.argv[1], sys.argv[2])
            # if num_argv == 4:
            #     logging.debug('Arguments passed are - msisdn:%s and automattion_log:%s', sys.argv[1], sys.argv[2])
            # else:
            #     logging.debug('Arguments passed are : msisdn=%s and search_date=%s', sys.argv[1], sys.argv[2])
                
        r_period = 1
        hostname = socket.gethostname()
        data = Path("common.json").read_text()
        config = json.loads(data)
        
        if config:
            logging.info('data rentention is by default defined for 1 day.')
            bdt = datetime.today() - timedelta(days=r_period)
            back_date = datetime.strftime(bdt, "%Y%m%d")
            logging.info('back date: %s', back_date)
                
            outputDirectory_object = Path('out')
            try:
                outputDirectory_object.mkdir(exist_ok=False)
            except FileExistsError as error:
                logging.info('out directory already exists.')
            
            outputDirectory_object = Path('out/prism_auto_log')
            try:
                outputDirectory_object.mkdir(exist_ok=False)
            except FileExistsError as error:
                logging.info('out/automation directory already exists. Going to fetch %s dated files and remove.', back_date)
            
            logging.info('\n')
            logging.info('Log aggregation for automation started')
            logging.info("*******************************************")
            
            self.remove_backdated_files(outputDirectory_object, back_date)
            validation_object = InputValidation(sys.argv[1], sys.argv[2])
            
            try:
                if num_argv == 4:
                    fmsisdn, input_date = self.validate_input(validation_object, num_argv)
            except Exception as error:
                logging.exception(error)
                
            msisdn = sys.argv[1]
            
            logging.info('\n')
            
            if validation_object.is_input_valid:
                initializedPath_object = LogPathFinder(hostname, config, input_date)
                try:
                    for i in config[hostname]:
                        try:
                            if config[hostname]["GRIFF"] and i == 'GRIFF':
                                initializedPath_object.initialize_tomcat_path(i)
                                logging.info('\n')
                                if initializedPath_object.griff_tomcat_log_path_dict:
                                    logging.info('%s TOMCAT PATH INITIALIZED', i)
                                    formatter = "#" * 100
                                    logging.info('%s', formatter)
                                    for key, value in initializedPath_object.griff_tomcat_log_path_dict.items():
                                        logging.info('%s : %s', key, value)
                                else:
                                    logging.info('%s TOMCAT PATH NOT INITIALIZED', i)
                        except KeyError as error:
                            logging.exception(error)                               
                        except ValueError as error:
                            logging.warning('%s tomcat path not initialized. %s', i, error)
                        except Exception as error:
                            logging.warning(error)
                            
                        try:
                            if config[hostname]["PACKS"] and i == 'PACKS':
                                initializedPath_object.initialize_tomcat_path(i)
                                logging.info('\n')
                                if initializedPath_object.packs_tomcat_log_path_dict:
                                    logging.info('%s TOMCAT PATH INITIALIZED', i)
                                    formatter = "#" * 100
                                    logging.info('%s', formatter)
                                    for key, value in initializedPath_object.packs_tomcat_log_path_dict.items():
                                        logging.info('%s : %s', key, value)
                                else:
                                    logging.error('%s TOMCAT PATH NOT INITIALIZED', i)
                        except KeyError as error:
                            logging.exception(error)
                        except ValueError as error:
                            logging.warning('%s tomcat path not initialized. %s', i, error)
                        except Exception as error:
                            logging.warning(error)
                except KeyError as ex:
                    logging.error('invalid hostname key')
            
            
            if num_argv == 4:
                processor_object = PROCESSOR(initializedPath_object, msisdn, fmsisdn, input_date, outputDirectory_object, validation_object, sys.argv[3])
                processor_object.process()
            else:
                logging.error('xyz')

                logging.info('Log aggregation finished.')
                logging.info("**********************************")
            
        end = datetime.now()
        logging.debug('end of execution time: %s', end)
            
        duration = end.timestamp() - start.timestamp()
        logging.debug('Total time taken %s', duration)
        
    def remove_backdated_files(self, outputDirectory_object, back_date):
        outfiles = [p for p in outputDirectory_object.glob(f"*_{back_date}__*.*")]
        if bool(outfiles):
            for file in outfiles:
                if os.path.isfile(file):
                    os.remove(file)
                    logging.info('back dated files removed: %s', file)
                else:
                    logging.info('back dated file does not exists: %s', file)
        else:
            logging.info('back dated file does not exists')
        
    def validate_input(self, validation_object, cmd_argv):
        try:
            if cmd_argv == 4:
                fmsisdn = validation_object.validate_msisdn()
                input_date = validation_object.validate_date()
                return (fmsisdn, input_date)
        except Exception as error:
            raise    
        
        
if __name__ == '__main__':
    main_object = Main()
    main_object.init()