from datetime import datetime


def struct_time_to_datetime(struct_time):
    return datetime(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday,
                    struct_time.tm_hour, struct_time.tm_min, struct_time.tm_sec)


def datetime_to_str(time_datetime):
    """
    从datetime格式的时间转换成str
    :param datetime time_datetime:datetime格式的时间
    :return str: str格式的时间
    """
    return time_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def str_to_date(date_str):
    """
    从str格式的时间转换成date
    :param str date_str: str格式的时间
    :return date: date格式的时间
    """
    return datetime.strptime(date_str, '%Y-%m-%d').date()
