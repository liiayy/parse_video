# -*- coding: utf-8 -*-

# 抖音无水印视频解析

import re
import PySimpleGUI as sg
import requests
import threading
import time
sg.change_look_and_feel("Default1")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}

sj_headers = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
}


class ParseVideo(object):
    """
    根据分享链接，解析抖音无水印视频
    """

    def __init__(self, url):
        self.url = url
        self.xhr_url = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}"
        self.wsy_url = "https://aweme-hl.snssdk.com/aweme/v1/play/?video_id={}"
        self.headers = headers
        self.sj_headers = sj_headers

    def get_url_id(self):
        """
        获取跳转后的id
        """
        response = requests.get(url=self.url, headers=self.headers, allow_redirects=False)

        location = response.headers.get("location")

        url_id = re.search(r'video/(.*?)/', location).group(1)
        print(url_id)

        return url_id

    def get_video_id(self, v_id):
        """
        获取video_id
        """
        url = self.xhr_url.format(v_id)

        response = requests.get(url=url, headers=self.headers)
        data = response.json()

        v_url = data['item_list'][0]['video']['play_addr']['url_list'][0]

        video_id = re.search(r'video_id=(.*?)&', v_url).group(1)
        print(video_id)

        return video_id

    def get_real_url(self, v_id):
        """获取无水印url"""
        url = self.wsy_url.format(v_id)

        response = requests.get(url=url, headers=self.sj_headers, allow_redirects=False)

        real_url = response.headers.get('location')
        print(real_url)
        return real_url

    def run(self):
        url_id = self.get_url_id()
        video_id = self.get_video_id(url_id)
        # self.get_real_url(video_id)
        return self.get_real_url(video_id)


class Kuaishou(object):
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3329.0 Mobile Safari/537.36'}
        self.req = requests.get(url=url, headers=self.headers).url
        self.headers1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': 'did=web_282e70945a114e2389e104b8bdc7388a; didv=1596413681000; clientid=3; client_key=65890b29; Hm_lvt_86a27b7db2c5c0ae37fee4a8a35033ee=1596413682; Hm_lpvt_86a27b7db2c5c0ae37fee4a8a35033ee=1596413697',
            'Cookie': 'did=web_282e70945a114e2389e104b8bdc7388a; didv=1596413681000; clientid=3; client_key=65890b29; Hm_lvt_86a27b7db2c5c0ae37fee4a8a35033ee=1596413682; Hm_lpvt_86a27b7db2c5c0ae37fee4a8a35033ee=1596413697',
            'Host': 'v.kuaishou.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36', }
        self.est1 = requests.get(url=self.req, headers=self.headers1).text
        self.url = re.findall('srcNoMark":"(.*?)"', self.est1)[0]

    def rt(self):
        return self.url


class Gui(object):
    def __init__(self):
        self.tab1_layout = [[sg.Text('抖音分享链接(一行一个可批量)')],
                            [sg.Multiline(key='url',size=(100,15))],
                            [sg.OK('解析',size=(15,2)), sg.Cancel('关闭',size=(15,2))],

                            ]
        self.tab2_layout = [[sg.Text('快手分享链接(一行一个可批量)')],
                            [sg.Multiline(key='ks_url',size=(100,15))],
                            [sg.OK('解析',size=(15,2)), sg.Cancel('关闭',size=(15,2))],

                            ]
        self.layout = [
            [sg.TabGroup([[sg.Tab('抖音', self.tab1_layout), sg.Tab('快手', self.tab2_layout)]])],
            [sg.Text('',key='msg',size=(100,2))],
            [sg.Button('下载视频', key='but_dow', visible=False,size=(10,3))]
        ]
        self.window = sg.Window('抖音快手无水印视频批量版 V1.2 By 李彦军', self.layout, size=(750,500))
        self.downurl_list = []
    def down_video(self, url, path):
        try:
            res = requests.get(url, headers=headers).content
            with open(path, 'wb') as f:
                f.write(res)
            save_out = '保存成功'
        except Exception as e:
            save_out = '保存失败'
        return save_out
    def ui_douyin(self,values):
        url = values[r'url']
        url = re.findall('https://.*/', url)

        if url not in (None, []):
            self.window['msg'].update('提示：发现了{}个视频正在解析中....'.format(len(url)))
            for c, i in enumerate(url):
                if i.find('douyin') == -1:
                    self.window['msg'].update('提示：包含非抖音链接')
                    break
                test = ParseVideo(url=i)
                self.val = test.run()
                self.downurl_list.append(self.val)
                self.window['msg'].update('提示：正在解析第{}个视频'.format(c + 1))
            self.window['but_dow'].update(visible=True)
            self.window['msg'].update('提示：{}个视频解析完毕，点击下方按钮下载'.format(len(url)))
        else:
            self.window['msg'].update('提示：分享链接错误')
            # sg.Popup('分享链接错误', no_titlebar='True', background_color='#fff')

    def ui_kuaishou(self,values):
        url = values[r'ks_url']
        url = re.findall('https://.*', url)

        if url not in (None, []):
            self.window['msg'].update('提示：发现了{}个视频正在解析中....'.format(len(url)))
            for c, i in enumerate(url):
                test = Kuaishou(url=i)
                self.val = test.rt()
                self.downurl_list.append(self.val)
                self.window['msg'].update('提示：正在解析第{}个视频'.format(c + 1))
                self.window['but_dow'].update(visible=True)
                self.window['msg'].update('提示：{}个视频解析完毕，点击下方按钮下载'.format(len(url)))
        else:
            self.window['msg'].update('提示：分享链接错误')

    def ui_but_dow(self):
        text = sg.popup_get_folder('message', no_window=True, )
        for i, v in enumerate(self.downurl_list):
            if text != '':
                self.window['msg'].update('提示：正在下载第{i}个视频，还有{s}个视频等待下载'.format(i=(i+1), s=len(self.downurl_list) - (i + 1)))
                out_save = self.down_video(v, str(text) + '/{}.mp4'.format(time.strftime("%m%d-%H%M-", time.localtime())+str(i+1)))
                # sg.Popup(out_save, no_titlebar='True', background_color='#fff')
        self.window['msg'].update('提示：视频全部下载完毕')

    def run(self):
        while True:
            event, values = self.window.read()

            if event in (None, '关闭', '关闭1'):  # if user closes window or clicks cancel
                break
            elif event == '解析':
                t1 = threading.Thread(target=self.ui_douyin,args=(values,))
                t1.start()

            elif event == '解析0':
                t1 = threading.Thread(target=self.ui_kuaishou,args=(values,))
                t1.start()
            elif event == 'but_dow':
                t1 = threading.Thread(target=self.ui_but_dow)
                t1.start()




if __name__ == '__main__':
    douyin_window = Gui()
    douyin_window.run()