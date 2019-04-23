import falcon
import json, uuid, os, codecs
from constant import *
from constant import RequestException, AppException, DatabaseException
from database.dao.session_dao import SessionDAO

from chatbot.NLU.nlu_rule import NLU
from chatbot.NLG.nlg import NLG
from chatbot.DM.dm import DM

class RootResponder(object):

    def on_get(self, req, res):
        # TODO: CHECK FOR PARAMS `user_id`
        try:
            user_id = req.params.get("user_id")
            if user_id is not None:
                new_session = DM(check_constraint=2)
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
                user_action = {}
                response_action = {}
                if not session.state['history'] and '加盟' in user_input:
                    SessionDAO.kill_user_session(session_id)
                    res.status = falcon.HTTP_200
                    res.body = json.dumps({
                        'output': '好的，您可以直接拨打4006101100进行咨询，感谢您对瑞思英语的关注，祝您生活愉快，再见！',
                        'ended': 1,
                        'action_info': {
                            'user_action': json.dumps(user_action, ensure_ascii=False),
                            'response_action': json.dumps(response_action, ensure_ascii=False)
                        },
                        'status': {
                            'code': 200,
                            'message': 'Successfully produced the reponse'
                        }
                    }, ensure_ascii=False)
                    return res
                user_action = ConstantCenter.nlu.get_diaact(user_input, history=session.state['history'], \
                    last_request_slot=session.state['last_request_slot'])
                response_action = session.response(user_action)
                response = ConstantCenter.nlg.get_sentence(response_action)

                if session.is_dialog_over():
                    SessionDAO.kill_user_session(session_id)
                else:
                    SessionDAO.set_user_session(session_id, session, 600)
                if not os.path.exists(ConstantCenter.app_env['app']['SAVE_PATH']):
                    os.makedirs(ConstantCenter.app_env['app']['SAVE_PATH'])
                with codecs.open(os.path.join(ConstantCenter.app_env['app']['SAVE_PATH'], session_id + '.txt'), 'w', encoding='utf-8') as f_out:
                    f_out.write(json.dumps(session.state['history'], indent=4, ensure_ascii=False))
                res.status = falcon.HTTP_200
                res.body = json.dumps({
                    'output': response,
                    'ended': int(session.is_dialog_over()),
                    'action_info': {
                        'user_action': json.dumps(user_action, ensure_ascii=False),
                        'response_action': json.dumps(response_action, ensure_ascii=False)
                    },
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
                'action_info': {
                    'user_action': json.dumps(user_action, ensure_ascii=False),
                    'response_action': json.dumps(response_action, ensure_ascii=False)
                },
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
                'action_info': {
                    'user_action': json.dumps(user_action, ensure_ascii=False),
                    'response_action': json.dumps(response_action, ensure_ascii=False)
                },
                'status': {
                    'code': 40000,
                    'message': traceback.format_exc()
                }
            }, ensure_ascii=False)
            return res