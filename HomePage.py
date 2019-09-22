import tkinter as tk
import requests
import json
from PIL import ImageTk, Image
from tkinter import font  as tkfont

class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        self.twitter_blue = '#%02x%02x%02x' % (68,162,242)
        tk.Frame.__init__(self,
                        parent
                        )
        self.pages = controller.get_frames() # prende le pagine
        self.controller = controller
        # user creation
        self.user_id = None
        self.n_times_shown = 0 # we'll use this to trigger the creation of the User at start
        self.bind("<<ShowFrame>>", self._on_first_show_frame) # binda all'evento, serve per dire quando viene mostrata

    def _read(self):
        print(f"Ok {self.controller.get_user_id()}, let's see what is going on in the World!")
        self.controller.show_frame("ReadPage")

    def _write(self):
        print(f'{self.controller.get_user_id()}, write something!')
        self.controller.show_frame("WritePage")

    def _streaming(self):
        print(f'Ok {self.controller.get_user_id()}, streaming mode!')
        self.controller.show_frame("StreamingPage")

    def _on_first_show_frame(self, event):
        if self.n_times_shown == 0:
            self.user_id = self.controller.get_user_id()

            # label
            font = tkfont.Font(family='Helvetica', size=25, weight='bold')
            label = tk.Label(self, text=f"What do you want to do, {self.controller.user_id}?", wraplength=400,height='3', fg='white',font=font, background=self.twitter_blue)
            label.pack(side="top", fill='both')

            # read mode button
            read_button = tk.Button(self, text="Read", command=self._read, height="2", width="30").pack(pady=(30,5))

            # streaming mode button
            streaming_button = tk.Button(self, text="Streaming", command=self._streaming, height="2", width="30").pack(pady=5)

            # write mode button
            write_button = tk.Button(self, text="Write", command=self._write, height="2", width="30").pack(pady=5)

            # carica logo
            img = Image.open("logo.jpg")
            w,h = img.size
            img_resized = img.resize((w//3,h//3), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(img_resized)
            panel = tk.Label(self, image = image, background='white')
            panel.photo = image
            panel.pack(side='bottom',fill='both', pady=10)


            self.n_times_shown =-1
