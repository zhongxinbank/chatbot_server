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

## TODO
对话核心逻辑未添加，只是个基础架构


## docker部署（hold）