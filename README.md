# 「一」这是一个kumo对接onebot平台的bot的框架

## 小小趴框架是如何工作的？
### xxp_l.py
xxp_l.py使用websockets连接多个go-cq实例，并接收来自它们的信息。它使用aiohttp异步框架将接收到的信息转发到Flask主进程xxp_c.py。
### xxp_c.py | xxp_p.py
xxp_c.py作为一个Flask应用，监听来自xxp_l.py的消息。一旦收到消息，它将根据插件名单动态导入xxp_p.py中的函数作为插件，从而实现插件管理。

在处理完消息后，xxp_c.py通过http将结果上报回go-cq。


##### 也就是说，初期配置之后，大部分情况只需要在xxp_p.py编写插件，xxp_c.py注册插件，完全不需要管其他部分（除非你想要修改框架本身）。

## 小小趴框架的优点？
小小趴框架继承了纯flask框架**同步编程**的优点
同时可以实现**多账号连接**
**插件管理**也算是锦上添花的功能
一切还有待完善～
一起加油吧～
爱你们

# 「二」环境以及部署

## 1.安装python3以及必须库
我们推荐您安装python3.9以上的版本，例如python3.11/3.10
#### 必须库
```shell
pip install flask aiohttp asyncio websockets requests
```
或尝试
```shell
pip3 install flask aiohttp asyncio websockets requests
```

## 2.安装和配置go-cqhttp
在官网下载最新版，按照官网教程创建出yaml以后，用下面的配置覆盖掉原来的部分
```yaml
# 连接服务列表
servers:
  - http: # HTTP 通信设置
      address: 0.0.0.0:16800 # HTTP监听地址
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
      universal: ws://localhost:6800
      # 重连间隔 单位毫秒
      reconnect-interval: 300
      middlewares:
        <<: *default # 引用默认中间件
```


## 3.配置config文件夹
### *bot1.json*
```json
{
    "qq_number": 114514,
    "http_port": 16800,
    "ws_port": 6800
}
```
qq_number填写bot的QQ号
剩下和go-cqhttp的yaml文件填写一致即可
### *path.json*
由于 macOS 与 Linux 没有盘符，只需要填写
```json
[
    {
        "administer": "file://"
    }
]
```
而Windows需要填写
```json
[
    {
        "administer": "file:///"
    }
]
```
**如果不行你可以自己研究一下，主要是cq码用**
```python
# 路径 🔧
path = path_str + current_dir + '/'
```
（把本地的文件拖入浏览器，看地址栏即可
## 4.关于运行
每次运行时,你需要启动
>go-cqhttp

>xxp_l.py

>xxp_c.py

**运行时需要保证对应端口统一且没被占用**
**一般来说按照上面填就不会有问题**
（如果你是在Linux环境下，注意程序的保活（如用pm2管理））

**初始设定下，在运行时修改文件并保存，bot就会重启**
你可以将**debug**和**use_reloader**设置为**False**防止自动重启
如：
```python
if __name__ == '__main__':
    app.run(port=send_port, host='0.0.0.0', debug=False, use_reloader=False)
```

# 「三」添加一个插件

## 1.在xxp_c.py中注册
一般情况下只需要注册群聊
**注册私聊插件需要特别判断user_id**
**注意句末的逗号「 , 」**
格式为
>{"plugin": "函数名", "nickname": "描述"},

插入以下位置
```python
# 全部插件
plugins = [
    {"plugin": "ran", "nickname": "事件骰子"},
    {"plugin": "jue", "nickname": "撅@"},
    {"plugin": "be_poke", "nickname": "戳一戳"},
    {"plugin": "test", "nickname": "测试用"},
    {"plugin": "echo", "nickname": "管理员指令"}
]
# 私聊插件
plugins_private = [
    {"plugin_private": "ran", "nickname": "事件骰子"}
]
```
## 2.根据需要创建函数
下面举了一个例子
```python
def test():
    # msg是从cq收到的json
    msg = request.get_json()
    # mm是json里的一个键，值为收到的消息
    mm = msg['message']
    if mm == '/test':
        aa = '''test ★★
test -> test
'''
        # 使用API类里的send函数发送
        API.send(aa)
        # 返回类型是字符串，可以任意，return的作用是结束函数
        return 'ok'
    # 判断mm是否在列表里
    if mm in ['晚上好', '晚好']:
        API.send('好你吗')
        return 'ok'
    return 'ok'
```
在这个例子里我们只需要使用mm（收到的消息）
1.当mm为/test的时候给出 使用说明/提示
2.当mm在['晚上好', '晚好']这个列表里的时候，使用API类里的send函数发送 好你吗
如果都不符合就不管，直接return 'ok'结束函数

### 另外，如果你想要使用其他的API，可以在API类里面添加，然后在xxp_c.py里面导入
例如改名
### 推荐使用函数发送cq图片/语音 简化流程
例如
```python
def cq_img(file_name) -> str:
    return '[CQ:image,file={}{}]'.format(path, file_name)
```
原本我需要使用
```python
API.send(f"[CQ:image,file={path}bpk/小小趴/1.jpg]")
```
现在只需要
```python
API.send(cq_img('bpk/小小趴/1.jpg'))
```

# 「四」连接多个go-cqhtp

## 1.在config文件夹新建bot2.json
### *bot2.json*
```json
{
    "qq_number": 114515,
    "http_port": 16900,
    "ws_port": 6900
}
```
端口和之前bot不同即可
## 2.配置新添加账号的go-cqhttp
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
## 3.修改 xxp_l.py，以读取QQ号/上报端口 信息
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
## 4.在 xxp_l.py 的 start_servers 函数里添加协程
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
