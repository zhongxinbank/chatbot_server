from constant import ConstantCenter 


class AuditMiddleware(object):
    def process_request(self, req, res):
        audit_log = req.method + ' ' + req.uri
        ConstantCenter.info_logger.info(audit_log, extra={"host": ConstantCenter.host_addr})
