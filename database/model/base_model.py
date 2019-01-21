import os
import traceback
import redis
from constant import ConstantCenter


REDIS_HOST = ConstantCenter.app_env['redis']['REDIS_HOST']
REDIS_PORT = int(ConstantCenter.app_env['redis']['REDIS_PORT'])
REDIS_DB = int(ConstantCenter.app_env['redis']['REDIS_DB'])
try:
	redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
except:
	ConstantCenter.error_logger.error("Redis读取失败, %s", traceback.format_exc(),  extra={"host": ConstantCenter.host_addr})
	exit()

