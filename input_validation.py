from datetime import datetime
import logging


class InputValidation:
    """
    input data validation class
    """
    
    def __init__(self, msisdn, start_date, end_date):
        self.msisdn = msisdn
        self.fmsisdn = ""
        self.start_date = start_date
        self.end_date = end_date
        # self.service_keyword = ""
        self.is_input_valid = False
        # self.f_cur_date_time = ""
        # self.f_diff_date_time = ""
        # self.is_tlog = False
        # self.keyword = ""

    def validate_msisdn(self):
        """
        Validate msisdn.
        """
        try:
            msisdn = self.msisdn
            special_characters = ['/', '#', '$', '*', '&', '@']
            self.fmsisdn = "".join(filter(lambda char: char not in special_characters , msisdn))
            logging.info('msisdn:%s and formatted msisdn after removal of special character just for creating out file:%s', self.msisdn, self.fmsisdn)
        except Exception as error:
            logging.error('Invalid msisdn')
            raise

    def validate_date(self):
        """
        Validate date.
        """
        try:
            self.start_date = datetime.strptime(self.start_date, "%Y%m%d")
            self.end_date = datetime.strptime(self.end_date, "%Y%m%d")
            self.is_input_valid = True
            logging.debug('start date: %s and end date: %s entered is valid', datetime.strftime(self.start_date, "%Y%m%d"), datetime.strftime(self.end_date, "%Y%m%d"))
        except Exception as error:
            logging.error('start date: %s or/and end date: %s entered is of invalid format. The format should be "yyyymmdd".', self.start_date, self.end_date)
            self.is_input_valid = False
            raise