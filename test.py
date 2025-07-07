from datetime import datetime

time = datetime(1, 1, 1)
print(datetime.now() > time)
print(datetime.now().timestamp())
print(type(datetime.now().timestamp()))