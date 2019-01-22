from client import Client

user_id = 0
host = "localhost"
port = 5000

cli = Client(user_id=user_id, host=host, port=port, session_id=None)
print("Successfully created a session with ID: " + cli.session_id)

print("agent: 您好，学科英语首创品牌“瑞思学科英语”欢迎您，本月免费试听中，名额有限！留下姓名及联系方式马上获取试听机会！抢约：400-610-1100")
ended = False
while not ended:
    user_input = input("user: ")
    resp = cli.response(user_input)
    ended = cli.ended
    print("agent: ", resp)