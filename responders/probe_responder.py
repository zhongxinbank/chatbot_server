import falcon
import json, uuid
from constant import *
from constant import RequestException, AppException, DatabaseException
from database.dao.session_dao import SessionDAO


class ProbeResponder(object):

    def on_get(self, req, res):
        # 此处需要对请求参数做校验
        try:
            user_id = req.params.get("user_id")
            if user_id is not None:
                # 此处初始化一个sesssion,存入redis,返回session_id
                session_id = str(uuid.uuid1())
                SessionDAO.set_user_session(session_id, "test", 600)  # 此处需要修改成DM instance
                res.status = falcon.HTTP_200
                res.body = json.dumps({
                    'session_id': session_id,
                    'status': {
                        'code': 200,
                        'message': 'Successfully created a session for user {} for 10 mins'.format(user_id)
                    }
                }, ensure_ascii=False)
                return res
            else:
                raise RequestException(500, 'No suffient params in request url')   # 传参错误统一返回500
        except (AppException, RequestException, DatabaseException) as error:
            res.status = falcon.HTTP_200
            res.body = json.dumps({ 
                'status': {
                    'code': error.get_code(),
                    'message': error.get_message()
                }
            }, ensure_ascii=False)
            return res
        except:
            ConstantCenter.error_logger.error(traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            res.status = falcon.HTTP_200
            res.body = json.dumps({
                'status': {
                    'code': 40000,
                    'message': traceback.format_exc()
                }
            }, ensure_ascii=False)
            return res
        
    def on_post(self, req, res):
        try: 
            req_body = json.loads(req.stream.read())
            session_id = req_body.get('session_id')
            user_input = req_body.get('user_input')
            if session_id is not None and SessionDAO.get_user_session(session_id) and user_input is not None:
                session = SessionDAO.get_user_session(session_id)
                output_message = user_input  # DM执行返回的结果 TODO  对话结束时要直接kill session
                res.status = falcon.HTTP_200
                res.body = json.dumps({ 
                    'output': output_message,
                    'status': {
                        'code': 200,
                        'message': "执行成功"
                    }
                }, ensure_ascii=False)
                return res
            else:
                raise RequestException(500, 'No suffient params in request url or the user session has been killed')
        except (AppException, RequestException, DatabaseException) as error:
            res.status = falcon.HTTP_200
            res.body = json.dumps({ 
                'status': {
                    'code': error.get_code(),
                    'message': error.get_message()
                }
            }, ensure_ascii=False)
            return res
        except:
            ConstantCenter.error_logger.error(traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            res.status = falcon.HTTP_200
            res.body = json.dumps({
                'status': {
                    'code': 40000,
                    'message': traceback.format_exc()
                }
            }, ensure_ascii=False)
            return res