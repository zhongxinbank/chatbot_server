# Dialogue manager

- 功能

  1. 输入user action，根据内部对话逻辑返回相应的agent response action
  2. 不同slot的回复机制不同
   
     - 如果设置为必填slot，会反复提问三次
     - 如果为非必填slot，则会在用户未回答该slot后跳过该项
  
  3. 存储对话历史
   
   
- 格式
  
  Input：user action
  ```
  [{"diaact":"inform", "inform_slots":{},'request_slots': {},"nl":''},{}]
  ```

  Output：agent response action

  ```
  [{"diaact":"inform", "inform_slots":{},'request_slots': {},"nl":''},{}]
  ```
  history
  ```
  [
      { "speaker": "user or agent",
        "turn": "0"
        "content": [{ 'diaact': '',
                      'inform_slots': {},
                      'request_slots': {},
                      'nl': ''},     #如果是agent，nl为空字符串
                    {'diaact': '',
                      'inform_slots': {},
                      'request_slots': {},
                      'nl': ''}
                    ]},

      { "speaker": "user or agent",
        "turn": "1"
        "content": [{ 'diaact': '',
                      'inform_slots': {},
                      'request_slots': {},
                      'nl': ''},
                    {'diaact': '',
                      'inform_slots': {},
                      'request_slots': {},
                      'nl': ''}
                    ]}
  ]
   ```
- 特殊情况
  
  1. 以下需要check是否告知过child_age
   
        - know_about_ruisi
        - class_type
    
      返回：
        value = "0,1,2,3,4,UNK"
  

