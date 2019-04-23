import json
import random


class NLG():
    def __init__(self, nlg_template_path="./chatbot/NLG/nlg_template.json"):
        # 读取dataset
        with open(nlg_template_path, "r", encoding="utf-8") as f:
            template = json.load(f)
            self.request = template["request"]  # list
            self.inform = template["inform"]
            self.thanks = template["thanks"]
            self.greeting = template["greeting"]
            self.bye = template["bye"]

    def get_sentence(self, response_action):
        """对DM给出的response_action进行回复
        """
        sentence = ""
        for action in response_action:
            sentence += self.get_one_sentence(action)
        return sentence

    def get_one_sentence(self, action):
        """对一个三元组进行回复
        """
        sentence = ""
        if action["diaact"] == "request":
            for one_item in self.request:
                if action["request_slots"].keys() == one_item["request_slots"].keys() and action["inform_slots"] == {}:
                    try:
                        values = list(action["request_slots"].values())
                        semantic_index = values[0] if values != ["UNK"] else "0"
                        index = random.randint(0, len(one_item["nl"][semantic_index]) - 1)
                        sentence = one_item["nl"][semantic_index][index]
                    except Exception:
                        sentence = one_item["nl"]["0"][0]
                    return sentence
        elif action["diaact"] == "inform":
            for one_item in self.inform:
                if action["inform_slots"].keys() == one_item["inform_slots"].keys() and action["request_slots"] == {}:
                    try:
                        values = list(action["inform_slots"].values())
                        semantic_index = values[0] if (values != ["UNK"] or values != [""]) else "0"
                        index = random.randint(0, len(one_item["nl"][semantic_index]) - 1)
                        sentence = one_item["nl"][semantic_index][index]
                    except Exception:
                        sentence = one_item["nl"]["0"][0]
                    return sentence
        elif action["diaact"] == "greeting":
            tem = self.greeting[0]
            try:
                index = random.randint(0, len(tem["nl"]["0"]) - 1)
                sentence = tem["nl"]["0"][index]
            except Exception:
                sentence = tem["nl"]["0"][0]
            return sentence
        elif action["diaact"] == "thanks":
            tem = self.thanks[0]
            try:
                index = random.randint(0, len(tem["nl"]["0"]) - 1)
                sentence = tem["nl"]["0"][index]
            except Exception:
                sentence = tem["nl"]["0"][0]
            return sentence
        elif action["diaact"] == "bye":
            tem = self.bye[0]
            try:
                index = random.randint(0, len(tem["nl"]["0"]) - 1)
                sentence = tem["nl"]["0"][index]
            except Exception:
                sentence = tem["nl"]["0"][0]
            return sentence
        else:
            return "您说的我不是很理解呢，请换一种方式说吧"

        
            

if __name__ == '__main__':
    print("testing.........")
    # dia_act = [
    #             {'diaact': 'request',
    #             'request_slots': {'know_about_ruisi': 'UNK'},
    #             'inform_slots': {}
    #             },
    #             {'diaact': 'request',
    #             'request_slots': {'know_about_ruisi': '2'},
    #             'inform_slots': {}
    #             },
    #             {'diaact': 'request',
    #             'request_slots': {'child_name': 'UNK'},
    #             'inform_slots': {}
    #             },
    #             {'diaact': 'request',
    #             'request_slots': {'phone_number': '1'},
    #             'inform_slots': {}
    #             },
    #            {'diaact': 'inform',
    #             'request_slots': {},
    #             'inform_slots': {'class_type': 'UNK'}
    #             },
    #            {'diaact': 'greeting',
    #             'request_slots': {},
    #             'inform_slots': {}
    #             },
    #            {'diaact': 'bye',
    #             'request_slots': {},
    #             'inform_slots': {}
    #             }
    #            ]
    dia_act = [{'diaact': 'inform', 'inform_slots': {'audition_free': ''}, 'request_slots': {}}, {'diaact': 'request', 'inform_slots': {}, 'request_slots': {'child_age': 'UNK'}}]
    nlg = NLG("nlg_template.json")
    for action in dia_act:
        print(nlg.get_one_sentence(action))

    print(nlg.get_sentence(dia_act))
