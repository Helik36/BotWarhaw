from datetime import datetime

set_time = "SET_TIME_12"

qq = set_time.split("_")

ww = next(j for j in qq if j.isdigit())

print(ww)

print(datetime.now().day)