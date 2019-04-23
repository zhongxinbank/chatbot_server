# -*- coding:utf-8 -*- 
import random
import json
import pdb
import copy
import re
import os
import warnings


class DM:
    def __init__(self, slot_path="./chatbot/DM/data/request_slots.json", check_constraint=2):
        '''初始化参数
        @params:
            slot: list, agent所有要问的slot

            slot_flag ：list,[true/false] 要问的slot 是否为必填项

            check_constraint : int ,必填项被问几次才跳过

        '''
        with open(slot_path, encoding='utf-8') as f:
            content = json.load(f)
            self.slots_asked = content["all_request_slots"]  # 所有agent需要问的问题 list
            self.slots_dict = content["slots_check"]      # 所有agent需要问的 dictionary {"slot":false/true}
            
        self.state = {}
        self.turn = 0
        self.user_action = {}
        #self.slots_asked = list(self.slots_dict.keys())
        self.bye_flag = False
        #self.slot_flag = list(self.slots_dict.values())
        #self.check_list = [slot for i, slot in enumerate(self.slot_asked) if self.slot_flag[i]]
        self.check_list = [slots for slots in self.slots_dict.keys() if self.slots_dict[slots]==True]
        #print("check_list",self.check_list)
        self.check_constraint = check_constraint

        self.state['rest_slots'] = copy.deepcopy(self.slots_asked)  # agent该问的slot
        self.state['user_informed_slot'] = {}  # user告知过了slot

        self.state['diaact'] = ""
        self.state['inform_slots'] = {}
        self.state['request_slots'] = {}

        self.state['turn'] = 0
        self.state['last_request_slot'] = ''
        self.state["history"] = []
        # [
        #     {"speaker": "user or agent",
        #      "turn": "0"
        #         "content": [{'diaact': '',
        #                      'inform_slots': {},
        #                      'request_slots': {},
        #                      'nl': ''},   # 如果是agent，nl为空字符串
        #                     {'diaact': '',
        #                      'inform_slots': {},
        #                      'request_slots': {},
        #                      'nl': ''}
        #                     ]},

        #     {"speaker": "user or agent",
        #      "turn": "1"
        #         "content": [{'diaact': '',
        #                      'inform_slots': {},
        #                      'request_slots': {},
        #                      'nl': ''},
        #                     {'diaact': '',
        #                      'inform_slots': {},
        #                      'request_slots': {},
        #                      'nl': ''}
        #                     ]}
        # ]

        self.check_time = self.check_constraint

    def response(self, user):
        '''回复用户的action
        @params:
            user_action: list, [{"diaact":"inform", "inform_slots":{},'request_slots': {},"nl":''},{}], 用户的action序列
        
        @return:
            response_action: list, 同上
        '''

        user_action = []
        agent = []

        # 在user中先删掉nl 

        for user_ in copy.deepcopy(user):
            del user_['nl']
            user_action.append(user_)

        self.state["history"].append({"speaker":"user", "turn":copy.deepcopy(self.state["turn"]), "content":user}) # update history
        self.state["turn"] += 1

        if len(user_action) > 1:

            response_action = self.multi_response(user_action)

        else:
            response_action = self.single_response(user_action)

        # 在agent中加上"nl"

        for agent_ in copy.deepcopy(response_action):
            agent_["nl"] = ""
            agent.append(agent_)
       
        self.state["history"].append({"speaker":"agent", "turn":copy.deepcopy(self.state["turn"]), "content":agent})  # update history
        self.state["turn"] += 1
        # print("history", self.state["history"])

        # 判断bye_flag

        self.bye_flag = bool([True for action in response_action if "bye" in action.values()])

        return response_action

    def multi_response(self, user_action):
        '''对user_action中有多个action的情况进行回复
        @params:
            user_action: list, [{"diaact":"inform", "inform_slots":{}...},{}], 用户的action序列
        
        @return:
            response_action_multi: list, 同上
        '''
        response_action_multi = []
        for action in user_action:
            if action['diaact'] == "bye":
                response_action_0 = self.response_bye(action)
                self.bye_flag = True
                return response_action_0

        for action in user_action:

            if action['diaact'] == "request":
                self.update_state(action)
                response_action_1 = self.response_multi_request(action)
                response_action_multi.extend(response_action_1)

        for action in user_action:

            if action["diaact"] == "inform":
                self.update_state(action)
                # print("5",response_action_multi)
                response_action_2 = self.response_inform(action)
                # print('8', response_action_multi)
                response_action_multi.extend(response_action_2)

        for act in response_action_multi:
            if act["request_slots"]:
                self.state['last_request_slot'] = list(act["request_slots"].keys())[0]
            else:
                self.state['last_request_slot'] = ''

        return response_action_multi  # list

    def single_response(self, user_action):
        ''' 对用户的单个action进行回复
        @params:
            user_action: list[dict], {}, 三元组.py

        @return:
            response_action: list, [{},{}]

        '''

        self.update_state(user_action[0])  # 更新state
        # print(user_action)
        if user_action[0]["diaact"] == "bye":
            response_action = self.response_bye(user_action[0])
            self.bye_flag = True
        elif user_action[0]["diaact"] == "inform":
            response_action = self.response_inform(user_action[0])
        elif user_action[0]["diaact"] == "request":
            response_action = self.response_single_request(user_action[0])
        else:
            response_action = []  # 没有这种情况？ NLU
            warnings.warn("user diaact not in [bye, inform, request], exit")
            # exit()
        for act in response_action:
            if act["request_slots"]:
                self.state['last_request_slot'] = list(act["request_slots"].keys())[0]
            else:
                self.state['last_request_slot'] = ''

        return response_action  # list nlg要做判断

    def update_state(self, user_action):
        ''' 根据用户的action更新当前系统状态
            将用户已经告知的信息存储下来
        @params:
            user_action: dict,三元组
        '''
        self.state["user_informed_slot"].update(user_action["inform_slots"])  # update.????
        if user_action["inform_slots"]:
            for slot in user_action["inform_slots"].keys():
                if slot in self.state["rest_slots"]:
                    self.state["rest_slots"].remove(slot)

    def response_inform(self, user_action):
        ''' 对用户的inform进行回复
        @params:
            user_action: dict, 三元组

        @return:
            response_action: list, [{},{}]

        '''

        response_action_list = []
        response_action = {}
        # 答非所问
        # print(user_action)
        # print("last_request_slot", self.state["last_request_slot"])
        if self.state["last_request_slot"] not in user_action["inform_slots"].keys():  # 未回答上一轮问的问题
            if self.state["last_request_slot"] in self.check_list:  # 上一轮问的问题在必填项中
                slot = copy.deepcopy(self.state["last_request_slot"])

                if self.check_time > 1:
                    # 在check_list中的slot需要被check是否正确格式或者包含敏感词，如果检查不正确且check-time大于1的话
                    self.state["diaact"] = "request"  # state
                    self.state["request_slots"][slot] = "1"
                    self.state["inform_slots"] = {}
                    self.check_time -= 1

                elif self.check_time == 1:
                    # 还有一次机会提问的话，infor-slot是tip
                    self.state["diaact"] = "request"  # state
                    self.state["request_slots"][slot] = "2"
                    self.state["inform_slots"] = {}
                    self.check_time -= 1

                elif self.check_time == 0:
                    self.state["rest_slots"].remove(self.state["last_request_slot"])
                    if self.state["rest_slots"] != []:
                        self.state["diaact"] = "request"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"].clear()
                        self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                    else:  # 全部slot问完的情况下，结束对话
                        self.state["diaact"] = "bye"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"] = {}

                    self.check_time = self.check_constraint
            else:  # 不在必填项中
                # self.state["last_request_slot"] 有为空的情况
                if self.state["last_request_slot"]:
                    self.state["rest_slots"].remove(self.state["last_request_slot"])
                    if self.state["rest_slots"] != []:
                        self.state["diaact"] = "request"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"].clear()
                        # 处理Know about ruisi
                        if self.state["rest_slots"][0] == "know_about_ruisi":
                            self.state["request_slots"][self.state["rest_slots"][0]] = self.check_age()
                        else:
                            self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                    else:  # 全部slot问完的情况下，结束对话
                        self.state["diaact"] = "bye"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"] = {}

                    self.check_time = self.check_constraint  #?
                # print("self.dia", self.state["diaact"])
                else:

                    if self.state["rest_slots"] != []:
                        self.state["diaact"] = "request"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"].clear()
                        # 处理Know about ruisi
                        if self.state["rest_slots"][0] == "konw_about_ruisi":
                            self.state["request_slots"][self.state["rest_slots"][0]] = self.check_age()
                        else:
                            self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                        # print("self.dia", self.state["diaact"])
                    else:  # 全部slot问完的情况下，结束对话
                        self.state["diaact"] = "bye"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"] = {}

                    self.check_time = self.check_constraint


        # 回答问题
        else:
            if self.state["rest_slots"] != []:  # 还有没问完的slot，继续问
                self.state["diaact"] = "request"
                self.state["inform_slots"] = {}
                self.state["request_slots"].clear()
                # 处理Know about ruisi
                slot = copy.deepcopy(self.state["rest_slots"][0])
                if self.state["rest_slots"][0] == "know_about_ruisi":
                    self.state["request_slots"][slot] = self.check_age()
                else:
                    self.state["request_slots"][slot] = "UNK"
            else:  # 全部slot问完的情况下，结束对话
                self.state["diaact"] = "bye"
                self.state["inform_slots"] = {}
                self.state["request_slots"] = {}

            self.check_time = self.check_constraint

        response_action["diaact"] = copy.deepcopy(self.state["diaact"])
        response_action["inform_slots"] = copy.deepcopy(self.state['inform_slots'])
        response_action["request_slots"] = copy.deepcopy(self.state['request_slots'])

        response_action_list.append(response_action)

        return response_action_list

    def response_multi_request(self, user_action, response_num=1):
        """ 对多个action的情况下的用户提问进行回复
        @params:
            user_action: dict, 三元组
            response_num: int, 一次回复用户的提问数，默认为1
        
        @return：
            response_action: dict, 三元组，异常情况下输出空字典{}
        
        """
        response_action_list = []
        response_action = {}
        if user_action["request_slots"]:
            # for i in range(response_num):

            # print(user_action["request_slots"])
            request_slot = random.choice(list(user_action["request_slots"]))

            self.state["diaact"] = "inform"
            self.state["inform_slots"].clear()
            self.state["request_slots"] = {}
            if request_slot == "class_type":
                self.state["inform_slots"][request_slot] = self.check_age()
            else:
                self.state["inform_slots"][request_slot] = ""

                # self.state["inform_slots"][request_slot] = ""

            response_action["diaact"] = copy.deepcopy(self.state['diaact'])
            response_action["inform_slots"] = copy.deepcopy(self.state['inform_slots'])
            response_action["request_slots"] = copy.deepcopy(self.state['request_slots'])

        else:  # 异常情况，debug用
            # print("request_action should have request_slots, but this is %s" % user_action)
            response_action = {}
            warnings.warn("if user request is empty, should exit")
            #exit()
        response_action_list.append(response_action)

        return response_action_list

    def response_single_request(self, user_action):

        """对用户仅提问进行回复
        @params:
            user_action: dict, {}, 三元组
        @return:
            response_action_single: list,[{},{}]
        """
        # print("1",user_action)
        response_action_1 = {}
        response_action_2 = {}
        response_action_single = []
        request_slot = random.choice(list(user_action["request_slots"].keys()))  # 随机选一个user的问题来回答
        # print("d", request_slot)
        self.state["diaact"] = "inform"
        self.state["inform_slots"].clear()
        if request_slot == "class_type":
            self.state["inform_slots"][request_slot] = self.check_age()
        else:
            self.state["inform_slots"][request_slot] = ""
        self.state["request_slots"] = {}
        # self.state["inform_slots"][request_slots] = ""

        response_action_1["diaact"] = copy.deepcopy(self.state['diaact'])
        response_action_1["inform_slots"] = copy.deepcopy(self.state['inform_slots'])
        response_action_1["request_slots"] = copy.deepcopy(self.state['request_slots'])
        # print("1", response_action_1)
        response_action_single.append(response_action_1)

        # 此时认为 inform是空
        if self.state["last_request_slot"]:  # self.state["last_request_slot"]可能为空,不为空则判断user是否回答
            # 未回答上一轮问的问题
            ############################################################
            # copy from response_infom 来处理单个action，user在request但未回答上一轮的agent的request
            ############################################################

            if self.state["last_request_slot"] in self.check_list:  # 上一轮问的问题在必填项中
                slot = self.state["last_request_slot"]

                if self.check_time > 1:
                    # 在check_list中的slot需要被check是否正确格式或者包含敏感词，如果检查不正确且check-time大于1的话
                    self.state["diaact"] = "request"  # state
                    self.state["inform_slots"] = {}
                    self.state["request_slots"].clear()
                    self.state["request_slots"][slot] = "1"

                    self.check_time -= 1

                elif self.check_time == 1:
                    # 还有一次机会提问的话，infor-slot是tip
                    self.state["diaact"] = "request"
                    self.state["inform_slots"] = {}
                    self.state["request_slots"].clear()
                    self.state["request_slots"][slot] = "2"
                    self.check_time -= 1

                elif self.check_time == 0:
                    self.state["rest_slots"].remove(self.state["last_request_slot"])
                    if self.state["rest_slots"] != []:
                        self.state["diaact"] = "request"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"].clear()
                        self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                    else:  # 全部slot问完的情况下，结束对话
                        self.state["diaact"] = "bye"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"] = {}
                    self.check_time = self.check_constraint
            else:  # 不在必填项中
                # self.state["last_request_slot"] 有为空的情况
                if self.state["last_request_slot"]:
                    self.state["rest_slots"].remove(self.state["last_request_slot"])
                    if self.state["rest_slots"] != []:
                        self.state["diaact"] = "request"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"].clear()
                        # 处理Know about ruisi
                        if self.state["rest_slots"][0] == "konw_about_ruisi":
                            self.state["request_slots"][self.state["rest_slots"][0]] = self.check_age()
                        else:
                            self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                    else:  # 全部slot问完的情况下，结束对话
                        self.state["diaact"] = "bye"
                        self.state["inform_slots"] = {}
                        self.state["request_slots"] = {}

                    self.check_time = self.check_constraint
            # slot = self.state["last_request_slot"]
            # self.state["diaact"] = "request"
            # self.state["inform_slots"] = {}
            # self.state["request_slots"].clear()
            # self.state["request_slots"][slot] = "UNK"
        else:
            if self.state["rest_slots"] != []:
                self.state["diaact"] = "request"
                self.state["inform_slots"] = {}
                self.state["request_slots"].clear()
                # 处理Know about ruisi
                if self.state["rest_slots"][0] == "konw_about_ruisi":
                    self.state["request_slots"][self.state["rest_slots"][0]] = self.check_age()
                else:
                    self.state["request_slots"][self.state["rest_slots"][0]] = "UNK"
                # print("self.dia", self.state["diaact"])
            else:  # 全部slot问完的情况下，结束对话
                self.state["diaact"] = "bye"
                self.state["inform_slots"] = {}
                self.state["request_slots"] = {}

        response_action_2["diaact"] = copy.deepcopy(self.state['diaact'])
        response_action_2["inform_slots"] = copy.deepcopy(self.state['inform_slots'])
        response_action_2["request_slots"] = copy.deepcopy(self.state['request_slots'])

        response_action_single.append(response_action_2)
        # print("7", response_action_single)

        return response_action_single

    def response_bye(self, user_action):
        '''对用户的bye进行回复
        @return:
            response_action: []

        '''
        response_list = []
        response_action = {}
        self.state["diaact"] = "bye"
        self.state["inform_slots"] = {}
        self.state["request_slots"] = {}

        response_action["diaact"] = copy.deepcopy(self.state['diaact'])
        response_action["inform_slots"] = copy.deepcopy(self.state['inform_slots'])
        response_action["request_slots"] = copy.deepcopy(self.state['request_slots'])
        response_list.append(response_action)
        return response_list

    def is_dialog_over(self):
        """
        判断对话是否结束：True代表结束
        :return: bool
        """
        return self.bye_flag

    def check_age(self):
        """ 处理特殊slot： know_about_ruisi和class_type，将value填上相应的age值
        @params:
            self.state["user_informed_slot"]： list, 更新state过后,存储user告知过的slots
        
        @return：
            value: "UNK"或者int(child_age的value)
        
        """

        if "child_age" in self.state["user_informed_slot"].keys():
            #print("age", self.state["user_informed_slot"])
            value = copy.deepcopy(self.state["user_informed_slot"]["child_age"])
            try:
                value = int(re.findall("\d+", value)[0])  # 将字符串转化为数字
                if value in range(3, 6):
                    value = "1"
                elif value in range(6, 13):
                    value = "2"
                elif value in range(13, 19):
                    value = "3"
                elif value < 3 or value > 18:
                    value = "4"
                else:
                    value = "UNK"  # TODO  UNK???
            except Exception:
                value = "UNK"
        else:
            value = "UNK"
        return value


if __name__ == "__main__":
    # nlu_input = [{'diaact': 'inform', 'request_slots': {}, 'inform_slots': {'child_age': '5岁'}}, {'diaact': 'request', 'request_slots': {'class_type': 'UNK'}, 'inform_slots': {}}]
    # nlu_input = [{'diaact': 'inform', 'request_slots': {}, 'inform_slots': {'child_age': '5岁', 'child_name': "lili"}}]
    #nlu_input = [{'diaact': 'request', 'request_slots': {'class_type': 'UNK'}, 'inform_slots': {}, "nl": 'abcdeffg'}]
    # nlu_input = [{'diaact': 'request', 'request_slots': {'class_type': 'UNK',"teacher_nation":'UNK'}, 'inform_slots': {}}]
    #nlu_input = [{'diaact': 'bye', 'request_slots': {}, 'inform_slots': {}, "nl": 'abcdeffg'}]
    nlu_input = [{'diaact': 'inform', 'request_slots': {}, 'inform_slots': {'child_age': '5岁'}}, {'diaact': 'bye', 'request_slots': {}, 'inform_slots': {}}]

    nl = 'abcdeffg'

    dm = DM()
    response_action = dm.response(nlu_input)

    print(response_action)
