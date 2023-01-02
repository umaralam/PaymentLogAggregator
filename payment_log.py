#!/usr/local/bin/python3.6
from datetime import datetime, timedelta
import logging


class Main:

    def init(self):
        logging.basicConfig(filename='log_aggregator.log', filemode='w', format='[%(asctime)s,%(msecs)d]%(pathname)s:(%(lineno)d)-%(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
        
        start = datetime.now()
        logging.debug('start of execution time: %s', start)
        logging.info("testing....")
        
if __name__ == '__main__':
    main_object = Main()
    main_object.init()