from flask import Flask, request
# 导入，以及名为API的类
from xxp_c import API
import xxp_c as xiaoxiaopa_control
import random
import os
import json

current_dir = os.path.dirname(__file__)
# 切换到当前文件所在的目录
os.chdir(current_dir)

path = xiaoxiaopa_control.path

# 从主文件导入管理员的QQ号
top_administer_id = xiaoxiaopa_control.top_administer_id

qq_send_dict = xiaoxiaopa_control.qq_send_dict


# 插件管理
def sb_plugin():
    msg = request.get_json()
    mm = msg['message']
    user_id = msg['user_id']
    group_id = msg['group_id']

    def plugin_g():
        with open('plugin/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list_json_all_and_help = json.load(f)
        black_list_json_plugin = [item['plugin'] for item in black_list_json_all_and_help]
        plugins_list_all_and_help = xiaoxiaopa_control.plugins
        nicknames = []
        # 这不是你写答辩的理由*
        for item in plugins_list_all_and_help:
            if item['plugin'] not in black_list_json_plugin:
                nicknames.append('⬇/{}\n'.format(item['plugin']) + item['nickname'])
        on_plugin = '\n'.join(nicknames)

        black_nickname = []
        for item in plugins_list_all_and_help:
            if item['plugin'] in black_list_json_plugin:
                black_nickname.append('⬇/{}\n'.format(item['plugin']) + item['nickname'])

        off_plugin = '\n'.join(black_nickname)
        
        itr = """用「/ + 指令简称」查询～"""
        output_1 = '\n★★★★★已启用\n' + on_plugin
        output_2 = '\n★★★★★未启用\n' + off_plugin
        output = itr + output_1 + output_2
        return output

    if mm in ['help', '帮助', '使用说明', '/help', '插件管理']:
        a_xxp = '''xiaoxiaopa.com -> 小小趴官网～

/echo -> 查看echo用法～
停用echo -> 停用echo功能
启用echo -> 启用echo功能

》》echo是「 指令名 」
↓全部「 指令名 」'''
        if not os.path.exists('plugin/{}black_list.json'.format(group_id)):
            black_list = [
                {"plugin": "jue"}
            ]
            with open('plugin/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
                json.dump(black_list, f, ensure_ascii=False)

        output = plugin_g()

        send = a_xxp + output
        API.send(send)

    elif mm.startswith('停用'):
        mm = mm.replace("停用", "")
        plugins = xiaoxiaopa_control.plugins
        # print(plugins)
        plugins = [item['plugin'] for item in plugins]
        # print(plugins)
        with open('plugin/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list = json.load(f)
        # 检测插件是否已经在黑名单中
        for plugin in black_list:
            if plugin['plugin'] == mm:
                API.send('该插件已经被停用！')
                return
        for plugin_name in plugins:
            # print(plugin_name)
            # print(mm)
            if plugin_name == mm:
                # 找到了插件
                break
        else:
            # 没有找到插件
            API.send('没找到哦～！')
            return
        # 如果要停用的插件不在黑名单中，则添加新元素
        new_plugin = {"plugin": mm}
        black_list.append(new_plugin)
        # 将更新后的列表写入 JSON 文件
        with open('plugin/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(black_list, f, ensure_ascii=False, indent=4)
        API.send('插件已停用！')

    elif mm.startswith('启用'):
        mm = mm.replace("启用", "")
        with open('plugin/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
            black_list = json.load(f)
        # 查找指定插件
        for plugin in black_list:
            if plugin["plugin"] == mm:
                # 从黑名单列表中移除插件
                black_list.remove(plugin)
                with open('plugin/{}black_list.json'.format(group_id), 'w', encoding='utf-8') as f:
                    json.dump(black_list, f, ensure_ascii=False, indent=4)
                API.send('插件已启用！')
                break  # 找到插件后退出循环
        else:
            # 循环完仍未找到插件，说明插件不在黑名单中
            API.send('没找到哦～')
    return "ok"


def cq_img(file_name) -> str:
    return '[CQ:image,file={}{}]'.format(path, file_name)


# 戳一戳
def be_poke():
    def get_send(mode):
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
            return '加点图/文'
        random_send = random.choice(data_list)
        return random_send

    msg = request.get_json()

    group_id = msg['group_id']

    # 获得群聊 模式 赋值 -> mode_group
    if os.path.exists('bpk/mode_/{}.json'.format(group_id)):
        with open('bpk/mode_/{}.json'.format(group_id), 'r', encoding='utf-8') as f:
            user_choose_data = json.load(f)
        mode_group = [item['mode'] for item in user_choose_data][0]
    else:
        data_new_user = [{"mode": '小小趴'}]
        with open('bpk/mode_/{}.json'.format(group_id), 'w', encoding='utf-8') as f:
            json.dump(data_new_user, f, ensure_ascii=False)
        mode_group = '小小趴'

    if msg['post_type'] == 'notice':
        if msg.get('self_id') == msg.get('target_id'):
            # {'post_type': 'notice', 'notice_type': 'notify', 'time': 1681355176, 'self_id': 3512457938, 'sub_type': 'poke', 'target_id': 2220357553, 'group_id': 737704963, 'user_id': 1528593481, 'sender_id': 1528593481}
            s = get_send(mode_group)
            if s == '':
                API.send_by_poke('加点图/文字吧～')
                return
            API.send_by_poke(s)
            return

    if 'message' not in msg:
        return

    mm = msg['message']
    if mm == '/be_poke':
        a = '''be_poke ★★★★★
戳一戳 -> 戳一戳基础版

》》确保协议支持'''
        API.send_by_poke(a)
    return "OK"


# 举例插件1
def jue():
    msg = request.get_json()
    mm = msg['message']
    if mm == '/jue':
        aa = '''jue ★★★★★
撅@ -> 随机三种情况

》》@后面可以加字'''
        API.send(aa)
        return
    if mm.startswith('撅[CQ:at,qq='):
        rr = mm[11:]
        b = '你撅了[CQ:at,qq={}'.format(rr)
        c = '你不许撅了'
        f = '你被[CQ:at,qq={}'.format(rr)
        f = f.replace(' ', '') + '撅了'
        d = random.choice([b, c, f])
        API.send(d)
    return "ok"


# 举例插件2
def ran():
    msg = request.get_json()
    mm = msg['message']
    user_id = msg['user_id']
    if mm == '/ran':
        aa = '''ran ★★★
！r 吃饭 睡觉 冲榜 -> 随机决定

》》中文感叹号'''
        API.send(aa)
        return
    if mm.startswith('！r'):
        if ' ' not in mm:
            return
        else:
            pass
        rr = mm[2:]
        rr = rr.split()
        rr = random.choice(rr)
        b = '[CQ:at,qq=' + str(user_id) + ']' + '小小趴建议' + rr + '~'
        API.send(b)
    return "ok"


# 举例插件3
def echo():
    msg = request.get_json()
    mm = msg['message']
    user_id = msg['user_id']
    if mm == '/echo':
        aa = '''echo ★★★★★
小小趴说123 -> 123

》》管理员指令'''
        API.send(aa)
        return
    if mm.startswith('小小趴说') and user_id in top_administer_id:
        mm = mm.replace('小小趴说', '')
        API.send(mm)
    return 'kumo'


# 添加新的插件记得在xxp_c.py注册

def test():
    msg = request.get_json()
    mm = msg['message']
    if mm == '/test':
        aa = '''test ★★★★★
test -> test
'''
    if mm in ['晚上好', '晚好']:
        API.send('好你吗')
        return 'ok'
    return 'ok'
