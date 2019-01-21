## Run in Ubuntu
1. 安装依赖
```
pip install -r requirements.txt
```
2. 执行server
```
gunicorn -b 0.0.0.0:5000 main:api
```
3. 查看是否成功启动：使用POSTMAN测试

## 接口说明
1. `GET /probe` -- 申请一个新的会话

所需参数
--------
* `user_id`: 用户的唯一ID

返回结果（若成功调用）
--------
一个JSON对象，其中`session_id`字段为此次会话分配到的UID (string类型)，之后使用POST方式交互均需要提供此UID作为参数。此次获取到的`session_id`会在对话结束或最后一次回复10分钟后失效。

成功调用示例
------------
```
GET http://localhost:5000/probe?user_id=123456
```
返回结果:
```
{
    "session_id": "0b9f54ae-1d15-11e9-9a75-0f9226be1a37",
    "status": {
        "code": 200,
        "message": "Successfully created a session for user 123456 for 10 mins"
    }
}
```

错误调用示例
------------
```
GET http://localhost:5000/probe
```
返回结果:
```
{
    "status": {
        "code": 500,
        "message": "No suffient params in request url"
    }
}
```
错误原因: `user_id`参数未指定

2. `POST /probe` -- 与之前通过`GET /probe`申请的会话进行交互

所需参数
--------
* `session_id`: 此前通过`GET /probe`获取到的会话ID
* `user_input`: 用户输入的对话文本

返回结果（若成功调用）
--------
一个JSON对象，其中`output`字段为系统返回的对于此次输入`user_input`的回复结果。

成功调用示例
------------
```
POST http://localhost:5000/probe 
```
request.body:
```
{
    "session_id": "0b9f54ae-1d15-11e9-9a75-0f9226be1a37",
    "user_input": "你好"
}
```
返回结果:
```
{
    "output": "恩，请问您是给几岁的孩子咨询瑞思的课程呢？",
    "status": {
        "code": 200,
        "message": "Successfully produced the response"
    }
}
```

错误调用示例1
-------------
request.body:
```
{
    "session_id": "0b9f54ae-1d15-11e9-9a75-0f9226be1a37",
}
```
返回结果:
```
{
    "status": {
        "code": 500,
        "message": "No suffient params in request url or the user session has been killed"
    }
}
```
错误原因: `user_input`未指定

错误调用示例2
-------------
request.body:
```
[
    'session_id': "0b9f54ae-1d15-11e9-9a75-0f9226be1a37"
    'user_input': "你好"
]
```
返回结果:
```
{
    "status": {
        "code": 40000,
        "message": "Traceback (most recent call last):\n  File ..."
    }
}
```
错误原因: JSON字符串格式错误

错误调用示例3
-------------
request.body:
```
{
    "session_id": "Some expired/wrong session id",
    "user_input": "你好"
}
```
返回结果:
```
{
    "status": {
        "code": 500,
        "message": "No suffient params in request url or the user session has been killed"
    }
}
```
可能的错误原因:
* 该`session_id`有误（即：该`session_id`不是此前通过`GET`方法获取到的`session_id`）
* 该`session_id`对应的会话已经过期（即在申请`session_id`后或最后一次交互后已经过10分钟）
* 该`session_id`对应的会话已经关闭（即此轮对话已经结束）
## docker部署（hold）
