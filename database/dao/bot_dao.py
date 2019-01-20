from database.model.user_model import UserModel
from database.model.bot_model import  BotModel
from playhouse.shortcuts import model_to_dict, dict_to_model
from peewee import fn
import traceback
import json
import uuid
from constant import AuthException, AppException, DatabaseException, ConstantCenter

class BotDAO(object):

    @staticmethod
    def format_bot(bot):
        bot = model_to_dict(bot)
        bot['logic'] = json.loads(bot['logic'], encoding='utf-8')
        bot['created_at'] = bot['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        bot['updated_at'] = bot['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        return bot

    @staticmethod
    def create_bot(id, name, logic, creator_id):
        try: 
            bot = BotModel.create(
                id=id if id != None else str(uuid.uuid1()),
                name = name,
                logic = json.dumps(logic, ensure_ascii=False),
                creator_id = creator_id
            )
            return BotDAO.format_bot(bot)
        except:
            ConstantCenter.error_logger.error('create_bot 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())

    @staticmethod
    def update_bot(id, name, logic):
        try:
            (BotModel.update(name=name, logic=json.dumps(logic, ensure_ascii=False)).where(BotModel.id == id)).execute()
            return True
        except:
            ConstantCenter.error_logger.error('update_bot 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())

    @staticmethod
    def get_bot_with_id(id):
        try: 
            bot = BotModel.get(BotModel.id == id, BotModel.is_active == True)
            return BotDAO.format_bot(bot)
        except:
            ConstantCenter.error_logger.error('find_bot 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())

    @staticmethod
    def get_all_bots():
        try: 
            bots = (BotModel.select().where(BotModel.is_active == True)).execute()
            all_bots = []
            for bot in bots:
                all_bots.append(BotDAO.format_bot(bot))
            return all_bots
        except:
            ConstantCenter.error_logger.error('find_bot 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())
    
    @staticmethod
    def get_bot_with_name(name):
        try: 
            bots = (BotModel.select().where(BotModel.name == name).order_by(BotModel.created_at.desc()).limit(1)).execute()
            all_bots = []
            for bot in bots:
                all_bots.append(BotDAO.format_bot(bot))
            return all_bots
        except:
            ConstantCenter.error_logger.error('find_bot 发生错误： %s', traceback.format_exc(), extra={"host": ConstantCenter.host_addr})
            raise DatabaseException(40000, traceback.format_exc())
