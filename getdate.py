from datetime import datetime, timedelta
from main import save_json_file

def print_weekly_dates(start_date_str, year):
    # 将字符串转换为日期对象
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    dates = []
    # 计算该年的最后一天的日期
    end_date = datetime(year, 12, 31)

    # 初始化当前日期为起始日期
    current_date = start_date

    # 生成每隔一周的日期，直到年末
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        print(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(weeks=1)
    return dates


dates = print_weekly_dates("2023-01-01", 2023)
save_json_file({"dates": dates}, "2023_dates.json")