import pickle
import traceback
from constant import ConstantCenter, DatabaseException
from database.model.base_model import redis_db

class SessionDAO():
    
    @staticmethod
    def set_user_session(id, session, session_duration=600):
        try:
            redis_db.set(id, pickle.dumps(session), ex=session_duration)
        except:
            ConstantCenter.error_logger.error('set_user_session 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())

    @staticmethod
    def get_user_session(id):
        try:
            user_session = redis_db.get(id)
            if user_session:
                return pickle.loads(user_session)
            else:
                return False
        except:
            ConstantCenter.error_logger.error('get_user_session 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())

    @staticmethod
    def kill_user_session(id):
        try:
            user_session = redis_db.get(id)
            if user_session:
                redis_db.delete(id)
            else:
                return "No session_id in redis"
        except:
            ConstantCenter.error_logger.error('get_user_session 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())