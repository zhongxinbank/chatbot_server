import json
import requests

class Client:
    def __init__(self, user_id=0, host="localhost", port=5000, session_id=None):
        '''
        Start a new session with user id `user_id`.
        args:
            user_id the user id passed to server
            session_id if not None, it will be set as the session id
            host host name of the server
            port port of the server
        '''
        self.url = "http://" + host + ":" + str(port) + "/"
        if session_id is not None:
            self.session_id = session_id
        else:
            resp = requests.get(self.url + "?user_id=" + str(user_id))
            resp = resp.json()
            if resp["status"]["code"] == 200:
                self.session_id = resp["session_id"]
            else:
                raise RequestException(resp["status"]["code"], resp["status"]["message"])
        self.ended = False

    def response(self, user_input):
        '''
        Get the response to the `user_input` from server.
        args:
            user_input the input sentence from user
        '''
        resp = requests.post(self.url, data = json.dumps({"session_id": self.session_id, "user_input": user_input}))
        resp = resp.json()
        if resp["status"]["code"] == 200:
            self.ended = True if resp["ended"] == 1 else False
            return resp["output"]
        else:
            raise RequestException(resp["status"]["code"], resp["status"]["message"])

class RequestException(BaseException):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        
    def get_code(self):
        return self.code

    def get_message(self):
        return self.message