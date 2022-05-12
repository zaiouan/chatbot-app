import tkinter as tk
from audioop import reverse
from calendar import Calendar
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.messagebox import askyesno, askokcancel, showinfo

import PIL
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox
import pickle
from datetime import datetime
import os
import threading
import struct

import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
import json
import random

model = load_model('ensab.h5')
print(model)

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class SaisirInfoPersonnel(tk.Tk):
    usern = ""

    def __init__(self):
        super().__init__()

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        self.x_co = int((screen_width / 2) - (550 / 2))
        self.y_co = int((screen_height / 2) - (400 / 2)) - 80
        self.geometry("550x400")
        self.title("ChatBot ENSAB")

        self.user = None
        self.image_extension = None
        self.image_path = None

        self.frame = tk.Frame(self, bg="sky blue")
        self.frame.pack(fill="both", expand=True)

        app_icon = Image.open('images/chat_ca.png')
        app_icon = ImageTk.PhotoImage(app_icon)

        self.iconphoto(False, app_icon)

        background = Image.open("images/login_bg_ca1.jpg")
        background = background.resize((550, 400), Image.ANTIALIAS)
        background = ImageTk.PhotoImage(background)

        upload_image = Image.open('images/upload_ca.png')
        upload_image = upload_image.resize((25, 25), Image.ANTIALIAS)
        upload_image = ImageTk.PhotoImage(upload_image)

        self.user_image = 'images/user.png'

        tk.Label(self.frame, image=background).place(x=0, y=0)

        self.profile_label = tk.Label(self.frame, bg="grey")
        self.profile_label.place(x=350, y=75, width=150, height=140)

        """upload_button = customtkinter.CTkButton(master=self.frame,
                                                text="Choisir Image",
                                                command=self.add_photo,
                                                width=120,
                                                height=32,
                                                fg_color='green',
                                                hover_color=CTkColorManager.MAIN_HOVER,
                                                border_color=None,
                                                border_width=0,
                                                image=upload_image,
                                                text_font="lucida 12 bold",
                                                corner_radius=6)"""
        upload_button = tk.Button(self.frame, image=upload_image, compound="left", text="Upload Image",
                                  cursor="hand2", font="lucida 12 bold", padx=2, command=self.add_photo)
        upload_button.place(x=325, y=220)

        self.username = tk.Label(self.frame, text="Votre Nom", font="lucida 12 bold", bg="#fbd324")
        self.username.place(x=80, y=100)
        self.username_entry = tk.Entry(self.frame, font="lucida 12 bold", width=10,
                                       highlightcolor="blue", highlightthickness=1)
        self.username_entry.place(x=195, y=100)

        self.sex = int()
        self.radio1 = Radiobutton(self.frame, variable=self.sex, font="lucida 12 bold", text="Feminin", value=1,
                                  bg="#fbd324")
        self.radio1.place(x=80, y=200)
        self.radio2 = Radiobutton(self.frame, variable=self.sex, font="lucida 12 bold", text="Masculin", value=0,
                                  bg="#fbd324")
        self.radio2.place(x=195, y=200)

        self.username_entry.focus_set()
        """submit_button = customtkinter.CTkButton(master=self.frame,
                                                text="Valider",
                                                command=self.process_data,
                                                width=160,
                                                height=32,
                                                fg_color=CTkColorManager.MAIN,
                                                hover_color=CTkColorManager.MAIN_HOVER,
                                                border_color=None,
                                                border_width=0,
                                                text_font="lucida 20 bold",
                                                corner_radius=6)"""

        submit_button = tk.Button(self.frame, text="Connect", font="lucida 12 bold", padx=30, cursor="hand2",
                                  command=self.process_data, bg="#16cade", relief="solid", bd=2)

        submit_button.place(x=200, y=275)
        self.resizable(0, 0)  # will disable max/min tab of window
        self.mainloop()

    def add_photo(self):
        self.image_path = filedialog.askopenfilename()
        image_name = os.path.basename(self.image_path)
        self.image_extension = image_name[image_name.rfind('.') + 1:]

        if self.image_path:
            user_image = Image.open(self.image_path)
            user_image = user_image.resize((150, 140), Image.ANTIALIAS)
            user_image.save('resized' + image_name)
            user_image.close()

            self.image_path = 'resized' + image_name
            user_image = Image.open(self.image_path)

            user_image = ImageTk.PhotoImage(user_image)
            self.profile_label.image = user_image
            self.profile_label.config(image=user_image)

    def process_data(self):
        if self.username_entry.get():
            self.profile_label.config(image="")

            if len((self.username_entry.get()).strip()) > 6:
                self.user = self.username_entry.get()[:6] + "."
            else:
                self.user = self.username_entry.get()

            if not self.image_path:
                self.image_path = self.user_image
            with open(self.image_path, 'rb') as image_data:
                image_bytes = image_data.read()

            ChatScreen(self, self.frame)


