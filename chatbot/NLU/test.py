# Created by Helic on 2017/9/19
import jieba
import json
import numpy
import jieba.posseg as pseg
import re
history = [
    {
        'speaker': 'agent',
        'nl': '',
        'dia_act': {'diaact': 'inform', 'inform_slots': {'client_name': '何邺'}, 'request_slots': {}},
        'index': 0,
        'end': True
    },
    {
        'speaker': 'agent',
        'nl': '',
        'iob': [],
        'diaact': {'diaact': 'inform', 'inform_slots': {'client_name': '何邺'}, 'request_slots': {}},
        'index': 0,
        'end': False
    }
]

sentence = {
    '1': [              # 一段完整对话
        {
            # 一句话
            'nl': '',
            'participle': [],
            'iob': [],
            'diaact': {},
            'speaker': ''
        },
        {
            'nl': '',
            'iob': [],
            'diaact': {},
            'speaker': ''
        }
    ],
    '2': [
        {
            'nl': '',
            'iob': [],
            'diaact': {},
            'speaker': ''
        },
        {
            'nl': '',
            'iob': [],
            'diaact': {},
            'speaker': ''
        }
    ]
}
# print(jieba.lcut('1年级'))
# with open('jsonFile.json', 'w', encoding='utf-8') as f:
#     jsObj = json.dump(sentence, f, ensure_ascii=False)         # 中文



request_slots = ['school_location', 'school_phone', 'sale', 'other_contact', 'cut_in', 'class_schedule',
                 'have_school_somewhere', 'attend_class_alone', 'allow_audition', 'audition_free', 'child_attend',
                 'allow_parents_together', 'class_length', 'audition_introduction', 'textbook', 'fulltime_or_sparetime',
                 'class_size', 'length_of_per_period', 'allow_return_premium', 'lesson_accompany', 'school_type',
                 'teacher_nation', 'class_type', 'online_course', 'online_course_location', 'fee']
inform_slots = ['client_name', 'client_gender', 'child_name', 'child_age', 'child_grade', 'client_location',
                'reserve_location', 'phone_number', 'english_level', 'special_need', 'attend_class_before',
                'know_about_ruisi', 'user_goal', 'person_accompany']


# s = '外教授课，瑞思英语'
# print(jieba.lcut(s))
# with open('3.json', 'r', encoding='utf-8') as f:
#     value = json.load(f)
#     new_json = {}
#     j = 343
#     for i in value.keys():
#         new_json[str(j)] = value[i]
#         j += 1
#     print(j)
#     with open('new_3.json', 'w', encoding='utf-8') as h:
#         jsObj = json.dump(new_json, h, ensure_ascii=False)

dic = {
    "a": 0,
    "b": 1
}
l = list(map(lambda x: dic[x], ['a', 'b']))
print(l)

print(numpy.random.choice(['a', 'b', 'c'], size=4))

# with open('3.json', 'r', encoding='utf-8') as f:
#     value = json.load(f)
#     new_json = {}
#     index = 177
#     for i in value.keys():
#         new_json[str(index)] = value[i]
#         index += 1

# with open('new_3.json', 'w', encoding='utf-8') as f:
#     jsObj = json.dump(new_json, f, ensure_ascii=False)         # 中文

l = re.findall("\d+岁.*?月|\d岁半|\d岁|\d+号上午|\d+号下午|\d+号晚上|\d+号|\d+[:：]\d+|[一二三四五六七八九]年级", "一年级")
m = re.findall("(.*?)市(.*?)区", "北京市海淀区")
print(m)
for i in l:
    jieba.add_word(i, freq=4)
    print(i)

print(pseg.lcut('6:30'))  # [pair('6', 'x'), pair(':', 'x'), pair('30', 'm')]
print(pseg.lcut('大班'))
print(pseg.lcut('两岁'))
print(pseg.lcut('2岁半'))
print(pseg.lcut('四岁半'))
print(pseg.lcut('6:30'))
print(pseg.lcut('2岁9个月'))
print(pseg.lcut('26号'))
print(pseg.lcut('六年级'))
print(pseg.lcut('11点'))
print(pseg.lcut('11点半'))
print(pseg.lcut('下午1点'))
print(pseg.lcut('26号下午'))

print(re.findall("\d", "5岁"))
