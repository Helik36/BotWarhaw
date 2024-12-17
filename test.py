from datetime import datetime
import calendar

my_time = datetime.today().weekday()

weekday = datetime.now().day

year, motnh, day = datetime.now().year, datetime.now().month, datetime.now().day
day += 2
select_weekday = calendar.weekday(year, motnh, day)

# print(select_weekday)


day = 23

dday = day

day = 222

print(day, dday)