class ChatScreen(tk.Canvas):
    def __init__(self, parent, frame):
        super().__init__(parent, bg="sky blue")

        self.window = 'ChatScreen'
        self.frame = frame
        self.frame.pack_forget()

        self.parent = parent
        self.parent.bind('<Return>', lambda e: self.sent_message_format(e))

        # self.parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.frame))
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        # x_co = int((screen_width / 2) - (680 / 2))
        # y_co = int((screen_height / 2) - (750 / 2)) - 80
        self.parent.geometry("470x700")

        user_image = Image.open(self.parent.image_path)
        user_image = user_image.resize((40, 40), Image.ANTIALIAS)
        self.user_image = ImageTk.PhotoImage(user_image)

        container = tk.Frame(self)
        # 595656
        # d9d5d4
        container.place(x=10, y=60, width=450, height=550)
        self.canvas = tk.Canvas(container, bg="#46abbd")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#46abbd")

        scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def configure_scroll_region(e):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        def resize_frame(e):
            self.canvas.itemconfig(scrollable_window, width=e.width)

        self.scrollable_frame.bind("<Configure>", configure_scroll_region)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", resize_frame)
        self.canvas.pack(fill="both", expand=True)
        # --------------------- send -------------louja





        im = PIL.Image.open('send.png')
        im = ImageTk.PhotoImage(im)

        # x1 = tk.Button(self)
        # photo = PhotoImage(file="Re.png")
        # x1.config(image=im, width="40", height="40", activebackground="black"
        #          , bg="black", bd=0, command=self.sent_message_format)
        """send_button = Button(self, font=("Verdana", 12, 'bold'), image=im, width="45", height="45",
                             bd=0, activebackground="#3c9d9b", fg='#000000',
                             command=self.sent_message_format)"""
        send_button = Button(self, font=("Verdana", 12, 'bold'), text="Envoyer", width="6", height="1",
                            bd=0, activebackground="sky blue", fg='#000000', command=self.sent_message_format)
        send_button.place(x=375, y=620)

        self.entry = tk.Text(self, font="lucida 10 bold", width=38, height=2,
                             highlightcolor="blue", highlightthickness=1)
        self.entry.place(x=15, y=621)

        self.entry.focus_set()
        m_frame = tk.Frame(self.scrollable_frame, bg="#d9d5d4")

        t_label = tk.Label(m_frame, bg="#d9d5d4", text=datetime.now().strftime('%H:%M'), font="lucida 9 bold")
        t_label.pack()

        b = tk.Label(self, image=self.user_image, compound="left", fg="white", bg="orange", font="lucida 10 bold",
                     padx=15)
        b.place(x=10, y=10)

        m_label = tk.Label(m_frame, wraplength=250, text=f"Chatbot ENSAB 2021-2022",
                           font="lucida 10 bold", bg="yellow")
        m_label.pack(fill="x")

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.pack(fill="both", expand=True)
        user = str(self.parent.user)
        print(user)

        resp = "Hi "+user+", good morning I'm a chatbot developed by ENSAB Students "
        print(resp)
        self.received_message_format(resp)

        t = threading.Thread(target=self.receive_data)
        t.setDaemon(True)
        t.start()

    def receive_data(self):
        print(1)

    def on_closing(self):
        if self.window == 'ChatScreen':
            res = messagebox.askyesno(title='Warning !', message="Do you really want to disconnect ?")
            if res:
                self.parent.destroy()
        else:
            self.parent.destroy()

    def received_message_format(self, message):

        im = Image.open('images/bot.png')
        im = im.resize((40, 40), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(im)

        m_frame = tk.Frame(self.scrollable_frame, bg="#46abbd")
        m_frame.columnconfigure(1, weight=1)
        t_label = tk.Label(m_frame, bg="#46abbd", fg="white", text=datetime.now().strftime('%H:%M'),
                           font="lucida 7 bold",
                           justify="left", anchor="w")
        t_label.grid(row=0, column=1, padx=2, sticky="w")

        m_label = tk.Label(m_frame, wraplength=250, fg="black", bg="#c5c7c9", text=message, font="lucida 9 bold",
                           justify="left",
                           anchor="w")
        m_label.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        i_label = tk.Label(m_frame, bg="#46abbd", image=im)
        i_label.image = im
        i_label.grid(row=0, column=0, rowspan=2)

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def sent_message_format(self, event=None):

        message = self.entry.get('1.0', 'end-1c').strip()
        # self.entry.delete("0.0", END)
        if message != '':
            self.entry.delete("1.0", "end-1c")

            m_frame = tk.Frame(self.scrollable_frame, bg="#46abbd")

            m_frame.columnconfigure(0, weight=1)

            t_label = tk.Label(m_frame, bg="#46abbd", fg="white", text=datetime.now().strftime('%H:%M'),
                               font="lucida 7 bold", justify="right", anchor="e")
            t_label.grid(row=0, column=0, padx=2, sticky="e")

            m_label = tk.Label(m_frame, wraplength=250, text=message, fg="black", bg="#40C961",
                               font="lucida 9 bold", justify="left",
                               anchor="e")
            m_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")

            i_label = tk.Label(m_frame, bg="#46abbd", image=self.user_image)
            i_label.image = self.user_image
            i_label.grid(row=0, column=1, rowspan=2, sticky="e")

            m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

            msg = chatbot_response(message)

            self.received_message_format(msg)

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)

        ##=======================================================


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if (i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

    # ==================================================================================================

    def first_screen(self):
        self.destroy()
        self.parent.geometry(f"550x400+{self.parent.x_co}+{self.parent.y_co}")
        self.parent.frame.pack(fill="both", expand=True)
        self.window = None


SaisirInfoPersonnel()
