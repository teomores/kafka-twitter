import tkinter as tk
import requests
import json
from tkinter import messagebox
from PIL import ImageTk, Image

class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.user_id = None

        # application login endpoint
        self.login_url = 'http://127.0.0.1:5000/users/id'

        # basic dummy graphics
        # image rendering
        img = Image.open("logo.jpg")
        w,h = img.size
        img_resized = img.resize((w//3,h//3), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(img_resized)
        panel = tk.Label(self, image = image, background='white')
        panel.photo = image
        panel.pack(side='top', pady=50)
        # entry boxes
        name_label = tk.Label(self, text="Username:", font=self.controller.title_font).pack(side="top", fill="x", pady=5)
        self.name_box = tk.Entry(self,width=20)
        self.name_box.pack()

        submit_btn = tk.Button(self, text="Login",command=self._submit, height="2", width="30").pack(pady=20)

    def _submit(self):
        # login only if non empty username
        if (self.name_box.get().strip()!=''):
            # twitter user creation
            self.user_id = self.name_box.get().strip()
            self.controller.set_user_id(self.user_id)
            # session creation
            s = requests.Session() # TODO: implementare un secret token?
            self.controller.set_session(s)
            # subscribe + cookie creation
            r = requests.post(self.login_url,data={'id': self.user_id})
            print(r.text)

            # show HomePage
            self.controller.show_frame("HomePage")

        else:
            messagebox.showerror("Whoops", "It seems that your credentials are invalid or empty...")
