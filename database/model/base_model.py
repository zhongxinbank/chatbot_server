import os
import traceback
import redis
from constant import ConstantCenter


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
try:
	redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
except:
	ConstantCenter.error_logger.error("Redis读取失败, %s", traceback.format_exc(),  extra={"host": ConstantCenter.host_addr})
	exit()

