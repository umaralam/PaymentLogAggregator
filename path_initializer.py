from datetime import datetime
import logging
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import socket

class LogPathFinder():
    """
    Path finder class
    """
    def __init__(self, hostname, config, validation_object):
        
        self.config = config
        self.validation_object = validation_object
        self.start_date = validation_object.start_date
        self.end_date = validation_object.end_date
        self.hostname = hostname
        self.debugMsisdn = ""
        
        #griff tomcat dictionary object
        self.griff_tomcat_log_path_dict = {}
        self.griff_tomcat_log4j_property_dict = {}
        
        #packs tomcat dictionary object
        self.packs_tomcat_log_path_dict = {}
        self.packs_tomcat_log4j_property_dict = {}
        
        #prism dictionary objects
        self.prism_tomcat_log_path_dict = {}
        self.prism_daemon_log_path_dict = {}
        self.prism_smsd_log_path_dict = {}
        
        #griff catalina home and access path paramter
        self.griff_process_home_directory = "griff_process_home_directory"
        self.griff_tomcat_access_path = "griff_tomcat_access_path"
        
        
        #packs catalina home and access path paramter
        self.packs_process_home_directory = "packs_process_home_directory"
        self.packs_tomcat_access_path = "packs_tomcat_access_path"
        
        #prism catalina home and access path paramter, tlog , req-resp path parameters
        self.prism_process_home_directory = "prism_process_home_directory"
        self.prism_tomcat_access_path = "prism_tomcat_access_path"
        self.prism_tomcat_tlog_path = "prism_tomcat_tlog_path"
        self.prism_daemon_tlog_path = "prism_daemon_tlog_path"
        self.prism_smsd_tlog_path = "prism_smsd_tlog_path"
        self.prism_tomcat_generic_http_handler_req_resp_path = "prism_tomcat_generic_http_handler_req_resp_path"
        self.prism_tomcat_generic_soap_handler_req_resp_path = "prism_tomcat_generic_soap_handler_req_resp_path"
        self.prism_tomcat_callbackV2_req_resp_path = "prism_tomcat_callbackV2_req_resp_path"
        self.prism_tomcat_req_resp_path = "prism_tomcat_req_resp_path"
        self.prism_tomcat_perf_log_path = "prism_tomcat_perf_log_path"
        self.prism_daemon_generic_http_handler_req_resp_path = "prism_daemon_generic_http_handler_req_resp_path"
        self.prism_daemon_generic_soap_handler_req_resp_path = "prism_daemon_generic_soap_handler_req_resp_path"
        self.prism_daemon_callbackV2_req_resp_path = "prism_daemon_callbackV2_req_resp_path"
        self.prism_daemon_req_resp_path = "prism_daemon_req_resp_path"
        self.prism_daemon_perf_log_path = "prism_daemon_perf_log_path"
        
        #boolean path paramters
        self.is_griff_access_path = False
        self.is_packs_access_path = False
        self.is_routing_success = False
        self.is_prism_access_path = False
        self.is_debug_msisdn = False
        
        
    def parse_transaction_logging(self, process_name):
        """
        Parse log paths
        """
        search_date = datetime.strftime(self.start_date, "yyyy-MM-dd")
        pname = process_name
        
        if pname == 'GRIFF':
            try:
                if self.config[self.hostname][pname]['GRIFF_TOMCAT']['ACCESS_LOG_PATH'] != "":
                    self.griff_tomcat_log_path_dict[self.griff_tomcat_access_path] = self.config[self.hostname][pname]['GRIFF_TOMCAT']['ACCESS_LOG_PATH']
                    self.is_griff_access_path = True
                else:
                    logging.info('%s access log path not available in common.json file.'\
                                    'Hence access log will not be fetched.', pname)
            except KeyError as error:
                # logging.error('Eigther %s/GRIFF_TOMCAT/ACCESS_LOG key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence access log will not be fetched.')
        
            try:
                if self.config[self.hostname][pname]['GRIFF_TOMCAT']['LOG4J2_XML'] != "":
                    log4j2_path = self.config[self.hostname][pname]['GRIFF_TOMCAT']['LOG4J2_XML']
                    self.parse_log4j_property(pname, log4j2_path)
                else:
                    logging.error('%s tomcat LOG4J2_XML not present in common.json file', pname)
                    logging.error('Hence LOG4J2_XML log will not be fetched for parsing and initializing logs path.')
            except KeyError as error:
                # logging.error('Eigther %s/GRIFF_TOMCAT/LOG4J2_XML key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence LOG4J2_XML log will not be fetched for parsing and initializing logs path.')
            
            try:
                if self.config[self.hostname][pname]['GRIFF_TOMCAT']['PROCESS_HOME_DIR'] != "":
                    self.griff_tomcat_log_path_dict[self.griff_process_home_directory] = self.config[self.hostname][pname]['GRIFF_TOMCAT']['PROCESS_HOME_DIR']
                    
                    if self.griff_tomcat_log4j_property_dict:  
                        for key, value in self.griff_tomcat_log4j_property_dict.items():    
                            if (
                                    str(value).startswith('${sys:catalina.home}')\
                                    or str(value).startswith('%d{yyyy-MM-dd}-%i')\
                                ):
                                
                                replacedValue = str(value).replace("${sys:catalina.home}",\
                                                self.griff_tomcat_log_path_dict[self.griff_process_home_directory])\
                                                .replace("%d{yyyy-MM-dd}-%i", f'{search_date}-*')
                                logging.info('replaced value: %s', replacedValue)
                                self.griff_tomcat_log4j_property_dict[key] = replacedValue
                        
                        logging.info('\n')
                        formatter = "#" * 100
                        logging.info('%s TOMCAT LOG4J2 PROPERTY INITIALIZED \n %s', pname, formatter)
                        # logging.info('%s', formatter)
                        
                        for key, value in self.griff_tomcat_log4j_property_dict.items():
                            logging.info('%s : %s', key, value)
                        
                        logging.info('\n')
                        
                        self.is_msisdn_in_debugMsisdn_list(pname)
                        self.parse_logger(pname, log4j2_path)
                    else:
                        logging.info('Properties not defined in %s log4j2.xml,'\
                                        'We will try to fetch appender path without place holder.', pname)
                else:
                    logging.error('%s tomcat TRANS_BASE_DIR path not present in common.json file.'\
                                    'Hence substitution in log4j2.xml for catalina home will not be done.', pname)
            except KeyError as error:
                # logging.error('Eigther %s/GRIFF_TOMCAT/PROCESS_HOME_DIR key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence catalina home path cannot be used for substitution in log4j property.')
            
        elif pname == 'PACKS':
            try:
                if self.config[self.hostname][pname]['PACKS_TOMCAT']['ACCESS_LOG_PATH'] != "":
                    self.packs_tomcat_log_path_dict[self.packs_tomcat_access_path] = self.config[self.hostname][pname]['PACKS_TOMCAT']['ACCESS_LOG_PATH']
                    self.is_packs_access_path = True
                else:
                    logging.info('%s access log path not available in common.json file.'\
                                    'Hence access log will not be fetched.', pname)
            except KeyError as error:
                # logging.error('Eigther %s/PACKS_TOMCAT/ACCESS_LOG key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence access log will not be fetched.')

            try:
                if self.config[self.hostname][pname]['PACKS_TOMCAT']['LOG4J2_XML'] != "":
                    log4j2_path = self.config[self.hostname][pname]['PACKS_TOMCAT']['LOG4J2_XML']
                    self.parse_log4j_property(pname, log4j2_path)
                else:
                    logging.error('%s tomcat LOG4J2_XML path not present in common.json file', pname)
                    logging.error('Hence LOG4J2_XML log will not be fetched for parsing and initializing logs path.')
            except KeyError as error:
                # logging.error('Eigther %s/PACKS_TOMCAT/LOG4J2_XML key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence LOG4J2_XML log will not be fetched for parsing and initializing logs path.')
            
            try:   
                if self.config[self.hostname][pname]['PACKS_TOMCAT']['PROCESS_HOME_DIR'] != "":
                    self.packs_tomcat_log_path_dict[self.packs_process_home_directory] = self.config[self.hostname][pname]['PACKS_TOMCAT']['PROCESS_HOME_DIR']
                    
                    if self.packs_tomcat_log4j_property_dict:
                        for key, value in self.packs_tomcat_log4j_property_dict.items():    
                            if (
                                    str(value).startswith('${sys:catalina.home}')\
                                    or str(value).startswith('%d{yyyy-MM-dd}-%i')\
                                    or str(value).startswith('${sys.log.backupBasePath}')\
                                    or str(value).startswith('${log.backupPath}')
                                ):
                                
                                replacedValue = str(value).replace("${sys:catalina.home}",\
                                                self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                .replace("%d{yyyy-MM-dd}-%i", f'{search_date}-*')\
                                                .replace("${sys.log.backupBasePath}",\
                                                self.packs_tomcat_log4j_property_dict['sys.log.backupBasePath'])\
                                                .replace("${log.backupPath}",\
                                                self.packs_tomcat_log4j_property_dict['log.backupPath'])
                                self.packs_tomcat_log4j_property_dict[key] = replacedValue
                        
                        logging.info('\n')
                        formatter = "#" * 100
                        logging.info('%s TOMCAT LOG4J2 PROPERTY INITIALIZED \n %s', pname, formatter)
                        # logging.info('%s', formatter)
                        
                        for key, value in self.packs_tomcat_log4j_property_dict.items():
                            logging.info('%s : %s', key, value)
                        
                        logging.info('\n')
                        
                        self.is_msisdn_in_debugMsisdn_list(pname)
                        self.parse_logger(pname, log4j2_path)
            
                    else:
                        logging.info('Properties not defined in %s log4j2.xml,'\
                                        'We will try to fetch appender path without place holder.', pname)
                else:
                    logging.info('%s tomcat process home directory path not present in common.json file.'\
                                    'Hence substitution in log4j2.xml for catalina home will not be done.', pname)
            except KeyError as error:
                # logging.error('Eigther %s/PACKS_TOMCAT/PROCESS_HOME_DIR key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence catalina home path cannot be used for substitution in log4j property.')
                
        elif pname == "PRISM":
            hostname = socket.gethostname()
            try:
                if self.config[hostname]['PRISM']['PRISM_TOMCAT']['ACCESS_LOG_PATH'] != "":
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_access_path] = self.config[hostname]['PRISM']['PRISM_TOMCAT']['ACCESS_LOG_PATH']
                    self.is_prism_access_path = True
                else:
                    logging.info('%s access log path not available in common.json file.'\
                                    'Hence access log will not be fetched.', pname)
            except KeyError as error:
                # logging.error('Eigther %s/GRIFF_TOMCAT/ACCESS_LOG key not present in common.json file.'\
                #                 'Please check with OARM team', pname)
                logging.exception(error)
                logging.error('Hence %s access log will not be fetched.', pname) 
            
            try:
                if self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR'] != "":
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_tlog_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/BILLING_REALTIME"
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_generic_http_handler_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/REQUEST_RESPONSE_GENERIC_HTTP"
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_generic_soap_handler_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/REQUEST_RESPONSE"
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_callbackV2_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/CBCK-V2-REQ-RESPONSE"
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/REQUEST_LOG"
                    self.prism_tomcat_log_path_dict[self.prism_tomcat_perf_log_path] = f"{self.config[hostname]['PRISM']['PRISM_TOMCAT']['TRANS_BASE_DIR']}/TLOG/PERF"
                    # self.is_tomcat_tlog_path = True
                else:
                    logging.error('%s tomcat TRANS_BASE_DIR path not available in %s file, hence tomcat tlog path will not be processed', pname, hostname) 
                
                if self.config[hostname]['PRISM']['PRISM_TOMCAT']['LOG4J2_XML'] != "":
                    log4j2_path = self.config[hostname]['PRISM']['PRISM_TOMCAT']['LOG4J2_XML']
                    self.parse_logger(pname, log4j2_path, "PRISM_TOMCAT")
                else:
                    logging.error('%s tomcat LOG4J2_XML path not present in common.json file', pname)
                    logging.error('Hence %s LOG4J2_XML log will not be fetched for parsing and initializing logs path.', pname)
            
                if self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR'] != "":
                    self.prism_daemon_log_path_dict[self.prism_daemon_tlog_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/BILLING"
                    self.prism_daemon_log_path_dict[self.prism_daemon_generic_http_handler_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/REQUEST_RESPONSE_GENERIC_HTTP"
                    self.prism_daemon_log_path_dict[self.prism_daemon_generic_soap_handler_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/REQUEST_RESPONSE"
                    self.prism_daemon_log_path_dict[self.prism_daemon_callbackV2_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/CBCK-V2-REQ-RESPONSE"
                    self.prism_daemon_log_path_dict[self.prism_daemon_req_resp_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/REQUEST_LOG"
                    self.prism_daemon_log_path_dict[self.prism_daemon_perf_log_path] = f"{self.config[hostname]['PRISM']['PRISM_DEAMON']['TRANS_BASE_DIR']}/TLOG/PERF"
                    # self.is_tomcat_tlog_path = True
                else:
                    logging.error('%s daemon TRANS_BASE_DIR path not available in %s file, hence tomcat tlog will not be fetched', pname, hostname) 
                
                if self.config[hostname]['PRISM']['PRISM_DEAMON']['LOG4J2_XML'] != "":
                    log4j2_path = self.config[hostname]['PRISM']['PRISM_DEAMON']['LOG4J2_XML']
                    self.parse_logger(pname, log4j2_path, "PRISM_DEAMON")
                else:
                    logging.error('%s prismD LOG4J2_XML path not present in common.json file', pname)
                    logging.error('Hence %s LOG4J2_XML log will not be fetched for parsing and initializing logs path.', pname)
                
                if self.config[hostname]['PRISM']['PRISM_SMSD']['TRANS_BASE_DIR'] != "":
                    self.prism_smsd_log_path_dict[self.prism_smsd_tlog_path] = f"{self.config[hostname]['PRISM']['PRISM_SMSD']['TRANS_BASE_DIR']}/TLOG/SMS"
                    # self.is_tomcat_tlog_path = True
                else:
                    logging.error('%s smsd TRANS_BASE_DIR path not available in %s file, hence tomcat tlog will not be fetched', pname, hostname) 
                
                if self.config[hostname]['PRISM']['PRISM_SMSD']['LOG4J2_XML'] != "":
                    log4j2_path = self.config[hostname]['PRISM']['PRISM_SMSD']['LOG4J2_XML']
                    self.parse_logger(pname, log4j2_path, "PRISM_SMSD")
                else:
                    logging.error('%s prismD LOG4J2_XML path not present in common.json file', pname)
                    logging.error('Hence %s LOG4J2_XML log will not be fetched for parsing and initializing logs path.', pname)
                    
            except KeyError as error:
                logging.exception(error)
                # logging.error('Hence LOG4J2_XML log will not be fetched for parsing and initializing logs path.')
            
                
    def parse_log4j_property(self, pname, log4j):
        """
        Parse log4j2 property
        """
        logging.info('\n')
        logging.info('process name: %s and log4j path: %s', pname, log4j)
        
        tree = ET.parse(log4j)
                
        if pname == 'GRIFF':
            try:
                for prop in tree.findall('./Properties/Property'):
                    if (
                            prop.attrib.get('name') == 'log.basePath'\
                            or prop.attrib.get('name') == 'log.backupBasePath'\
                            or prop.attrib.get('name') == 'log.rollover.datePattern'\
                            or prop.attrib.get('name') == 'log.rollover.extension'
                        ):
                        
                        self.griff_tomcat_log4j_property_dict[prop.attrib.get('name')] = prop.text
                
            except ET.ParseError as ex:
                logging.debug(ex)
                
        elif pname == 'PACKS':
            try:
                # root = tree.getroot()
                # root.tag = self.remove_namespace_prefix(root.tag)
                # for child in root:
                #     child.tag = self.remove_namespace_prefix(child.tag)

                #     if child.tag == "Properties":
                #         for prop in child:
                #             prop.tag = self.remove_namespace_prefix(prop.tag)
                #             logging.info('property tag: %s', prop)
                for prop in tree.findall('./Properties/Property'):
                    if (
                            prop.attrib.get('name') == 'log.path'\
                            or prop.attrib.get('name') == 'log.output'\
                            or prop.attrib.get('name') == 'sys.log.backupBasePath'\
                            or prop.attrib.get('name') == 'log.backupPath'\
                            or prop.attrib.get('name') == 'log.rollover.basePath'\
                            or prop.attrib.get('name') == 'log.rollover.datePattern'\
                            or prop.attrib.get('name') == 'log.rollover.extension'
                        ):
                        
                        self.packs_tomcat_log4j_property_dict[prop.attrib.get('name')] = prop.text
                        
            except ET.ParseError as ex:
                logging.debug(ex)
    
    def parse_logger(self, pname, log4j2_path, sub_process=None):
        """
        Logger reference call to appender
        """
        try:
            tree = ET.parse(log4j2_path)
                
            if pname == 'GRIFF':
                for data in tree.findall('./Loggers/AsyncLogger'):
                    self.parse_appender(data, tree, pname)
            
            elif pname == 'PACKS':
                # root = tree.getroot()
                # root.tag = self.remove_namespace_prefix(root.tag)
                # for child in root:
                #     child.tag = self.remove_namespace_prefix(child.tag)
                #     if child.tag == "Loggers":
                #         for logger in child:
                #             logger.tag = self.remove_namespace_prefix(logger.tag)
                for data in tree.findall('./Loggers/Logger'):
                    self.parse_appender(data, tree, pname)
            
            elif pname == 'PRISM' and sub_process != None:
                for data in tree.findall('./Loggers/Logger'):
                    self.parse_appender(data, tree, pname, sub_process)
                
                for data in tree.findall('./Loggers/Root'):
                    self.parse_appender(data, tree, pname, sub_process)
            
        except ET.ParseError as ex:
            logging.debug(ex)
                  
    def parse_appender(self, data, tree, pname, sub_process=None):
        """
        Parse appender for loggers reference
        """
        try:
            for logger in data.findall('AppenderRef'):
                if pname == 'PACKS':
                    logger_ref = str(logger.attrib.get('ref'))\
                            .replace("${log.output}", self.packs_tomcat_log4j_property_dict['log.output'])
                
                elif pname == 'GRIFF':
                    logger_ref = str(logger.attrib.get('ref'))
                
                elif pname == 'PRISM' and sub_process != None:
                    logger_ref = str(logger.attrib.get('ref'))
                   
                for routing in tree.findall('./Appenders/Routing'):
                    if logger_ref == str(routing.attrib.get('name')):
                        for routes in tree.findall('./Appenders/Routing/Routes'):
                            #call to routing for re-routing the references
                            self.parse_routing_appender(routes, tree, pname, logger_ref, routing, sub_process)
                            
                        if self.is_routing_success:
                            break  
                else:            
                    for appender in tree.findall('./Appenders/RollingRandomAccessFile'):
                        if logger_ref == str(appender.attrib.get('name')):
                            if (
                                    str(appender.attrib.get('fileName')).startswith('${log.basePath}')\
                                    or str(appender.attrib.get('fileName')).startswith('${sys:catalina.home}')\
                                    or str(appender.attrib.get('fileName')).startswith('${log.path}')
                                ):
                                if pname == 'GRIFF':
                                    replacedValue = str(appender.attrib.get('fileName'))\
                                                    .replace("${log.basePath}", self.griff_tomcat_log4j_property_dict['log.basePath'])\
                                                    .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])
                                
                                    self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_log"] = replacedValue
                                
                                elif pname == 'PACKS':
                                    replacedValue = str(appender.attrib.get('fileName'))\
                                                    .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                    .replace("${log.path}", self.packs_tomcat_log4j_property_dict['log.path'])
                                
                                    self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_log"] = replacedValue
                                    
                                if (
                                        str(appender.attrib.get('filePattern')).startswith('${log.backupBasePath}')\
                                        or str(appender.attrib.get('filePattern')).startswith('${sys:catalina.home}')\
                                        or str(appender.attrib.get('filePattern')).startswith('${log.rollover.basePath}')
                                    ):
                                    
                                    if pname == 'GRIFF':
                                        replacedValue = str(appender.attrib.get('filePattern'))\
                                                .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])\
                                                .replace("${log.backupBasePath}", self.griff_tomcat_log4j_property_dict['log.backupBasePath'])\
                                                .replace("${log.rollover.datePattern}", self.griff_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                .replace("${log.rollover.extension}", self.griff_tomcat_log4j_property_dict['log.rollover.extension'])
                                        
                                        self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_backup_log"] = replacedValue
                                        
                                    elif pname == 'PACKS': 
                                        replacedValue = str(appender.attrib.get('filePattern'))\
                                                .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                .replace("${log.backupBasePath}", self.packs_tomcat_log4j_property_dict['sys.log.backupBasePath'])\
                                                .replace("${log.rollover.datePattern}", self.packs_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                .replace("${log.rollover.extension}", self.packs_tomcat_log4j_property_dict['log.rollover.extension'])\
                                                .replace("${log.rollover.basePath}", self.packs_tomcat_log4j_property_dict['log.rollover.basePath'])
                                        
                                        self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_backup_log"] = replacedValue   
                                else:
                                    if pname == 'GRIFF':
                                        self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_backup_log"] = appender.attrib.get('filePattern')
                                    elif pname == 'PACKS':
                                        self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_backup_log"] = appender.attrib.get('filePattern')
                                        
                            else:
                                if pname == 'GRIFF':
                                    self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_log"] = appender.attrib.get('fileName')
                                elif pname == 'PACKS':
                                    self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_log"] = appender.attrib.get('fileName')
                                    
                            break
                    else:
                        for appender in tree.findall('./Appenders/RollingFile'):
                            if logger_ref == str(appender.attrib.get('name')):
                                if (
                                        str(appender.attrib.get('fileName')).startswith('${log.basePath}')\
                                        or str(appender.attrib.get('fileName')).startswith('${sys:catalina.home}')\
                                        or str(appender.attrib.get('fileName')).startswith('${log.path}')
                                    ):
                                    if pname == 'GRIFF':
                                        replacedValue = str(appender.attrib.get('fileName'))\
                                                        .replace("${log.basePath}", self.griff_tomcat_log4j_property_dict['log.basePath'])\
                                                        .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])
                                    
                                        self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_log"] = replacedValue
                                    
                                    elif pname == 'PACKS':
                                        replacedValue = str(appender.attrib.get('fileName'))\
                                                        .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                        .replace("${log.path}", self.packs_tomcat_log4j_property_dict['log.path'])
                                    
                                        self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_log"] = replacedValue
                                    
                                    if (
                                            str(appender.attrib.get('filePattern')).startswith('${log.backupBasePath}')\
                                            or str(appender.attrib.get('filePattern')).startswith('${sys:catalina.home}')\
                                            or str(appender.attrib.get('filePattern')).startswith('${log.rollover.basePath}')
                                        ):
                                        
                                        if pname == 'GRIFF':
                                            replacedValue = str(appender.attrib.get('filePattern'))\
                                                    .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])\
                                                    .replace("${log.backupBasePath}", self.griff_tomcat_log4j_property_dict['log.backupBasePath'])\
                                                    .replace("${log.rollover.datePattern}", self.griff_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                    .replace("${log.rollover.extension}", self.griff_tomcat_log4j_property_dict['log.rollover.extension'])
                                            
                                            self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_backup_log"] = replacedValue
                                        
                                        elif pname == 'PACKS':
                                            replacedValue = str(appender.attrib.get('filePattern'))\
                                                    .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                    .replace("${log.backupBasePath}", self.packs_tomcat_log4j_property_dict['sys.log.backupBasePath'])\
                                                    .replace("${log.rollover.datePattern}", self.packs_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                    .replace("${log.rollover.extension}", self.packs_tomcat_log4j_property_dict['log.rollover.extension'])\
                                                    .replace("${log.rollover.basePath}", self.packs_tomcat_log4j_property_dict['log.rollover.basePath'])
                                                    
                                            self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_backup_log"] = replacedValue
                                            
                                    else:
                                        if pname == 'GRIFF':
                                            self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_backup_log"] = appender.attrib.get('filePattern')
                                        elif pname == 'PACKS':
                                            self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_backup_log"] = appender.attrib.get('filePattern')
                                else:
                                    if pname == 'GRIFF':
                                        self.griff_tomcat_log_path_dict[f"griff_{logger_ref}_log"] = appender.attrib.get('fileName')
                                    
                                    elif pname == 'PACKS':
                                        self.packs_tomcat_log_path_dict[f"packs_{logger_ref}_log"] = appender.attrib.get('fileName')
                                    
                                    elif pname == 'PRISM' and sub_process != None:
                                        yearAndmonth = datetime.strftime(self.start_date, 'yyyy-MM')
                                        search_date = datetime.strftime(self.start_date, "yyyy-MM-dd")
                                        
                                        replacedValue = str(appender.attrib.get('filePattern'))\
                                                            .replace("$${date:yyyy-MM}", f'{yearAndmonth}')\
                                                            .replace("%d{yyyy-MM-dd.HH}-%i", f'{search_date}*')
                                        
                                        if sub_process == 'PRISM_TOMCAT':
                                            self.prism_tomcat_log_path_dict[f"prism_tomcat_{logger_ref}_log"] = appender.attrib.get('fileName')
                                            self.prism_tomcat_log_path_dict[f"prism_tomcat_{logger_ref}_backup_log"] = replacedValue
                                        
                                        elif sub_process == 'PRISM_DEAMON':
                                            self.prism_daemon_log_path_dict[f"prism_daemon_{logger_ref}_log"] = appender.attrib.get('fileName')
                                            self.prism_daemon_log_path_dict[f"prism_daemon_{logger_ref}_backup_log"] = replacedValue
                                        
                                        elif sub_process == 'PRISM_SMSD':
                                            self.prism_smsd_log_path_dict[f"prism_smsd_{logger_ref}_log"] = appender.attrib.get('fileName')
                                            self.prism_smsd_log_path_dict[f"prism_smsd_{logger_ref}_backup_log"] = replacedValue
                                        
                                break
                        else:
                            logging.info('No Appender defined for the logger: %s', logger_ref)
                
        except ET.ParseError as ex:
            logging.debug(ex)
        
    def parse_routing_appender(self, data, tree, pname, logger_ref, routing, sub_process=None):
        """
        Re-route for logger reference and parse appender
        """
        try:
            for route in data.findall('Route'):
                if pname != 'PRISM':
                    if self.is_debug_msisdn:
                        for rollingFile in route.findall('RollingFile'):
                            if (
                                    str(rollingFile.attrib.get('fileName')).startswith('${log.basePath}')\
                                    or str(rollingFile.attrib.get('fileName')).startswith('${log.path}')
                                ):
                                    
                                if pname == "GRIFF":
                                    replacedValue = str(rollingFile.attrib.get('fileName'))\
                                                    .replace("${log.basePath}", self.griff_tomcat_log4j_property_dict['log.basePath'])\
                                                    .replace("${ctx:debugmsisdn}", self.debugMsisdn)
                                    
                                    self.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"] = replacedValue
                            
                                elif pname == 'PACKS':
                                    replacedValue = str(rollingFile.attrib.get('fileName'))\
                                                    .replace("${log.path}", self.packs_tomcat_log4j_property_dict['log.path'])\
                                                    .replace("${ctx:DEBUGMSISDN}", self.debugMsisdn)
                                    
                                    self.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"] = replacedValue
                                
                                if (
                                        str(rollingFile.attrib.get('filePattern')).startswith('${log.backupBasePath}')\
                                        or str(rollingFile.attrib.get('filePattern')).startswith('${log.rollover.basePath}')
                                    ):
                                    
                                    if pname == 'GRIFF':
                                        replacedValue = str(rollingFile.attrib.get('filePattern'))\
                                                        .replace("${log.backupBasePath}", self.griff_tomcat_log4j_property_dict['log.backupBasePath'])\
                                                        .replace("${ctx:debugmsisdn}", self.debugMsisdn)\
                                                        .replace("${log.rollover.datePattern}", self.griff_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                        .replace("${log.rollover.extension}", self.griff_tomcat_log4j_property_dict['log.rollover.extension'])
                                        
                                        self.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_backup_log"] = replacedValue
                                    
                                    elif pname == 'PACKS':
                                        replacedValue = str(rollingFile.attrib.get('filePattern'))\
                                                        .replace("${log.rollover.basePath}", self.packs_tomcat_log4j_property_dict['log.rollover.basePath'])\
                                                        .replace("${ctx:DEBUGMSISDN}", self.debugMsisdn)\
                                                        .replace("${log.rollover.datePattern}", self.packs_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                        .replace("${log.rollover.extension}", self.packs_tomcat_log4j_property_dict['log.rollover.extension'])\
                                        
                                        self.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_backup_log"] = replacedValue
                                else:
                                    if pname == 'GRIFF':
                                        self.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_backup_log"] = rollingFile.attrib.get('filePattern')   
                                    elif pname == 'PACKS':
                                        self.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_backup_log"] = rollingFile.attrib.get('filePattern')   
                            else:
                                if pname == 'GRIFF':
                                    self.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"] = rollingFile.attrib.get('fileName')
                                elif pname == 'PACKS':
                                    self.packs_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"] = rollingFile.attrib.get('fileName')
                    
                    for appender in tree.findall('./Appenders/RollingRandomAccessFile'):
                        if route.attrib.get('ref') == appender.attrib.get('name'):
                            if (
                                    str(appender.attrib.get('fileName')).startswith('${log.basePath}')\
                                    or str(appender.attrib.get('fileName')).startswith('${sys:catalina.home}')\
                                    or str(appender.attrib.get('fileName')).startswith('${log.path}')
                                ):
                                
                                if pname == 'GRIFF':
                                    replacedValue = str(appender.attrib.get('fileName'))\
                                                    .replace("${log.basePath}", self.griff_tomcat_log4j_property_dict['log.basePath'])\
                                                    .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])
                                    
                                    self.griff_tomcat_log_path_dict[f"griff_{route.attrib.get('ref')}_log"] = replacedValue
                                
                                elif pname == 'PACKS':
                                    replacedValue = str(appender.attrib.get('fileName'))\
                                                    .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                    .replace("${log.path}", self.packs_tomcat_log4j_property_dict['log.path'])
                                    
                                    self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_log"] = replacedValue
                                    
                                if (
                                        str(appender.attrib.get('filePattern')).startswith('${log.backupBasePath}')\
                                        or str(appender.attrib.get('filePattern')).startswith('${sys:catalina.home}')\
                                        or str(appender.attrib.get('filePattern')).startswith('${log.rollover.basePath}')
                                    ):
                                    
                                    if pname == 'GRIFF':
                                        replacedValue = str(appender.attrib.get('filePattern'))\
                                                        .replace("${log.backupBasePath}", self.griff_tomcat_log4j_property_dict['log.backupBasePath'])\
                                                        .replace("${log.rollover.datePattern}", self.griff_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                        .replace("${log.rollover.extension}", self.griff_tomcat_log4j_property_dict['log.rollover.extension'])\
                                                        .replace("${sys:catalina.home}", self.griff_tomcat_log_path_dict[self.griff_process_home_directory])
                                        
                                        self.griff_tomcat_log_path_dict[f"griff_{route.attrib.get('ref')}_backup_log"] = replacedValue
                                    
                                    elif pname == 'PACKS':
                                        replacedValue = str(appender.attrib.get('filePattern'))\
                                                        .replace("${log.backupBasePath}", self.packs_tomcat_log4j_property_dict['sys.log.backupBasePath'])\
                                                        .replace("${log.rollover.datePattern}", self.packs_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                        .replace("${log.rollover.extension}", self.packs_tomcat_log4j_property_dict['log.rollover.extension'])\
                                                        .replace("${sys:catalina.home}", self.packs_tomcat_log_path_dict[self.packs_process_home_directory])\
                                                        .replace("${log.rollover.basePath}", self.packs_tomcat_log4j_property_dict['log.rollover.basePath'])\
                                        
                                        self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_backup_log"] = replacedValue
                                
                                else:
                                    if pname == 'GRIFF':
                                        self.griff_tomcat_log_path_dict[f"griff_{route.attrib.get('ref')}_backup_log"] = appender.attrib.get('filePattern')   
                                    elif pname == 'PACKS':
                                        self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_backup_log"] = appender.attrib.get('filePattern')   
                            else:
                                if pname == 'GRIFF':
                                    self.griff_tomcat_log_path_dict[f"griff_{route.attrib.get('ref')}_log"] = appender.attrib.get('fileName')
                                elif pname == 'PACKS':
                                    self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_log"] = appender.attrib.get('fileName')
                
                    else:
                        for appender in tree.findall('./Appenders/RollingFile'):
                            if route.attrib.get('ref') == appender.attrib.get('name'):
                                if (str(appender.attrib.get('fileName')).startswith('${log.path}')):
                                    
                                    if pname == 'PACKS':
                                        replacedValue = str(appender.attrib.get('fileName'))\
                                                        .replace("${log.path}", self.packs_tomcat_log4j_property_dict['log.path'])
                                        
                                        self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_log"] = replacedValue
                                        
                                    if (str(appender.attrib.get('filePattern')).startswith('${log.rollover.basePath}')):
                                    
                                        if pname == 'PACKS':
                                            replacedValue = str(appender.attrib.get('filePattern'))\
                                                            .replace("${log.rollover.datePattern}", self.packs_tomcat_log4j_property_dict['log.rollover.datePattern'])\
                                                            .replace("${log.rollover.extension}", self.packs_tomcat_log4j_property_dict['log.rollover.extension'])\
                                                            .replace("${log.rollover.basePath}", self.packs_tomcat_log4j_property_dict['log.rollover.basePath'])\
                                            
                                            self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_backup_log"] = replacedValue
                                    
                                    else:  
                                        if pname == 'PACKS':
                                            self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_backup_log"] = appender.attrib.get('filePattern')   
                                else:
                                    if pname == 'PACKS':
                                        self.packs_tomcat_log_path_dict[f"packs_{route.attrib.get('ref')}_log"] = appender.attrib.get('fileName')
                        else:
                            pass
                else:
                    self.reinitialize_is_debug_msisdn()
                    
                    if route.attrib.get('key') == f'TEST_{self.validation_object.fmsisdn}' and logger_ref == str(routing.attrib.get('name')):
                        for file in route.findall('File'):
                            replacedValue = str(file.attrib.get('fileName'))\
                                                .replace("${ctx:SUB_ID}", f"{route.attrib.get('key')}")
                                                        
                        if sub_process == "PRISM_TOMCAT":
                            self.prism_tomcat_log_path_dict[f"prism_tomcat_{route.attrib.get('key')}_log"] = replacedValue
                            break
                        
                        elif sub_process == "PRISM_DEAMON":
                            self.prism_daemon_log_path_dict[f"prism_daemon_{route.attrib.get('key')}_log"] = replacedValue
                            break
                        self.debugMsisdn = True
                    
                    elif route.attrib.get('key') == 'PROCESSOR_99' and logger_ref == str(routing.attrib.get('name')):
                        for file in route.findall('File'):
                            replacedValue = str(file.attrib.get('fileName'))\
                                                .replace("${ctx:QUEUE_ID}", f"{route.attrib.get('key')}")
                                                        
                        if sub_process == "PRISM_TOMCAT":
                            self.prism_tomcat_log_path_dict[f"prism_tomcat_{route.attrib.get('key')}_log"] = replacedValue
                            break
                        elif sub_process == "PRISM_DEAMON":
                            self.prism_daemon_log_path_dict[f"prism_daemon_{route.attrib.get('key')}_log"] = replacedValue
                            break
                        elif sub_process == "PRISM_SMSD":
                            self.prism_smsd_log_path_dict[f"prism_smsd_{route.attrib.get('key')}_log"] = replacedValue
                            break
                    self.is_routing_success = True
                    
        except ET.ParseError as ex:
            logging.debug(ex)
    
    def is_msisdn_in_debugMsisdn_list(self, pname):
        #check and fetch debug msisdn log path
        self.reinitialize_is_debug_msisdn()
        
        if pname == "GRIFF":
            if self.griff_tomcat_log_path_dict[self.griff_process_home_directory]:
                property_directory = f"{self.griff_tomcat_log_path_dict[self.griff_process_home_directory]}/conf/griff/resources"
                path = Path(f"{property_directory}/service.properties")
                
        elif pname == "PACKS":
            if self.packs_tomcat_log_path_dict[self.packs_process_home_directory]:
                property_directory = f"{self.packs_tomcat_log_path_dict[self.packs_process_home_directory]}/conf/packs"
                path = Path(f"{property_directory}/packs.properties")
        
        with open(path) as property:
            if pname == "GRIFF":
                DEBUG_MSISDN_LIST = [data.split("=")[1].split("|") for data in property.readlines() if re.search("DEBUG_MSISDN_LIST",data, re.DOTALL)]
            elif pname == "PACKS":
                DEBUG_MSISDN_LIST = [data.split("=")[1].split(",") for data in property.readlines() if re.search("debug_msisdn_list",data, re.DOTALL)]
            
            logging.info('debug msisdn list= %s', DEBUG_MSISDN_LIST)
            for mdn in DEBUG_MSISDN_LIST:
                for msisdn in mdn:
                    if self.validation_object.fmsisdn in msisdn:
                        self.debugMsisdn = msisdn.strip()
                        self.is_debug_msisdn = True
                        logging.info('%s present in %s debug msisdn list :debug msisdn=%s', self.validation_object.fmsisdn, pname, self.debugMsisdn)
                        
                        # if pname == "GRIFF":
                        #     self.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"] = f'{str(self.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"]).split(".")[0]}'+f'-{debugMsisdn}.log'
                        # elif pname == "PACKS":
                        #     self.griff_tomcat_log_path_dict["packs_DEBUGMSISDN_LOG"] = f'{str(self.griff_tomcat_log_path_dict["griff_GRIFFORIGINAL_log"]).split(".")[0]}'+f'-{debugMsisdn}.log'
    
    
    def remove_namespace_prefix(self, tag):
        # Define a function to remove the namespace prefix from element tags
        return tag.split('}')[-1]
    
    def reinitialize_is_debug_msisdn(self):
        self.is_debug_msisdn = False
        
    def initialize_path(self, section):
            """
            Initialize tomcat path.
            """
            try:
                self.parse_transaction_logging(section)
            except ValueError as error:
                raise ValueError(error)
            except Exception as error:
                raise