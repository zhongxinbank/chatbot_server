# Created by Helic on 2017/9/18

import jieba
import jieba.posseg as pseg
import json
import re
import warnings
from .intent import IntentInference


class NLU:
    def __init__(self, dic_path="./chatbot/NLU/data/dic.txt", slot_semantic_path="./chatbot/NLU/data/slot_semantic_dict.json",
                 stopwords_path="./chatbot/NLU/data/stopwords.txt",
                 intent_classifier_template_path="./chatbot/NLU/data/intent_classifier_template.json"):
        jieba.load_userdict(dic_path)
        with open(slot_semantic_path, encoding='utf-8') as f:
            self.slot_dict = json.load(f)

        # 读取stopwords
        self.stopwords = []
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            for item in f.readlines():
                self.stopwords.append(item.strip())
        self.stopwords.extend(['，', '。', '？', '“', '”', '‘', '’', '；', '：', '！', '、', '（', '）', '-', '=',
                               '【', '】', ' ', '{', '}', ',', '.', '/', '\\', '(', ')', '?', '!', ';', ':', '\'',
                               '"', '[', ']', '~', '\n', '\t'])

        # 读取意图分类模板
        with open(intent_classifier_template_path, encoding='utf-8') as f:
            self.intent_classifier_template = json.load(f)
        # 初始化神经网络意图分类模型
        self.intent_model = IntentInference(stopwords=self.stopwords, model_path="./chatbot/NLU/models",
                                            train_iob_path="./chatbot/NLU/data/processed_train_data.pkl")

        # diaact
        self.diaact = ['inform', 'request', 'thanks', 'bye']
        # 结束语
        self.bye_words = ['再见', 'bye', '拜', '拜拜', '白白', 'byebye']
        # thanks
        self.thanks_words = ['谢谢', 'thanks']
        # user request slots
        self.request_slots = list(self.intent_classifier_template.keys())
        # user inform slots
        self.inform_slots = ["child_age", "english_level", "special_need", "know_about_ruisi", "client_location",
                             "phone_number", "client_name", "client_gender", "child_name"]

    def participle(self, raw_sentence):
        """对原始语句分词，去标点，返回两个列表，第一个为分词结果，第二个为词性列表"""
        m = []
        n = []
        # 年龄处理
        replace_dict = {"一岁": "1岁", "二岁": "2岁", "两岁": "2岁", "三岁": "3岁", "四岁": "4岁", "五岁": "5岁", "六岁": "6岁", "七岁": "7岁", \
            "八岁": "8岁", "九岁": "9岁", "十岁": "10岁", "十一岁": "11岁", "十二岁": "12岁", "十三岁": "13岁", "十四岁": "14岁", "十五岁": "15岁", \
                "十六岁": "16岁", "十七岁": "17岁", "十八岁": "18岁", "十九岁": "19岁", "一年级": "7岁", "二年级": "8岁", "三年级": "9岁", \
                    "四年级": "10岁", "五年级": "11岁", "六年级": "12岁", "七年级": "13岁", "八年级": "14岁", "九年级": "15岁", "1年级": "7岁", \
                        "2年级": "8岁", "3年级": "9岁", "4年级": "10岁", "5年级": "11岁", "6年级": "12岁", "7年级": "13岁", "8年级": "14岁", \
                            "9年级": "15岁"}
        for key in replace_dict:
            raw_sentence = raw_sentence.replace(key, replace_dict[key])
        age_list = re.findall("\d+岁.*?月|\d+岁半|\d+岁|\d+年级|[一二三四五六七八九]年级", raw_sentence)
        # 日期时间处理
        time_list = re.findall("\d+号上午\d+点|\d+号下午\d+点|\d+号上午|\d+号下午|\d+号晚上|\d+号|\d+[:：]\d+", raw_sentence)
        total = age_list + time_list
        for i in total:
            jieba.add_word(i)
        for i, j in pseg.lcut(raw_sentence):  # 去标点
            if i not in self.stopwords:
                m.append(i)
                n.append(j)
        # 把地址合在一起，例如将['北京市','海淀区','西土城路']合称为'北京市海淀区西土城路'
        index = []
        for i in range(len(n)):
            if n[i] == 'ns':
                index.append(i)
        if len(index) > 1:
            for i in range(index[-1] - index[0]):
                m[index[0]] += m[index[0] + i + 1]
                m[index[0] + i + 1] = ''
                n[index[0] + i + 1] = ''
            x, y = [], []
            for i in m:
                if i != '':
                    x.append(i)
            for i in n:
                if i != '':
                    y.append(i)
        else:
            x, y = m, n
        return x, y

    def get_iob(self, m, n, history=None, last_request_slot=None):
        """m为分词后的列表,n为词性列表"""
        iob = []
        i = 0
        while i < len(m):
            if n[i] == 'nr':  # 判别client_name和child_name，需要根据前一句话来判断
                if last_request_slot and last_request_slot == 'client_name':
                    iob.append('B-client_name')
                elif last_request_slot and last_request_slot == 'child_name':
                    iob.append('B-child_name')
                else:
                    iob.append('B-client_name')
            elif n[i] == 'ns':  # 地名
                # if 'client_location' in self.history[-1]['dia_act']['request_slots']:
                #     iob.append('B-client_location')
                # if 'school_location' in self.history[-1]['dia_act']['request_slots']:
                #     iob.append('B-school_location')
                # if 'reserve_location' in self.history[-1]['dia_act']['request_slots']:
                #     iob.append('B-reserve_location')
                iob.append('B-client_location')
            else:
                if m[i] in self.slot_dict['child_age'] or re.findall('岁', m[i]) or re.findall("年级", m[i]):
                    iob.append('B-child_age')
                elif m[i] in self.slot_dict['phone_number'] or re.findall("[1][358]\d{9}", m[i]):
                    iob.append('B-phone_number')
                elif m[i] in self.slot_dict['teacher_nation']:
                    iob.append('B-teacher_nation')
                elif m[i] in self.slot_dict['class_type']:
                    iob.append('B-class_type')
                elif m[i] in self.slot_dict['client_gender']:
                    iob.append('B-client_gender')
                elif m[i] in self.slot_dict['textbook']:
                    iob.append('B-textbook')
                elif m[i] in self.slot_dict['sale']:
                    iob.append('B-sale')
                elif m[i] in self.slot_dict['audition_free']:
                    iob.append('B-audition_free')
                else:
                    iob.append('O')
            i += 1
        return iob

    # TODO 考虑如何处理同一句话中既包含inform信息又包含request信息，例如“我孩子5岁，适合上什么课程?”
    # 既应该返回 {"request": "class_type"} ，又需要将 {"child_age": "5岁"} 的信息提取出来
    def iob_to_diaact(self, iob, string, history, raw_sentence):
        """将iob转化为diaact,iob没有bos和intent，string是一个分词后列表（去stopwords）"""
        diaact = {}
        diaact['diaact'] = ""
        diaact['request_slots'] = {}
        diaact['inform_slots'] = {}

        # confirm iob != [],or return diaact = {}
        if iob == []:
            return {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {}}

        string.append('EOS')
        string.insert(0, 'BOS')
        pre_tag_index = 0
        pre_tag = 'bos'
        index = 1
        slot_val_dict = {}

        # bye
        for i in string:
            if i in self.bye_words:
                diaact['diaact'] = 'bye'
                diaact['inform_slots'] = {}
                diaact['request_slots'] = {}
                return diaact

        # confirm_answer
        # if history and history[-1]['diaact']['diaact'] == 'confirm_question':
        #     diaact['diaact'] = 'confirm_answer'
        #     slot = list(history[-1]['diaact']['inform_slots'].keys())[0]
        #     if string[1] in ['可以', '好的', '没问题', '好']:
        #         diaact['inform_slots'][slot] = list(history[-1]['diaact']['inform_slots'].values())[0]
        #     else:
        #         diaact['request_slots'][slot] = 'UNK'
        #     return diaact

        while index < len(iob) + 1:
            cur_tag = iob[index - 1]
            if cur_tag == 'O' and pre_tag.startswith('B-'):
                slot = pre_tag.split('-')[1]  # slot_name
                slot_val_str = ' '.join(string[pre_tag_index:index])  # B-slot 对应的word
                slot_val_dict[slot] = slot_val_str
            elif cur_tag.startswith('B-') and pre_tag.startswith('B-'):
                slot = pre_tag.split('-')[1]
                slot_val_str = ' '.join(string[pre_tag_index:index])
                slot_val_dict[slot] = slot_val_str
            elif cur_tag.startswith('B-') and pre_tag.startswith('I-'):
                if cur_tag.split('-')[1] != pre_tag.split('-')[1]:
                    slot = pre_tag.split('-')[1]
                    slot_val_str = ' '.join(string[pre_tag_index:index])
                    slot_val_dict[slot] = slot_val_str
            elif cur_tag == 'O' and pre_tag.startswith('I-'):
                slot = pre_tag.split('-')[1]
                slot_val_str = ' '.join(string[pre_tag_index:index])
                slot_val_dict[slot] = slot_val_str

            if cur_tag.startswith('B-'):
                pre_tag_index = index

            pre_tag = cur_tag
            index += 1

        if cur_tag.startswith('B-') or cur_tag.startswith('I-'):
            slot = cur_tag.split('-')[1]
            slot_val_str = ' '.join(string[pre_tag_index:-1])
            slot_val_dict[slot] = slot_val_str
            # print('slot_val_dict:', slot_val_dict)

        for item in slot_val_dict.keys():
            if item in self.request_slots:
                diaact['request_slots'][item] = 'UNK'
            elif item in self.inform_slots:
                diaact['inform_slots'][item] = slot_val_dict[item]
            else:
                pass

        # 判断intent
        if diaact['request_slots'] == {}:
            diaact['diaact'] = 'inform'
        else:
            diaact['diaact'] = 'request'
        # greeting and thanks
        # if diaact['request_slots'] == {} and diaact['inform_slots'] == {}:
        #     for i in string:
        #         if i in self.greeting_words:
        #             diaact['diaact'] = 'greeting'
        #             return diaact
        #         elif i in self.thanks_words:
        #             diaact['diaact'] = 'thanks'
        #             return diaact
        #         else:
        #             pass

        # set user_goal value = '预约' or '加盟'
        if 'user_goal' in diaact['inform_slots'] and diaact['inform_slots']['user_goal'] in ['预约', "咨询"]:
            diaact['inform_slots']['user_goal'] = "预约"

        # english_level,special_need,know_about_ruisi
        temp = ""
        if history and history[-1]["content"]:
            try:
                for item in history[-1]["content"]:
                    if item["diaact"] == "request":
                        temp = list(item["request_slots"].keys())[0]
                        break  # agent每次只会问一个slot
            except Exception:
                temp = ""
        if temp in ['english_level', 'special_need', 'know_about_ruisi']:
            diaact['inform_slots'][temp] = raw_sentence
        # elif temp == "child_name":
        #     diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
        # elif temp == "client_name":
        #     diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
        # elif temp == "client_gender":
        #     diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
        else:
            pass

        return diaact

    def get_diaact(self, raw_sentence, history=None, last_request_slot=None):
        """
        输入首先分句，之后分别要经过意图分类器，之后根据意图识别结果执行相应动作：
            1. 如果识别是request_xxx，则直接返回{'diaact': 'request', 'request_slots': {'request_xxx': 'UNK'}, 'inform_slots': {}}；
            2. 如果是request，则直接返回{'diaact': 'request', 'request_slots': {}, 'inform_slots': {}}；
            3. 如果是inform，则进行IOB标注
        :param raw_sentence: str
        :param history: [
                           {    "speaker": "user or agent",
                                "turn": "0"
                                "content": [{  'diaact':'',
                                 'inform_slots':{},
                                 'request_slots':{},
                                 'nl':''},   # 如果是agent，nl为空字符串
                                   {  'diaact':'',
                                 'inform_slots':{},
                                 'request_slots':{},
                                 'nl':''}
                             ]},

                         {    "speaker": "user or agent",
                                "turn": "1"
                                "content": [{  'diaact':'',
                                 'inform_slots':{},
                                 'request_slots':{},
                                 'nl':''},
                                   {  'diaact':'',
                                 'inform_slots':{},
                                 'request_slots':{},
                                 'nl':''}
                             ]}
                        ]
        :return: list, [{'diaact': '', 'request_slots': {}, 'inform_slots': {}}]
        """
        result = []
        # TODO raw_sentence需要校验
        sentence_list = None
        for s in ['，', '。', '？', '；', '：', '！', '、', ',', '.', '?', '!', ';', ':', '~', '\n', '\t']:
            if s in raw_sentence:
                sentence_list = raw_sentence.split(s)
                break
        sentence_list = sentence_list if sentence_list else [raw_sentence]
        # 意图分类
        for s in sentence_list:
            intent = self.intent_classify(s)
            if "request_" in intent:
                slot_name = re.findall('request_(.*?)$', intent)[0]
                result.append({'diaact': 'request', 'request_slots': {slot_name: 'UNK'}, 'inform_slots': {}, 'nl': s})
            # elif intent == "request":
            #     # 通用回复
            #     result.append({'diaact': 'request', 'request_slots': {}, 'inform_slots': {}, 'nl': s})
            else:
                m, n = self.participle(s)
                # print("word:{} ; gender:{}".format(m, n))
                iob = self.get_iob(m, n, last_request_slot=last_request_slot)
                # print("iob:", iob)
                diaact = self.iob_to_diaact(iob, m, history, raw_sentence)
                diaact['nl'] = s
                result.append(diaact)

        # 对于多个diaact的情况，需要做一些后处理：如果是两个inform（或request）的diaact，则需要合并成一个
        request_slots, inform_slots = {}, {}
        for i in range(len(result)):
            if result[i]['diaact'] == 'bye':
                return [{'diaact': 'bye', 'request_slots': {}, 'inform_slots': {}, 'nl': raw_sentence}]
            request_slots.update(result[i]['request_slots'])
            inform_slots.update(result[i]['inform_slots'])
        if request_slots and inform_slots:
            result = [{'diaact': 'request', 'request_slots': request_slots, 'inform_slots': {}, 'nl': raw_sentence},
                      {'diaact': 'inform', 'request_slots': {}, 'inform_slots': inform_slots, 'nl': raw_sentence}]
        elif not request_slots and inform_slots:
            result = [{'diaact': 'inform', 'request_slots': {}, 'inform_slots': inform_slots, 'nl': raw_sentence}]
        elif request_slots and not inform_slots:
            result = [{'diaact': 'request', 'request_slots': request_slots, 'inform_slots': {}, 'nl': raw_sentence}]
        else:
            result = [{'diaact': 'inform', 'request_slots': {}, 'inform_slots': {}, 'nl': raw_sentence}]
        return result

    # TODO 当agent request child_age时，用户正常的回答一旦涉及“年级”（例如“上1年级了”、“上小学二年级”等），
    # 就大概率会被分到request_class_type中，而无法返回应有的inform中，原因是request_class_type的训练数据
    # 大量包含用户阐述自己孩子年龄、年级然后进行询问的样本（例如“我家孩子现在上一年级了，上什么课程比较好？”），
    # 导致模型对此相当敏感。
    def intent_classify(self, raw_sentence, threshold=0.8):
        """
        意图分类器: rule + network
        :param raw_sentence: str
        :param threshold: 0.7 for model
        :return: str 默认返回inform
        """
        # rule
        for intent in self.intent_classifier_template:
            for pattern in self.intent_classifier_template[intent]:
                if re.search(pattern, raw_sentence):
                    return "request_" + intent
        # model
        result = self.intent_model.inference_sent(sentence=raw_sentence, threshold=threshold)
        warnings.warn("model predict : {}".format(result))
        return "request_" + result['label'] if result['label'] else "inform"


if __name__ == '__main__':
    sentence = "5岁，课程主要有哪些内容？"
    history = [
        {
            'speaker': 'agent',
            'nl': '',
            'diaact': {'diaact': 'inform', 'inform_slots': {'client_name': '何邺'}, 'request_slots': {}},
            'index': 0,
            'end': True
        }
    ]
    nlu = NLU(dic_path="./data/dic.txt", slot_semantic_path="./data/slot_semantic_dict.json",
              stopwords_path="./data/stopword.txt",
              intent_classifier_template_path="./data/intent_classifier_template.json")
    print(nlu.get_diaact(sentence, history))
