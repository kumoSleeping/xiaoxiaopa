# <span style="color: orange;">这是一个kumo自用对接onebot平台的bot的框架</span>

# 「一」不用读这个，直接看下面的部署教程就行了（（
### xxp_l.py
xxp_l.py使用websockets连接多个go-cq实例，并接收来自它们的信息。它使用aiohttp异步框架将接收到的信息转发到Flask主进程xxp_c.py。
### xxp_c.py | xxp_p.py
xxp_c.py作为一个Flask应用，监听来自xxp_l.py的消息。一旦收到消息，它将根据插件名单动态**循环启用每一个插件函数**，每个插件都会向xxp_c.py请求必要数据，请求过程中，如果**发现插件被停用**或处于 **/模式**，xxp_c.py会**发送给插件的虚假的message**和**bot自身QQ号**，使得指令不被匹配，从而实现**插件管理**和 **/模式**。

在处理完消息后，xxp_c.py通过http将结果上报回go-cq。


##### 也就是说，初期配置之后，大部分情况只需要在xxp_p.py编写插件，在config文件夹注册插件，完全不需要管其他部分（除非你想要修改框架本身）。

## 小小趴框架的优点？
小小趴框架继承了纯flask框架**同步编程**的简单
同时可以实现**多账号连接**
**插件管理** 和 **/模式** 也算是锦上添花的功能

》》**/模式：被标记的插件必须加上 / 作为前缀才能触发**
一切还有待完善～
一起加油吧～
爱你们

# 「二」环境以及部署

