from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import json
import re
from io import BytesIO
import base64



# from flask import Flask, request
# # 导入，以及名为API的类
# import random
# import pandas as pd
# from PIL import Image, ImageDraw, ImageFont, ImageEnhance
# import time
# import datetime
# import numpy as np
# import os
# import copy
# import requests
# import textwrap
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta, timezone
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import json
# import math
# # 调用了unibot的代码(5k兆年
# import string
# import re
# import urllib.parse
# from io import BytesIO
# import glob
# import matplotlib.pyplot as plt
# from sklearn.linear_model import LinearRegression
# import matplotlib.ticker as mticker
# import matplotlib.dates as mdates
# from collections import Counter
# from pydub import AudioSegment





current_dir = os.path.dirname(__file__)
# 切换到当前文件所在的目录
os.chdir(current_dir)

with open('config/path.json', 'r', encoding='utf-8') as f:
    path_json = json.load(f)
path_str = path_json['path']
# 路径 🔧
path = path_str + current_dir + '/'


def cq_img(file_name) -> str:
    return '[CQ:image,file={}{}]'.format(path, file_name)


def pillow_to_cq(img) -> str:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    link = f"[CQ:image,file=base64://{img_str}]"
    return link


def cq_at(user_id) -> str:
    return '[CQ:at,qq={}]'.format(user_id)


class API:
    @staticmethod
    def get_msg():
        return mm, user_id, group_id, self_id
    # 标记为静态
    @staticmethod
    # 定义标准send，用于发送大部分通过接收到「消息」进行的「回复」
    def send(message):
        # 正则检测cq码形式图片并替换为[图片]
        pattern = re.compile(r'\[CQ:image,file=(.*?)\]')
        rpl = re.sub(pattern, '[图片]', message)

        # 输出消息
        # print(rpl)
        print("\x1b[31mbot: " + "\x1b[32m" + rpl + "\x1b[0m")

        # 检查消息中是否包含图片
        images = re.findall(pattern, message)
        for url in images:
            # 判断图片路径是否为base64编码
            if url.startswith("base64://"):
                # 移除base64协议前缀
                data = url[9:]
                # 将base64编码的数据解码成二进制数据
                image_data = base64.b64decode(data)
                # 创建BytesIO对象
                image_stream = BytesIO(image_data)
                # 使用Pillow打开图片
                image = Image.open(image_stream)
                # 显示图片
                image.show()
            else:
                # 调用show_image方法显示图片
                API.show_image(url)

    # 定义一个新的方法，用于显示图片
    @staticmethod
    def show_image(url):
        # 打开图片并读取数据
        image_data = urlopen(url).read()
        # 将图片数据转为二进制流
        image_stream = BytesIO(image_data)
        # 使用pillow打开图片
        image = Image.open(image_stream)
        # 显示图片
        image.show()

def show_user_mm():
    '''展示提示/用户消息'''
    print(f"\n\x1b[33m[ xiaoxiaopa_sandbox ]\n\n\x1b[31m平台群组{group_id} 用户{user_id}: \x1b[32m{mm} \x1b[0m")
    return 'sb'


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


'''
mm为用户输入的消息
user_id为用户QQ号
自行添加更多需要的信息
'''
mm = '喜报 我炸了'
group_id = 123
user_id = 123456
self_id = 114514

# 启用必要函数
show_user_mm()



'''启用函数'''
test()