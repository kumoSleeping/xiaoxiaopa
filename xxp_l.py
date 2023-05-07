import asyncio
import websockets
import os
import json
import re
import aiohttp
import datetime


# 获取当前文件所在的目录
current_dir = os.path.dirname(__file__)
# 切换到当前文件所在的目录
os.chdir(current_dir)


# 用于aiohttp转发到xxp_c.py，如果需要修改请修改请同步修改xxp_c.py
send_port = 12709

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


with open('config/path.json', 'r', encoding='utf-8') as f:
    path_json = json.load(f)
path_str = path_json['path']


# 路径 🔧
path = path_str + current_dir + '/'


async def handle_message(websocket, ws_path, port):
    async for message in websocket:
        asyncio.create_task(process_message(websocket, message, port))
        asyncio.create_task(show_log(websocket, message, port))


async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    # server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    # server3 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port3), "localhost", port3)
    await server1.wait_closed()
    # await server2.wait_closed()
    # await server3.wait_closed()


async def process_message(websocket, message, port):
    try:
        msg = json.loads(message)
        # print(msg)
        url = f"http://127.0.0.1:{send_port}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(msg), headers={"Content-Type": "application/json"}) as response:
                await response.text()
    except Exception:
        print('Exception', message)
        pass


async def show_log(websocket, message, port):
    global mm, send_port_
    # print(message)
    try:
        msg = json.loads(message)
        mm = msg['message']

        if "[CQ:ima" in mm:
            show_mm = re.sub(r'\[.*?\]', '[图片]', mm)
        elif "[CQ:at" in mm:
            show_mm = re.sub(r'\[.*?\]', '[@消息]', mm)
        elif "[CQ:rep" in mm:
            show_mm = re.sub(r'\[.*?\]', '[回复消息]', mm)
        elif "[CQ:fac" in mm:
            show_mm = re.sub(r'\[.*?\]', '[表情]', mm)
        elif "[CQ:sha" in mm:
            show_mm = re.sub(r'\[.*?\]', '[分享]', mm)
        elif "[CQ:musi" in mm:
            show_mm = re.sub(r'\[.*?\]', '[音乐]', mm)
        elif "[CQ:redbag" in mm:
            show_mm = re.sub(r'\[.*?\]', '[红包]', mm)
        elif "[CQ:forward" in mm:
            show_mm = re.sub(r'\[.*?\]', '[转发消息]', mm)
        elif "[CQ:record" in mm:
            show_mm = re.sub(r'\[.*?\]', '[语音消息]', mm)
        elif "[CQ:" in mm:
            show_mm = re.sub(r'\[.*?\]', '[其他CQ消息]', mm)
        else:
            show_mm = mm
        mm_replace = show_mm.replace('\n', ' ')
        # 设置实时日志显示的消息长度 「   🔧   」
        max_length = 39
        if len(mm_replace) > max_length:
            truncated_mm = mm_replace[:max_length] + "..."
        else:
            truncated_mm = mm_replace
        try:
            print(f"[群组]{msg['group_id']}｜{msg['sender']['nickname']}: {truncated_mm}")
        except:
            try:
                print(f"[个人]{msg['sender']['nickname']}: {truncated_mm}")
            except:
                pass
        return

    except Exception:
        pass
        return


asyncio.get_event_loop().run_until_complete(start_servers())
asyncio.get_event_loop().run_forever()

