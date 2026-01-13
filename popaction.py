
import tkinter as tk
from tkinter import *
from customtkinter import *
from tkinter import messagebox
from PIL import Image , ImageTk , ImageGrab
from pathlib import Path
import cv2
import webbrowser
import mysql.connector
import CTkListbox as ctl
import datetime
import random
import qrcode
import io
import hashlib
import json


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets")
TICKETS_PATH = OUTPUT_PATH / Path(r"bookings")
CONFIG_PATH = OUTPUT_PATH / Path(r"config")


def relative_to_assets(path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):  # PyInstaller bundles files in a temporary directory
        base_path = Path(sys._MEIPASS)
        return base_path / "assets" / path
    else:
        return ASSETS_PATH / path

def tickets_booked(path: str) -> Path:
    return TICKETS_PATH / Path(path)

def database_config(path: str) -> Path:
    return CONFIG_PATH / Path(path)


window = CTk()
window.geometry("1220x775")
window.title("Popaction™")
window.iconbitmap(relative_to_assets("logo-pop-ico.ico"))
window.configure(fg_color = "#111111")


class AutoCompleteEntry(CTkEntry):

    def __init__(self, master, suggestions, placeholder=None, **kwargs):
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.suggestions = suggestions
        self.placeholder = placeholder

        if self.placeholder:
            self.insert_placeholder()

        self.var.trace_add('write', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self.lb_up = False
        self.lb_frame = None
        self.lb = None
        self.listbox_destroyed = False

    def insert_placeholder(self):
        self.insert(0, self.placeholder)
        self.configure(fg_color="#242424")

    def remove_placeholder(self):
        current_text = self.get()
        if current_text == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg_color="#242424")

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg_color="#242424")

    def on_focus_out(self, event):
        if not self.get():
            self.insert_placeholder()

    def changed(self, *args):
        if self.var.get() == '' or self.listbox_destroyed:
            self.destroy_listbox()
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb_frame = CTkFrame(self.master)
                    self.lb = ctl.CTkListbox(self.lb_frame,
                                             width=400,
                                             border_width=0,
                                             fg_color="#242424",
                                             font=("Satoshi-Regular", 20),
                                             text_color="#F3F3F3",
                                             bg_color="#111111",
                                             hover_color="#373737",
                                             command=self.show_value)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Return>", self.selection)
                    self.lb.pack(side="top", fill="both", expand=True)
                    self.lb_frame.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True
                if self.lb and self.lb.winfo_exists():
                    self.lb.delete(0, tk.END)
                    for w in words:
                        self.lb.insert(tk.END, w)
            else:
                self.destroy_listbox()

    def destroy_listbox(self):
        if self.lb_up:
            if self.lb and self.lb.winfo_exists():
                self.lb.destroy()
                self.lb = None  # Set to None after destruction
            if self.lb_frame and self.lb_frame.winfo_exists():
                self.lb_frame.destroy()
                self.lb_frame = None  # Set to None after destruction
            self.lb_up = False
            self.listbox_destroyed = False

    def selection(self, event):
        if self.lb_up and self.lb and self.lb.winfo_exists():
            try:
                self.var.set(self.lb.get(tk.ACTIVE))
            except tk.TclError:
                return
            self.destroy_listbox()
            self.icursor(tk.END)

    def move_up(self, event):
        if self.lb_up and self.lb and self.lb.winfo_exists():
            try:
                if self.lb.curselection() == ():
                    index = '0'
                else:
                    index = self.lb.curselection()[0]
                if index != '0':
                    self.lb.selection_clear(first=index)
                    index = str(int(index) - 1)
                    self.lb.selection_set(first=index)
                    self.lb.activate(index)
            except tk.TclError:
                return

    def move_down(self, event):
        if self.lb_up and self.lb and self.lb.winfo_exists():
            try:
                if self.lb.curselection() == ():
                    index = '-1'
                else:
                    index = self.lb.curselection()[0]
                if index != tk.END:
                    self.lb.selection_clear(first=index)
                    index = str(int(index) + 1)
                    self.lb.selection_set(first=index)
                    self.lb.activate(index)
            except tk.TclError:
                return

    def comparison(self):
        if self.listbox_destroyed:
            return []
        pattern = self.var.get()
        return [w for w in self.suggestions if w.lower().startswith(pattern.lower())]

    def show_value(self, selected_option):
        movie_update(selected_option)

file_data = open(database_config("config.json"))
config = json.load(file_data)
def database():
    try:
        global connect    
        connect = mysql.connector.connect(
            host = config["db_host"],
            user = config["db_user"],
            password = config["db_password"],
        )
        global cur
        cur = connect.cursor()
        print("Connection is established.")
    except:
        messagebox.showerror("Error" , "Database connectivity issue!")
        return

def loadingmain(canvas):

    video = cv2.VideoCapture(relative_to_assets("loadingshort.mov"))

    titlelabel = Label(
        master = window,
        bd = 0
    )
    titlelabel.place(
        relx = 0.5,
        rely = 0.5,
        anchor = "center"
    )

    def update_frame():
        ret, frame = video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame_image = ImageTk.PhotoImage(image=frame)
            titlelabel.config(image=frame_image)
            titlelabel.image = frame_image  
            window.after(1, update_frame)  
        else:
            video.release()
            titlelabel.destroy()
            lambda : titlecanvas.destroy()
            if canvas == "titlecanvas":
                temphome()
            elif canvas == "landingcanvas":
                tempmain()
            elif canvas == "detailcanvas":
                detailselect()
            elif canvas == "bookingcanvas":
                booking()
            elif canvas == "ticketshowcanvas":
                ticketshow()
            else:
                prebooked(canvas)
    
    update_frame()

def tempload():

    def titleload():
        
        global titlecanvas
        titlecanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        titlecanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )

        video = cv2.VideoCapture(relative_to_assets("popaction.mov"))

        titlelabel = Label(
            master = titlecanvas,
            bd = 0
        )
        titlelabel.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )

        def update_frame():
            ret, frame = video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frame_image = ImageTk.PhotoImage(image=frame)
                titlelabel.config(image=frame_image)
                titlelabel.image = frame_image  
                window.after(1, update_frame)  
            else:
                video.release()
                titlelabel.destroy()
                loadingmain("titlecanvas")
        
        update_frame()
            
    titleload()

def permelements(canvas):

    image_logo = Image.open(relative_to_assets("logo-pop.png"),"r")
    logolabel = CTkLabel(
        master = canvas,
        text = "",
        image = CTkImage(
            light_image = image_logo,
            dark_image = image_logo,
            size = (20,20)
        )
    )
    logolabel.place(
        x = 10,
        y = 10,
        anchor = "center"
    )

    def privacy():
        webbrowser.open(relative_to_assets("PrivacyPolicy.html") , 1)
    button_privacy = CTkButton(
        master = canvas,
        text = "Privacy Policy | Terms of Condition",
        font = ("GeneralSans-Regular" , 12 * -1),
        text_color = "#EEEEEE",
        fg_color = "#111111",
        hover_color = "#111111",
        command = lambda : privacy()
    )
    button_privacy.bind("<Enter>", lambda event : button_privacy.configure(text_color="#CCCCCC")) 
    button_privacy.bind("<Leave>", lambda event : button_privacy.configure(text_color="#EEEEEE"))   
    button_privacy.place(
        relx = 0.01,
        rely = 0.99,
        anchor = "sw"
    )

logname = str(None)
cityname = str(None)
movie = str(None)

