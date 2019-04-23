# -*- coding:utf8 -*-
# Created by Helic on 2019/4/12
import sys

from chatbot.NLU.nlu_rule import NLU
from chatbot.NLG.nlg import NLG
from chatbot.DM.dm import DM

if __name__ == '__main__':
    nlu = NLU()
    dm = DM()
    nlg = NLG()
    print("请输入：")
    while not dm.is_dialog_over():
        user_input = input("user : ")

        # scene classification
        if not dm.state['history'] and "加盟" in user_input: # use `dm.state["history"]` to check if it's the first time or not
            print("agent :", "好的，您可以直接拨打4006101100进行咨询,感谢您对瑞思英语的关注，祝您生活愉快，再见！")
            sys.exit(1)

        diaact = nlu.get_diaact(user_input, history=dm.state['history'], last_request_slot=dm.state['last_request_slot'])
        print("user diaact :", diaact)
        response_action = dm.response(diaact)
        print("response_action :", response_action)
        response_nl = nlg.get_sentence(response_action)
        print("agent :", response_nl)