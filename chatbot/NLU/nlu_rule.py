# Created by Helic on 2017/9/18

import jieba
import jieba.posseg as pseg
import json
import re


class NLU:
    def __init__(self):
        jieba.load_userdict('chatbot/NLU/data/dic.txt')
        with open("chatbot/NLU/data/slot_semantic_dict.json", encoding='utf-8') as f:
            self.slot_dict = json.load(f)

        # 读取stopwords
        self.stopwords = []
        with open("chatbot/NLU/data/stopword.txt", 'r', encoding='utf-8') as f:
            for item in f.readlines():
                self.stopwords.append(item.strip())
        self.stopwords.extend(['，', '。', '？', '“', '”', '‘', '’', '；', '：', '！', '、', '（', '）', '-', '=',
                               '【', '】', ' ', '{', '}', ',', '.', '/', '\\', '(', ')', '?', '!', ';', ':', '\'',
                               '"', '[', ']', '~', '\n', '\t'])
        # diaact
        self.diaact = ['inform', 'request', 'confirm_question', 'confirm_answer', 'thanks', 'bye', 'select', 'greeting']
        # 结束语
        self.bye_words = ['再见', 'bye', '拜', '拜拜', '白白', 'byebye']
        # greeting
        self.greeting_words = ['您好', '你好']
        # thanks
        self.thanks_words = ['谢谢', 'thanks']
        # user request slots
        self.request_slots = ['school_location', 'school_phone', 'sale', 'other_contact', 'cut_in', 'class_schedule',
                              'have_school_somewhere', 'attend_class_alone', 'allow_audition', 'audition_free',
                              'child_attend', 'allow_parents_together', 'class_length', 'audition_introduction',
                              'textbook', 'fulltime_or_sparetime', 'class_size', 'length_of_per_period',
                              'allow_return_premium', 'lesson_accompany', 'school_type', 'teacher_nation', 'class_type',
                              'online_course', 'online_course_location', 'fee']
        # user inform slots
        self.inform_slots = ['client_name', 'client_gender', 'child_name', 'child_age', 'child_grade', 'client_location'
                             , 'reserve_location', 'phone_number', 'english_level', 'special_need',
                             'attend_class_before', 'know_about_ruisi', 'user_goal', 'person_accompany', 'user_goal']

    def participle(self, raw_sentence):
        """对原始语句分词，去标点，返回两个列表，第一个为分词结果，第二个为词性列表"""
        m = []
        n = []
        # 年龄处理
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
            for i in range(index[-1]-index[0]):
                m[index[0]] += m[index[0]+i+1]
                m[index[0]+i+1] = ''
                n[index[0]+i+1] = ''
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

    def get_iob(self, m, n):
        """m为分词后的列表,n为词性列表"""
        iob = []
        i = 0
        while i < len(m):
            if n[i] == 'nr':  # 判别client_name和child_name，需要根据前一句话来判断
                # if 'B-client_name' in self.history[-1]['iob']:
                #     iob.append('B-client_name')
                # elif 'B-child_name' in self.history[-1]['iob']:
                #     iob.append('B-child_name')
                # else:
                #     pass
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
                elif m[i] in self.slot_dict['child_grade']:
                    iob.append('B-child_grade')
                elif m[i] in self.slot_dict['client_location']:
                    iob.append('B-client_location')
                elif m[i] in self.slot_dict['school_location']:
                    iob.append('B-school_location')
                elif m[i] in self.slot_dict['phone_number'] or re.findall("[1][358]\d{9}", m[i]):
                    iob.append('B-phone_number')
                elif m[i] in self.slot_dict['english_level']:
                    iob.append('B-english_level')
                elif m[i] in self.slot_dict['teacher_nation']:
                    iob.append('B-teacher_nation')
                elif m[i] in self.slot_dict['fee']:
                    iob.append('B-fee')
                elif m[i] in self.slot_dict['special_need']:
                    iob.append('B-special_need')
                elif m[i] in self.slot_dict['reserve_time']:
                    iob.append('B-reserve_time')
                elif m[i] in self.slot_dict['attend_class_before']:
                    iob.append('B-attend_class_before')
                elif m[i] in self.slot_dict['class_type']:
                    iob.append('B-class_type')
                elif m[i] in self.slot_dict['user_goal']:
                    iob.append('B-user_goal')
                else:
                    iob.append('O')
            i += 1
        return iob

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
        if history != [] and history[-1]['diaact']['diaact'] == 'confirm_question':
            diaact['diaact'] = 'confirm_answer'
            slot = list(history[-1]['diaact']['inform_slots'].keys())[0]
            if string[1] in ['可以', '好的', '没问题', '好']:
                diaact['inform_slots'][slot] = list(history[-1]['diaact']['inform_slots'].values())[0]
            else:
                diaact['request_slots'][slot] = 'UNK'
            return diaact

        while index < len(iob)+1:
            cur_tag = iob[index-1]
            if cur_tag == 'O' and pre_tag.startswith('B-'):
                slot = pre_tag.split('-')[1]   # slot_name
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
        if diaact['request_slots'] == {} and diaact['inform_slots'] == {}:
            for i in string:
                if i in self.greeting_words:
                    diaact['diaact'] = 'greeting'
                    return diaact
                elif i in self.thanks_words:
                    diaact['diaact'] = 'thanks'
                    return diaact
                else:
                    pass

        # set user_goal value = '预约' or '加盟'
        if 'user_goal' in diaact['inform_slots'] and diaact['inform_slots']['user_goal'] in ['预约', "咨询"]:
            diaact['inform_slots']['user_goal'] = "预约"
        # english_level,special_need,know_about_ruisi
        if history != [] and history[-1]["diaact"]["request_slots"] != {}:
            temp = list(history[-1]["diaact"]["request_slots"].keys())[0]
            if temp in ['english_level', 'special_need', 'know_about_ruisi']:
                diaact['inform_slots'][temp] = raw_sentence
            elif temp == "reserve_location":
                diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
            elif temp == "child_name":
                diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
            elif temp == "client_name":
                diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
            elif temp == "reserve_time":
                diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
            elif temp == "client_gender":
                diaact = {'diaact': 'inform', 'request_slots': {}, 'inform_slots': {temp: raw_sentence}}
            else:
                pass

        return diaact

    def get_diaact(self, raw_sentence, history):
        m, n = self.participle(raw_sentence)
        # print("word:{} ; gender:{}".format(m, n))
        iob = self.get_iob(m, n)
        # print("iob:", iob)
        diaact = self.iob_to_diaact(iob, m, history, raw_sentence)
        return diaact

# nlu = NLU()
# s = '2:30'
# m, n = nlu.participle(s)
# print(s)
# print(nlu.participle(s))


