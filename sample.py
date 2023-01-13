from datetime import datetime, timedelta

def date_range_list(start_date, end_date):
    # Return list of datetime.date objects between start_date and end_date (inclusive).
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list


d1 = datetime.strftime(datetime.strptime("20230110", "%Y%m%d"), "%Y%m%d")
d2 = datetime.strftime(datetime.strptime("20230114", "%Y%m%d"), "%Y%m%d")
dates = date_range_list(d1, d2)
for date in dates:
    print(datetime.strftime(date, "%Y-%m-%d"))