from datetime import datetime
import logging
import xml.etree.ElementTree as ET

class LogPathFinder():
    """
    Path finder class
    """
    def __init__(self, hostname, config, input_date):
        
        self.config = config
        self.input_date = input_date
        self.hostname = hostname
        
        #griff tomcat dictionary object
        self.griff_tomcat_log_path_dict = {}
        self.griff_tomcat_log4j_property_dict = {}
        
        #packs tomcat dictionary object
        self.packs_tomcat_log_path_dict = {}
        self.packs_tomcat_log4j_property_dict = {}
        
        #griff catalina home and access path paramter
        self.griff_process_home_directory = "griff_process_home_directory"
        self.griff_tomcat_access_path = "griff_tomcat_access_path"
        
        #griff catalina home and access path paramter
        self.packs_process_home_directory = "packs_process_home_directory"
        self.packs_tomcat_access_path = "packs_tomcat_access_path"
        
        #boolean path paramters
        self.is_griff_access_path = False
        self.is_packs_access_path = False
        self.is_routing_success = False
        
    def parse_transaction_logging(self, process_name):
        """
        Parse log paths
        """
        search_date = datetime.strftime(datetime.strptime(self.input_date, "%Y%m%d"), "yyyy-MM-dd")
        pname = process_name
        
        if pname == 'GRIFF':
            try:
                if self.config[self.hostname][pname]['GRIFF_TOMCAT']['ACCESS_LOG_PATH'] != "":
                    self.griff_tomcat_log_path_dict[self.griff_tomcat_access_path] = self.config[self.hostname][pname]['GRIFF_TOMCAT']['ACCESS_LOG_PATH']
                    self.is_griff_access_path = True
                else:
                    logging.info('access log path not available in common.json file.'\
                                    'Hence access log will not be fetched.')
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
                                self.griff_tomcat_log4j_property_dict[key] = replacedValue
                        
                        logging.info('\n')
                        logging.info('%s TOMCAT LOG4J2 PROPERTY INITIALIZED', pname)
                        formatter = "#" * 100
                        logging.info('%s', formatter)
                        
                        for key, value in self.griff_tomcat_log4j_property_dict.items():
                            logging.info('%s : %s', key, value)
                        
                        logging.info('\n')
                        
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
                    logging.info('access log path not available in common.json file.'\
                                    'Hence access log will not be fetched.')
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
                        logging.info('%s TOMCAT LOG4J2 PROPERTY INITIALIZED', pname)
                        formatter = "#" * 100
                        logging.info('%s', formatter)
                        
                        for key, value in self.packs_tomcat_log4j_property_dict.items():
                            logging.info('%s : %s', key, value)
                        
                        logging.info('\n')
                        
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
    
    def parse_log4j_property(self, pname, log4j):
        """
        Parse log4j2 property
        """
        logging.info('\n')
        logging.info('process name: %s and log4j path: %s', pname, log4j)
        if pname == 'GRIFF':
            try:
                tree = ET.parse(log4j)
                for data in tree.findall('./Properties/Property'):
                    if (
                            data.attrib.get('name') == 'log.basePath'\
                            or data.attrib.get('name') == 'log.backupBasePath'\
                            or data.attrib.get('name') == 'log.rollover.datePattern'\
                            or data.attrib.get('name') == 'log.rollover.extension'
                        ):
                        
                        self.griff_tomcat_log4j_property_dict[data.attrib.get('name')] = data.text
                
            except ET.ParseError as ex:
                logging.debug(ex)
                
        elif pname == 'PACKS':
            try:
                tree = ET.parse(log4j)
                for data in tree.findall('./Properties/Property'):
                    if (
                            data.attrib.get('name') == 'log.path'\
                            or data.attrib.get('name') == 'log.output'\
                            or data.attrib.get('name') == 'sys.log.backupBasePath'\
                            or data.attrib.get('name') == 'log.backupPath'\
                            or data.attrib.get('name') == 'log.rollover.basePath'\
                            or data.attrib.get('name') == 'log.rollover.datePattern'\
                            or data.attrib.get('name') == 'log.rollover.extension'
                        ):
                        
                        self.packs_tomcat_log4j_property_dict[data.attrib.get('name')] = data.text
                        
            except ET.ParseError as ex:
                logging.debug(ex)
    
    def parse_logger(self, pname, log4j2_path):
        """
        Logger reference call to appender
        """
        try:
            tree = ET.parse(log4j2_path)
            if pname == 'GRIFF':
                for data in tree.findall('./Loggers/AsyncLogger'):
                    self.parse_appender(data, tree, pname)
            
            elif pname == 'PACKS':
                for data in tree.findall('./Loggers/Logger'):
                    self.parse_appender(data, tree, pname)
                        
        except ET.ParseError as ex:
            logging.debug(ex)
                  
    def parse_appender(self, data, tree, pname):
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
                for routing in tree.findall('./Appenders/Routing'):
                    if logger_ref == str(routing.attrib.get('name')):
                        for routes in tree.findall('./Appenders/Routing/Routes'):
                            #call to routing for re-routing the references
                            self.parse_routing_appender(routes, tree, pname)
                            
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
                                break
                        else:
                            logging.info('No Appender defined for the logger: %s', logger_ref)
                
        except ET.ParseError as ex:
            logging.debug(ex)
        
    def parse_routing_appender(self, data, tree, pname):
        """
        Re-route for logger reference and parse appender
        """
        try:
            for route in data.findall('Route'):
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
                                
                    self.is_routing_success = True
                    
        except ET.ParseError as ex:
            logging.debug(ex)
    
    def initialize_tomcat_path(self, section):
            """
            Initialize griff tomcat path.
            """
            try:
                self.parse_transaction_logging(section)
            except ValueError as error:
                raise ValueError(error)
            except Exception as error:
                raise