def temphome():

    homecanvas = CTkCanvas(
        master = window,
        bd = 0,
        bg = "#111111" ,
        width = 1220,
        height = 775,
        highlightthickness = 0,
        borderwidth = 0
    )
    homecanvas.place(
        relx = 0.5, 
        rely = 0.5,
        anchor = "center"
    )

    video = cv2.VideoCapture(relative_to_assets("background.mov"))

    backlabel = Label(
        master = homecanvas,
        bd = 0
    )
    backlabel.place(
        x = 1015,
        rely = 0.5,
        anchor = "center"
    )

    def video_loop(root, cap, label):
        
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 
            ret, frame = cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=frame)

            label.configure(image=photo)
            label.image = photo  

            root.after(5, lambda: video_loop(root, cap, label))  
            
    video_loop(window , video , backlabel)

    def loading(tempcanvas):

        video = cv2.VideoCapture(relative_to_assets("loadingsmall.mov"))

        titlelabel = Label(
            master = tempcanvas,
            bd = 0
        )
        titlelabel.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )
        

        def update_frame():
            ret, frame = video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frame_image = ImageTk.PhotoImage(image=frame)
                titlelabel.config(image=frame_image)
                titlelabel.image = frame_image  
                window.after(5, update_frame)  
            else:
                video.release()
                titlelabel.destroy()
                tempcanvas.destroy()
        
        update_frame()

    def homepage():

        homemaincanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        homemaincanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        permelements(homemaincanvas)

        sloganlabel = CTkLabel(
            master = homemaincanvas,
            text = "Where's your next action?",
            font = ("GeneralSans-Bold" , (20 * 1)),
            text_color = "#E0E0E0"
        )
        sloganlabel.place(
            relx = 0.5,
            y = 10,
            anchor = "center"
        )

        mainslogan2label = CTkLabel(
            master = homemaincanvas,
            text = "Theatre Experience.",
            font = ("Satoshi-Black" , (64 * 1)),
            text_color = "#EEEEEE"
        )
        mainslogan2label.place(
            relx = 0.5,
            rely = 0.4,
            anchor = "center"
        )
        mainsloganredlabel = CTkLabel(
            master = homemaincanvas,
            text = ".",
            font = ("Satoshi-Black" , (64 * 1)),
            text_color = "#DF1827"
        )
        mainsloganredlabel.place(
            relx = 0.877,
            rely = 0.4,
            anchor = "center"
        )

        mainsloganlabel = CTkLabel(
            master = homemaincanvas,
            text = "Elevate your",
            font = ("Satoshi-Light" , (64 * 1)),
            text_color = "#EEEEEE"
        )
        mainsloganlabel.place(
            relx = 0.107,
            rely = 0.3,
            anchor = "w"
        )
        
        buttongetstarted = CTkButton(
            master = homemaincanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Get Started",
            font = ("Satoshi-Medium" , (40 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : (homemaincanvas.destroy() , signup())
        )
        buttongetstarted.bind("<Enter>", lambda event : buttongetstarted.configure(
            text_color="#CCCCCC",
            fg_color = "#7B0D15"
            )
        ) 
        buttongetstarted.bind("<Leave>", lambda event : buttongetstarted.configure(
            text_color="#EEEEEE",
            fg_color = "#DF1827"
            )
        ) 
        buttongetstarted.place(
            x = 535,
            rely = 0.6,
            anchor = "center"
        )

        buttonlogin = CTkButton(
            master = homemaincanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Login",
            font = ("Satoshi-Medium" , (40 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#414141",
            hover_color = "#242424",
            command = lambda : (homemaincanvas.destroy() , login())
        )
        buttonlogin.bind("<Enter>", lambda event : buttonlogin.configure(
            text_color="#CCCCCC",
            fg_color = "#242424"
            )
        ) 
        buttonlogin.bind("<Leave>", lambda event : buttonlogin.configure(
            text_color="#EEEEEE",
            fg_color = "#414141"
            )
        ) 
        buttonlogin.place(
            x = 260,
            rely = 0.6,
            anchor = "center"
        )

        mainsloganlabel = CTkLabel(
            master = homemaincanvas,
            text = "or continue via",
            font = ("GeneralSans-Regular" , (24 * 1)),
            text_color = "#EEEEEE"
        )
        mainsloganlabel.place(
            relx = 0.5,
            rely = 0.7,
            anchor = "center"
        )

        image_image_meta = Image.open(relative_to_assets("meta.png") , "r")
        image_meta = CTkImage(
            light_image = image_image_meta,
            dark_image = image_image_meta,
            size = (24 , 24)
        )
        button_meta = CTkButton(
            master = homemaincanvas,
            width = 22.0,
            height = 22.0,
            text = "",
            image = image_meta,
            fg_color = "#414141",
            hover_color = "#242424",
            corner_radius = 10.0,
            border_color = "#C3C3C3",
            border_width = 1,
            command = lambda : messagebox.showinfo("Important!" , "This feature is still under development!")
        )   
        button_meta.place(
            relx = 0.42,
            rely = 0.75,
            anchor = "center"
        )

        image_image_google = Image.open(relative_to_assets("google.png") , "r")
        image_google = CTkImage(
            light_image = image_image_google,
            dark_image = image_image_google,
            size = (24 , 24)
        )
        button_google = CTkButton(
            master = homemaincanvas,
            width = 22.0,
            height = 22.0,
            text = "",
            image = image_google,
            fg_color = "#414141",
            hover_color = "#242424",
            corner_radius = 10.0,
            border_color = "#C3C3C3",
            border_width = 1,
            command = lambda : messagebox.showinfo("Important!" , "This feature is still under development!")
        )   
        button_google.place(
            relx = 0.5,
            rely = 0.75,
            anchor = "center"
        )

        image_image_github = Image.open(relative_to_assets("github.png") , "r")
        image_github = CTkImage(
            light_image = image_image_github,
            dark_image = image_image_github,
            size = (24 , 24)
        )
        button_github = CTkButton(
            master = homemaincanvas,
            width = 22.0,
            height = 22.0,
            text = "",
            image = image_github,
            fg_color = "#414141",
            hover_color = "#242424",
            corner_radius = 10.0,
            border_color = "#C3C3C3",
            border_width = 1,
            command = lambda : messagebox.showinfo("Important!" , "This feature is still under development!")
        )   
        button_github.place(
            relx = 0.58,
            rely = 0.75,
            anchor = "center"
        )

    def logsignperm(canvas):
        
        def temphome():
            homemaintempcanvas = CTkCanvas(
                master = homecanvas,
                bd = 0,
                bg = "#111111" ,
                width = 795,
                height = 745,
                highlightthickness = 0,
                borderwidth = 0
            )
            homemaintempcanvas.place(
                x = 412.5, 
                rely = 0.5,
                anchor = "center"
            )

            loading(homemaintempcanvas)
        
        homebutton = CTkButton(
            master = canvas,
            text = "Home",
            font = ("GeneralSans-Regular" , 18 * -1),
            text_color = "#EEEEEE",
            fg_color = "#111111",
            hover_color = "#111111",
            command = lambda : (canvas.destroy() , homepage() , temphome())
        )
        homebutton.bind("<Enter>", lambda event : homebutton.configure(text_color="#CCCCCC")) 
        homebutton.bind("<Leave>", lambda event : homebutton.configure(text_color="#EEEEEE"))   
        homebutton.place(
            x = 285,
            y = 10,
            anchor = "center"
        )

        supportbutton = CTkButton(
            master = canvas,
            text = "Support",
            font = ("GeneralSans-Regular" , 18 * -1),
            text_color = "#EEEEEE",
            fg_color = "#111111",
            hover_color = "#111111",
            command = lambda : messagebox.showinfo("Important!" , "This feature is still under development!")
        )
        supportbutton.bind("<Enter>", lambda event : supportbutton.configure(text_color="#CCCCCC")) 
        supportbutton.bind("<Leave>", lambda event : supportbutton.configure(text_color="#EEEEEE"))   
        supportbutton.place(
            x = 515,
            y = 10,
            anchor = "center"
        )

    def dynamic_place_small(entry , label):
        user = entry.get()
        if user == "":
            entry.focus_set()
            label.place(
            relx = 0.04,
            rely = 0.15,
            anchor = "w"
            )
            

    def dynamic_remove_small(entry , label):
        user = entry.get()
        if user == "":
            label.focus_set()
            label.place_forget()


    def dynamic_place_large(entry , label):
        user = entry.get()
        if user == "":
            entry.focus_set()
            label.place(
            relx = 0.017,
            rely = 0.15,
            anchor = "w"
            )
            

    def dynamic_remove_large(entry , label):
        user = entry.get()
        if user == "":
            label.focus_set()
            label.place_forget()

    image_image_show = Image.open(relative_to_assets("show.png") , "r")
    image_show = CTkImage(
        light_image = image_image_show,
        dark_image = image_image_show,
        size = (27 , 27)
    )

    image_image_hide = Image.open(relative_to_assets("hide.png") , "r")
    image_hide = CTkImage(
        light_image = image_image_hide,
        dark_image = image_image_hide,
        size = (27 , 27)
    )

    def show_password(entry):
        button_password = CTkButton(
            master = entry,
            width = 34,
            text = "",
            image = image_hide,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda  : hide_password(entry)
        )   
        button_password.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )
        entry.configure(show = "")

    def hide_password(entry):
        button_password = CTkButton(
            master = entry,
            width = 34,
            text = "",
            image = image_show,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda  : show_password(entry)
        )   
        button_password.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )
        entry.configure(show = "*")

    def signup():

        def userregister():
            if entry_fname.get() == '' or entry_lname.get() == '' or entry_email.get() == '' or entry_password.get() == '' or entry_conpassword.get() == '':
                messagebox.showerror("Error" , "All fields are required!")
            else:
                database()
                try:
                    cur.execute("CREATE DATABASE popaction_data")
                    cur.execute("USE popaction_data")
                    cur.execute("CREATE TABLE credentials (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL , first_name VARCHAR(50) , last_name VARCHAR(50) , email VARCHAR(50) , password VARCHAR(50))")
                except:
                    cur.execute("USE popaction_data")

                cur.execute("SELECT * FROM credentials WHERE email = %s" , (entry_email.get(),))
                row = cur.fetchone()
                if row != None:
                    messagebox.showerror("Error" , "Email already exists!")
                else:
                    if '@' not in entry_email.get():
                        messagebox.showerror("Error" , "Invalid Email!")
                    elif len(entry_password.get()) < 8:
                        messagebox.showerror("Error" , "Password must have 8 or more characters!")
                    elif entry_password.get() != entry_conpassword.get():
                        messagebox.showerror("Error" , "Password Mismatch!")
                    else:
                        cur.execute("INSERT INTO credentials (first_name , last_name , email , password) values (%s , %s , %s , %s)" , (entry_fname.get() , entry_lname.get() , entry_email.get() , entry_password.get()))
                        connect.commit()
                        connect.close()
                        messagebox.showinfo("Success" , "Registration is successful!")
                        signupcanvas.destroy()
                        login()

        signupcanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        signupcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )
        
        tempsignupcanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        tempsignupcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        loading(tempsignupcanvas)
            
        permelements(signupcanvas)

        logsignperm(signupcanvas)

        button_login = CTkButton(
            master = signupcanvas,
            text = "Login.",
            font = ("Satoshi-Black" , 18 * -1),
            text_color = "#DF1827",
            fg_color = "#111111",
            hover_color = "#111111",
            command = lambda : (signupcanvas.destroy() , login())
        )
        button_login.bind("<Enter>", lambda event : button_login.configure(text_color="#7B0D15")) 
        button_login.bind("<Leave>", lambda event : button_login.configure(text_color="#DF1827"))   
        button_login.place(
            relx = 0.425,
            rely = 0.224,
            anchor = "center"
        )

        mainslogan3label = CTkLabel(
            master = signupcanvas,
            text = "Already have an account?",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan3label.place(
            relx = 0.1,
            rely = 0.225,
            anchor = "w"
        )

        mainslogan2label = CTkLabel(
            master = signupcanvas,
            text = "Create new account",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#EEEEEE"
        )
        mainslogan2label.place(
            relx = 0.097,
            rely = 0.175,
            anchor = "w"
        )
        mainsloganredlabel = CTkLabel(
            master = signupcanvas,
            text = ".",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#DF1827"
        )
        mainsloganredlabel.place(
            relx = 0.635,
            rely = 0.175,
            anchor = "w"
        )

        mainslogan1label = CTkLabel(
            master = signupcanvas,
            text = "START FOR FREE",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan1label.place(
            relx = 0.1,
            rely = 0.13,
            anchor = "w"
        )

        image__image_user = Image.open(relative_to_assets("user.png") , "r")
        image_user = CTkImage(
            light_image = image__image_user,
            dark_image = image__image_user,
            size = (34 , 34)
        )

        frame_fname = CTkFrame(
            master = signupcanvas,
            width = 310,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_fname.place(
            relx = 0.2923,
            rely = 0.32,
            anchor = "center"
        )
        label_fname = CTkLabel(
            master = frame_fname,
            text = "First Name",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_fname = CTkEntry(
            master = frame_fname,
            width = 300,
            height = 42,
            placeholder_text = "First Name",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC"
        )
        entry_fname.bind("<Enter>" , lambda event : dynamic_place_small(entry_fname , label_fname)) 
        entry_fname.bind("<Leave>" , lambda event : dynamic_remove_small(entry_fname , label_fname))
        entry_fname.bind("<Tab>" , lambda event : entry_fname.focus_set())
        entry_fname.bind("<FocusIn>" , lambda event : dynamic_place_small(entry_fname , label_fname))
        entry_fname.bind("<FocusOut>" , lambda event : dynamic_remove_small(entry_fname , label_fname))
        entry_fname.place(
            x = 155,
            rely = 0.93,
            anchor = "s"
        )
        labelusername = CTkLabel(
            master = entry_fname,
            text = "",
            image = image_user,
            bg_color = "transparent",
            fg_color = "#373737"
        )
        labelusername.place(
            relx = 0.993,
            rely = 0.5,
            anchor = "e"
        )

        frame_lname = CTkFrame(
            master = signupcanvas,
            width = 310,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_lname.place(
            relx = 0.7077,
            rely = 0.32,
            anchor = "center"
        )
        label_lname = CTkLabel(
            master = frame_lname,
            text = "Last Name",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_lname = CTkEntry(
            master = frame_lname,
            width = 300,
            height = 42,
            placeholder_text = "Last Name",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC"
        )
        entry_lname.bind("<Enter>" , lambda event : dynamic_place_small(entry_lname , label_lname)) 
        entry_lname.bind("<Leave>" , lambda event : dynamic_remove_small(entry_lname , label_lname))
        entry_lname.bind("<Tab>" , lambda event : entry_lname.focus_set())
        entry_lname.bind("<FocusIn>" , lambda event : dynamic_place_small(entry_lname , label_lname))
        entry_lname.bind("<FocusOut>" , lambda event : dynamic_remove_small(entry_lname , label_lname))
        entry_lname.place(
            x = 155,
            rely = 0.93,
            anchor = "s"
        )
        labelusername = CTkLabel(
            master = entry_lname,
            text = "",
            image = image_user,
            bg_color = "transparent",
            fg_color = "#373737"
        )
        labelusername.place(
            relx = 0.993,
            rely = 0.5,
            anchor = "e"
        )

        frame_email = CTkFrame(
            master = signupcanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_email.place(
            relx = 0.5,
            rely = 0.435,
            anchor = "center"
        )
        label_email = CTkLabel(
            master = frame_email,
            text = "Email",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_email = CTkEntry(
            master = frame_email,
            width = 630,
            height = 42,
            placeholder_text = "Email",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC"
        )
        entry_email.bind("<Enter>" , lambda event : dynamic_place_large(entry_email , label_email)) 
        entry_email.bind("<Leave>" , lambda event : dynamic_remove_large(entry_email , label_email))
        entry_email.bind("<Tab>" , lambda event : entry_email.focus_set())
        entry_email.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_email , label_email))
        entry_email.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_email , label_email)) 
        entry_email.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        image_image_email = Image.open(relative_to_assets("email.png") , "r")
        image_email = CTkImage(
            light_image = image_image_email,
            dark_image = image_image_email,
            size = (34 , 34)
        )
        label_image_email = CTkLabel(
            master = entry_email,
            text = "",
            image = image_email,
            bg_color = "transparent",
            fg_color = "#373737"
        )
        label_image_email.place(
            relx = 0.994,
            rely = 0.5,
            anchor = "e"
        )

        frame_password = CTkFrame(
            master = signupcanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_password.place(
            relx = 0.5,
            rely = 0.55,
            anchor = "center"
        )
        label_password = CTkLabel(
            master = frame_password,
            text = "Password",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_password = CTkEntry(
            master = frame_password,
            width = 630,
            height = 42,
            placeholder_text = "Password",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC",
            show = "*"
        )
        entry_password.bind("<Enter>" , lambda event : dynamic_place_large(entry_password , label_password)) 
        entry_password.bind("<Leave>" , lambda event : dynamic_remove_large(entry_password , label_password))
        entry_password.bind("<Tab>" , lambda event : entry_password.focus_set())
        entry_password.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_password , label_password))
        entry_password.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_password , label_password)) 
        entry_password.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        
        button_image_password = CTkButton(
            master = entry_password,
            width = 34,
            text = "",
            image = image_show,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda : show_password(entry_password)
        )
        button_image_password.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )

        frame_conpassword = CTkFrame(
            master = signupcanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_conpassword.place(
            relx = 0.5,
            rely = 0.665,
            anchor = "center"
        )
        label_conpassword = CTkLabel(
            master = frame_conpassword,
            text = "Confirm Password",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_conpassword = CTkEntry(
            master = frame_conpassword,
            width = 630,
            height = 42,
            placeholder_text = "Confirm Password",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC",
            show = "*"
        )
        entry_conpassword.bind("<Enter>" , lambda event : dynamic_place_large(entry_conpassword , label_conpassword)) 
        entry_conpassword.bind("<Leave>" , lambda event : dynamic_remove_large(entry_conpassword , label_conpassword))
        entry_conpassword.bind("<Tab>" , lambda event : entry_conpassword.focus_set())
        entry_conpassword.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_conpassword , label_conpassword))
        entry_conpassword.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_conpassword , label_conpassword)) 
        entry_conpassword.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        
        button_image_conpassword = CTkButton(
            master = entry_conpassword,
            width = 34,
            text = "",
            image = image_show,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda : show_password(entry_conpassword)
        )
        button_image_conpassword.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )

        buttongetstarted = CTkButton(
            master = signupcanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Register",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : userregister()
        )
        buttongetstarted.bind("<Enter>", lambda event : buttongetstarted.configure(
            text_color="#CCCCCC",
            fg_color = "#7B0D15"
            )
        ) 
        buttongetstarted.bind("<Leave>", lambda event : buttongetstarted.configure(
            text_color="#EEEEEE",
            fg_color = "#DF1827"
            )
        ) 
        buttongetstarted.place(
            x = 535,
            rely = 0.8,
            anchor = "center"
        )

        buttonchange = CTkButton(
            master = signupcanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Change Method",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#414141",
            hover_color = "#242424",
            command = lambda : (signupcanvas.destroy() , signup())
        )
        buttonchange.bind("<Enter>", lambda event : buttonchange.configure(
            text_color="#CCCCCC",
            fg_color = "#242424"
            )
        ) 
        buttonchange.bind("<Leave>", lambda event : buttonchange.configure(
            text_color="#EEEEEE",
            fg_color = "#414141"
            )
        ) 
        buttonchange.place(
            x = 260,
            rely = 0.8,
            anchor = "center"
        )


    def login():

        def userlogin():
            if entry_email.get() == '' or entry_password.get() == '':
                messagebox.showerror("Error" , "All fields are required!")
            else:
                database()
                try:
                    cur.execute("CREATE DATABASE popaction_data")
                    cur.execute("USE popaction_data")
                    cur.execute("CREATE TABLE credentials (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL , first_name VARCHAR(50) , last_name VARCHAR(50) , email VARCHAR(50) , password VARCHAR(50))")
                except:
                    cur.execute("USE popaction_data")
                cur.execute("SELECT * FROM credentials WHERE email = %s" , (entry_email.get() , ))
                data = cur.fetchone()
                if data == None:
                    messagebox.showerror("Error!" , "Invalid Email!")
                elif data[4] != entry_password.get():
                    messagebox.showerror("Error!" , "Invalid Password!")
                else:
                    cur.execute("SELECT first_name FROM credentials WHERE email = %s" , (entry_email.get() , ))
                    global logname
                    logname = cur.fetchone()[0]
                    cur.execute("SELECT id FROM credentials WHERE email = %s" , (entry_email.get() , ))
                    global logid
                    logid = cur.fetchone()[0]
                    video.release()
                    homecanvas.destroy()
                    loadingmain("landingcanvas")
        
        logincanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        logincanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )
        
        templogincanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        templogincanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        loading(templogincanvas)
        
        permelements(logincanvas)

        logsignperm(logincanvas)
        
        button_register = CTkButton(
            master = logincanvas,
            text = "Register.",
            font = ("Satoshi-Black" , 18 * -1),
            text_color = "#DF1827",
            fg_color = "#111111",
            hover_color = "#111111",
            command = lambda : (logincanvas.destroy() , signup())
        )
        button_register.bind("<Enter>", lambda event : button_register.configure(text_color="#7B0D15")) 
        button_register.bind("<Leave>", lambda event : button_register.configure(text_color="#DF1827"))   
        button_register.place(
            relx = 0.415,
            rely = 0.224,
            anchor = "center"
        )
        
        mainslogan3label = CTkLabel(
            master = logincanvas,
            text = "Don't have an account?",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan3label.place(
            relx = 0.1,
            rely = 0.225,
            anchor = "w"
        )

        mainslogan2label = CTkLabel(
            master = logincanvas,
            text = "Welcome back!",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#EEEEEE"
        )
        mainslogan2label.place(
            relx = 0.1,
            rely = 0.175,
            anchor = "w"
        )
        mainsloganredlabel = CTkLabel(
            master = logincanvas,
            text = "!",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#DF1827"
        )
        mainsloganredlabel.place(
            relx = 0.5,
            rely = 0.175,
            anchor = "w"
        )

        mainslogan1label = CTkLabel(
            master = logincanvas,
            text = "LOGIN TO YOUR ACCOUNT",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan1label.place(
            relx = 0.1,
            rely = 0.13,
            anchor = "w"
        )

        frame_email = CTkFrame(
            master = logincanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_email.place(
            relx = 0.5,
            rely = 0.32,
            anchor = "center"
        )
        label_email = CTkLabel(
            master = frame_email,
            text = "Email",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_email = CTkEntry(
            master = frame_email,
            width = 630,
            height = 42,
            placeholder_text = "Email",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC"
        )
        entry_email.bind("<Enter>" , lambda event : dynamic_place_large(entry_email , label_email)) 
        entry_email.bind("<Leave>" , lambda event : dynamic_remove_large(entry_email , label_email))
        entry_email.bind("<Tab>" , lambda event : entry_email.focus_set())
        entry_email.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_email , label_email))
        entry_email.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_email , label_email)) 
        entry_email.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        image_image_email = Image.open(relative_to_assets("email.png") , "r")
        image_email = CTkImage(
            light_image = image_image_email,
            dark_image = image_image_email,
            size = (34 , 34)
        )
        label_image_email = CTkLabel(
            master = entry_email,
            text = "",
            image = image_email,
            bg_color = "transparent",
            fg_color = "#373737"
        )
        label_image_email.place(
            relx = 0.994,
            rely = 0.5,
            anchor = "e"
        )

        frame_password = CTkFrame(
            master = logincanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_password.place(
            relx = 0.5,
            rely = 0.435,
            anchor = "center"
        )
        label_password = CTkLabel(
            master = frame_password,
            text = "Password",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_password = CTkEntry(
            master = frame_password,
            width = 630,
            height = 42,
            placeholder_text = "Password",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC",
            show = "*"
        )
        entry_password.bind("<Enter>" , lambda event : dynamic_place_large(entry_password , label_password)) 
        entry_password.bind("<Leave>" , lambda event : dynamic_remove_large(entry_password , label_password))
        entry_password.bind("<Tab>" , lambda event : entry_password.focus_set())
        entry_password.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_password , label_password))
        entry_password.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_password , label_password)) 
        entry_password.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        
        button_image_password = CTkButton(
            master = entry_password,
            width = 34,
            text = "",
            image = image_show,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda : show_password(entry_password)
        )
        button_image_password.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )

        button_forgot = CTkButton(
            master = logincanvas,
            text = "Forgot Password?",
            font = ("Satoshi-Regular" , 17 * -1),
            text_color = "#FFFFFF",
            fg_color = "#11181D",
            hover_color = "#11181D",
            command = lambda : (logincanvas.destroy() , newpass())
        )
        button_forgot.bind("<Enter>", lambda event : button_forgot.configure(text_color="#CCCCCC")) 
        button_forgot.bind("<Leave>", lambda event : button_forgot.configure(text_color="#EEEEEE"))   
        button_forgot.place(
            relx = 0.097,
            rely = 0.5,
            anchor = "w"
        )

        buttongetlogged = CTkButton(
            master = logincanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Login",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : userlogin()
        )
        buttongetlogged.bind("<Enter>", lambda event : buttongetlogged.configure(
            text_color="#CCCCCC",
            fg_color = "#7B0D15"
            )
        ) 
        buttongetlogged.bind("<Leave>", lambda event : buttongetlogged.configure(
            text_color="#EEEEEE",
            fg_color = "#DF1827"
            )
        ) 
        buttongetlogged.place(
            x = 535,
            rely = 0.635,
            anchor = "center"
        )

        buttonchange = CTkButton(
            master = logincanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Change Method",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#414141",
            hover_color = "#242424",
            command = lambda : (logincanvas.destroy() , login())
        )
        buttonchange.bind("<Enter>", lambda event : buttonchange.configure(
            text_color="#CCCCCC",
            fg_color = "#242424"
            )
        ) 
        buttonchange.bind("<Leave>", lambda event : buttonchange.configure(
            text_color="#EEEEEE",
            fg_color = "#414141"
            )
        ) 
        buttonchange.place(
            x = 260,
            rely = 0.635,
            anchor = "center"
        )

    def newpass():

        def userreset():
            if entry_email.get() == '' or entry_password.get() == '':
                messagebox.showerror("Error" , "All fields are required!")
            else:
                database()
                try:
                    cur.execute("CREATE DATABASE popaction_data")
                    cur.execute("USE popaction_data")
                    cur.execute("CREATE TABLE credentials (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL , first_name VARCHAR(50) , last_name VARCHAR(50) , email VARCHAR(50) , password VARCHAR(50))")
                except:
                    cur.execute("USE popaction_data")
                cur.execute("SELECT * FROM credentials WHERE email = %s" , (entry_email.get() , ))
                data = cur.fetchone()
                if data == None:
                    messagebox.showerror("Error!" , "Invalid Email!")
                else:
                    if len(entry_password.get()) < 8:
                        messagebox.showerror("Error" , "Password must have 8 or more characters!")
                    else:
                        cur.execute("UPDATE credentials SET password = %s WHERE email = %s" , (entry_password.get() , entry_email.get()))
                        connect.commit()
                        connect.close()
                        messagebox.showinfo("Success" , "Password Updated!")
                        newpasscanvas.destroy()
                        login()

        newpasscanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        newpasscanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )
        
        tempnewpasscanvas = CTkCanvas(
            master = homecanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        tempnewpasscanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        loading(tempnewpasscanvas)
        
        permelements(newpasscanvas)

        logsignperm(newpasscanvas)

        button_register = CTkButton(
            master = newpasscanvas,
            text = "Login.",
            font = ("Satoshi-Black" , 18 * -1),
            text_color = "#DF1827",
            fg_color = "#111111",
            hover_color = "#111111",
            command = lambda : (newpasscanvas.destroy() , login())
        )
        button_register.bind("<Enter>", lambda event : button_register.configure(text_color="#7B0D15")) 
        button_register.bind("<Leave>", lambda event : button_register.configure(text_color="#DF1827"))   
        button_register.place(
            relx = 0.443,
            rely = 0.224,
            anchor = "center"
        )
        
        mainslogan3label = CTkLabel(
            master = newpasscanvas,
            text = "Remember your password?",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan3label.place(
            relx = 0.1,
            rely = 0.225,
            anchor = "w"
        )

        mainslogan2label = CTkLabel(
            master = newpasscanvas,
            text = "Enter new credentials.",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#EEEEEE"
        )
        mainslogan2label.place(
            relx = 0.098,
            rely = 0.175,
            anchor = "w"
        )
        mainsloganredlabel = CTkLabel(
            master = newpasscanvas,
            text = ".",
            font = ("Satoshi-Black" , (44 * 1)),
            text_color = "#DF1827"
        )
        mainsloganredlabel.place(
            relx = 0.7,
            rely = 0.175,
            anchor = "w"
        )

        mainslogan1label = CTkLabel(
            master = newpasscanvas,
            text = "RESET PASSWORD",
            font = ("Satoshi-Black" , (18 * 1)),
            text_color = "#C3C3C3"
        )
        mainslogan1label.place(
            relx = 0.1,
            rely = 0.13,
            anchor = "w"
        )

        frame_email = CTkFrame(
            master = newpasscanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_email.place(
            relx = 0.5,
            rely = 0.32,
            anchor = "center"
        )
        label_email = CTkLabel(
            master = frame_email,
            text = "Email",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_email = CTkEntry(
            master = frame_email,
            width = 630,
            height = 42,
            placeholder_text = "Email",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC"
        )
        entry_email.bind("<Enter>" , lambda event : dynamic_place_large(entry_email , label_email)) 
        entry_email.bind("<Leave>" , lambda event : dynamic_remove_large(entry_email , label_email))
        entry_email.bind("<Tab>" , lambda event : entry_email.focus_set())
        entry_email.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_email , label_email))
        entry_email.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_email , label_email)) 
        entry_email.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        image_image_email = Image.open(relative_to_assets("email.png") , "r")
        image_email = CTkImage(
            light_image = image_image_email,
            dark_image = image_image_email,
            size = (34 , 34)
        )
        label_image_email = CTkLabel(
            master = entry_email,
            text = "",
            image = image_email,
            bg_color = "transparent",
            fg_color = "#373737"
        )
        label_image_email.place(
            relx = 0.994,
            rely = 0.5,
            anchor = "e"
        )

        frame_password = CTkFrame(
            master = newpasscanvas,
            width = 640,
            height = 70,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        frame_password.place(
            relx = 0.5,
            rely = 0.435,
            anchor = "center"
        )
        label_password = CTkLabel(
            master = frame_password,
            text = "Password",
            text_color = "#CCCCCC",
            font = ("Satoshi-Regular", 14 * -1)
        )
        entry_password = CTkEntry(
            master = frame_password,
            width = 630,
            height = 42,
            placeholder_text = "Password",
            font = ("Satoshi-Regular" , 24 * -1),
            bg_color = "transparent",
            fg_color = "#373737",
            border_width = 0,
            text_color = "#EEEEEE",
            placeholder_text_color = "#CCCCCC",
            show = "*"
        )
        entry_password.bind("<Enter>" , lambda event : dynamic_place_large(entry_password , label_password)) 
        entry_password.bind("<Leave>" , lambda event : dynamic_remove_large(entry_password , label_password))
        entry_password.bind("<Tab>" , lambda event : entry_password.focus_set())
        entry_password.bind("<FocusIn>" , lambda event : dynamic_place_large(entry_password , label_password))
        entry_password.bind("<FocusOut>" , lambda event : dynamic_remove_large(entry_password , label_password)) 
        entry_password.place(
            x = 320,
            rely = 0.93,
            anchor = "s"
        )
        
        button_image_password = CTkButton(
            master = entry_password,
            width = 34,
            text = "",
            image = image_show,
            bg_color = "transparent",
            fg_color = "#373737",
            hover_color = "#373737",
            command = lambda : show_password(entry_password)
        )
        button_image_password.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )

        buttongetlogged = CTkButton(
            master = newpasscanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Validate",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : userreset()
        )
        buttongetlogged.bind("<Enter>", lambda event : buttongetlogged.configure(
            text_color="#CCCCCC",
            fg_color = "#7B0D15"
            )
        ) 
        buttongetlogged.bind("<Leave>", lambda event : buttongetlogged.configure(
            text_color="#EEEEEE",
            fg_color = "#DF1827"
            )
        ) 
        buttongetlogged.place(
            x = 535,
            rely = 0.57,
            anchor = "center"
        )

        buttonchange = CTkButton(
            master = newpasscanvas,
            width = 250,
            height = 65,
            corner_radius = 10,
            text = "Change Method",
            font = ("Satoshi-Medium" , (30 * 1)),
            text_color = "#EEEEEE",
            bg_color = "transparent",
            fg_color = "#414141",
            hover_color = "#242424",
            command = lambda : (newpasscanvas.destroy() , newpass())
        )
        buttonchange.bind("<Enter>", lambda event : buttonchange.configure(
            text_color="#CCCCCC",
            fg_color = "#242424"
            )
        ) 
        buttonchange.bind("<Leave>", lambda event : buttonchange.configure(
            text_color="#EEEEEE",
            fg_color = "#414141"
            )
        ) 
        buttonchange.place(
            x = 260,
            rely = 0.57,
            anchor = "center"
        )


    homepage()

