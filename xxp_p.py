from flask import Flask, request
# 导入，以及名为API的类
from xxp_c import API
import xxp_c as xiaoxiaopa_control
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import json
from io import BytesIO
import base64


current_dir = os.path.dirname(__file__)
# 切换到当前文件所在的目录
os.chdir(current_dir)

path = xiaoxiaopa_control.path

qq_send_dict = xiaoxiaopa_control.qq_send_dict


def cq_img(file_name) -> str:
    return '[CQ:image,file={}{}]'.format(path, file_name)


def cq_at(user_id) -> str:
    return '[CQ:at,qq={}]'.format(user_id)


def pillow_to_cq(img) -> str:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    b64_cq = f"[CQ:image,file=base64://{img_str}]"
    return b64_cq


def sb_plugin():
    global output_img
    mm, user_id, group_id, self_id = API.get_msg()
    # 如果不是message类型消息可以结束了
    if mm is None or mm == '':
        return
    # 用于生成插件管理图片
    
    # 检查 黑名单 xxp标记 是否存在，如果不存在则创建
    file_path = 'config/plugin_config/{}negative_list.json'.format(group_id)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('[]')
        print("文件已创建！")
    if not os.path.exists('config/plugin_config/{}black_list.json'.format(group_id)):
        black_list = [
            {"plugin": "lfmb"},
            {"plugin": "scj"},
            {"plugin": "hj"},
            {"plugin": "test"}
        ]
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(black_list, f, ensure_ascii=False)

    def plugin_rpl():
        if group_id == 0:
            plugins_private = xiaoxiaopa_control.plugins_private
            nicknames = []
            for item in plugins_private:
                if item['plugin_private']:
                    nicknames.append('⬇/{}\n'.format(item['plugin_private']) + item['nickname'])
            on_plugin = '\n'.join(nicknames)
            output = """用「/ + 指令简称」查询～
下面是私聊插件～"""
            rpl = output + '\n' + on_plugin
            return rpl
        
        negative_list_json_plugin = []  # 存储具有 / 标记 插件名
        
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list_json_all_and_help = json.load(f)
        black_list_json_plugin = [item['plugin'] for item in black_list_json_all_and_help]
        
        # 检查是否存在 / 标记的插件
        file_path = 'config/plugin_config/{}negative_list.json'.format(group_id)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                negative_list = json.load(f)
                negative_list_json_plugin = [item['plugin'] for item in negative_list]
        
        plugins_list_all_and_help = xiaoxiaopa_control.plugins
        
        nicknames_on = []  # 启用的插件
        nicknames_xxp = []  # 含有 / 标记的插件
        nicknames_off = []  # 未启用的插件
        
        for item in plugins_list_all_and_help:
            if item['plugin'] not in black_list_json_plugin:
                if item['plugin'] in negative_list_json_plugin:  # 检查是否含有 / 标记
                    nicknames_xxp.append('⬇/{}\n'.format(item['plugin']) + item['nickname'])
                else:
                    nicknames_on.append('⬇/{}\n'.format(item['plugin']) + item['nickname'])
            else:
                nicknames_off.append('⬇/{}\n'.format(item['plugin']) + item['nickname'])
        
        on_plugin = '\n'.join(nicknames_on)
        xxp_plugin = '\n'.join(nicknames_xxp)
        off_plugin = '\n'.join(nicknames_off)

        output_1 = '\n★★★★★已启用\n' + on_plugin
        output_2 = '\n★★★★★含有 / 标记\n' + xxp_plugin
        output_3 = '\n★★★★★未启用\n' + off_plugin
        output = output_1 + output_2 + output_3
        rpl = output
        return rpl

    if mm == 'help' or mm == '帮助' or mm == '使用说明' or mm == '/help' or mm == '插件管理':
        a_xxp = '''xiaoxiaopa.com -> 小小趴官网～

/插件名 -> 查看插件用法～
停用 插件名 -> 停用插件
启用 插件名 -> 启用插件
-/ 插件名 -> 删除 / 标记
+/ 插件名 -> 添加 / 标记

》》/ 标记：被标记的插件必须加上 / 作为前缀才能触发
'''
        rpl = plugin_rpl()
        t2 = '''》》任何人都有权限使用～🍊'''
        send = a_xxp + rpl + t2
        API.send(send)       
         
    elif mm.startswith('停用'):
        mm = mm.replace("停用", "").strip()
        plugins = xiaoxiaopa_control.plugins
        
        # 获取插件列表
        plugins = [item['plugin'] for item in plugins]
        
        # 读取黑名单列表
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list = json.load(f)
        
        # 检测插件是否已经在黑名单中
        if any(plugin['plugin'] == mm for plugin in black_list):
            API.send('该插件已经被停用！')
            return
        
        # 检查要停用的插件是否存在
        if mm not in plugins:
            # API.send('没找到哦～！')
            return
        
        # 如果要停用的插件不在黑名单中，则添加新元素
        new_plugin = {"plugin": mm}
        black_list.append(new_plugin)
        
        # 将更新后的列表写入 JSON 文件
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(black_list, f, ensure_ascii=False, indent=4)
        
        API.send('插件已停用！')

    elif mm.startswith('启用'):
        # 获取插件名
        mm = mm.replace("启用", "").strip()

        # 读取黑名单列表
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list = json.load(f)

        # 检查插件是否在黑名单中
        if not any(plugin['plugin'] == mm for plugin in black_list):
            API.send('没找到哦～')
            return

        # 从黑名单列表中移除指定插件
        black_list = [plugin for plugin in black_list if plugin['plugin'] != mm]

        # 更新黑名单列表
        with open('config/plugin_config/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(black_list, f, ensure_ascii=False, indent=4)

        # 发送消息确认插件已启用
        API.send('插件已启用！')
        
    elif mm.startswith('-/'):
        # 获取插件名
        mm = mm[2:].strip()

        # 读取负面列表
        with open('config/plugin_config/{}negative_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            negative_list = json.load(f)

        # 检查插件是否在负面列表中
        if not any(plugin_dict['plugin'] == mm for plugin_dict in negative_list):
            API.send('没找到哦～')
            return

        # 从负面列表中移除指定插件
        negative_list = [plugin_dict for plugin_dict in negative_list if plugin_dict['plugin'] != mm]

        # 更新负面列表
        with open('config/plugin_config/{}negative_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(negative_list, f, ensure_ascii=False, indent=4)

        # 发送消息确认插件已移除负面标记
        API.send('插件已移除xxp标记～')
    elif mm.startswith('+/'):
        # 获取插件名
        mm = mm[4:].strip()
        
        if mm not in [item['plugin'] for item in xiaoxiaopa_control.plugins]:
            return ''
        

        # 读取负面列表
        with open('config/plugin_config/{}negative_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            negative_list = json.load(f)

        # 检查插件是否已经带有负面标记
        is_negative_list = any(plugin_dict['plugin'] == mm for plugin_dict in negative_list)
        if is_negative_list:
            API.send(f"插件 '{mm}' 已带有 / 标记～")
            return

        # 添加插件到负面列表
        new_plugin = {"plugin": mm}
        negative_list.append(new_plugin)

        # 更新负面列表
        with open('config/plugin_config/{}negative_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(negative_list, f, ensure_ascii=False, indent=4)

        # 发送消息确认插件已添加负面标记
        API.send('插件已添加 / 标记～')

    return "ok"


def jue():
    mm, user_id, group_id, self_id = API.get_msg()
    if mm == '/jue':
        help = '''jue ★★★★★
撅@ -> 随机6种情况

》》@后面可以加字'''
        API.send(help)
        return
    if mm.startswith('撅[CQ:at,qq='):
        rr = mm[11:]
        rr = rr[:-1]
        rep_1 = f'你撅了{cq_at(rr)}'
        rep_2 = f'你不许撅了'
        rep_3 = f'撅什么呢（'
        rep_4 = f'你被{cq_at(rr)}撅爆炸了！'
        rep_5 = f'你被{cq_at(rr)}撅了'
        rep_6 = f'你狠狠的撅了{cq_at(rr)}！'
        rep = random.choice([rep_1, rep_2, rep_3, rep_4, rep_5, rep_6])
        API.send(rep)
    return "ok"


def jpg():
    mm, user_id, group_id, self_id = API.get_msg()
    if mm == '/jpg':
        aa = '''jpg ★★★★
喜报 xx -> 太高兴了
悲报 xx -> 更高兴了

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
    elif mm.startswith('悲报 '):
        a = mm[2:]
        # 打开图片
        image = Image.open('multiple_Image/base/bb.png')
        # 获取图片的宽度和高度
        width, height = image.size
        # 创建图片绘制对象
        draw = ImageDraw.Draw(image)
        # 选择字体（这里使用了吉太缝合的黑体emoji版，非常好）
        font = ImageFont.truetype('multiple_Image/base/123.ttf', 36)
        # 获取文字的宽度和高度
        text_width = draw.textlength(a, font=font)
        text_height = font.getbbox(a)[3]
        # 计算文字的坐标
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        # 在图片上绘制文字
        draw.text((x, y), a, font=font, fill=(0, 0, 0))
        # 保存修改后的图片
        API.send(pillow_to_cq(image))
    return "ok"


def echo():
    mm, user_id, group_id, self_id = API.get_msg()
    if mm == '/echo':
        aa = '''echo ★★★★★
echo 123 -> 123

》》管理员指令'''
        API.send(aa)
        return
    if mm.startswith('echo '):
        mm = mm.replace('echo ', '')
        API.send(mm)
    return ''


def be_poke():
    mm, user_id, group_id, self_id = API.get_msg()
    msg_ = request.get_json()

    def get_send(mode: str) -> str:
        with open('bpk/{}.json'.format(mode), 'r') as f:
            json_data = json.load(f)
        texts = [item['text'] for item in json_data]
        # 读取图
        image_folder_path = 'bpk/{}/'.format(mode)

        image_paths = [os.path.join(image_folder_path, filename) for filename in os.listdir(image_folder_path)]

        cq_codes = [f"[CQ:image,file={path}{bpk}]" if 'bpk' in bpk else bpk for bpk in image_paths]
        # 创建json
        data_list = texts + cq_codes
        # print(data_list)

        if not data_list:
            return '没东西回复诶'
        random_send = random.choice(data_list)
        return random_send

    if msg_['post_type'] == 'notice':
        if self_id == msg_.get('target_id'):
            # {'post_type': 'notice', 'notice_type': 'notify', 'time': 1681355176, 'self_id': 3512457938, 'sub_type': 'poke', 'target_id': 2220357553, 'group_id': 737704963, 'user_id': 1528593481, 'sender_id': 1528593481}
            s = get_send('默认')
            if s == '':
                API.send('没东西回复诶')
                return
            API.send(s)
            return

    # 如果不是message类型消息可以结束了
    if 'message' not in msg_:
        return

