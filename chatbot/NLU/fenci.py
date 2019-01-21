# Created by Helic on 2017/9/21

from NLU.nlu_rule import NLU
import json
import xlrd
import re

# 打开文件
workbook = xlrd.open_workbook('data/ruisi.xlsx')
sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
total_row = sheet1.nrows             # 行
total_col = sheet1.ncols             # 列

# 初始化nlu
nlu = NLU()

# 读取Excel
i = 0
dialog_id = -1
sentence = {}
dialog = []
all_dialog = {}
while i < total_row:
    row_value = sheet1.row_values(i)
    # print('row_value : ', row_value)
    if row_value != ['', '']:
        if re.findall('\d', str(row_value[0])):
            dialog_id += 1
            # print('dialog_id : ', dialog_id)
        else:
            speaker = row_value[0]
            content = str(row_value[1]).strip()
            sentence['nl'] = content
            sentence['speaker'] = speaker
            if speaker == 'client':
                sentence['participle'], n = nlu.participle(content)
                sentence['iob'] = nlu.get_iob(sentence['participle'], n)
                # sentence['diaact'] = nlu.iob_to_diaact(sentence['iob'], sentence['participle'])
                sentence['diaact'] = {'diaact': '', 'inform_slots': {}, 'request_slots': {}}
            else:
                if not re.findall('抢约：400-610-1100', content):
                    sentence['participle'] = []
                    sentence['iob'] = []
                    sentence['diaact'] = {'diaact': '', 'inform_slots': {}, 'request_slots': {}}
                else:
                    sentence['participle'] = []
                    sentence['iob'] = []
                    sentence['diaact'] = {'diaact': 'greeting', 'inform_slots': {}, 'request_slots': {}}
            dialog.append(sentence)
            sentence = {}
    else:
        all_dialog[str(dialog_id)] = dialog
        dialog = []
    i += 1
# 最后一个对话
all_dialog[str(dialog_id)] = dialog
# print('dialog : ', dialog)

# 写入json
# dic = {}
# for i in range(len(all_dialog)):
#     dic[str(i)] = all_dialog[str(i)]
#     i += 1
with open('data/ruisi.json', 'w', encoding='utf-8') as f:
    jsObj = json.dump(all_dialog, f, ensure_ascii=False)         # 中文
