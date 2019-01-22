# -*- coding: utf-8 -*-

import json
import os
import falcon
from falcon_cors import CORS

from constant import ConstantCenter
from middlewares.audit_middleware import AuditMiddleware
from responders.root_responder import RootResponder


# 允许所有的跨域请求
cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

api = falcon.API(media_type='application/json', middleware=[AuditMiddleware(), cors.middleware])

api.add_route('/', RootResponder())


ConstantCenter.info_logger.info('服务器初始化成功', extra={"host": ConstantCenter.host_addr})
