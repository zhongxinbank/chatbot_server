```
# Input

[
    {
        "diaact": "request",
        "inform_slots": {},
        "request_slots": {"child_age":"UNK"}  # value一般为"UNK"，也可能为"0","1","2"等
    },
    {
        "diaact": "inform",
        "inform_slots": {"teacher_nation":""},  # value一般为""，也可能为"0","1","2"等
        "request_slots": {}
    }
]
```
### 特殊情况说明
##### know_about_ruisi
- “0”表示不知道孩子的具体年龄
- “1”表示孩子的年龄在3-5岁之间（包含边界年龄）
- “2”表示孩子的年龄在6-12岁之间（包含边界年龄）
- “3”表示孩子的年龄在13-18岁之间（包含边界年龄）
- “4”表示孩子的年龄不在3-18岁之间

##### 针对可追问的slot，如phone_number
- “0”表示正常询问
- “1”表示用户未回答，系统第一次追问
- “2”表示用户未回答，系统第二次追问

```
# template

{
    "request": [
            {
                "request_slots": {"child_age":"UNK"},
                "nl": {"0": ["恩，请问您是给几岁的孩子咨询瑞思的课程呢？"]},
                "inform_slots": {}
            }],
    
    "inform":[
            {
                "request_slots": {}，
                "nl": {"0": ["好的，您可以直接拨打4006101100进行咨询,感谢您对瑞思英语的关注，祝您生活愉快，再见！"]},
                "inform_slots": {"user_goa":""}
            },
            { },
            { }]
}
```
### 需具备的功能
- 根据input和template给出相应的输出，输出为一个字符串
- 每个模板里“nl”是一个字典，key包括“0”，“1”，“2”，“3”等，这个数字有两个来源，一个是在输入中给出，一个是随机选择
- Input中给出的request_slots的value可能是"UNK"也可能是"0","1"等，当值为"UNK"时随机从nl中选择一句输出，当值为"0","1"等时选定对应句子输出

- 同理，Input中给出的inform_slots的value可能是""（空字符串）也可能是"0","1"等，当值为""时随机从nl中选择一句输出，当值为"0","1"等时选定对应句子输出

### Note
##### diaact
- 共五种：request，inform，greeting，bye，thanks

##### inform slots（用户提问系统需要回复的）
- sale: 优惠活动（最近有什么优惠活动吗？）
- other_contact: 用户确认能否留下其他的联系方式（留QQ/微信可以吗？）
- class_schedule: 时间安排、课时安排、上课时间（待定)
- audition_free: 询问试听是否免费（试听课免费吗？试听课是不是免费参加？）
- class_length: 询问一节课的长度（一节课有多长？）
- audition_introduction: 试听课介绍（你们有试听课吗？试听课怎么样？）
- textbook: 教材（你们用的是什么教材？）
- class_size: 班级人数（一个班有多少人？）
- length_of_per_period: 询问一期课程的长度（一个学期有多长？）
- teacher_nation: 老师的国籍（是外教吗？）
- class_type: 针对不同年龄段的课程介绍（？）
- fee: 学费（一期课多少钱？学费是多少？）
- ruisi_introduction: 瑞思的介绍（瑞思是个怎么样的机构？）
```
[sale, other_contact, class_schedule, audition_free, class_length, audition_introduction, textbook, class_size, length_of_per_period, teacher_nation, class_type, fee, ruisi_introduction]
```

##### request slots（系统可能会像用户提问的问题）
- child_age: 孩子的年龄
- english_level: 现在的英语水平
- special_need: 想提高孩子的哪些能力
- know_about_ruisi: 之前是否了解过瑞思
- client_location: 客户所在地
- phone_number: 联系电话
- client_name: 客户的称呼
- client_gender: 客户的性别
- child_name: 客户孩子的称呼
```

[child_age, english_level, special_need, know_about_ruisi, client_location, phone_number, client_name, client_gender, child_name]
```