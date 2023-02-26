import logging
from path_initializer import LogPathFinder
from log_processor import PROCESSOR


class Initializer:
    def __init__(self, hostname, outputDirectory_object, config, validation_object, log_mode, uid):
        self.hostname = hostname
        self.outputDirectory_object = outputDirectory_object
        self.config =  config
        self.validation_object = validation_object
        self.log_mode = log_mode
        self.oarm_uid = uid
    
    def initialize_process(self):
        initializedPath_object = LogPathFinder(self.hostname, self.config, self.validation_object)
        try:
            for i in self.config[self.hostname]:
                try:
                    if self.config[self.hostname]["ONMOPAY"] and i == 'ONMOPAY':
                        initializedPath_object.initialize_path(i)
                        if initializedPath_object.onmopay_consumer_log_path_dict:
                            formatter = "#" * 100
                            logging.info('\n')
                            logging.info('%s CONSUMER PATH INITIALIZED \n %s', i, formatter)
                            # logging.info('%s', formatter)
                            for key, value in initializedPath_object.onmopay_consumer_log_path_dict.items():
                                logging.info('%s : %s', key, value)
                        else:
                            logging.info('%s CONSUMER PATH NOT INITIALIZED', i)
                except KeyError as error:
                    logging.info('onmopay CONSUMER process not present in %s.json file, hence processing would not be done for CONSUMER', self.hostname)                              
                except ValueError as error:
                    logging.warning('%s CONSUMER path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["ONMOPAY"] and i == 'ONMOPAY':
                        initializedPath_object.initialize_path(i)
                        if initializedPath_object.onmopay_paycore_log_path_dict:
                            formatter = "#" * 100
                            logging.info('\n')
                            logging.info('%s PAYCORE PATH INITIALIZED \n %s', i, formatter)
                            # logging.info('%s', formatter)
                            for key, value in initializedPath_object.onmopay_paycore_log_path_dict.items():
                                logging.info('%s : %s', key, value)
                        else:
                            logging.info('%s PAYCORE PATH NOT INITIALIZED', i)
                except KeyError as error:
                    logging.info('onmopay PAYCORE process not present in %s.json file, hence processing would not be done for PAYCORE', self.hostname)                              
                except ValueError as error:
                    logging.warning('%s PAYCORE path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["ONMOPAY"] and i == 'ONMOPAY':
                        initializedPath_object.initialize_path(i)
                        if initializedPath_object.onmopay_paycoreWebApi_log_path_dict:
                            formatter = "#" * 100
                            logging.info('\n')
                            logging.info('%s PAYCORE WEBAPI PATH INITIALIZED \n %s', i, formatter)
                            # logging.info('%s', formatter)
                            for key, value in initializedPath_object.onmopay_paycoreWebApi_log_path_dict.items():
                                logging.info('%s : %s', key, value)
                        else:
                            logging.info('%s PAYCORE WEBAPI PATH NOT INITIALIZED', i)
                except KeyError as error:
                    logging.info('onmopay PAYCORE WEBAPI process not present in %s.json file, hence processing would not be done for PAYCORE WEBAPI', self.hostname)                              
                except ValueError as error:
                    logging.warning('%s PAYCORE WEBAPI path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["ONMOPAY"] and i == 'ONMOPAY':
                        initializedPath_object.initialize_path(i)
                        if initializedPath_object.onmopay_callbackDelivery_log_path_dict:
                            formatter = "#" * 100
                            logging.info('\n')
                            logging.info('%s CALLBACK DELIVERY PATH INITIALIZED \n %s', i, formatter)
                            # logging.info('%s', formatter)
                            for key, value in initializedPath_object.onmopay_callbackDelivery_log_path_dict.items():
                                logging.info('%s : %s', key, value)
                        else:
                            logging.info('%s CALLBACK DELIVERY PATH NOT INITIALIZED', i)
                except KeyError as error:
                    logging.info('onmopay CALLBACK DELIVERY process not present in %s.json file, hence processing would not be done for CALLBACK DELIVERY', self.hostname)                              
                except ValueError as error:
                    logging.warning('%s CALLBACK DELIVERY path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["ONMOPAY"] and i == 'ONMOPAY':
                        initializedPath_object.initialize_path(i)
                        if initializedPath_object.onmopay_failedLogProcessor_log_path_dict:
                            formatter = "#" * 100
                            logging.info('\n')
                            logging.info('%s FAILED LOG PROCESSOR PATH INITIALIZED \n %s', i, formatter)
                            # logging.info('%s', formatter)
                            for key, value in initializedPath_object.onmopay_failedLogProcessor_log_path_dict.items():
                                logging.info('%s : %s', key, value)
                        else:
                            logging.info('%s FAILED LOG PROCESSOR PATH NOT INITIALIZED', i)
                except KeyError as error:
                    logging.info('onmopay FAILED LOG PROCESSOR process not present in %s.json file, hence processing would not be done for FAILED LOG PROCESSOR', self.hostname)                              
                except ValueError as error:
                    logging.warning('%s FAILED LOG PROCESSOR path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                    
                try:
                    if self.config[self.hostname]["GRIFF"] and i == 'GRIFF':
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
                    logging.info('\n')
                    logging.info('GRIFF process not present in %s.json file, hence processing would not be done for GRIFF', self.hostname)                             
                except ValueError as error:
                    logging.warning('%s tomcat path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["PACKS"] and i == 'PACKS':
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
                    logging.info('\n')
                    logging.info('PACKS process not present in %s.json file, hence processing would not be done for PACKS', self.hostname)
                except ValueError as error:
                    logging.warning('%s tomcat path not initialized. %s', i, error)
                except Exception as error:
                    logging.warning(error)
                
                try:
                    if self.config[self.hostname]["PRISM"] and i == 'PRISM':
                        if self.config[self.hostname]["PRISM"]["PRISM_TOMCAT"] != "":
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
                                            Hence PRISM_TOMCAT logs will not be initialized and fetched', i, self.hostname
                                        )
                        
                        if self.config[self.hostname]["PRISM"]["PRISM_DEAMON"] != "":
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
                                            Hence PRISM_DEAMON logs will not be initialized and fetched', i, self.hostname
                                        )

                        if self.config[self.hostname]["PRISM"]["PRISM_SMSD"] != "":
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
                                            Hence PRISM_SMSD logs will not be initialized and fetched', i, self.hostname
                                        )
                except KeyError as error:
                    logging.info('\n')
                    logging.info('PRISM process not present in %s.json file, hence processing would not be done for PRISM', self.hostname)
                except ValueError as error:
                    logging.warning('any of the %s path not initialized', i)
                except Exception as error:
                    logging.warning(error)
                    
            logging.info('\n')
            logging.info('log mode: %s', self.log_mode)     
            
            #processor is called
            processor_object = PROCESSOR(initializedPath_object, self.outputDirectory_object, self.validation_object, self.log_mode, self.oarm_uid, self.config)
            processor_object.process()
                
        except KeyError as error:
            logging.exception(error)