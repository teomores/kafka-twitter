import tkinter as tk
import requests
import json
import datetime
from tkinter import messagebox

class ReadPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.pages = controller.get_frames() # prende le pagine
        self.controller = controller

        # base url
        self.base_read_url = 'http://127.0.0.1:5000/tweets'
        # user creation
        self.user_id = None
        self.n_times_shown = 0 # we'll use this to trigger the creation of the User at start
        self.bind("<<ShowFrame>>", self._on_first_show_frame) # binda all'evento, serve per dire quando viene mostrata
        # filter entries
        city_label = tk.Label(self,text="If you want, insert a city filter:", font=self.controller.title_font).pack(side="top")
        self.cf = tk.Entry(self, width=20)
        self.cf.pack()

        mention_label = tk.Label(self,text="If you want, insert a mention filter (without @):", font=self.controller.title_font).pack(side="top")
        self.mf = tk.Entry(self, width=20)
        self.mf.pack()

        tag_label = tk.Label(self,text="If you want, insert a tag filter (without #):", font=self.controller.title_font).pack(side="top")
        self.tf = tk.Entry(self, width=20)
        self.tf.pack()

        # scrollbar
        self.scrollbar =  tk.Scrollbar(self)
        self.scrollbar.pack(side = 'left', fill='y')
        self.msg_list = tk.Listbox(self, height="70",width="50",yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.msg_list.yview )

    def _on_first_show_frame(self, event):
        if self.n_times_shown == 0:
            self.user_id = self.controller.get_user_id()

            # label
            label = tk.Label(self, text=f"Apply filters and start reading!", font=self.controller.title_font)
            label.pack(side="top", fill="x", pady=10)
            fetch = tk.Button(self, text="Read Messages!", command=self._read, height="2", width="30").pack()
            back_btn = tk.Button(self, text="<- Back to Home", command=self._back_to_home, height="2", width="30").pack()
            self.n_times_shown =-1

    def _read(self):
        self._destroy_msg_list()

        # convert all to lower case
        c_filter = self.cf.get().lower()
        m_filter = self.mf.get().lower()
        t_filter = self.tf.get().lower()

        # if no filter is applied, select all city/mention/tag
        if c_filter=='':
            c_filter = 'ALL'
        if m_filter=='':
            m_filter = 'ALL'
        if t_filter=='':
            t_filter = 'ALL'

        req_url = self.base_read_url + f'/cityfilter={c_filter}&mentionfilter={m_filter}&tagfilter={t_filter}/latest'

        cookies={'username': self.controller.get_user_id()}
        r = requests.get(req_url, cookies=cookies)
        msgs = []
        for m in r.json()['results']:
            msgs.append(m)

        for m in msgs:
            self.msg_list.insert('end',m) # 'end' per metterlo infondo
        self._clear_text()
        self.msg_list.pack(pady=5)


    def _destroy_msg_list(self):
        self.msg_list.delete('0', 'end')

    def _back_to_home(self):
        print('Back to Home.')
        self.controller.show_frame("HomePage")
        self._destroy_msg_list()
        self._clear_text()

    def _clear_text(self):
        self.cf.delete(0, 'end')
        self.tf.delete(0, 'end')
        self.mf.delete(0, 'end')
