import tkinter as tk
from tkinter import font  as tkfont

from HomePage import HomePage
from LoginPage import LoginPage
from WritePage import WritePage
from ReadPage import ReadPage
from StreamingPage import StreamingPage

class KafkaTwitter(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # setup properties
        self.title_font = tkfont.Font(family='Helvetica', size=18)
        self.title('KafkaTwitter')
        self.geometry("500x500")
        self.resizable(0, 0)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # username
        self.user_id = None
        self.session = None
        # per controllare quale pagina è mostrata
        self.frames = {}
        for F in (LoginPage, HomePage, WritePage, ReadPage, StreamingPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update()
        frame.event_generate("<<ShowFrame>>")

    def set_user_id(self,ui):
        self.user_id = ui

    def get_user_id(self):
        return self.user_id

    def set_session(self,s):
        self.session = s

    def get_session(self,s):
        return self.session

    def get_frames(self):
        return self.frames

if __name__ == "__main__":
    app = KafkaTwitter()
    app.mainloop()