def tempmain():
    

    # Data to insert
    times = [
        ("INOX_Insignia", "10_00", "12_00", "14_00", "16_00", "18_00", "20_00"),
        ("IMAX", "09_00", "11_00", "13_00", "15_00", "17_00", "19_00"),
        ("SRS_Cinemas", "10_30", "12_30", "14_45", "16_30", "18_25", "20_30"),
        ("Cinepolis", "09_10", "11_30", "13_35", "16_45", "18_55", "20_10"),
        ("ScreenX", "09_10", "11_10", "13_10", "15_10", "17_10", "19_10"),
        ("Carnival_Cinemas", "10_30", "11_30", "14_45", "16_45", "18_25", "20_30"),
        ("PVR_Cinemas", "10_10", "12_10", "14_10", "16_10", "18_10", "20_10"),
        ("Miraj_Cinemas", "09_30", "11_25", "13_35", "16_24", "19_25", "20_30"),
        ("Wave_Cinemas", "09_30", "11_25", "13_35", "16_24", "19_25", "20_30"),
        ("ESQUARE_TALKIES", "10_30", "11_30", "14_45", "15_10", "17_10", "19_10"),
        ("Satyam_Cinemas", "09_30", "11_25", "13_35", "16_24", "19_25", "20_30"),
        ("SPI_Cinemas", "10_30", "11_30", "14_45", "16_45", "18_55", "20_10"),
        ("Mukta_A2_Cinemas", "09_00", "11_00", "13_00", "15_00", "17_00", "19_00"),
    ]

    halls = [
        ("Kolkata", "INOX_Insignia", "IMAX", "SRS_Cinemas", "Cinepolis", "ScreenX", "Carnival_Cinemas"),
        ("Delhi", "Mukta_A2_Cinemas", "IMAX", "PVR_Cinemas", "Miraj_Cinemas", "Carnival_Cinemas", "Wave_Cinemas"),
        ("Mumbai", "INOX_Insignia", "IMAX", "ESQUARE_TALKIES", "Wave_Cinemas", "ScreenX", "Satyam_Cinemas"),
        ("Chennai", "Miraj_Cinemas", "IMAX", "PVR_Cinemas", "Cinepolis", "ScreenX", "SPI_Cinemas")
    ]

    movies = [
        ("Oppenheimer", "oppenheimer" , "English" , "English" , "U/A"),
        ("Godzilla X Kong:The New Empire", "godzillaxkong" , "English" , "English" , "PG-13"),
        ("Dune:Part Two", "dune2" , "English" , "English" , "PG-13"),
        ("Fall Guy", "fallguy" , "English" , "English" , "PG-13"),
        ("Evil Does Not Exist", "evildoesnotexist" , "English" , "English" , "U/A"),
        ("Kingdom of the Planet of the Apes", "kingdomofapes" , "English" , "English" , "U/A"),
        ("The Boy and The Heron", "theboyandtheheron" , "Japanese" , "English" , "U/A"),
        ("The First Omen", "thefirstomen" , "English" , "English" , "U/A"),
        ("The Crow", "thecrow" , "English" , "English" , "PG-13"),
        ("Monkey Man", "monkeyman" , "English" , "English" , "A"),
        ("Monster", "monster" , "English" , "English" , "PG-13"),
        ("IF", "if" , "English" , "English" , "U/A"),
        ("The Strangers:Chapter 1", "strangers" , "English" , "English" , "U/A"),
        ("Atlas", "atlas" , "English" , "English" , "PG-13"),
        ("Furiosa:A Mad Max Saga", "furiosa" , "English" , "English" , "PG-13"),
        ("Kung Fu Panda 4", "kungfupanda4" , "English" , "English" , "PG"),
        ("Tarot", "tarot" , "English" , "English" , "PG-13"),
        ("Savi", "savi" , "Hindi" , "English" , "U/A"),
        ("The Garfield Movie", "thegarfield Movie" , "English" , "English" , "PG-13"),
        ("Srikanth", "srikanth" , "Hindi" , "English" , "U/A")
    ]

    database()
    cur.execute("USE popaction_data")


    def convert_to_12_hour_format(times):
        formatted_times = []
        for time in times:
            hour, minute = map(int, time.split('_'))
            period = "AM" if hour < 12 else "PM"
            hour = hour % 12
            hour = hour if hour != 0 else 12  # Adjust hour 0 to 12
            formatted_times.append(f"{hour}:{minute:02d} {period}")
        return formatted_times
    

    try:
        # Create tables
        cur.execute("""
        CREATE TABLE times (
            time_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            hall_name VARCHAR(50),
            time1 VARCHAR(50),
            time2 VARCHAR(50),
            time3 VARCHAR(50),
            time4 VARCHAR(50),
            time5 VARCHAR(50),
            time6 VARCHAR(50)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS halls (
            hall_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            city_name VARCHAR(50),
            hall_name VARCHAR(50),
            time_id INT,
            FOREIGN KEY (time_id) REFERENCES times(time_id) ON DELETE CASCADE
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies_kolkata (
            movie_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            mov_name VARCHAR(50),
            mov_images VARCHAR(50),
            language VARCHAR(50),
            subtitles_language VARCHAR(50),
            rating VARCHAR(50),
            hall1 VARCHAR(50),
            hall2 VARCHAR(50),
            hall3 VARCHAR(50),
            hall4 VARCHAR(50),
            time1_1 VARCHAR(50),
            time1_2 VARCHAR(50),
            time1_3 VARCHAR(50),
            time1_4 VARCHAR(50),
            time2_1 VARCHAR(50),
            time2_2 VARCHAR(50),
            time2_3 VARCHAR(50),
            time2_4 VARCHAR(50),
            time3_1 VARCHAR(50),
            time3_2 VARCHAR(50),
            time3_3 VARCHAR(50),
            time3_4 VARCHAR(50),
            time4_1 VARCHAR(50),
            time4_2 VARCHAR(50),
            time4_3 VARCHAR(50),
            time4_4 VARCHAR(50)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies_delhi (
            movie_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            mov_name VARCHAR(50),
            mov_images VARCHAR(50),
            language VARCHAR(50),
            subtitles_language VARCHAR(50),
            rating VARCHAR(50),
            hall1 VARCHAR(50),
            hall2 VARCHAR(50),
            hall3 VARCHAR(50),
            hall4 VARCHAR(50),
            time1_1 VARCHAR(50),
            time1_2 VARCHAR(50),
            time1_3 VARCHAR(50),
            time1_4 VARCHAR(50),
            time2_1 VARCHAR(50),
            time2_2 VARCHAR(50),
            time2_3 VARCHAR(50),
            time2_4 VARCHAR(50),
            time3_1 VARCHAR(50),
            time3_2 VARCHAR(50),
            time3_3 VARCHAR(50),
            time3_4 VARCHAR(50),
            time4_1 VARCHAR(50),
            time4_2 VARCHAR(50),
            time4_3 VARCHAR(50),
            time4_4 VARCHAR(50)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies_mumbai (
            movie_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            mov_name VARCHAR(50),
            mov_images VARCHAR(50),
            language VARCHAR(50),
            subtitles_language VARCHAR(50),
            rating VARCHAR(50),
            hall1 VARCHAR(50),
            hall2 VARCHAR(50),
            hall3 VARCHAR(50),
            hall4 VARCHAR(50),
            time1_1 VARCHAR(50),
            time1_2 VARCHAR(50),
            time1_3 VARCHAR(50),
            time1_4 VARCHAR(50),
            time2_1 VARCHAR(50),
            time2_2 VARCHAR(50),
            time2_3 VARCHAR(50),
            time2_4 VARCHAR(50),
            time3_1 VARCHAR(50),
            time3_2 VARCHAR(50),
            time3_3 VARCHAR(50),
            time3_4 VARCHAR(50),
            time4_1 VARCHAR(50),
            time4_2 VARCHAR(50),
            time4_3 VARCHAR(50),
            time4_4 VARCHAR(50)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies_chennai (
            movie_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            mov_name VARCHAR(50),
            mov_images VARCHAR(50),
            language VARCHAR(50),
            subtitles_language VARCHAR(50),
            rating VARCHAR(50),
            hall1 VARCHAR(50),
            hall2 VARCHAR(50),
            hall3 VARCHAR(50),
            hall4 VARCHAR(50),
            time1_1 VARCHAR(50),
            time1_2 VARCHAR(50),
            time1_3 VARCHAR(50),
            time1_4 VARCHAR(50),
            time2_1 VARCHAR(50),
            time2_2 VARCHAR(50),
            time2_3 VARCHAR(50),
            time2_4 VARCHAR(50),
            time3_1 VARCHAR(50),
            time3_2 VARCHAR(50),
            time3_3 VARCHAR(50),
            time3_4 VARCHAR(50),
            time4_1 VARCHAR(50),
            time4_2 VARCHAR(50),
            time4_3 VARCHAR(50),
            time4_4 VARCHAR(50)
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id VARCHAR(50) PRIMARY KEY NOT NULL,
            log_id INT,
            FOREIGN KEY (log_id) REFERENCES credentials(id) ON DELETE CASCADE,
            mov_name VARCHAR(100),
            date_time VARCHAR(100),
            rating_info VARCHAR(100),
            seats VARCHAR(50),
            hall_info VARCHAR(100),
            detail_seat VARCHAR(100),
            no_tickets INT,
            price VARCHAR(50),
            adv_detail VARCHAR(64)
        )
        """)

        # Insert data into the times table
        query_time = "INSERT INTO times (hall_name, time1, time2, time3, time4, time5, time6) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(query_time, times)
        connect.commit()

        # Fetch hall names and their time IDs
        cur.execute("SELECT time_id, hall_name FROM times")
        hall_time_map = cur.fetchall()
        hall_name_to_time_id = {hall_name: time_id for time_id, hall_name in hall_time_map}

        # Insert data into the halls table
        halls_with_ids = []
        for city, *halls_in_city in halls:
            for hall_name in halls_in_city:
                time_id = hall_name_to_time_id.get(hall_name)
                if time_id:
                    halls_with_ids.append((city, hall_name, time_id))

        query_hall = "INSERT INTO halls (city_name, hall_name, time_id) VALUES (%s, %s, %s)"
        cur.executemany(query_hall, halls_with_ids)
        connect.commit()

        # Prepare and insert movie data for each city
        query_movie = """
        INSERT INTO movies_{city} (
            mov_name, mov_images, language, subtitles_language, rating,
            hall1, hall2, hall3, hall4,
            time1_1, time1_2, time1_3, time1_4,
            time2_1, time2_2, time2_3, time2_4,
            time3_1, time3_2, time3_3, time3_4,
            time4_1, time4_2, time4_3, time4_4
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cities = ["kolkata", "delhi", "mumbai", "chennai"]
        halls_dict = {city[0].lower(): city[1:] for city in halls}

        for city in cities:
            movies_data = []
            for movie_name, movie_image, language, subtitles_language, rating in movies:
                hall_names = halls_dict[city]
                selected_halls = random.sample(hall_names, 4)  # Randomly select 4 halls

                hall_times = []
                for hall in selected_halls:
                    cur.execute("SELECT * FROM times WHERE hall_name = %s", (hall ,))
                    hall_time = cur.fetchone()
                    if hall_time:
                        available_times = hall_time[2:]  # Get available times
                        selected_times = random.sample(available_times, 4)  # Randomly select 4 times
                        selected_times.sort()  # Ensure the selected times are in ascending order
                        hall_times.append(convert_to_12_hour_format(selected_times))  # Convert to 12-hour format
                    else:
                        hall_times.append(["N/A"] * 4)  # Placeholder if no times found

                row = (
                    movie_name, movie_image, language, subtitles_language, rating,
                    selected_halls[0], selected_halls[1], selected_halls[2], selected_halls[3],
                    *hall_times[0], *hall_times[1], *hall_times[2], *hall_times[3]
                )
                movies_data.append(row)

            cur.executemany(query_movie.format(city=city), movies_data)
            connect.commit()

        connect.close()
        print("Database setup completed successfully.")

    except:
        pass

    def landing():

        window.protocol('WM_DELETE_WINDOW', lambda : window.destroy())

        landingcanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        landingcanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )

        homemainleftcanvas = CTkCanvas(
            master = landingcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        homemainleftcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        homemainrightcanvas = CTkCanvas(
            master = landingcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 380,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        homemainrightcanvas.place(
            x = 1015, 
            rely = 0.5,
            anchor = "center"
        )

        video1 = cv2.VideoCapture(relative_to_assets("oppenheimer.mp4"))

        titlelabel = Label(
            master = homemainrightcanvas,
            bd = 0
        )
        titlelabel.place(
            relx = 0.5,
            rely = 0.33,
            anchor = "center"
        )

        def video_loop(root, cap, label):
        
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  
                ret, frame = cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=frame)

                label.configure(image=photo)
                label.image = photo  

                root.after(5, lambda: video_loop(root, cap, label))  
        
        video_loop(window , video1 , titlelabel)

        video2 = cv2.VideoCapture(relative_to_assets("monkeyman.mp4"))

        titlelabel2 = Label(
            master = homemainrightcanvas,
            bd = 0
        )
        titlelabel2.place(
            relx = 0.5,
            rely = 0.74,
            anchor = "center"
        )

        def video_loop(root, cap, label):
        
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  
                ret, frame = cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=frame)

                label.configure(image=photo)
                label.image = photo  

                root.after(5, lambda: video_loop(root, cap, label))  
        
        video_loop(window , video2 , titlelabel2)

        permelements(homemainleftcanvas)

        profileframe = CTkFrame(
            master = homemainrightcanvas,
            width = 300,
            height = 72,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        profileframe.place(
            relx = 1,
            y = 36,
            anchor = "e"
        )

        pictureframe = CTkFrame(
            master = profileframe,
            width = 50,
            height = 50,
            corner_radius = 50,
            fg_color = "#373737",
            bg_color = "transparent"
        )
        pictureframe.place(
            relx = 0.11,
            rely = 0.5,
            anchor = "center"
        )
        picturelabel = CTkLabel(
            master = pictureframe,
            width = 0,
            fg_color = "#373737",
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("user.png"),"r"),
                dark_image = Image.open(relative_to_assets("user.png"),"r"),
                size = (35,35)
            )
        )
        picturelabel.place(
            relx = 0.4897,
            rely = 0.5,
            anchor = "center"
        )

        seperation = CTkFrame(
            master = profileframe,
            width = 215,
            height = 3,
            corner_radius = 2,
            fg_color = "#EEEEEE",
            bg_color = "transparent"
        )
        seperation.place(
            relx = 0.585,
            rely = 0.5,
            anchor = "center"
        )
        
        database()
        cur.execute("USE popaction_data")
        cur.execute("SELECT booking_id FROM bookings WHERE log_id = %s" , (logid ,))
        data = cur.fetchall()
        prebookingval = []
        for i in data:
            prebookingval.append(i[0])
            
        def ticket_callback(choice):
            search.destroy()  # This should safely destroy the widget
            video1.release()
            video2.release()
            landingcanvas.place_forget()
            loadingmain(f"{choice}")
                
        
        ticketbox = CTkComboBox(
            master = profileframe,
            dropdown_fg_color = "#242424",
            border_width = 0,
            button_color = "#242424",
            fg_color = "#242424",
            text_color = "#EEEEEE",
            dropdown_text_color = "#EEEEEE",
            dropdown_hover_color = "#373737",
            button_hover_color = "#373737",
            values = prebookingval,
            font = ("GeneralSans-Bold" , 1 * 1),
            dropdown_font= ("GeneralSans-Bold" , 14 * 1),
            command = ticket_callback
        )
        ticketbox.place(
            relx = 0.23,
            rely = 0.27,
            anchor = "w"
        )
        ticketbox.set("Select")

        loglabel = CTkLabel(
            master = profileframe,
            height = 0,
            fg_color = "#242424",
            text_color = "#EEEEEE",
            text = "Hey, " + logname + "!",
            font = ("GeneralSans-Bold" , 16 * 1)
        )
        loglabel.place(
            relx = 0.23,
            rely = 0.3,
            anchor = "w"
        )

        def city_callback(choice):
            global cityname
            cityname = choice

        citybox = CTkComboBox(
            master = profileframe,
            dropdown_fg_color = "#242424",
            border_width = 0,
            button_color = "#242424",
            fg_color = "#242424",
            text_color = "#EEEEEE",
            dropdown_text_color = "#EEEEEE",
            dropdown_hover_color = "#373737",
            button_hover_color = "#373737",
            values = ["Kolkata" , "Delhi" , "Mumbai" , "Chennai"],
            font = ("GeneralSans-Bold" , 17 * 1),
            dropdown_font= ("GeneralSans-Bold" , 14 * 1),
            command = city_callback
        )
        citybox.place(
            relx = 0.207,
            rely = 0.73,
            anchor = "w"
        )
        citybox.set("Select City")

        recotext = CTkLabel(
            master = homemainleftcanvas,
            width = 0,
            text = "Recommended Movies",
            font = ("GeneralSans-Bold" , 36 * 1),
            text_color = "#EEEEEE"
        )
        recotext.place(
            relx = 0.01,
            rely = 0.13,
            anchor = "w"
        )

        newreltext = CTkLabel(
            master = homemainleftcanvas,
            width = 0,
            text = "New Releases",
            font = ("GeneralSans-Bold" , 36 * 1),
            text_color = "#EEEEEE"
        )
        newreltext.place(
            relx = 0.01,
            rely = 0.545,
            anchor = "w"
        )

        feattext = CTkLabel(
            master = homemainrightcanvas,
            width = 0,
            text = "Featured Movies",
            font = ("GeneralSans-Bold" , 24 * 1),
            text_color = "#EEEEEE"
        )
        feattext.place(
            relx = 0.5,
            rely = 0.16,
            anchor = "center"
        )
        
        global movie_update
        def movie_update(name):
            global movie
            movie = name
            if cityname!= str(None):
                search.destroy()  # This should safely destroy the widget
                video1.release()
                video2.release()
                landingcanvas.place_forget()
                loadingmain("detailcanvas")
            else:
                messagebox.showwarning("Warning!","Select a city before proceeding!")
            
            
        backico = Image.open(relative_to_assets("back.png"),"r")
        nextico = Image.open(relative_to_assets("next.png"),"r")
        
        def recframe_1():
            
            butrec1 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("oppenheimer.png"),"r"),
                    dark_image = Image.open(relative_to_assets("oppenheimer.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Oppenheimer") 
            )
            butrec1.place(
                x = 114.25,
                rely = 0.33,
                anchor = "center"
            )

            butrec2 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("godzillaxkong.png"),"r"),
                    dark_image = Image.open(relative_to_assets("godzillaxkong.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Godzilla X Kong:The New Empire")
            )
            butrec2.place(
                x = 299.25,
                rely = 0.33,
                anchor = "center"
            )

            butrec3 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("dune2.png"),"r"),
                    dark_image = Image.open(relative_to_assets("dune2.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Dune:Part Two")
            )
            butrec3.place(
                x = 484.25,
                rely = 0.33,
                anchor = "center"
            )

            butrec4 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("if.png"),"r"),
                    dark_image = Image.open(relative_to_assets("if.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("IF")
            )
            butrec4.place(
                x = 669.25,
                rely = 0.33,
                anchor = "center"
            )

        def recframe_2():
            
            butrec5 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("evildoesnotexist.png"),"r"),
                    dark_image = Image.open(relative_to_assets("evildoesnotexist.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Evil Does Not Exist")
            )
            butrec5.place(
                x = 114.25,
                rely = 0.33,
                anchor = "center"
            )

            butrec6 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("kungfupanda4.png"),"r"),
                    dark_image = Image.open(relative_to_assets("kungfupanda4.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Kung Fu Panda 4")
            )
            butrec6.place(
                x = 299.25,
                rely = 0.33,
                anchor = "center"
            )
            
            butrec7 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("fallguy.png"),"r"),
                    dark_image = Image.open(relative_to_assets("fallguy.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Fall Guy")
            )
            butrec7.place(
                x = 484.25,
                rely = 0.33,
                anchor = "center"
            )

            butrec8 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("monster.png"),"r"),
                    dark_image = Image.open(relative_to_assets("monster.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Monster")
            )
            butrec8.place(
                x = 669.25,
                rely = 0.33,
                anchor = "center"
            )

        def check_rec(count):
            if count == 1:
                recframe_1()
            else:
                recframe_2()

        def back_f1(count):
            if count == 1:
                count = 1
                back_rec.place_forget()
                next_rec.place(
                    relx = 0.973,
                    rely = 0.33,
                    anchor = "center",
                )
            else:
                count -= 1
            check_rec(count)


        def next_f1(count):
            if count == 2:
                count = 2
            else:
                count += 1
                next_rec.place_forget()
                back_rec.place(
                    relx = 0.011,
                    rely = 0.33,
                    anchor = "center",
                )
            check_rec(count)
            

        count_f1 = 1

        back_rec = CTkButton(
            master = homemainleftcanvas,
            width = 0,
            height = 0,
            text = "",
            fg_color = "#111111",
            hover_color = "#111111",
            image = CTkImage(
                light_image = backico,
                dark_image = backico,
                size = (25,25)
            ),
            command = lambda : back_f1(count_f1)
        )
        
        next_rec = CTkButton(
            master = homemainleftcanvas,
            width = 0,
            height = 0,
            text = "",
            fg_color = "#111111",
            hover_color = "#111111",
            image = CTkImage(
                light_image = nextico,
                dark_image = nextico,
                size = (25,25)
            ),
            command = lambda : next_f1(count_f1)
        )
        next_rec.place(
            relx = 0.973,
            rely = 0.33,
            anchor = "center"
        )
        
        check_rec(count_f1)
        
        def newframe_1():
            
            newrec1 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("monkeyman.png"),"r"),
                    dark_image = Image.open(relative_to_assets("monkeyman.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Monkey Man") 
            )
            newrec1.place(
                x = 114.25,
                rely = 0.74,
                anchor = "center"
            )

            newrec2 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("tarot.png"),"r"),
                    dark_image = Image.open(relative_to_assets("tarot.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Tarot")
            )
            newrec2.place(
                x = 299.25,
                rely = 0.74,
                anchor = "center"
            )

            newrec3 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("thecrow.png"),"r"),
                    dark_image = Image.open(relative_to_assets("thecrow.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("The Crow")
            )
            newrec3.place(
                x = 484.25,
                rely = 0.74,
                anchor = "center"
            )

            newrec4 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("thefirstomen.png"),"r"),
                    dark_image = Image.open(relative_to_assets("thefirstomen.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("The First Omen")
            )
            newrec4.place(
                x = 669.25,
                rely = 0.74,
                anchor = "center"
            )

        def newframe_2():
            
            newrec5 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("strangers.png"),"r"),
                    dark_image = Image.open(relative_to_assets("strangers.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("The Strangers:Chapter 1")
            )
            newrec5.place(
                x = 114.25,
                rely = 0.74,
                anchor = "center"
            )

            newrec6 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("theboyandtheheron.png"),"r"),
                    dark_image = Image.open(relative_to_assets("theboyandtheheron.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("The Boy and The Heron")
            )
            newrec6.place(
                x = 299.25,
                rely = 0.74,
                anchor = "center"
            )
            
            newrec7 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("kingdomofapes.png"),"r"),
                    dark_image = Image.open(relative_to_assets("kingdomofapes.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Kingdom of the Planet of the Apes")
            )
            newrec7.place(
                x = 484.25,
                rely = 0.74,
                anchor = "center"
            )

            newrec8 = CTkButton(
                master = homemainleftcanvas,
                width = 175,
                height = 232,
                image = CTkImage(
                    light_image = Image.open(relative_to_assets("srikanth.png"),"r"),
                    dark_image = Image.open(relative_to_assets("srikanth.png"),"r"),
                    size = (175,232)
                ),
                bg_color = "transparent",
                text = "",
                border_width = 0,
                border_spacing = 0,
                fg_color = "#111111",
                hover_color = "#111111",
                command = lambda : movie_update("Srikanth")
            )
            newrec8.place(
                x = 669.25,
                rely = 0.74,
                anchor = "center"
            )
            
        def check_new(count):
            if count == 1:
                newframe_1()
            else:
                newframe_2()

        def back_f2(count):
            if count == 1:
                count = 1
                back_new.place_forget()
                next_new.place(
                    relx = 0.973,
                    rely = 0.74,
                    anchor = "center",
                )
            else:
                count -= 1
            check_new(count)


        def next_f2(count):
            if count == 2:
                count = 2
            else:
                count += 1
                next_new.place_forget()
                back_new.place(
                    relx = 0.011,
                    rely = 0.74,
                    anchor = "center",
                )
            check_new(count)
            

        count_f2 = 1

        back_new = CTkButton(
            master = homemainleftcanvas,
            width = 0,
            height = 0,
            text = "",
            fg_color = "#111111",
            hover_color = "#111111",
            image = CTkImage(
                light_image = backico,
                dark_image = backico,
                size = (25,25)
            ),
            command = lambda : back_f2(count_f2)
        )
        
        next_new = CTkButton(
            master = homemainleftcanvas,
            width = 0,
            height = 0,
            text = "",
            fg_color = "#111111",
            hover_color = "#111111",
            image = CTkImage(
                light_image = nextico,
                dark_image = nextico,
                size = (25,25)
            ),
            command = lambda : next_f2(count_f2)
        )
        next_new.place(
            relx = 0.973,
            rely = 0.74,
            anchor = "center"
        )
        
        check_new(count_f2)

        searchframe = CTkFrame(
            master = landingcanvas,
            width = 500,
            height = 40,
            fg_color = "#242424"
        )
        searchframe.place(
            relx = 0.335,
            rely = 0.047,
            anchor = "center"
        )

        suggestions = ["Oppenheimer" , "Godzilla X Kong:The New Empire" , "Dune:Part Two" , "Fall Guy" , "Evil Does Not Exist" , "Kingdom of the Planet of the Apes" , "The Boy and The Heron" , "The First Omen" , "The Crow" , "Monkey Man" , "Monster" , "IF" , "The Strangers:Chapter 1" , "Atlas" , "Furiosa:A Mad Max Saga" , "Kung Fu Panda 4" , "Tarot" , "Savi" , "The Garfield Movie" , "Srikanth"]
        placeholder_text = "Search..."
        search = AutoCompleteEntry(landingcanvas , suggestions , placeholder=placeholder_text)
        search.configure(border_width = 0,
                         fg_color = "#242424",
                         bg_color = "#242424", 
                         height = 40,
                         width = 460,
                         font = ("Satoshi-Regular" , 20 * 1),
                         text_color = "#EEEEEE",
                        )
        search.place(
            relx = 0.348,
            rely = 0.048,
            anchor = "center"
        )
        searchlabel = CTkLabel(
            master = searchframe,
            width = 0,
            fg_color = "#242424",
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("search.png"),"r"),
                dark_image = Image.open(relative_to_assets("search.png"),"r"),
                size = (35,35)
            ),
            bg_color = "transparent",
        )
        searchlabel.place(
            relx = 0.04,
            rely = 0.5,
            anchor = "center"
        )
    
    global detailselect
    def detailselect():

        detailcanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        detailcanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )

        detailleftcanvas = CTkCanvas(
            master = detailcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        detailleftcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        detailrightcanvas = CTkCanvas(
            master = detailcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 380,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        detailrightcanvas.place(
            x = 1015, 
            rely = 0.5,
            anchor = "center"
        )

        permelements(detailleftcanvas)

        database()
        cur.execute("USE popaction_data")
        cur.execute("SELECT * FROM movies_" + cityname.lower() + " WHERE mov_name = %s" , (movie, ))
        row = cur.fetchone()
        global rating
        rating = row[3:6]
        print(rating[0])
        movieselected = row[1]
        global poster
        poster = row[2]
        connect.close()
        
        
        posterlabel = CTkLabel(
            master = detailrightcanvas,
            height = 266,
            width = 200,
            fg_color = "#111111",
            image = CTkImage(
                light_image = Image.open(relative_to_assets(poster + ".png"),"r"),
                dark_image = Image.open(relative_to_assets(poster + ".png"),"r"),
                size = (200 , 266)
            ),
            text = "",
            bg_color = "transparent"
        )
        posterlabel.place(
            relx = 0.5,
            rely = 0.45,
            anchor = "center"
        )
        namelabel = CTkLabel(
            master = detailrightcanvas,
            fg_color = "#111111",
            text = movieselected,
            bg_color = "transparent",
            font = ("Satoshi-Medium" , 24 * 1),
            text_color = "#EEEEEE"
        )
        namelabel.place(
            relx = 0.5,
            rely = 0.67,
            anchor = "center"
        )

        profileframe = CTkFrame(
            master = detailrightcanvas,
            width = 300,
            height = 72,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        profileframe.place(
            relx = 1,
            y = 36,
            anchor = "e"
        )

        pictureframe = CTkFrame(
            master = profileframe,
            width = 50,
            height = 50,
            corner_radius = 50,
            fg_color = "#373737",
            bg_color = "transparent"
        )
        pictureframe.place(
            relx = 0.11,
            rely = 0.5,
            anchor = "center"
        )
        picturelabel = CTkLabel(
            master = pictureframe,
            width = 0,
            fg_color = "#373737",
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("user.png"),"r"),
                dark_image = Image.open(relative_to_assets("user.png"),"r"),
                size = (35,35)
            )
        )
        picturelabel.place(
            relx = 0.4897,
            rely = 0.5,
            anchor = "center"
        )

        seperation = CTkFrame(
            master = profileframe,
            width = 215,
            height = 3,
            corner_radius = 2,
            fg_color = "#EEEEEE",
            bg_color = "transparent"
        )
        seperation.place(
            relx = 0.585,
            rely = 0.5,
            anchor = "center"
        )

        loglabel = CTkLabel(
            master = profileframe,
            height = 0,
            fg_color = "#242424",
            text_color = "#EEEEEE",
            text = "Hey, " + logname + "!",
            font = ("GeneralSans-Bold" , 16 * 1)
        )
        loglabel.place(
            relx = 0.23,
            rely = 0.3,
            anchor = "w"
        )
        citylabel = CTkLabel(
            master = profileframe,
            height = 0,
            fg_color = "#242424",
            text_color = "#EEEEEE",
            text = cityname,
            font = ("GeneralSans-Bold" , 17 * 1)
        )
        citylabel.place(
            relx = 0.23,
            rely = 0.73,
            anchor = "w"
        )

        sloganlabel = CTkLabel(
            master = detailleftcanvas,
            text = "Almost there!",
            font = ("GeneralSans-Bold" , (20 * 1)),
            text_color = "#E0E0E0"
        )
        sloganlabel.place(
            relx = 0.5,
            y = 10,
            anchor = "center"
        )

        back_button = CTkButton(
            master = detailleftcanvas,
            width = 86.0,
            height = 40.0,
            text = "Back",
            text_color = "#EEEEEE",
            font = ("GeneralSans-Medium" , 20* -1),
            border_width = 0,
            corner_radius = 10,
            fg_color = "#414141",
            hover_color = "#242424",
            image = CTkImage(
                dark_image = Image.open(relative_to_assets("previous.png"),"r"),
                light_image = Image.open(relative_to_assets("previous.png"),"r"),
                size = (30,30)
                ),
            command = lambda : loadingmain("landingcanvas")
        )
        back_button.place(
            x = 70.0,
            y = 60.0,
            anchor = "center"
        )
        
        global adv_detail
        global count 
        count = 0
        
        seatavail = []
        alpha = 65
        for i in range(0,10):
            ch_alpha = chr(alpha)
            num = 1
            for j in range(0,21):
                seats_av = ((ch_alpha+str(num)) , )
                seatavail.append(seats_av)
                num += 1
            alpha += 1

        today = datetime.date.today()

        def date_callback(choice):

            global date
            global ticketdate
            ticketdate = str(choice)
            date = str(choice).replace(",","")
            date = date.replace(" ","")
            print(date)

            if date != None:
                
                try:
                    
                    def select_time(id , time , button):
                        
                        global adv_detail
                        global tickettime
                        tickettime = time_data[id]
                        adieu = movie.lower()
                        adieu = adieu.replace(" " , "")
                        adieu = adieu.replace(":" , "")
                        adv_detail = date + adieu + adv_detail + time
                        adv_detail = adv_detail.replace(":","")
                        adv_detail = adv_detail.replace(" ","")
                        if len(adv_detail) > 64:
                            x = adv_detail.find("y")
                            adv_detail = adv_detail[x + 1:]
                            if "theplanetofthe" in adv_detail:
                                adv_detail = adv_detail.replace("planetofthe" , "")
                            if "godzillaxkong" in adv_detail:
                                adv_detail = adv_detail.replace("godzillaxkong" , "gxk")
                        button.configure(
                            text_color = "#C0C0C0",
                            border_color = "#C0C0C0"
                        )
                        print(adv_detail)
                        
                        for j in range(0,4):
                            time_button[time_data[j]].configure(
                                state = "disabled"
                            )
                            
                        screenlabel = CTkLabel(
                            master = detailleftcanvas,
                            fg_color = "#111111",
                            image = CTkImage(
                                light_image = Image.open(relative_to_assets("screen.png"),"r"),
                                dark_image = Image.open(relative_to_assets("screen.png"),"r"),
                                size = (580 , 20)
                            ),
                            text = "",
                            bg_color = "transparent"
                        )
                        screenlabel.place(
                            relx = 0.5,
                            rely = 0.88,
                            anchor = "center"
                        )
                        screentextlabel = CTkLabel(
                            master = detailleftcanvas,
                            height = 0,
                            fg_color = "#242424",
                            text_color = "#EEEEEE",
                            text = "Eyes this way please!",
                            font = ("GeneralSans-Bold" , 16 * 1)
                        )
                        screentextlabel.place(
                            relx = 0.5,
                            rely = 0.92,
                            anchor = "center"
                        )
                        
                        seatframe = CTkFrame(
                            master = detailleftcanvas,
                            width = 700,
                            height = 400,
                            fg_color = "#111111",
                            bg_color = "transparent"
                        )
                        seatframe.place(
                            relx = 0.5,
                            rely = 0.3,
                            anchor = "n"
                        )

                        global topprice
                        global midprice
                        global lowprice
                        if "pvr" in adv_detail or "inox" in adv_detail or "imax" in adv_detail or "screenx" in adv_detail:
                            top = "Recliner : Rs.560"
                            mid = "Exclusive : Rs.350"
                            low = "Classic : Rs.270"
                            topprice = 560
                            midprice = 350
                            lowprice = 270
                        else:
                            top = "Recliner : Rs.370"
                            mid = "Exclusive : Rs.260"
                            low = "Classic : Rs.180"
                            topprice = 370
                            midprice = 260
                            lowprice = 180

                        toptext = CTkLabel(
                            master = seatframe,
                            text = top,
                            font = ("Satoshi-Bold" , 15 * -1),
                            text_color = "#EEEEEE"
                        )
                        toptext.place(
                            x = 5.0,
                            y = 15.0,
                            anchor = "w"
                        )

                        midtext = CTkLabel(
                            master = seatframe,
                            text = mid,
                            font = ("Satoshi-Bold" , 15 * -1),
                            text_color = "#EEEEEE"
                        )
                        midtext.place(
                            x = 5.0,
                            y = 77.0,
                            anchor = "w"
                        )

                        lowtext = CTkLabel(
                            master = seatframe,
                            text = low,
                            font = ("Satoshi-Bold" , 15 * -1),
                            text_color = "#EEEEEE"
                        )
                        lowtext.place(
                            x = 5.0,
                            y = 287.0,
                            anchor = "w"
                        )

                        stairs = []
                        if "inox" in adv_detail or "pvr" in adv_detail:
                            stairs = [17 , 18 , 19 , 20]
                        elif "imax" in adv_detail or "screenx" in adv_detail:
                            stairs = [11 , 12 , 13 , 14]
                        else:
                            stairs = [7 , 8 , 9 , 10]

                        global selected_seat
                        selected_seat = []

                        def select_seat(seat_id , button):
                            print(seat_id)
                            button.configure(
                                text_color = "#C0C0C0",
                                border_color = "#C0C0C0",
                                command = print("selected")
                            )
                            selected_seat.append(seat_id)
                            continuebutton.configure(
                                fg_color = "#DF1827",
                                state = "active"
                            )
                            continuebutton.bind("<Enter>", lambda event : continuebutton.configure(
                                text_color="#CCCCCC",
                                fg_color = "#7B0D15"
                                )
                            ) 
                            continuebutton.bind("<Leave>", lambda event : continuebutton.configure(
                                text_color="#EEEEEE",
                                fg_color = "#DF1827"
                                )
                            )  

                        database()
                        cur.execute("USE popaction_data")
                        try:
                            cur.execute("CREATE TABLE " + adv_detail + "(id INT AUTO_INCREMENT PRIMARY KEY NOT NULL , movie_seat VARCHAR(15))")
                            query_seat = "INSERT INTO " + adv_detail + "(movie_seat) values (%s)"
                            cur.executemany(query_seat , seatavail)
                            connect.commit()
                        except:
                            pass

                        alpha = 65
                        y_cord = 41.0
                        numb_button = {}
                        for i in range (1,13):
                            numb = 1
                            x_cord = 39.0
                            if i == 2 or i == 9:
                                y_cord += 30.0
                            else:
                                alpha_button = CTkButton(
                                    master = seatframe,
                                    width = 25.0,
                                    height = 25.0,
                                    text = chr(alpha),
                                    text_color = "#DF1827",
                                    font = ("Satoshi-Bold" , 15 * -1),
                                    corner_radius = 5,
                                    fg_color = "#111111",
                                    hover_color= "#111111",
                                    border_color = "#DF1827",
                                    border_width = 1
                                )
                                alpha_button.place(
                                    x = 5.0,
                                    y = y_cord,
                                    anchor = "w"
                                )
                                for j in range(1,23):
                                    if j in stairs:
                                        x_cord += 30.0
                                    else:
                                        numb_button[(i,j)] = CTkButton(
                                            master = seatframe,
                                            width = 25.0,
                                            height = 25.0,
                                            text = str(numb),
                                            text_color = "#79B791",
                                            font = ("Satoshi-Bold" , 15 * -1),
                                            corner_radius = 5,
                                            fg_color = "#111111",
                                            hover_color= "#111111",
                                            border_color = "#79B791",
                                            border_width = 1,
                                            command = lambda selected_seat = chr(alpha) + str(numb) , i = i, j = j : select_seat(selected_seat , numb_button[(i,j)])
                                        )
                                        cur.execute("SELECT id FROM " + adv_detail + " WHERE movie_seat = %s" , ((chr(alpha) + str(numb)) , ))
                                        data = cur.fetchone()
                                        if data == None:
                                            numb_button[(i,j)].configure(
                                                border_color = "#C0C0C0",
                                                state = "disabled"
                                            )
                                        numb_button[(i,j)].place(
                                            x = x_cord,
                                            y = y_cord,
                                            anchor = "w"
                                        )
                                        numb += 1
                                        x_cord += 30.0    
                                alpha += 1
                                y_cord += 30.0
                        
                            

                    resetbutton = CTkButton(
                        master = detailrightcanvas,
                        height = 40,
                        width = 140,
                        text = "Reset",
                        text_color = "#EEEEEE",
                        font = ("Satoshi-Medium" , 20 * 1),
                        corner_radius = 10,
                        bg_color = "transparent",
                        fg_color = "#414141",
                        hover_color = "#242424",
                        command = lambda : (detailcanvas.destroy() , loadingmain("detailcanvas"))
                    )
                    resetbutton.bind("<Enter>", lambda event : resetbutton.configure(
                        text_color="#CCCCCC",
                        fg_color = "#242424"
                        )
                    ) 
                    resetbutton.bind("<Leave>", lambda event : resetbutton.configure(
                        text_color="#EEEEEE",
                        fg_color = "#414141"
                        )
                    ) 
                    resetbutton.place(
                        relx = 0.1,
                        rely = 0.75,
                        anchor = "w"
                    )    

                    continuebutton = CTkButton(
                        master = detailrightcanvas,
                        height = 40,
                        width = 140,
                        text = "Continue",
                        text_color = "#EEEEEE",
                        font = ("Satoshi-Medium" , 20 * 1),
                        corner_radius = 10,
                        bg_color = "transparent",
                        fg_color = "#7B0D15",
                        hover_color = "#7B0D15",
                        command = lambda : (detailcanvas.destroy() , loadingmain("bookingcanvas")),
                        state = "disabled"
                    )
                    continuebutton.place(
                        relx = 0.9,
                        rely = 0.75,
                        anchor = "e"
                    )
                             
                    def select_hall(id , hall , button):

                        global adv_detail
                        global tickethall
                        tickethall = hall_data[id-1]
                        adv_detail = hall
                        button.configure(
                            text_color = "#C0C0C0",
                            border_color = "#C0C0C0"
                        )

                        for j in range(0,4):
                            hall_button[hall_data[j]].configure(
                                state = "disabled"
                            )
                        
                        global time_data
                        if id == 1:
                            time_data = row[10:14]
                        if id == 2:
                            time_data = row[14:18]
                        if id == 3:
                            time_data = row[18:22]
                        if id == 4:
                            time_data = row[22:26]
                            
                        global time_button
                        time_button = {}
                        x_cd = 43.0
                        for i in range(0,4):
                            time_button[time_data[i]] = CTkButton(
                                master = detailleftcanvas,
                                height = 40.0,
                                width = 170.0,
                                text = time_data[i],
                                text_color = "#EEEEEE",
                                font = ("GeneralSans-Semibold" , 16 * -1),
                                corner_radius = 10,
                                fg_color = "#242424" ,
                                hover_color = "#414141",
                                border_color = "#111111",
                                border_width = 1,
                                command = lambda i = i: select_time(i , time_data[i].lower() , time_button[time_data[i]])
                            )
                            time_button[time_data[i]].place(
                                x = x_cd,
                                y =  175.0,
                                anchor = "w"
                            )
                            x_cd += 180.0
                    
                    hall_button = {}
                    x_cd = 43.0
                    for i in range(0,4):
                        hall_button[hall_data[i]] = CTkButton(
                            master = detailleftcanvas,
                            height = 40.0,
                            width = 170.0,
                            text = hall_data[i].replace("_" , " "),
                            text_color = "#EEEEEE",
                            font = ("GeneralSans-Semibold" , 16 * -1),
                            corner_radius = 10,
                            fg_color = "#242424" ,
                            hover_color = "#414141",
                            border_color = "#111111",
                            border_width = 1,
                            command = lambda i = i : select_hall(i+1 , cityname.lower() + hall_data[i].lower() , hall_button[hall_data[i]])
                        )
                        hall_button[hall_data[i]].place(
                            x = x_cd,
                            y =  125.0,
                            anchor = "w"
                        )
                        x_cd += 180.0
                
                except:
                    messagebox.showerror("Error" , "No Date Selected!")
            else:
                pass

        # Calculate future dates
        tomorrow = today + datetime.timedelta(days=1)
        twotomorrow = today + datetime.timedelta(days=2)
        threetomorrow = today + datetime.timedelta(days=3)

        # Format dates to a more readable format
        date_format = "%A, %B %d, %Y"  # Example format: "Monday, July 17, 2023"
        formatted_tomorrow = tomorrow.strftime(date_format)
        formatted_twotomorrow = twotomorrow.strftime(date_format)
        formatted_threetomorrow = threetomorrow.strftime(date_format)

        # Create the combo box with formatted dates
        date_box = CTkComboBox(
            master=detailleftcanvas,
            width=400,
            height=40,
            values=[formatted_tomorrow, formatted_twotomorrow, formatted_threetomorrow],
            corner_radius=10,
            border_color = "#242424",
            border_width =2,
            bg_color = "transparent",
            fg_color = "#242424",
            dropdown_fg_color = "#242424",
            font = ("GeneralSans-Medium", 20 * -1),
            dropdown_font =( "GeneralSans-Medium", 18 * -1),
            button_color = "#242424",
            button_hover_color = "#282828",
            command = date_callback,
            text_color = "#EEEEEE",
            dropdown_text_color = "#EEEEEE"
        )

        # Set the default value for the combo box
        date_box.set("Select Date")

        # Place the combo box on the canvas
        date_box.place(
            x = 200.0,
            y = 60.0,
            anchor="w"
        )

        hall_data = row[6:10]
        print(hall_data)
        

    global booking
    def booking():

        bookingcanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        bookingcanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )

        bookingleftcanvas = CTkCanvas(
            master = bookingcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        bookingleftcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        bookingrightcanvas = CTkCanvas(
            master = bookingcanvas,
            bd = 0,
            bg = "#111111",
            width = 494,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        bookingrightcanvas.place(
            x = 898, 
            rely = 0.5,
            anchor = "center"
        )
        
        permelements(bookingleftcanvas)

        infocanvas = CTkFrame(
            master = bookingleftcanvas,
            height = 700,
            width = 490,
            corner_radius = 10,
            fg_color = "#111111",
            bg_color = "transparent"
        )
        infocanvas.place(
            relx = 0.4,
            rely = 0.47,
            anchor = "center"
        )
        
        ticketbackinfo = CTkFrame(
            master = infocanvas,
            height = 90,
            width = 490,
            corner_radius = 10,
            fg_color = "#414141",
            bg_color = "transparent"
        )
        ticketbackinfo.place(
            relx = 0.5,
            rely = 0.06,
            anchor = "n"
        )
        ticketinfo = CTkFrame(
            master = infocanvas,
            height = 90,
            width = 490,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        ticketinfo.place(
            relx = 0.5,
            rely = 0.01,
            anchor = "n"
        )
        ticketinfofix1 = CTkFrame(
            master = ticketinfo,
            height = 10,
            width = 10,
            fg_color = "#242424",
            corner_radius = 0
        )
        ticketinfofix1.place(
            relx = 0,
            rely = 1,
            anchor = "sw"
        )
        ticketinfofix2 = CTkFrame(
            master = ticketinfo,
            height = 10,
            width = 10,
            fg_color = "#242424",
            corner_radius = 0
        )
        ticketinfofix2.place(
            relx = 1,
            rely = 1,
            anchor = "se"
        )

        ticketmovie = CTkLabel(
            master = ticketinfo,
            text = movie,
            font = ("Satoshi-Bold" , 22 * 1),
            text_color = "#EEEEEE"
        )
        ticketmovie.place(
            relx = 0.03,
            rely = 0.2,
            anchor = "w"
        )
        ticketmoviedate = CTkLabel(
            master = ticketinfo,
            height = 0,
            text = ticketdate + " | "  + tickettime,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        ticketmoviedate.place(
            relx = 0.034,
            rely = 0.53,
            anchor = "w"
        )
        tickethallcity = CTkLabel(
            master = ticketinfo,
            height = 0,
            text = tickethall.replace("_" , " ") + ", " + cityname,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        tickethallcity.place(
            relx = 0.032,
            rely = 0.79,
            anchor = "w"
        )
        notickets = CTkLabel(
            master = ticketinfo,
            height = 0,
            text = str(len(selected_seat)),
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        notickets.place(
            relx = 0.945,
            rely = 0.23,
            anchor = "w"
        )
        tickettext = CTkLabel(
            master = ticketinfo,
            height = 0,
            text = "M-Ticket",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#C0C0C0"
        )
        tickettext.place(
            relx = 0.83,
            rely = 0.53,
            anchor = "w"
        )
        canceltext = CTkLabel(
            master = ticketbackinfo,
            height = 0,
            text = "Cancelation Available",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        canceltext.place(
            relx = 0.032,
            rely = 0.8,
            anchor = "w"
        )
        infocancelbutton = CTkButton(
            master = ticketbackinfo,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("info.png") , "r"),
                dark_image = Image.open(relative_to_assets("info.png") , "r"),
                size = (20,20)
            ),
            text = "",
            fg_color = "#414141",
            hover_color = "#414141",
            command = lambda : messagebox.showinfo("Cancelation Policy" , "Cancelation is dependent upon each theatre's own policy. For more info search their own websites.")
        )
        infocancelbutton.place(
            relx = 0.925,
            rely = 0.8,
            anchor = "w"
        )

        pricebackinfo = CTkFrame(
            master = infocanvas,
            height = 90,
            width = 490,
            corner_radius = 10,
            fg_color = "#414141",
            bg_color = "transparent"
        )
        pricebackinfo.place(
            relx = 0.5,
            rely = 0.26,
            anchor = "n"
        )
        priceinfo = CTkFrame(
            master = infocanvas,
            height = 90,
            width = 490,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        priceinfo.place(
            relx = 0.5,
            rely = 0.21,
            anchor = "n"
        )
        priceinfofix1 = CTkFrame(
            master = priceinfo,
            height = 10,
            width = 10,
            fg_color = "#242424",
            corner_radius = 0
        )
        priceinfofix1.place(
            relx = 0,
            rely = 1,
            anchor = "sw"
        )
        priceinfofix2 = CTkFrame(
            master = priceinfo,
            height = 10,
            width = 10,
            fg_color = "#242424",
            corner_radius = 0
        )
        priceinfofix2.place(
            relx = 1,
            rely = 1,
            anchor = "se"
        )
        
        tickfee = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Ticket(s) Prices",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        tickfee.place(
            relx = 0.032,
            rely = 0.25,
            anchor = "w"
        )
        convenience = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Convenience Fees",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        convenience.place(
            relx = 0.032,
            rely = 0.5,
            anchor = "w"
        )
        igst = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Intergrated GST(IGST) @ 18%",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        igst.place(
            relx = 0.032,
            rely = 0.75,
            anchor = "w"
        )
        amounttext = CTkLabel(
            master = pricebackinfo,
            height = 0,
            text = "Amount Payable",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        amounttext.place(
            relx = 0.032,
            rely = 0.8,
            anchor = "w"
        )
        
        ticketprice = 0
        for i in selected_seat:
            if "A" in i:
                ticketprice += topprice
            elif "H" in i or "I" in i or "J" in i:
                ticketprice += lowprice
            else:
                ticketprice += midprice

        conveniencefee = 40 * len(selected_seat)

        igstfee = round((18/100) * conveniencefee , 2)
        igstfeetext = str(igstfee)
        x = igstfeetext.find(".") + 1
        imisc = igstfeetext[x : ]
        if len(imisc) == 1:
            igstfeetext += "0"

        payable = ticketprice + conveniencefee + igstfee
        global payabletext
        payabletext = str(payable)
        if len(imisc) == 1:
            payabletext += "0"

        ticketpricetext = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Rs. " + str(ticketprice) + ".00",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        ticketpricetext.place(
            relx = 0.965,
            rely = 0.25,
            anchor = "e"
        )
        conveniencepricetext = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Rs. " + str(conveniencefee) + ".00",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        conveniencepricetext.place(
            relx = 0.965,
            rely = 0.5,
            anchor = "e"
        )
        igstpricetext = CTkLabel(
            master = priceinfo,
            height = 0,
            text = "Rs. " + igstfeetext,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        igstpricetext.place(
            relx = 0.965,
            rely = 0.75,
            anchor = "e"
        )
        amountpricetext = CTkLabel(
            master = pricebackinfo,
            height = 0,
            text = "Rs. " + payabletext,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        amountpricetext.place(
            relx = 0.965,
            rely = 0.8,
            anchor = "e"
        )

        offerframe = CTkFrame(
            master = infocanvas,
            height = 40,
            width = 490,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        offerframe.place(
            relx = 0.5,
            rely = 0.41,
            anchor = "n"
        )

        disclabel = CTkLabel(
            master = offerframe,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("discount.png") , "r"),
                dark_image = Image.open(relative_to_assets("discount.png") , "r"),
                size = (25, 25)
            ),
            text = "",
            fg_color = "#242424",
            bg_color = "transparent"
        )
        disclabel.place(
            relx = 0.026,
            rely = 0.5,
            anchor = "w"
        )
        disctext = CTkLabel(
            master = offerframe,
            height = 0,
            width = 0,
            text = "Apply Offers",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "transparent"
        )
        disctext.place(
            relx = 0.085,
            rely = 0.5,
            anchor = "w"
        )
        discbutton = CTkButton(
            master = offerframe,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("next.png") , "r"),
                dark_image = Image.open(relative_to_assets("next.png") , "r"),
                size = (17,17)
            ),
            text = "",
            fg_color = "#242424",
            hover_color = "#242424",
            command = lambda : messagebox.showinfo("Discount Availability" , "No current active coupons!")
        )
        discbutton.place(
            relx = 0.925,
            rely = 0.5,
            anchor = "w"
        )

        database()
        cur.execute("USE popaction_data")
        cur.execute("SELECT email FROM credentials WHERE id = %s" , (logid , ))
        email = cur.fetchone()
    
        if cityname == "Kolkata":
            statename = "West Bengal"
        elif cityname == "Delhi":
            statename = "Delhi"
        elif cityname == "Mumbai":
            statename = "Maharashtra"
        else:
            statename = "Tamil Nadu"

        infoframe = CTkFrame(
            master = infocanvas,
            height = 90,
            width = 490,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent"
        )
        infoframe.place(
            relx = 0.5,
            rely = 0.49,
            anchor = "n"
        )
        confirmation = CTkLabel(
            master = infoframe,
            text = "Your Details(For Confirmation)",
            font = ("Satoshi-Bold" , 20 * 1),
            text_color = "#EEEEEE"
        )
        confirmation.place(
            relx = 0.031,
            rely = 0.24,
            anchor = "w"
        )
        emaillock = CTkLabel(
            master = infoframe,
            height = 0,
            text = email,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        emaillock.place(
            relx = 0.032,
            rely = 0.51,
            anchor = "w"
        )
        locationlock = CTkLabel(
            master = infoframe,
            height = 0,
            text = cityname + " | " + statename,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        locationlock.place(
            relx = 0.032,
            rely = 0.77,
            anchor = "w"
        )
        
        tempticket = CTkFrame(
            master = infocanvas,
            width = 490,
            height = 242,
            corner_radius = 10,
            fg_color = "#242424",
            bg_color = "transparent",
        )
        tempticket.place(
            relx = 0.5,
            rely = 0.645,
            anchor = "n"
        )

        posterlabel = CTkLabel(
            master = tempticket,
            height = 228,
            width = 172,
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                dark_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                size = (172 , 228)
            )
        )
        posterlabel.place(
            relx = 0.015,
            y = 121,
            anchor = "w"
        )

        ticketicon = CTkLabel(
            master = tempticket,
            height = 0,
            width = 0,
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("ticketicon.png") , "r"),
                dark_image = Image.open(relative_to_assets("ticketicon.png") , "r"),
                size = (57 , 57)
            )
        )
        ticketicon.place(
            x = 336,
            rely = 0.82,
            anchor = "center"
        )

        tickettexticon = CTkLabel(
            master = tempticket,
            height = 0,
            width = 0,
            text = "M-Ticket",
            font = ("Satoshi-Bold" , 20 * 1),
            text_color = "#EEEEEE"
        )
        tickettexticon.place(
            x = 336,
            rely = 0.62,
            anchor = "center"
        )

        seattext = CTkLabel(
            master = tempticket,
            height = 0,
            width = 0,
            text = str(selected_seat).replace("'" , "").replace("," , " ,"),
            font = ("Satoshi-Bold" , 20 * 1),
            text_color = "#EEEEEE"
        )
        seattext.place(
            x = 336,
            rely = 0.5,
            anchor = "center"
        )

        movietext = CTkLabel(
            master = tempticket,
            text = movie,
            font = ("Satoshi-Bold" , 19 * 1),
            text_color = "#EEEEEE"
        )
        movietext.place(
            x = 336,
            rely = 0.09,
            anchor = "center"
        )
        movietext = CTkLabel(
            master = tempticket,
            text = ticketdate + " | "  + tickettime,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        movietext.place(
            x = 336,
            rely = 0.21,
            anchor = "center"
        )
        halltext = CTkLabel(
            master = tempticket,
            text = tickethall.replace("_" , " ") + ", " + cityname,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        halltext.place(
            x = 336,
            rely = 0.3,
            anchor = "center"
        )
        
        paymentframe = CTkFrame(
            master = bookingrightcanvas,
            height = 176,
            width = 490,
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#242424"
        )
        paymentframe.place(
            relx = 0.5,
            rely = 0.39,
            anchor = "center"
        )

        confirmpaymenttext = CTkLabel(
            master = paymentframe,
            height = 0,
            width = 0,
            text = "Choose Payment Method",
            font = ("Satoshi-Bold" , 22 * 1),
            text_color = "#EEEEEE"
        )
        confirmpaymenttext.place(
            relx = 0.03,
            rely = 0.13,
            anchor = "w"
        )
        seperation1 = CTkFrame(
            master = paymentframe,
            width = 476,
            height = 3,
            corner_radius = 2,
            fg_color = "#C0C0C0",
            bg_color = "transparent"
        )
        seperation1.place(
            relx = 0.5,
            rely = 0.29,
            anchor = "center"
        )
        upilabel = CTkLabel(
            master = paymentframe,
            height = 14,
            width = 45,
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("upi.png") , "r"),
                dark_image = Image.open(relative_to_assets("upi.png") , "r"),
                size = (45 , 14)
            )
        )
        upilabel.place(
            relx = 0.03,
            rely = 0.4,
            anchor = "w"
        )
        upibutton = CTkButton(
            master = paymentframe,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("next.png") , "r"),
                dark_image = Image.open(relative_to_assets("next.png") , "r"),
                size = (17,17)
            ),
            text = "",
            fg_color = "#242424",
            hover_color = "#242424",
            command = lambda : messagebox.showinfo("Important!" , "UPI not available at the moment!")
        )
        upibutton.place(
            relx = 0.925,
            rely = 0.4,
            anchor = "w"
        )
        upitext = CTkLabel(
            master = paymentframe,
            height = 0,
            width = 0,
            fg_color = "#242424",
            bg_color = "transparent",
            text = "UPI",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        upitext.place(
            relx = 0.13,
            rely = 0.4,
            anchor = "w"
        )
        seperation2 = CTkFrame(
            master = paymentframe,
            width = 476,
            height = 3,
            corner_radius = 2,
            fg_color = "#C0C0C0",
            bg_color = "transparent"
        )
        seperation2.place(
            relx = 0.5,
            rely = 0.52,
            anchor = "center"
        )
        cardlabel = CTkLabel(
            master = paymentframe,
            height = 24,
            width = 24,
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("card.png") , "r"),
                dark_image = Image.open(relative_to_assets("card.png") , "r"),
                size = (24 , 25)
            )
        )
        cardlabel.place(
            relx = 0.047,
            rely = 0.63,
            anchor = "w"
        )
        cardbutton = CTkButton(
            master = paymentframe,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("next.png") , "r"),
                dark_image = Image.open(relative_to_assets("next.png") , "r"),
                size = (17,17)
            ),
            text = "",
            fg_color = "#242424",
            hover_color = "#242424",
            command = lambda : messagebox.showinfo("Important!" , "Card not available at the moment!")
        )
        cardbutton.place(
            relx = 0.925,
            rely = 0.63,
            anchor = "w"
        )
        cardtext = CTkLabel(
            master = paymentframe,
            height = 0,
            width = 0,
            fg_color = "#242424",
            bg_color = "transparent",
            text = "Credit/Debit Card",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        cardtext.place(
            relx = 0.13,
            rely = 0.63,
            anchor = "w"
        )
        seperation3 = CTkFrame(
            master = paymentframe,
            width = 476,
            height = 3,
            corner_radius = 2,
            fg_color = "#C0C0C0",
            bg_color = "transparent"
        )
        seperation3.place(
            relx = 0.5,
            rely = 0.75,
            anchor = "center"
        )
        poplabel = CTkLabel(
            master = paymentframe,
            height = 15,
            width = 15,
            text = "",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("logo-pop.png") , "r"),
                dark_image = Image.open(relative_to_assets("logo-pop.png") , "r"),
                size = (15 , 15)
            )
        )
        poplabel.place(
            relx = 0.058,
            rely = 0.87,
            anchor = "w"
        )
        poptext = CTkLabel(
            master = paymentframe,
            height = 0,
            width = 0,
            fg_color = "#242424",
            bg_color = "transparent",
            text = "Popaction™",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE"
        )
        poptext.place(
            relx = 0.13,
            rely = 0.87,
            anchor = "w"
        )

        def pbind():
            continuebutton.bind("<Enter>", lambda event : continuebutton.configure(
                text_color="#CCCCCC",
                fg_color = "#7B0D15"
                )
            ) 
            continuebutton.bind("<Leave>", lambda event : continuebutton.configure(
                text_color="#EEEEEE",
                fg_color = "#DF1827"
                )
            )  

        popbutton = CTkButton(
            master = paymentframe,
            height = 0,
            width = 0,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("next.png") , "r"),
                dark_image = Image.open(relative_to_assets("next.png") , "r"),
                size = (17,17)
            ),
            text = "",
            fg_color = "#242424",
            hover_color = "#242424",
            command = lambda : (messagebox.showinfo("Success!" , "Payment Method Selected!") , continuebutton.configure(fg_color = "#DF1827" , state = "active") , pbind())
        )
        popbutton.place(
            relx = 0.925,
            rely = 0.87,
            anchor = "w"
        )
        
        confirmframe = CTkFrame(
            master = bookingrightcanvas,
            height = 40,
            width = 490,
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#242424"
        )
        confirmframe.place(
            relx = 0.5,
            rely = 0.555,
            anchor = "center"
        )

        confirmtext = CTkLabel(
            master = confirmframe,
            height = 0,
            width = 0,
            text = "*By proceeding, I express my consent to complete this transaction.",
            font = ("Satoshi-Bold" , 15 * 1),
            text_color = "#EEEEEE"
        )
        confirmtext.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )
        
        buttonframe = CTkFrame(
            master = bookingrightcanvas,
            bg_color = "transparent",
            fg_color = "#111111",
            height = 54,
            width = 490,
            corner_radius = 10
        ) 
        buttonframe.place(
            relx = 0.5,
            rely = 0.642,
            anchor = "center"
        )
        
        def ask():
            response = messagebox.askquestion("Are you sure?" , "Do you want to cancel?")
            if response == "yes":
                loadingmain("landingcanvas")
            else:
                pass
            return
        
        def confirm():
            response = messagebox.askquestion("Confirm Payment" , "Finish Payment?")
            if response == "yes":
                database()
                cur.execute("USE popaction_data")
                for seat_sel in selected_seat:
                    cur.execute("DELETE FROM " + adv_detail + " WHERE movie_seat = %s" , (seat_sel , ))
                connect.commit()
                connect.close()
                bookingcanvas.destroy()
                loadingmain("ticketshowcanvas")
            else:
                pass
            return

        cancelbutton = CTkButton(
            master = buttonframe,
            height = 50,
            width = 232,
            text = "Cancel",
            text_color = "#EEEEEE",
            font = ("Satoshi-Medium" , 20 * 1),
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#414141",
            hover_color = "#242424",
            command = lambda : ask()
        )
        cancelbutton.bind("<Enter>", lambda event : cancelbutton.configure(
            text_color="#CCCCCC",
            fg_color = "#242424"
            )
        ) 
        cancelbutton.bind("<Leave>", lambda event : cancelbutton.configure(
            text_color="#EEEEEE",
            fg_color = "#414141"
            )
        )
        cancelbutton.place(
            relx = 0,
            rely = 0.5,
            anchor = "w"
        )

        continuebutton = CTkButton(
            master = buttonframe,
            height = 50,
            width = 232,
            text = "Continue",
            text_color = "#EEEEEE",
            font = ("Satoshi-Medium" , 20 * 1),
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#7B0D15",
            hover_color = "#7B0D15",
            state = "disabled",
            command = lambda : confirm()
        )   
        continuebutton.place(
            relx = 1,
            rely = 0.5,
            anchor = "e"
        )
        

    global ticketshow
    def ticketshow():
        
        ticketcanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketcanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )
        
        ticketleftcanvas = CTkCanvas(
            master = ticketcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketleftcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        ticketrightcanvas = CTkCanvas(
            master = ticketcanvas,
            bd = 0,
            bg = "#111111",
            width = 494,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketrightcanvas.place(
            x = 910, 
            rely = 0.5,
            anchor = "center"
        )

        permelements(ticketleftcanvas)

        ticketlabel = CTkLabel(
            master = ticketleftcanvas,
            height = 700,
            width = 490,
            fg_color = "#111111",
            bg_color = "transparent",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("mticket.png") , "r"),
                dark_image = Image.open(relative_to_assets("mticket.png") , "r"),
                size = (490 , 700)
            ),
            text = ""
        )
        ticketlabel.place(
            relx = 0.5,
            rely = 0.47,
            anchor = "center"
        )

        posterticket = CTkLabel(
            master = ticketlabel,
            height = 176,
            width = 132,
            fg_color = "#242424",
            bg_color = "transparent",
            image = CTkImage(
                light_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                dark_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                size = (132 , 176)
            ),
            text = ""
        )
        posterticket.place(
            relx = 0.17,
            rely = 0.02,
            anchor = "n"
        )

        movietext = CTkLabel(
            master = ticketlabel,
            text = movie,
            font = ("Satoshi-Bold" , 19 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424",
        )
        movietext.place(
            x = 314.0,
            rely = 0.02,
            anchor = "n"
        )
        movietext = CTkLabel(
            master = ticketlabel,
            text = ticketdate + " | "  + tickettime,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        movietext.place(
            x = 314.0,
            rely = 0.059,
            anchor = "n"
        )
        halltext = CTkLabel(
            master = ticketlabel,
            text = tickethall.replace("_" , " ") + ", " + cityname,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        halltext.place(
            x = 314.0,
            rely = 0.097,
            anchor = "n"
        )
        global rating
        langtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = rating[0] + " | Sub:" + rating[1] + " | " + rating[2],
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        langtext.place(
            x = 314.0,
            rely = 0.17,
            anchor = "n"
        )
        seattext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = str(selected_seat).replace("'" , "").replace("," , " ,"),
            font = ("Satoshi-Bold" , 20 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        seattext.place(
            x = 314.0,
            rely = 0.23,
            anchor = "n"
        )
        mtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = "M-Ticket",
            font = ("Satoshi-Bold" , 10 * 1),
            text_color = "#C0C0C0",
            fg_color = "#242424",
            bg_color = "#242424",
            wraplength = 1
        )
        mtext.place(
            x = 485.0,
            rely = 0.14,
            anchor = "e"
        )

        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 6,
            border = 4,
        )
        qr.add_data(adv_detail + str(selected_seat))
        qr.make(fit = True)

        img = qr.make_image(fill_color="#EEEEEE", back_color="#242424")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_pil = Image.open(img_byte_arr)
        img_ctk = CTkImage(
            light_image = img_pil,
            dark_image = img_pil,
            size=(img_pil.width, img_pil.height)
            )

        qrcodeimg = CTkLabel(
            master = ticketlabel,
            height = 200,
            width = 200,
            text = "",
            fg_color = "#555555",
            bg_color = "#242424",
            image = img_ctk
        )
        qrcodeimg.place(
            relx = 0.5,
            rely = 0.47,
            anchor = "center"
        )

        def generate_booking_id(sentence):
            # Encode the sentence to bytes
            encoded_sentence = sentence.encode()
            
            # Create a SHA-1 hash of the sentence
            sha1_hash = hashlib.sha1(encoded_sentence).hexdigest()
            
            # Take the first 7 characters of the hash
            booking_id = sha1_hash[:7].upper()
            
            return booking_id

        sentence = adv_detail + str(selected_seat)
        booking_id = generate_booking_id(sentence)

        qrtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = "Booking Id:" + booking_id,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        qrtext.place(
            relx = 0.5,
            rely = 0.65,
            anchor = "center"
        )

        notickets = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = str(len(selected_seat)) + " Ticket(s)",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        notickets.place(
            relx = 0.5,
            rely = 0.68,
            anchor = "center"
        )

        midframe = CTkFrame(
            master = ticketlabel,
            height = 40,
            width = 490,
            corner_radius = 0,
            fg_color = "#414141",
            bg_color = "#242424"
        )
        midframe.place(
            relx = 0.5,
            rely = 0.71,
            anchor = "n"
        )
        midframetext = CTkLabel(
            master = midframe,
            height = 0,
            width = 0,
            text = "Cancelation Available:Cut-Off Time 20 minutes before showtime",
            font = ("Satoshi-Bold" , 15 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#242424"
        )
        midframetext.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )

        def confirm():
            response = messagebox.askquestion("Are you sure?" , "Cancel Booking?")
            if response == "yes":
                database()
                cur.execute("USE popaction_data")
                for seat_sel in selected_seat:
                    cur.execute("INSERT INTO " + adv_detail + "(movie_seat) values (%s)" , (seat_sel , ))
                cur.execute("DELETE FROM bookings WHERE booking_id = %s" , (booking_id , ))
                connect.commit()
                connect.close()
                messagebox.showinfo("Success!" , "Your ticket has been successfully cancelled and refunded into Popaction™!")
                ticketcanvas.destroy()
                loadingmain("landingcanvas")
            else:
                pass
            return
        
        cancelbutton = CTkButton(
            master = ticketlabel,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("cancel.png") , "r"),
                dark_image = Image.open(relative_to_assets("cancel.png") , "r"),
                size = (33 , 33)
            ),
            text = "",
            fg_color = "#242424",
            bg_color = "#242424",
            hover_color = "#242424",
            command = lambda : confirm()
        )
        cancelbutton.place(
            relx = 0.4,
            rely = 0.83,
            anchor = "e"
        )
        canceltext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Cancel Booking",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        canceltext.place(
            relx = 0.26,
            rely = 0.88,
            anchor = "center"
        )

        contactbutton = CTkButton(
            master = ticketlabel,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("contact.png") , "r"),
                dark_image = Image.open(relative_to_assets("contact.png") , "r"),
                size = (33 , 33)
            ),
            text = "",
            fg_color = "#242424",
            bg_color = "#242424",
            hover_color = "#242424",
            command = lambda : messagebox.showinfo("Important!" , "Support not available at the moment!")
        )
        contactbutton.place(
            relx = 0.6,
            rely = 0.83,
            anchor = "w"
        )
        canceltext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Contact Support",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        canceltext.place(
            relx = 0.74,
            rely = 0.88,
            anchor = "center"
        )

        amounttext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Amount Paid",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#414141"
        )
        amounttext.place(
            relx = 0.032,
            rely = 0.97,
            anchor = "w"
        )

        amountpricetext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Rs. " + payabletext,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#414141"
        )
        amountpricetext.place(
            relx = 0.965,
            rely = 0.97,
            anchor = "e"
        )

        folder_path = tickets_booked("tickets")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = f"{booking_id}.jpeg"

        full_path = os.path.join(folder_path, filename)
        
        
        database()
        cur.execute("USE popaction_data")
        cur.execute("INSERT INTO bookings (booking_id , log_id , mov_name , date_time , rating_info , seats , hall_info , detail_seat , no_tickets , price , adv_detail) values(%s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s)" , (booking_id , logid , movie , str(ticketdate + " | "  + tickettime) , str(rating[0] + " | Sub:" + rating[1] + " | " + rating[2]) , str(selected_seat).replace("'" , "").replace("," , " ,") , tickethall.replace("_" , " ") + ", " + cityname , adv_detail + str(selected_seat) , len(selected_seat) , payabletext , adv_detail))
        connect.commit()
        connect.close()

        def tempfunc():
            messagebox.showinfo("Success!" , "Your Ticket was successfully saved in the bookings folder in your app install location!")
            ticketcanvas.destroy()
            loadingmain("landingcanvas")

        savebutton = CTkButton(
            master = ticketrightcanvas,
            height = 50,
            width = 232,
            text = "Save",
            text_color = "#EEEEEE",
            font = ("Satoshi-Medium" , 20 * 1),
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : (ImageGrab.grab((ticketlabel.winfo_rootx(), ticketlabel.winfo_rooty(), ticketlabel.winfo_rootx() + ticketlabel.winfo_width(), ticketlabel.winfo_rooty() + ticketlabel.winfo_height())).save(full_path) ,tempfunc())
        )   
        savebutton.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )
        
        def ask_screen():
            response = messagebox.askquestion("Are you done?", "Did you save your ticket's screenshot? If Yes check the bookings folder in your app install location!")
            if response == "yes":
                window.destroy()
            else:
                pass
        window.protocol('WM_DELETE_WINDOW', lambda : ask_screen())
        
        
    global prebooked
    def prebooked(booking_id):
        
        database()
        cur.execute("USE popaction_data")
        cur.execute("SELECT * FROM bookings WHERE booking_id = %s" , (booking_id , ))
        data = cur.fetchone()
        

        premovie = data[2]
        predatetime = data[3]
        preratinginfo = data[4]
        preseats = data[5]
        prelocation = data[6]
        predetail = data[7]
        prenotickets = data[8]
        preprice = data[9]
        preadvdetail = data[10]


        preseatslist = preseats.replace("[" , "").replace("]" , "").split(" , ")
        print(preseatslist)

        precity = data[6].split(", ")[1]
        print(precity)

        cur.execute("SELECT mov_images FROM movies_" + precity + " WHERE mov_name = %s" , (premovie , ))
        row = cur.fetchone()
        poster = row[0]

        ticketcanvas = CTkCanvas(
            master = window,
            bd = 0,
            bg = "#111111" ,
            width = 1220,
            height = 775,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketcanvas.place(
            relx = 0.5, 
            rely = 0.5,
            anchor = "center"
        )
        
        ticketleftcanvas = CTkCanvas(
            master = ticketcanvas,
            bd = 0,
            bg = "#111111" ,
            width = 795,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketleftcanvas.place(
            x = 412.5, 
            rely = 0.5,
            anchor = "center"
        )

        ticketrightcanvas = CTkCanvas(
            master = ticketcanvas,
            bd = 0,
            bg = "#111111",
            width = 494,
            height = 745,
            highlightthickness = 0,
            borderwidth = 0
        )
        ticketrightcanvas.place(
            x = 910, 
            rely = 0.5,
            anchor = "center"
        )

        permelements(ticketleftcanvas)

        ticketlabel = CTkLabel(
            master = ticketleftcanvas,
            height = 700,
            width = 490,
            fg_color = "#111111",
            bg_color = "transparent",
            image = CTkImage(
                light_image = Image.open(relative_to_assets("mticket.png") , "r"),
                dark_image = Image.open(relative_to_assets("mticket.png") , "r"),
                size = (490 , 700)
            ),
            text = ""
        )
        ticketlabel.place(
            relx = 0.5,
            rely = 0.47,
            anchor = "center"
        )

        posterticket = CTkLabel(
            master = ticketlabel,
            height = 176,
            width = 132,
            fg_color = "#242424",
            bg_color = "transparent",
            image = CTkImage(
                light_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                dark_image = Image.open(relative_to_assets(poster + ".png") , "r"),
                size = (132 , 176)
            ),
            text = ""
        )
        posterticket.place(
            relx = 0.17,
            rely = 0.02,
            anchor = "n"
        )

        movietext = CTkLabel(
            master = ticketlabel,
            text = premovie,
            font = ("Satoshi-Bold" , 19 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424",
        )
        movietext.place(
            x = 314.0,
            rely = 0.02,
            anchor = "n"
        )
        movietext = CTkLabel(
            master = ticketlabel,
            text = predatetime,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        movietext.place(
            x = 314.0,
            rely = 0.059,
            anchor = "n"
        )
        halltext = CTkLabel(
            master = ticketlabel,
            text = prelocation,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        halltext.place(
            x = 314.0,
            rely = 0.097,
            anchor = "n"
        )
        global rating
        langtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = preratinginfo,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        langtext.place(
            x = 314.0,
            rely = 0.17,
            anchor = "n"
        )
        seattext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = preseats,
            font = ("Satoshi-Bold" , 20 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        seattext.place(
            x = 314.0,
            rely = 0.23,
            anchor = "n"
        )
        mtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = "M-Ticket",
            font = ("Satoshi-Bold" , 10 * 1),
            text_color = "#C0C0C0",
            fg_color = "#242424",
            bg_color = "#242424",
            wraplength = 1
        )
        mtext.place(
            x = 485.0,
            rely = 0.14,
            anchor = "e"
        )

        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 6,
            border = 4,
        )
        qr.add_data(predetail)
        qr.make(fit = True)

        img = qr.make_image(fill_color="#EEEEEE", back_color="#242424")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_pil = Image.open(img_byte_arr)
        img_ctk = CTkImage(
            light_image = img_pil,
            dark_image = img_pil,
            size=(img_pil.width, img_pil.height)
            )

        qrcodeimg = CTkLabel(
            master = ticketlabel,
            height = 200,
            width = 200,
            text = "",
            fg_color = "#555555",
            bg_color = "#242424",
            image = img_ctk
        )
        qrcodeimg.place(
            relx = 0.5,
            rely = 0.47,
            anchor = "center"
        )

        qrtext = CTkLabel(
            master = ticketlabel,
            height = 0,
            width = 0,
            text = "Booking Id:" + booking_id,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        qrtext.place(
            relx = 0.5,
            rely = 0.65,
            anchor = "center"
        )

        notickets = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = str(prenotickets) + " Ticket(s)",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        notickets.place(
            relx = 0.5,
            rely = 0.68,
            anchor = "center"
        )

        midframe = CTkFrame(
            master = ticketlabel,
            height = 40,
            width = 490,
            corner_radius = 0,
            fg_color = "#414141",
            bg_color = "#242424"
        )
        midframe.place(
            relx = 0.5,
            rely = 0.71,
            anchor = "n"
        )
        midframetext = CTkLabel(
            master = midframe,
            height = 0,
            width = 0,
            text = "Cancelation Available:Cut-Off Time 20 minutes before showtime",
            font = ("Satoshi-Bold" , 15 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#242424"
        )
        midframetext.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )

        def confirm():
            response = messagebox.askquestion("Are you sure?" , "Cancel Booking?")
            if response == "yes":
                database()
                cur.execute("USE popaction_data")
                for seat_sel in preseatslist:
                    cur.execute("INSERT INTO " + preadvdetail + "(movie_seat) values (%s)" , (seat_sel , ))
                cur.execute("DELETE FROM bookings WHERE booking_id = %s" , (booking_id , ))
                connect.commit()
                connect.close()
                messagebox.showinfo("Success!" , "Your ticket has been successfully cancelled and refunded into Popaction™!")
                ticketcanvas.destroy()
                loadingmain("landingcanvas")
            else:
                pass
            return
        
        cancelbutton = CTkButton(
            master = ticketlabel,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("cancel.png") , "r"),
                dark_image = Image.open(relative_to_assets("cancel.png") , "r"),
                size = (33 , 33)
            ),
            text = "",
            fg_color = "#242424",
            bg_color = "#242424",
            hover_color = "#242424",
            command = lambda : confirm()
        )
        cancelbutton.place(
            relx = 0.4,
            rely = 0.83,
            anchor = "e"
        )
        canceltext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Cancel Booking",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        canceltext.place(
            relx = 0.26,
            rely = 0.88,
            anchor = "center"
        )

        contactbutton = CTkButton(
            master = ticketlabel,
            image = CTkImage(
                light_image = Image.open(relative_to_assets("contact.png") , "r"),
                dark_image = Image.open(relative_to_assets("contact.png") , "r"),
                size = (33 , 33)
            ),
            text = "",
            fg_color = "#242424",
            bg_color = "#242424",
            hover_color = "#242424",
            command = lambda : messagebox.showinfo("Important!" , "Support not available at the moment!")
        )
        contactbutton.place(
            relx = 0.6,
            rely = 0.83,
            anchor = "w"
        )
        canceltext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Contact Support",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#242424",
            bg_color = "#242424"
        )
        canceltext.place(
            relx = 0.74,
            rely = 0.88,
            anchor = "center"
        )

        amounttext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Amount Paid",
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#414141"
        )
        amounttext.place(
            relx = 0.032,
            rely = 0.97,
            anchor = "w"
        )

        amountpricetext = CTkLabel(
            master = ticketlabel,
            height = 0,
            text = "Rs. " + preprice,
            font = ("Satoshi-Bold" , 16 * 1),
            text_color = "#EEEEEE",
            fg_color = "#414141",
            bg_color = "#414141"
        )
        amountpricetext.place(
            relx = 0.965,
            rely = 0.97,
            anchor = "e"
        )

        folder_path = tickets_booked("tickets")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = f"{booking_id}.jpeg"

        full_path = os.path.join(folder_path, filename)

        def tempfunc():
            messagebox.showinfo("Success!" , "Your Ticket was successfully saved in the bookings folder in your app install location!")
            ticketcanvas.destroy()
            loadingmain("landingcanvas")
        
        savebutton = CTkButton(
            master = ticketrightcanvas,
            height = 50,
            width = 232,
            text = "Save",
            text_color = "#EEEEEE",
            font = ("Satoshi-Medium" , 20 * 1),
            corner_radius = 10,
            bg_color = "transparent",
            fg_color = "#DF1827",
            hover_color = "#7B0D15",
            command = lambda : (ImageGrab.grab((ticketlabel.winfo_rootx(), ticketlabel.winfo_rooty(), ticketlabel.winfo_rootx() + ticketlabel.winfo_width(), ticketlabel.winfo_rooty() + ticketlabel.winfo_height())).save(full_path) , tempfunc())
        )   
        savebutton.place(
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )
        
        def ask_screen():
            response = messagebox.askquestion("Are you done?", "Did you save your ticket's screenshot? If Yes check the bookings folder in your app install location!")
            if response == "yes":
                window.destroy()
            else:
                pass
        window.protocol('WM_DELETE_WINDOW', lambda : ask_screen())

        
    landing()

tempload()


window.resizable(False, False)
window.mainloop()