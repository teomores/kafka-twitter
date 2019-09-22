import tkinter as tk
import threading
import requests
import json
import datetime
from tkinter import messagebox
import time
from tkinter import font  as tkfont

class StreamingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.pages = controller.get_frames() # prende le pagine
        self.controller = controller
        self.twitter_blue = '#%02x%02x%02x' % (68,162,242)
        self.is_shown = False
        # default no filters
        self.cityfilter = 'ALL'
        self.mentionfilter = 'ALL'
        self.tagfilter = 'ALL'
        # messages to show
        self.msg_to_show = []
        # user creation
        self.user_id = None
        self.streaming_url = 'http://10.0.0.17:5000/tweets/streaming' #'http://10.0.0.17:5000/tweets/streaming'
        self.n_times_shown = 0 # we'll use this to trigger the creation of the User at start
        self.is_first_req = True # we'll use it to start the thread: threads cannot be restarted!
        self.new_stream_req = False # if new request, abort previous stream
        self.stream_stopped = True
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
        self.msg_list = tk.Listbox(self, height="70",width="50", yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.msg_list.yview)

    def get_is_shown(self):
        return self.is_shown

    def _on_first_show_frame(self, event):
        if self.n_times_shown == 0:
            self.user_id = self.controller.get_user_id()

            # label
            # label
            font = tkfont.Font(family='Helvetica', size=15, weight='bold')
            label = tk.Label(self, text=f"Press the below buttons to start/stop streaming!", wraplength=400, height='3', fg='white',font=font, background=self.twitter_blue)
            label.pack(side="top", fill='both')
            self.stream_btn = tk.Button(self, text="Read Messages!", command=self._stream, height="2", width="30")
            self.stream_btn.pack()
            stop_stream = tk.Button(self, text="Stop stream & Create a new one!", command=self._stop_stream, height="2", width="30").pack()
            back_btn = tk.Button(self, text="<- Back to Home", command=self._back_to_home, height="2", width="30").pack()

            self.n_times_shown =-1

        self.is_shown = True
        self.new_stream_req = False

    def _stop_stream(self):
        self.stream_stopped = True

    def _disable_read_button(self):
        # this is done at requesting
        self.stream_btn.config(state="disabled")

    def _enable_read_button(self):
        # this is done at end request
        self.stream_btn.config(state="active")

    def _stream(self):
        self._disable_read_button()
        self._destroy_msg_list()

        # convert all to lower case
        self.cityfilter = self.cf.get().lower()
        self.mentionfilter = self.mf.get().lower()
        self.tagfilter = self.tf.get().lower()

        # if no filter is applied, select all city/mention/tag
        if self.cityfilter=='':
            self.cityfilter = 'ALL'
        if self.mentionfilter=='':
            self.mentionfilter = 'ALL'
        if self.tagfilter=='':
            self.tagfilter = 'ALL'

        self.stream_stopped = False
        self.new_stream_req = True
        t = threading.Thread(target = self._stream_response, args = ())
        t.daemon = True
        t.start()
        self._display_msg()

    def _stream_response(self):
            # checks to stop the thread job
            payload = {
                'cityfilter': self.cityfilter,
                'mentionfilter': self.mentionfilter,
                'tagfilter': self.tagfilter
            }

            print(f'payload {payload}')

            cookies={'username': self.user_id}
            r = requests.post(self.streaming_url, data=payload, cookies=cookies, stream=True)
            msg_string = ""
            msg_list = []

            is_start=True
            for c in r.iter_content(decode_unicode=True):
                if self.is_shown and self.new_stream_req and not self.stream_stopped:
                    if (c):
                        if str(c) =='`' and is_start==True:
                            msg_string =''
                            is_start = False
                        elif str(c) =='`' and is_start==False:
                            print(json.loads(msg_string))
                            self.msg_to_show = [x for x in json.loads(msg_string)]
                            is_start=True
                        else:
                            msg_string += str(c)
                    else:
                        print('===')
                else:
                    break
            self._enable_read_button()
            print('STREAMING FINITO!')

    def _display_msg(self): # _get_msg_list rescheduled
        if self.is_shown == True: # altrimenti non ha senso che continui a fare richieste
            self._destroy_msg_list()
            for m in self.msg_to_show:
                self.msg_list.insert('end',m)
            self.msg_list.pack(pady=5)
            self.after(2000, self._display_msg)

    def _destroy_msg_list(self):
        self.msg_list.delete('0', 'end')

    def _back_to_home(self):
        self.is_shown = False
        self._destroy_msg_list()
        print('Back to Home.')
        self.controller.show_frame("HomePage")
