import os

import PySimpleGUI as sg
import requests
import threading


class app():
    def __init__(self):
        sg.theme('Light Brown 4')
        self.download_list = []
        self.data = [[]]
        self.started = False

    def init_layout(self):
        headers = [f'资源名称', f'下载链接']
        layout = [[sg.Button(button_text='开始抓取', key='--capture--'), sg.Button(button_text='停止抓取', key='--stop--'),
                   sg.Button(button_text='开始下载', key='--download--'), sg.CloseButton('关闭')],
                  [sg.Table(values=self.data, headings=headers, visible_column_map=[True, False],
                            header_font=('Default', 12),
                            justification='left',
                            font=('Default', 15), auto_size_columns=True,
                            expand_x=True, num_rows=20, display_row_numbers=True,
                            select_mode=sg.TABLE_SELECT_MODE_EXTENDED,

                            key='--list--', enable_events=True),
                   sg.Table(values=[[]], headings=['资源名称'], header_font=('宋体', 15), font=('宋体', 15),
                            auto_size_columns=True, justification='left',
                            display_row_numbers=True, expand_x=True, num_rows=20, key='--downlist--'
                            )],
                  ]

        return sg.Window(title='钉钉直播助手', layout=layout, size=(800, 500), disable_close=True, finalize=True)

    def poll(self, window=None):
        while True:
            try:
                print('poll....................................')
                resp = requests.get('http://127.0.0.1:5000/poll')
                data = resp.json()['data']
                if not data:
                    continue
                window.write_event_value('refresh', data)
            except:
                pass

    def start(self):
        url = "http://127.0.0.1:5000/capture"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.text)

    def stop(self):
        requests.get('http://127.0.0.1:5000/stop')

    def run(self):
        window = self.init_layout()
        user_click = True
        selected = []
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == '关闭':
                break
            elif event == '--capture--':
                try:
                    print('开始抓包')
                    if not self.started:
                        self.started = True
                        # 注意window传参方式，必须这样写
                        threading.Thread(target=self.poll, args=(window,), daemon=True).start()
                    self.start()
                except Exception as e:
                    print(e)
            elif event == '--stop--':
                self.stop()
                print('停止抓包')

            elif event == '--download--':
                print('开始下载')
                [self.download_list.append(item) for item in [[i] for i in selected] if item not in self.download_list]
                print(self.download_list)
                window['--downlist--'].update(self.download_list)

            elif event == '--list--':
                if user_click:
                    values_list = values['--list--']
                    if len(values_list) == 0:
                        continue
                    user_click = False
                    for item in values_list:
                        if item in selected:
                            selected.remove(item)
                        else:
                            selected.append(item)
                    window['--list--'].update(select_rows=selected)
                else:
                    user_click = True

            if event == 'refresh':
                print('刷新啦')
                urls = [[v['title'], v['m3u8_url']] for v in values['refresh'] if 'title' in v and 'm3u8_url' in v]
                window['--list--'].update(urls)
        window.close()


app = app()
app.run()
