from database.model.user_model import UserModel
from playhouse.shortcuts import model_to_dict, dict_to_model
from peewee import fn
import traceback
from constant import AuthException, AppException, DatabaseException, ConstantCenter

class UserDAO(object):

    pass