# Created by Helic on 2017/7/21
import json


class NLG:

    def __init__(self):
        # 读取dataset
        with open('chatbot/NLG/data/nlg_template.json', encoding='utf-8') as f:
            value = json.load(f)
            self.request = value['request']  # list
            self.inform = value['inform']
            self.select = value['select']
            self.greeting = value['greeting']
            self.bye = value['bye']

    def get_sentence(self, diaact):
        request_slots = []
        inform_slots = []
        slot_val = []
        num = []
        s = {}
        for i in diaact['request_slots']:
            request_slots.append(i)
        for i in diaact['inform_slots']:
            inform_slots.append(i)
        # print(request_slots, inform_slots)
        # print(diaact['inform_slots'][inform_slots[0]])
        if inform_slots != []:
            if diaact['inform_slots'][inform_slots[0]] != 'UNK':
                slot_val = diaact['inform_slots'][inform_slots[0]]
                # print(slot_val)
        if diaact["diaact"] == 'request':
            for dic in self.request:
                if dic['request_slots'] == request_slots and dic['inform_slots'] == inform_slots:
                    if slot_val == []:
                        s = dic['nl']['agt']
                    else:
                        s = dic['nl']['agt']
                        for i in s:
                            sentence = s[i]
                            sentence = sentence.replace('$slot_val$', slot_val)
                            s[i] = sentence
                        num = []
                    return s
        elif diaact["diaact"] == 'inform':
            for dic in self.inform:
                if dic['inform_slots'] == inform_slots:
                    if slot_val == []:
                        s = dic['nl']['agt']
                    else:
                        s = dic['nl']['agt']
                        for i in s:
                            sentence = s[i]
                            sentence = sentence.replace('$slot_val$', slot_val)
                            s[i] = sentence
                        num = []
                    return s
        elif diaact["diaact"] == 'select':
            for dic in self.select:
                # print(dic['inform_slots'])
                if dic['inform_slots'] == inform_slots:
                    if slot_val == []:
                        s = dic['nl']['agt']
                    else:
                        s = dic['nl']['agt']
                        for i in s:
                            sentence = s[i]
                            sentence = sentence.replace('$slot_val$', slot_val)
                            s[i] = sentence
                        num = []
                    return s
        elif diaact["diaact"] == 'greeting':
            return self.greeting[0]['nl']['agt']
        elif diaact["diaact"] == 'bye':
            return self.bye[0]['nl']['agt']
        else:
            return diaact



'''
dia_act = {'diaact': 'request',
           'request_slots': {'child_name': 'UNK'},
           'inform_slots': {}
          }
dia_act = {'diaact': 'request',
           'request_slots': {'child_name':'UNK'},
           'inform_slots': {'fee':'UNK'}
        }
dia_act = {'diaact': 'request',
           'request_slots': {'reserve_time':'UNK'},
           'inform_slots': {'school_phone':'一二三四五'}
        }
dia_act = {'diaact': 'inform',
           'request_slots': {},
           'inform_slots': {'fee':'UNK'}
        }

dia_act = {'diaact': 'inform',
           'request_slots': {},
           'inform_slots': {'school_phone':'一二三四五'}
        }
dia_act = {'diaact': 'select',
           'request_slots': {'reserve_location': 'UNK'},
           'inform_slots': {'reserve_location': '一，二，三'}
        }
dia_act = {'diaact': 'greeting',
           'request_slots':{},
           'inform_slots':{}
        }
dia_act = {'diaact': 'bye',
           'request_slots':{},
           'inform_slots':{}
        }

'''

# nlg = NLG()
# dia_act = {'diaact': 'request',
#            'request_slots': {'child_name': 'UNK'},
#            'inform_slots': {}
#           }
# s = nlg.get_sentence(dia_act)
# print(s)




'''
self.request_slots = ['school_location', 'school_phone', 'sale', 'other_contact', 'cut_in', 'class_schedule',
                              'have_school_somewhere', 'attend_class_alone', 'allow_audition', 'audition_free',
                              'child_attend', 'allow_parents_together', 'class_length', 'audition_introduction',
                              'textbook', 'fulltime_or_sparetime', 'class_size', 'length_of_per_period',
                              'allow_return_premium', 'lesson_accompany', 'school_type', 'teacher_nation', 'class_type',
                              'online_course', 'online_course_location', 'fee', 'ruisi_introduction']


# agent需要去问用户的slot
self.agent_request_slots = ["child_age", "english_level", "special_need", "know_about_ruisi", "client_location",
                            "phone_number", "client_name", "client_gender",
                            "child_name"] # "reserve_location", "reserve_time"
'''