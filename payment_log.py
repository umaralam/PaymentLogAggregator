#!/usr/local/bin/python3
from datetime import datetime, timedelta
import json
import logging
import os
from pathlib import Path
import shutil
import socket
import sys
from zipfile import ZipFile
import zipfile
from path_initializer import LogPathFinder
from input_validation import InputValidation
from input_tags import logMode
from log_processor import PROCESSOR


class Main:

    def init(self):
        logging.basicConfig(filename='log_aggregator.log', filemode='w', format='[%(asctime)s,%(msecs)d]%(pathname)s:(%(lineno)d)-%(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
        
        start = datetime.now()
        logging.debug('start of execution time: %s', start)
        
        num_argv = len(sys.argv)
        logging.debug('Number of arguments passed is: %s', num_argv - 1)
        
        #default log mode is data(to fetch only transaction data accross product)
        log_mode = "data"
        
        if num_argv == 6:
            for status in logMode:
                if status.value == sys.argv[4].split("=")[1]:
                    log_mode = status.value
                    logging.debug('Arguments passed are :- msisdn:%s, start_date:%s, end_date:%s and log_mode:%s', sys.argv[1], sys.argv[2], sys.argv[3], log_mode)
                    break
            else:
                logging.error('%s passed can eigther be "data/error/all", default value is "data"', sys.argv[4])
            
            
        # r_period = 1
        hostname = socket.gethostname()
        data = Path(f"{hostname}.json").read_text()
        config = json.loads(data)
        
        if config:
            # logging.info('data rentention period is by default 1 day.')
            # bdt = datetime.today() - timedelta(days=r_period)
            # back_date = datetime.strftime(bdt, "%Y%m%d")
            # logging.info('back date: %s', back_date)
                
            outputDirectory_object = Path('out')
            try:
                outputDirectory_object.mkdir(exist_ok=False)
            except FileExistsError as error:
                logging.info('out directory already exists. Hence removing the old out file and creating empty out file.')
                shutil.rmtree(outputDirectory_object)
                outputDirectory_object.mkdir()
            # outputDirectory_object = Path('out')
            # try:
            #     outputDirectory_object.mkdir(exist_ok=False)
            # except FileExistsError as error:
            #     logging.info('out/automation directory already exists. Going to fetch %s dated files and remove.', back_date)
            
            logging.info('\n')
            logging.info('Log aggregation for automation started')
            logging.info("*******************************************")
            
            # self.remove_backdated_files(outputDirectory_object, back_date)
            validation_object = InputValidation(sys.argv[1], sys.argv[2], sys.argv[3])
            
            try:
                if num_argv == 6:
                    validation_object.validate_msisdn()
                    validation_object.validate_date()
            except Exception as error:
                logging.exception(error)
            
            logging.info('\n')
            
            if validation_object.is_input_valid:
                initializedPath_object = LogPathFinder(hostname, config, validation_object)
                try:
                    for i in config[hostname]:
                        try:
                            if config[hostname]["GRIFF"] and i == 'GRIFF':
                                initializedPath_object.initialize_path(i)
                                if initializedPath_object.griff_tomcat_log_path_dict:
                                    formatter = "#" * 100
                                    logging.info('\n')
                                    logging.info('%s TOMCAT PATH INITIALIZED \n %s', i, formatter)
                                    # logging.info('%s', formatter)
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
                                initializedPath_object.initialize_path(i)
                                if initializedPath_object.packs_tomcat_log_path_dict:
                                    formatter = "#" * 100
                                    logging.info('\n')
                                    logging.info('%s TOMCAT PATH INITIALIZED \n %s', i, formatter)
                                    # logging.info('%s', formatter)
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
                        
                        try:
                            if config[hostname]["PRISM"] and i == 'PRISM':
                                if config[hostname]["PRISM"]["PRISM_TOMCAT"] != "":
                                    try:
                                        initializedPath_object.initialize_path(i)
                                        formatter = "#" * 100
                                        logging.info('\n')
                                        logging.info('%s TOMCAT PATH INITIALIZED \n %s', i, formatter)
                                        for key, value in initializedPath_object.prism_tomcat_log_path_dict.items():
                                            logging.info('%s : %s', key, value)
                                    except ValueError as error:
                                        logging.warning('%s Tomcat path not initialized. %s', i, error)
                                    except Exception as error:
                                        logging.warning(error)
                                else:
                                    logging.error(
                                                    '%s TOMCAT data not present in %s file,\
                                                    Hence PRISM_TOMCAT logs will not be initialized and fetched', i, hostname
                                                )
                                
                                if config[hostname]["PRISM"]["PRISM_DEAMON"] != "":
                                    try:
                                        initializedPath_object.initialize_path(i)
                                        formatter = "#" * 100
                                        logging.info('\n')
                                        logging.info('%s DAEMON PATH INITIALIZED \n %s', i, formatter)
                                        for key, value in initializedPath_object.prism_daemon_log_path_dict.items():
                                            logging.info('%s : %s', key, value)
                                    except ValueError as error:
                                        logging.warning('%s path not initialized. %s', i, error)
                                    except Exception as error:
                                        logging.warning(error)
                                else:
                                    logging.error(
                                                    '%s DEAMON data not present in %s file,\
                                                    Hence PRISM_DEAMON logs will not be initialized and fetched', i, hostname
                                                )

                                if config[hostname]["PRISM"]["PRISM_SMSD"] != "":
                                    try:
                                        initializedPath_object.initialize_path(i)
                                        formatter = "#" * 100
                                        logging.info('\n')
                                        logging.info('%s SMS PATH INITIALIZED \n %s', i, formatter)
                                        # logging.info('%s', formatter)
                                        for key, value in initializedPath_object.prism_smsd_log_path_dict.items():
                                            logging.info('%s : %s', key, value)
                                    except ValueError as error:
                                        logging.warning('%s path not initialized. %s', i, error)
                                    except Exception as error:
                                        logging.warning(error)
                                else:
                                    logging.error(
                                                    '%s SMSD data not present in %s file,\
                                                    Hence PRISM_SMSD logs will not be initialized and fetched', i, hostname
                                                )
                        except KeyError as error:
                            logging.exception(error)
                        except ValueError as error:
                            logging.warning('any of the %s path not initialized', i)
                        except Exception as error:
                            logging.warning(error)
                            
                    uid = sys.argv[5]
                    
                    if num_argv == 6:
                        processor_object = PROCESSOR(initializedPath_object, outputDirectory_object, validation_object, log_mode, uid, config)
                        processor_object.process()
                    else:
                        logging.error('Invalid number of argument')

                        logging.info('Log aggregation finished.')
                        logging.info("**********************************")
                        
                except KeyError as error:
                    logging.exception(error)
            
        #move log_aggregator.log from current directory to respective directory.
        log = outputDirectory_object/"log_aggregator.log"
        if Path('log_aggregator.log').exists():
            try:
                if os.path.isfile(outputDirectory_object/"log_aggregator.log"):
                    logging.info('log_aggregator.log file already exists. Hence removing and copying it.')
                    os.remove(log)
                shutil.move('log_aggregator.log', f'{outputDirectory_object}/')
            except Exception as error:
                logging.info(error)

        logging.info('out directory: %s', outputDirectory_object)
        
        end = datetime.now()
        logging.debug('end of execution time: %s', end)
            
        duration = end.timestamp() - start.timestamp()
        logging.debug('Total time taken %s', duration)
        
        if num_argv == 6:
            out_zipFile = f"{sys.argv[5]}_{hostname}_{Path('outfile.zip')}"
            with ZipFile(out_zipFile, "a", compression=zipfile.ZIP_DEFLATED) as zip:
                # for path in Path(outputDirectory_object).rglob(f"{sys.argv[4]}_*.*"):
                zip.write(outputDirectory_object)
            print(f"OARM_OUTPUT_FILENAME|{Path(out_zipFile).absolute()}")
        
    # def remove_backdated_files(self, outputDirectory_object, back_date):
    #     outfiles = [p for p in outputDirectory_object.glob(f"*_{back_date}__*.*")]
    #     if bool(outfiles):
    #         for file in outfiles:
    #             if os.path.isfile(file):
    #                 os.remove(file)
    #                 logging.info('back dated files removed: %s', file)
    #             else:
    #                 logging.info('back dated file does not exists: %s', file)
    #     else:
    #         logging.info('back dated file does not exists')        
        
if __name__ == '__main__':
    main_object = Main()
    main_object.init()