import falcon
import json, uuid
from constant import *
from constant import RequestException, AppException, DatabaseException
from database.dao.session_dao import SessionDAO

from chatbot.DialogManager.DialogManager import DM


class RootResponder(object):

    def on_get(self, req, res):
        # TODO: CHECK FOR PARAMS `user_id`
        try:
            user_id = req.params.get("user_id")
            if user_id is not None:
                new_session = DM()
                session_id = str(uuid.uuid1())
                SessionDAO.set_user_session(session_id, new_session, 600)
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
                raise RequestException(500, 'No suffient params in request url')
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
                agent_response_diaact, index = session.agent_response(user_input)
                try:
                    output_message = session.agent_nl(agent_response_diaact, index)
                except KeyError as e:
                    output_message = "家长可以留下您的联系方式哦，我们后续会安排专业的老师与您对接，为您详细介绍相关事宜。"
                if session.flag:
                    SessionDAO.kill_user_session(session_id)
                else:
                    SessionDAO.set_user_session(session_id, session, 600)
                with open(ConstantCenter.app_env['app']['SAVE_PATH'] + session_id, 'w') as f_out:
                    f_out.write(session.get_current_info())
                res.status = falcon.HTTP_200
                res.body = json.dumps({ 
                    'output': output_message,
                    'status': {
                        'code': 200,
                        'message': "Successfully produced the response"
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