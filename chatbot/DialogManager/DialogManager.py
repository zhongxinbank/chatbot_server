# Created by Helic on 2017/10/21
from chatbot.NLU.nlu_rule import NLU
from chatbot.NLG.nlg_rule import NLG
import json
import re


class DM:
    def __init__(self):
        # user request slots
        self.request_slots = ['school_location', 'school_phone', 'sale', 'other_contact', 'cut_in', 'class_schedule',
                              'have_school_somewhere', 'attend_class_alone', 'allow_audition', 'audition_free',
                              'child_attend', 'allow_parents_together', 'class_length', 'audition_introduction',
                              'textbook', 'fulltime_or_sparetime', 'class_size', 'length_of_per_period',
                              'allow_return_premium', 'lesson_accompany', 'school_type', 'teacher_nation', 'class_type',
                              'online_course', 'online_course_location', 'fee', 'ruisi_introduction']
        # user inform slots
        self.inform_slots = ['client_name', 'client_gender', 'child_name', 'child_age', 'child_grade', 'client_location'
                             , 'reserve_location', 'phone_number', 'english_level', 'special_need',
                             'attend_class_before', 'know_about_ruisi', 'user_goal', 'person_accompany', 'reserve_time']
        # agent需要去问用户的slot
        self.agent_request_slots = ["child_age", "english_level", "special_need", "know_about_ruisi", "client_location",
                                    "phone_number", "client_name", "client_gender",
                                    "child_name"] # "reserve_location", "reserve_time"
        # agent已经知道的slot
        self.agent_inform_slots = {}
        # 咨询记录模版
        self.record_template = {"child_name":" ", "child_age":" ", "english_level":" ", "client_name":" ", "client_gender":" ", "phone_number":" ",
                                "client_location":" ", "reserve_location":" ", "reserve_time":" ", "dialog_content":" "}
        # history存放所有之前的对话，包括客服和用户
        self.history = []
        self.nlu = NLU()
        self.nlg = NLG()
        # 同一个slot问的次数
        self.repeated_times = 1
        # nlg返回一个字典,此处index表示选择字典中的某句话
        self.index = 0
        self.last_request_slot = ''           # agent上次问的slot
        self.turn = 0   # 用户每说一句话,turn+1
        self.flag = False  # 对话是否结束
        with open("chatbot/NLG/data/location.json", encoding='utf-8') as f:
            self.location = json.load(f)
        # 存储对话内容
        self.dialog_content = ""

    def agent_response(self, raw_usr_sentence):
        """针对于用户的每句话，agent作出的回复，返回diaact"""
        self.dialog_content += 'user:' + raw_usr_sentence + '\t'
        usr_diaact = self.nlu.get_diaact(raw_usr_sentence, history=self.history)
        # print("usr_diaact:", usr_diaact)
        # 更新history
        dic = {
            "speaker": "user",
            "nl": raw_usr_sentence,
            "diaact": usr_diaact,
            "index": self.turn,
            "end": False
        }
        self.update_history(dic)

        # 存储用户通知的slot
        if usr_diaact["inform_slots"] != []:
            for i in usr_diaact["inform_slots"].keys():
                self.agent_inform_slots[i] = usr_diaact["inform_slots"][i]

        # user request slot(max=1)
        usr_current_request_slot = []
        if usr_diaact["request_slots"] != []:
            for i in usr_diaact["request_slots"].keys():
                usr_current_request_slot.append(i)

        if self.turn == 0:    # 第一次需要判断用户目的：咨询还是加盟
            if 'user_goal' in usr_diaact["inform_slots"] and usr_diaact["inform_slots"]["user_goal"] == "加盟":
                agent_diaact = {"diaact": "inform", "request_slots": {}, "inform_slots": {"user_goal": "加盟"}}
                self.flag = True
            elif 'user_goal' in usr_diaact["inform_slots"] and usr_diaact["inform_slots"]["user_goal"] == "预约":
                agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                "inform_slots": {}}
                self.last_request_slot = self.agent_request_slots[0]
                del self.agent_request_slots[0]
            else:
                if usr_current_request_slot != []:
                    agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                    "inform_slots": {usr_current_request_slot[0]: "UNK"}}
                    self.last_request_slot = self.agent_request_slots[0]
                    del self.agent_request_slots[0]
                else:
                    agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                    "inform_slots": {}}
                    self.last_request_slot = self.agent_request_slots[0]
                    del self.agent_request_slots[0]
        else:
            # 判断用户是否回答上次agent问的问题，如果回答，就继续问下一个问题；如果没有回答，就继续问这个问题
            if self.last_request_slot in self.agent_inform_slots:
                self.repeated_times = 0
                self.index = 0
                # 判断agent_request_slots是否为空，若为空，表示agent已经问完request_slots，对话可以结束
                if self.agent_request_slots != []:
                    # 判断用户是否在提问
                    if usr_current_request_slot != []:  # 默认user只能问一个问题
                        agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                        "inform_slots": {usr_current_request_slot[0]: "UNK"}}
                        self.last_request_slot = self.agent_request_slots[0]
                        del self.agent_request_slots[0]
                    else:
                        # 对用户inform的值做特殊处理，待补充
                        # 地址特殊处理
                        if "client_location" in usr_diaact["inform_slots"]:
                            # city, town = re.findall("(.*?)市(.*?)区", usr_diaact["inform_slots"]["client_location"])[0]
                            # agent_diaact = {"diaact": "select", "request_slots": {'reserve_location': 'UNK'},
                            #                 "inform_slots": {'reserve_location': str(self.location[city][town])}}
                            # self.agent_request_slots.remove("reserve_location")
                            # self.last_request_slot = 'reserve_location'
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {}}
                            self.last_request_slot = self.agent_request_slots[0]
                            del self.agent_request_slots[0]
                        elif "know_about_ruisi" in usr_diaact["inform_slots"]:
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {"ruisi_introduction": "UNK"}}
                            self.last_request_slot = self.agent_request_slots[0]
                            del self.agent_request_slots[0]
                        elif "special_need" in usr_diaact["inform_slots"]:
                            if 'child_age' in self.agent_inform_slots:  # 判断年龄
                                try:
                                    age = int(re.findall("\d", self.agent_inform_slots['child_age'])[0])
                                    if 3 <= age <= 5:
                                        self.index = 0
                                    elif 6 <= age <= 12:
                                        self.index = 1
                                    elif 13 <= age <= 18:
                                        self.index = 2
                                    else:
                                        self.index = 3   # no matching,close the dialog
                                        self.flag = True
                                except IndexError as e:
                                    self.index = 4
                            else:
                                # 未告知年龄
                                self.index = 4
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {}}
                            self.last_request_slot = self.agent_request_slots[0]
                            del self.agent_request_slots[0]
                        else:
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {}}
                            self.last_request_slot = self.agent_request_slots[0]
                            del self.agent_request_slots[0]
                else:
                    self.flag = True
                    agent_diaact = {"diaact": "bye", "request_slots": {}, "inform_slots": {}}
            else:
                if self.last_request_slot == "phone_number":
                    if self.repeated_times < 3:
                        self.index = self.repeated_times
                        self.repeated_times += 1

                        # 判断用户是否在提问
                        if usr_current_request_slot != []:  # 默认user只能问一个问题
                            agent_diaact = {"diaact": "request", "request_slots": {self.last_request_slot: "UNK"},
                                            "inform_slots": {usr_current_request_slot[0]: "UNK"}}
                        else:
                            agent_diaact = {"diaact": "request", "request_slots": {self.last_request_slot: "UNK"},
                                            "inform_slots": {}}
                    else:
                        self.index = 1
                        agent_diaact = {"diaact": "bye", "request_slots": {},
                                        "inform_slots": {}}
                        self.flag = True
                else:
                    self.index = 0
                    # 判断agent_request_slots是否为空，若为空，表示agent已经问完request_slots，对话可以结束
                    if self.agent_request_slots != []:
                        # 判断用户是否在提问
                        if usr_current_request_slot != []:  # 默认user只能问一个问题
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {usr_current_request_slot[0]: "UNK"}}
                        else:
                            agent_diaact = {"diaact": "request", "request_slots": {self.agent_request_slots[0]: "UNK"},
                                            "inform_slots": {}}
                        self.last_request_slot = self.agent_request_slots[0]
                        del self.agent_request_slots[0]
                    else:
                        self.flag = True
                        agent_diaact = {"diaact": "bye", "request_slots": {}, "inform_slots": {}}
        self.turn += 1
        # 更新history
        dic = {
                "speaker": "agent",
                "nl": raw_usr_sentence,
                "diaact": agent_diaact,
                "index": self.turn,
                "end": self.flag
        }
        self.update_history(dic)

        return agent_diaact, self.index

    def agent_nl(self, agent_diaact, index=0):
        try:
            self.dialog_content += "agent:" + self.nlg.get_sentence(agent_diaact)[str(index)] + '\t'
            return self.nlg.get_sentence(agent_diaact)[str(index)]
        except TypeError:
            return None

    def update_history(self, dic):
        """将之前的所有对话存下来"""
        self.history.append(dic)

    def get_current_info(self):
        record_row = {}
        for i in self.record_template.keys():
            if i in self.agent_inform_slots:
                record_row[i] = self.agent_inform_slots[i]
            else:
                record_row[i] = ""
        record_row["dialog_content"] = str(self.dialog_content)
        result = ""
        for i in record_row.keys():
            result += i + ": " + str(record_row[i]) + "\n"
        return result
