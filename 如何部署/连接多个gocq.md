# 1.在config文件夹新建bot2.json
### *bot2.json*
```json
{
    "qq_number": 114515,
    "http_port": 16900,
    "ws_port": 6900
}
```
端口和之前bot不同即可
# 2.配置新添加账号的go-cqhttp
使用和之前一样的方法，注意端口和新的bot2.json一致
```yaml
# 连接服务列表
servers:
  - http: # HTTP 通信设置
      address: 0.0.0.0:16900 # HTTP监听地址
      timeout: 500      # 反向 HTTP 超时时间, 单位秒，<5 时将被忽略
      long-polling:   # 长轮询拓展
        enabled: false       # 是否开启
        max-queue-size: 2000 # 消息队列大小, 0 表示不限制队列大小，谨慎使用
      middlewares:
        <<: *default # 引用默认中间件
      post:           # 反向HTTP POST地址列表

  - ws-reverse:
      # 是否禁用当前反向WS服务
      disabled: false
      # 反向WS Universal 地址
      universal: ws://localhost:6900
      # 重连间隔 单位毫秒
      reconnect-interval: 300
      middlewares:
        <<: *default # 引用默认中间件
```
# 3.修改 xxp_l.py，以读取QQ号/上报端口 信息
在文件中找到这么几行
```python
with open('config/bot1.json', 'r', encoding='utf-8') as f:
    config_1 = json.load(f)
port1 = config_1['ws_port']  # ws端口

# 根据「QQ号」获取「http上报端口」
qq_send_dict = {
    config_1['qq_number']: config_1['http_port'],
}
```
我们可以明显看出 这段代码用于用于**获取bot1.json的内容**，我们可以**复制一份**，**修改一下变量名**，然后再添加一个bot2.json的内容
修改后内容大致如下
```python
with open('config/bot1.json', 'r', encoding='utf-8') as f:
    config_1 = json.load(f)
port1 = config_1['ws_port']  # ws端口

with open('config/bot2.json', 'r', encoding='utf-8') as f:
    config_2 = json.load(f)
port2 = config_2['ws_port']  # ws端口

# 根据「QQ号」获取「http上报端口」
qq_send_dict = {
    config_1['qq_number']: config_1['http_port'],
    config_2['qq_number']: config_2['http_port'],
}
```
# 4.在 xxp_l.py 的 start_servers 函数里添加协程
找到如下代码
```python
async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    # server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    await server1.wait_closed()
    # await server2.wait_closed()
```
修改为
```python
async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    await server1.wait_closed()
    await server2.wait_closed()
```
同理，添加更多账号只需添加更多的协程