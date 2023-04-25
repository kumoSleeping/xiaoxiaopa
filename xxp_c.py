from flask import Flask, request
import requests
import xxp_p as xiaoxiaopa_plugin
import os
import json


# 获取当前文件所在的目录
current_dir = os.path.dirname(__file__)
# 切换到当前文件所在的目录
os.chdir(current_dir)

# 用于aiohttp转发到xxp_c.py，如果需要修改请修改请同步修改xxp_c.py
send_port = 12709

with open('config/bot1.json', 'r', encoding='utf-8') as f:
    config_1 = json.load(f)

port1 = config_1['ws_port']  # ws端口
qq_send_dict = {
    config_1['qq_number']: config_1['http_port']
}  # 根据「QQ号」获取「http上报端口」


with open('config/path.json', 'r', encoding='utf-8') as f:
    path_json = json.load(f)
path_str = path_json['path']


# 路径 🔧
path = path_str + current_dir + '/'


app = Flask(__name__)

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


# 这是一个类，用于处理发送消息的操作
class API:
    # 标记为静态
    @staticmethod
    # 定义标准send，用于发送大部分通过接收到「消息」进行的「回复」
    def send(message):
        # msg意思是从cqhttp收到的json中的信息（）
        msg = request.get_json()

        send_port_ = qq_send_dict.get(msg['self_id'])

        # print(msg)
        # 先通过一个赋值group_or_private，判断是群聊消息还是私聊消息
        group_or_private = msg['message_type']
        if 'group' == group_or_private:
            group_id = msg['group_id']
            send_to_gocq = {
                "message_type": group_or_private,
                "group_id": str(group_id),
                "message": message,
            }
        else:
            user_id = msg['user_id']
            send_to_gocq = {
                "message_type": group_or_private,
                "user_id": user_id,
                "message": message
            }
        # 这个是把小小趴产生的「消息」发给gocq，然后让gocq发到QQ里
        # send_port是上面的「gocq监听端口」
        url = "http://127.0.0.1:{}/send_msg".format(send_port_)
        print(send_to_gocq)

        requests.get(url, params=send_to_gocq)

    # 被戳发的信息 仅群聊 前提协议支持
    @staticmethod
    def send_by_poke(hello_qq):
        msg = request.get_json()

        send_port_ = qq_send_dict.get(msg['self_id'])
        print([send_port_])

        group_id = msg['group_id']
        papa = {
            "group_id": str(group_id),
            "message": hello_qq,
        }
        url = "http://127.0.0.1:{}/send_msg".format(send_port_)

        requests.get(url, params=papa)


@app.route('/', methods=["POST"])
def post_data():
    # global send_port
    # 获取请求中的 JSON 数据
    msg = request.get_json()
    print(msg)

    # 如果请求的类型是 提醒
    if msg['post_type'] in ['notice']:
        group_id = msg.get('group_id')
        if not group_id:
            return ''
        # 如果该群存在插件管理的 JSON 文件
        blacklist_file = f'plugin/{group_id}black_list.json'
        if not os.path.exists(blacklist_file):
            xiaoxiaopa_plugin.be_poke()
            return ''
        # print('插件管理已启用')
        with open(blacklist_file, 'r', encoding='utf-8') as f:
            blacklist = json.load(f)

        # 遍历插件列表
        for plugin in [{"plugin": "be_poke", "nickname": "她妈的老子不会json呜呜呜呜呜"}]:
            # 检查是否在黑名单中
            if any(plugin_dict['plugin'] == plugin['plugin'] for plugin_dict in blacklist):
                continue

            xiaoxiaopa_plugin.be_poke()

    # 如果请求的类型是 消息
    if msg['post_type'] in ['message']:
        # 区分群聊和私聊

        group_or_private = msg['message_type']
        # 就是说，如果确定是/bank 这样的查询help的插件 就全部启用
        if 'group' == group_or_private:
            group_id = msg['group_id']
            mm_help = msg['message'].replace('/', '')
            found = any(mm_help in p['plugin'] for p in plugins)
            # 这个函数目的是当用「/指令名」的时候加载所有插件以查询help
            if found:
                # 启用sb_plugin插件管理
                xiaoxiaopa_plugin.sb_plugin()
                for plugin in plugins:
                    # 使用getattr()动态获取相应的函数
                    func = getattr(xiaoxiaopa_plugin, plugin['plugin'])
                    # 调用函数
                    func()
            elif os.path.exists('plugin/{}black_list.json'.format(group_id)):
                xiaoxiaopa_plugin.sb_plugin()
                with open('plugin/{}black_list.json'.format(group_id), 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
                    # print(blacklist)
                # 按照json配制启用模块
                for plugin in plugins:
                    # 判断是否在黑名单中
                    if any(plugin_dict['plugin'] == plugin['plugin'] for plugin_dict in blacklist):
                        pass
                    else:
                        # 使用getattr()动态获取相应的函数
                        func = getattr(xiaoxiaopa_plugin, plugin['plugin'])
                        # 调用函数
                        func()
            else:
                # 启用sb_plugin插件管理
                xiaoxiaopa_plugin.sb_plugin()
                for plugin in plugins:
                    # 使用getattr()动态获取相应的函数
                    func = getattr(xiaoxiaopa_plugin, plugin['plugin'])
                    # 调用函数
                    func()
        else:
            # 加载私聊插件
            for plugin_private in plugins_private:
                # 使用getattr()动态获取相应的函数
                func = getattr(xiaoxiaopa_plugin, plugin_private['plugin_private'])
                print(plugin_private['plugin_private'])
                # 调用函数
                func()
    return "OK"


print(
    '喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵喵')
if __name__ == '__main__':
    app.run(port=send_port, host='0.0.0.0', debug=True, use_reloader=True)