## 1.安装python3以及必须库
[python官网](https://www.python.org/downloads/)
我们推荐您安装python3.9以上的版本，例如python3.11/3.10
#### 必须库
```shell
pip install flask aiohttp asyncio websockets requests pillow
```
或尝试
```shell
pip3 install flask aiohttp asyncio websockets requests pillow
```

## 2.安装和配置go-cqhttp
[go-cqhttp帮助中心](https://docs.go-cqhttp.org/guide/)
[go-cqhttp项目下载](https://github.com/Mrs4s/go-cqhttp/releases)
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
### <span style="color: red;">注意缩进！</span>
**可以更具需求修改 也可以直接使用给出的（推荐）**


## 3.配置config文件夹的 *bot1.json*
### 除了QQ号 你可以什么都不改
```json
{
    "qq_number": 114514,
    "http_port": 16800,
    "ws_port": 6800
}
```
qq_number填写bot的QQ号
剩下和go-cqhttp的yaml文件填写一致即可
## 4.配置config文件夹的 *path.json*
### 如果你是 Windows 你可以跳过，直接看「 5. 」
由于 macOS Linux 与 Windows 有盘符区别，我在文件夹里准备了备对应的path.json
根据系统选择对应的path.json

**如果不行你可以自己研究一下，主要是cq码用**
（把本地的文件拖入浏览器，看地址栏即可
## 5.关于运行
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
# 「三」使用沙盒编写一个插件
**注意xxp_sb.py**
这是一个模拟bot运行环境的沙盒
旨在方便的编写插件
***但是局限性非常大**

沙盒举了一个例子
```python
def test():
    mm, user_id, group_id, self_id = API.get_msg()
    if mm == '/jpg':
        aa = '''jpg ★★★★
喜报 xx -> 生成喜报图片

》》喵喵'''
        API.send(aa)
        return
    if mm.startswith('喜报 '):
        a = mm[2:]
        # 打开图片
        image = Image.open('multiple_Image/base/xb.png')
        # 获取图片的宽度和高度
        width, height = image.size
        # 创建图片绘制对象
        draw = ImageDraw.Draw(image)
        # 选择字体（这里使用了我从macOS搜出来的不知道什么玩意字体），字号36
        font = ImageFont.truetype("multiple_Image/base/123.ttf", 36)
        # 获取文字的宽度和高度
        text_width = draw.textlength(a, font=font)
        text_height = font.getbbox(a)[3]
        # 计算文字的坐标
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        # 设置文本颜色为红色
        text_color = (255, 0, 0)
        # 在图片上绘制文字
        draw.text((x, y), a, fill=text_color, font=font)
        # 保存修改后的图片
        # 发到cq
        API.send(pillow_to_cq(image))
    return "ok"
```

**当我们运行沙盒，会显示**
```
[ xiaoxiaopa_sandbox ]

平台群组123 用户123456: 喜报 我炸了 
bot: [图片]
```
**并展示图片**（如果有图形界面）
# 「四」注册/添加一个插件

## 1.注册插件
### 在config文件夹中的plugins.json中注册全部/群聊插件
### 在config文件夹中的private_plugins.json中注册私聊插件
**一般情况下只需要注册群聊注册私聊插件需要注意是否能运行**
**注意句末的英文逗号「 , 」**

>{"plugin": "函数名", "nickname": "描述"},

插入以下config文件夹对应的json中然后重启即可～
## 2.将函数粘贴到xxp_p.py中
就这么简单（
而你也可以通过导入调用外部文件什么都是可以的～

***推荐使用函数发送cq图片/语音 简化流程**
```python
# 路径+文件名转换cq码
def cq_img(file_name) -> str:
    return '[CQ:image,file={}{}]'.format(path, file_name)
```
```python
# pillow对象转换cq码（base64）
def pillow_to_cq(img) -> str:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    link = f"[CQ:image,file=base64://{img_str}]"
    return link
```

# 「五」连接多个go-cqhtp

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
## 3.修改 xxp_c.py，以读取QQ号/上报端口 信息
在文件中找到这么几行
```python
with open('config/bot1.json', 'r', encoding='utf-8') as f:
    config_1 = json.load(f)
port1 = config_1['ws_port']  # ws端口

# with open('config/bot2.json', 'r', encoding='utf-8') as f:
#     config_2 = json.load(f)
# port2 = config_2['ws_port']  # ws端口
#
# with open('config/bot3.json', 'r', encoding='utf-8') as f:
#     config_3 = json.load(f)
# port3 = config_3['ws_port']  # ws端口

# 根据「QQ号」获取「http上报端口」
qq_send_dict = {
    config_1['qq_number']: config_1['http_port'],
    # config_2['qq_number']: config_2['http_port'],
    # config_3['qq_number']: config_3['http_port'],
}
```
我们可以明显看出 被注释的代码用于用于**获取bot2.json，bot3.json的内容**，我们可以**把注释取消**
```python
with open('config/bot1.json', 'r', encoding='utf-8') as f:
    config_1 = json.load(f)
port1 = config_1['ws_port']  # ws端口

with open('config/bot2.json', 'r', encoding='utf-8') as f:
    config_2 = json.load(f)
port2 = config_2['ws_port']  # ws端口
#
# with open('config/bot3.json', 'r', encoding='utf-8') as f:
#     config_3 = json.load(f)
# port3 = config_3['ws_port']  # ws端口

# 根据「QQ号」获取「http上报端口」
qq_send_dict = {
    config_1['qq_number']: config_1['http_port'],
    config_2['qq_number']: config_2['http_port'],
    # config_3['qq_number']: config_3['http_port'],
}
```

## 4.修改 xxp_l.py，以读取QQ号/上报端口 信息
**切换到 xxp_l.py 文件，重复上面「 3. 」的操作就可以了**

## 5.在 xxp_l.py 的 start_servers 函数里添加协程
找到如下代码
```python
async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    # server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    # server3 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port3), "localhost", port3)
    await server1.wait_closed()
    # await server2.wait_closed()
    # await server3.wait_closed()
```
修改为
```python
async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    # server3 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port3), "localhost", port3)
    await server1.wait_closed()
    await server2.wait_closed()
    # await server3.wait_closed()
```
同理，添加更多账号只需添加更多的协程
