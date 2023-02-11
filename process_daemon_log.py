import logging
import signal
import subprocess
from outfile_writer import FileWriter

class DaemonLogProcessor:
    """
        Daemon log processor class
        fetching daemon log for the issue threads in the tlogs
    """
    def __init__(self, initializedPath_object, validation_object):
        self.initializedPath_object = initializedPath_object
        self.validation_object = validation_object
        
    def process_daemon_log(self, pname, tlog_thread):
        #creating out file writter object for writting log to out file
        fileWriter_object = FileWriter()
        
        if pname == "GRIFF":
            try:
                debugMsisdn_log_path = self.initializedPath_object.griff_tomcat_log_path_dict["griff_DEBUGMSISDN_LOG"]
                try:
                    logging.info('tlog thread: %s', tlog_thread)
                    thread_log = subprocess.check_output(f"grep -a {tlog_thread} {debugMsisdn_log_path}", universal_newlines=True, shell=True, preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL))
                    record = [data for data in thread_log]
                    
                    if record:
                        fileWriter_object.write_complete_thread_log(pname, tlog_thread, record)
                        
                except subprocess.CalledProcessError as error:
                    logging.info()
            except KeyError as error:
                logging.info('debug msisdn log path does not exists.\n %s', error)