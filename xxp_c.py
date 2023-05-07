from flask import Flask, request
import requests
import xxp_p as xiaoxiaopa_plugin
import os
import json
import inspect

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


# 内部管理员QQ 🔧
top_administer_id = [1528593481]

with open('config/plugins.json', 'r', encoding='utf-8') as f:
    plugins = json.load(f)
    
with open('config/plugins_private.json', 'r', encoding='utf-8') as f:
    plugins_private = json.load(f)

app = Flask(__name__)


# 这是一个类，用于处理发送消息的操作
class API:
    # 标记为静态
    @staticmethod
    def get_msg():
        '''用于每个插件（函数）获取：
        mm（消息），user_id（发送者QQ），group_id（群号），self_id（机器人QQ）
        四个参数
        并且进行「插件管理」和「xxp标记」的判断'''
        msg = request.get_json()
        try:
            mm = msg['message']
        except:
            mm = ''
        try:
            user_id = msg['user_id']
        except:
            user_id = -1
        try:
            group_id = msg['group_id']
        except:
            group_id = -1       
        try:
            self_id = msg['self_id']
        except:
            self_id = -1
            
        '''这是一个插件管理 当插件存在黑名单中时，将mm置空，self_id置为-1
        1.mm防止消息类型被启用
        2.self_id置为-1的原因是为了防止戳一戳被启用'''
        # 使用inspect模块获取当前函数名
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        function_name = caller_frame.f_code.co_name
        
        if os.path.exists('plugin/{}black_list.json'.format(group_id)):
            # '''如果该群存在 black_list 的 JSON 文件'''
            with open('plugin/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
            # print(blacklist)
            # print(function_name)
            is_blacklisted = any(plugin_dict['plugin'] == function_name for plugin_dict in blacklist)
            if is_blacklisted:
                # print(f"插件 '{function_name}' 在黑名单中")
                mm = ''
                self_id = -1

        '''这是一个xxp标记管理 当插件存在xxp标记时，
        1.mm以xxp / 小小趴 开头时，程序会自动将mm中的xxp / 小小趴 去掉
        2.mm不以xxp / 小小趴 开头时，程序会自动将mm置空,将user_id置为-1，self_id置为-1
        3.插件管理会被优先执行，所以带有xxp标记的插件仍然可以被黑名单屏蔽'''
        if os.path.exists('plugin/{}negative_list.json'.format(group_id)):
            # '''如果该群存在 +xxp 的 JSON 文件'''
            with open('plugin/{}negative_list.json'.format(group_id), 'r', encoding='utf-8') as f:
                negative_list = json.load(f)
            is_negative_list = any(plugin_dict['plugin'] == function_name for plugin_dict in negative_list)
            if is_negative_list:
                print(f"插件 '{function_name}' 含有+xxp标记")
                if mm.startswith('xxp') or mm.startswith('小小趴'):
                    mm = mm[3:]
                else:
                    mm = ''
                    self_id = -1
                    
        return mm, user_id, group_id, self_id
        
    # 标记为静态
    @staticmethod
    # 定义标准send，用于发送大部分通过接收到「消息」进行的「回复」
    def send(message):
        # msg意思是从cqhttp收到的json中的信息（）
        msg = request.get_json()

        send_port_ = qq_send_dict.get(msg['self_id'])

        # print(msg)
        # 先通过一个赋值group_or_private，判断是群聊消息还是私聊消息
        try:
            message_type = msg['message_type']
        except:
            message_type = 'group'
        if 'group' == message_type:
            group_id = msg['group_id']
            send_to_gocq = {
                "message_type": message_type,
                "group_id": str(group_id),
                "message": message,
            }
        else:
            user_id = msg['user_id']
            send_to_gocq = {
                "message_type": message_type,
                "user_id": user_id,
                "message": message
            }
        # 这个是把小小趴产生的「消息」发给gocq，然后让gocq发到QQ里
        # send_port是上面的「gocq监听端口」
        url = "http://127.0.0.1:{}/send_msg".format(send_port_)

        requests.post(url, json=send_to_gocq)


@app.route('/', methods=["POST"])
def post_data():
    '''无论是什么类型消息都要先启用sb_plugin插件（插件管理）
    '''
    xiaoxiaopa_plugin.sb_plugin()
    for plugin in plugins:
        # 使用getattr()动态获取相应的函数
        func = getattr(xiaoxiaopa_plugin, plugin['plugin'])
        # 调用函数
        func()
    return "OK"

print('开始重新运行喵！')
if __name__ == '__main__':
    app.run(port=send_port, host='0.0.0.0', debug=True, use_reloader=True)
