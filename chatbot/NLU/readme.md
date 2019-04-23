## How to use
```python
from ./NLU/nlu_rule import NLU

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
nlu = NLU(dic_path="./NLU/data/dic.txt", slot_semantic_path="./NLU/data/slot_semantic_dict.json",
          stopwords_path="./NLU/data/stopword.txt", intent_classifier_template_path="./NLU/data/intent_classifier_template.json")
print(nlu.get_diaact(sentence, history))  # 这个history参数暂时可以固定下来，之后会修改
```

**return format**: 

`[{'diaact': 'inform', 'request_slots': {}, 'inform_slots': {'child_age': '5岁'}}, {'diaact': 'request', 'request_slots': {'class_type': 'UNK'}, 'inform_slots': {}}]
`

Note: 如果出现未识别的情况，请在NLU/data/intent_classifier_template.json中添加规则，之后也会更新一版神经网络的意图识别，返回格式保持一致。