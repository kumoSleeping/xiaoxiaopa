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
# 根据「QQ号」获取「http上报端口」
qq_send_dict = {
    config_1['qq_number']: config_1['http_port'],
}

with open('config/path.json', 'r', encoding='utf-8') as f:
    path_json = json.load(f)
path_str = path_json['path']


# 路径 🔧
path = path_str + current_dir + '/'


async def handle_message(websocket, ws_path, port):
    async for message in websocket:
        asyncio.create_task(process_message(websocket, message, port))
        '''
        输出控制台/日志 需要可以启用
        '''
        # asyncio.create_task(show_log(websocket, message, port))


async def start_servers():
    server1 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port1), "localhost", port1)
    # server2 = await websockets.serve(lambda ws, ws_path: handle_message(ws, ws_path, port2), "localhost", port2)
    await server1.wait_closed()
    # await server2.wait_closed()
'''
还可以添加更多账号
'''


async def process_message(websocket, message, port):
    try:
        msg = json.loads(message)
        mm = msg['message']
        # print(msg)
        url = f"http://127.0.0.1:{send_port}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(msg), headers={"Content-Type": "application/json"}) as response:
                await response.text()
    except Exception:
        pass


# 输出控制台/日志
# async def show_log(websocket, message, port):
    # global mm, send_port_
    # try:
    #     msg = json.loads(message)
    #     mm = msg['message']

        # 输出日志用，多账号自行添加elif, 懒得写列表了 「   🔧   」
        # if port == port1:
        #     a = '1号趴'
        # else:
        #     a = '2号趴'
        #
        # if "[CQ:ima" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[图片]', mm)
        # elif "[CQ:at" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[@消息]', mm)
        # elif "[CQ:rep" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[回复消息]', mm)
        # elif "[CQ:fac" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[表情]', mm)
        # elif "[CQ:sha" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[分享]', mm)
        # elif "[CQ:musi" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[音乐]', mm)
        # elif "[CQ:redbag" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[红包]', mm)
        # elif "[CQ:forward" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[转发消息]', mm)
        # elif "[CQ:record" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[语音消息]', mm)
        # elif "[CQ:" in mm:
        #     show_mm = re.sub(r'\[.*?\]', '[其他CQ消息]', mm)
        # else:
        #     show_mm = mm
        # mm_replace = show_mm.replace('\n', ' ')
        # # 设置实时日志显示的消息长度 「   🔧   」
        # max_length = 39
        # if len(mm_replace) > max_length:
        #     truncated_mm = mm_replace[:max_length] + "..."
        # else:
        #     truncated_mm = mm_replace
        # print(f"{a}｜({msg['group_id']})｜{msg['sender']['nickname']}: {truncated_mm}")
        # log_msg = f"{a}｜({msg['group_id']})｜{msg['sender']['nickname']}: {mm}"
        #
        # today = datetime.date.today()
        # filename = f"log/{today}.txt"
        #
        # if os.path.exists(filename):
        #     with open(filename, "a", encoding='utf-8') as log_file:
        #         log_file.write(log_msg + "\n")
        # else:
        #     with open(filename, "w", encoding='utf-8') as log_file:
        #         log_file.write(log_msg + "\n")
    #
    #     return
    #
    # except Exception:
    #     pass
    #     return


asyncio.get_event_loop().run_until_complete(start_servers())
asyncio.get_event_loop().run_forever()

