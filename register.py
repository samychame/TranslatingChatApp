from tkinter import *
from tkinter import messagebox
import mysql.connector
from client import ChatApp

LANGUAGES = {
    'afrikaans': 'af',
    'albanian': 'sq',
    'amharic': 'am',
    'arabic': 'ar',
    'armenian': 'hy',
    'azerbaijani': 'az',
    'basque': 'eu',
    'belarusian': 'be',
    'bengali': 'bn',
    'bosnian': 'bs',
    'bulgarian': 'bg',
    'catalan': 'ca',
    'cebuano': 'ceb',
    'chichewa': 'ny',
    'chinese (simplified)': 'zh-cn',
    'chinese (traditional)': 'zh-tw',
    'corsican': 'co',
    'croatian': 'hr',
    'czech': 'cs',
    'danish': 'da',
    'dutch': 'nl',
    'english': 'en',
    'esperanto': 'eo',
    'estonian': 'et',
    'filipino': 'tl',
    'finnish': 'fi',
    'french': 'fr',
    'frisian': 'fy',
    'galician': 'gl',
    'georgian': 'ka',
    'german': 'de',
    'greek': 'el',
    'gujarati': 'gu',
    'haitian creole': 'ht',
    'hausa': 'ha',
    'hawaiian': 'haw',
    'hebrew': 'he',
    'hindi': 'hi',
    'hmong': 'hmn',
    'hungarian': 'hu',
    'icelandic': 'is',
    'igbo': 'ig',
    'indonesian': 'id',
    'irish': 'ga',
    'italian': 'it',
    'japanese': 'ja',
    'javanese': 'jw',
    'kannada': 'kn',
    'kazakh': 'kk',
    'khmer': 'km',
    'korean': 'ko',
    'kurdish (kurmanji)': 'ku',
    'kyrgyz': 'ky',
    'lao': 'lo',
    'latin': 'la',
    'latvian': 'lv',
    'lithuanian': 'lt',
    'luxembourgish': 'lb',
    'macedonian': 'mk',
    'malagasy': 'mg',
    'malay': 'ms',
    'malayalam': 'ml',
    'maltese': 'mt',
    'maori': 'mi',
    'marathi': 'mr',
    'mongolian': 'mn',
    'myanmar (burmese)': 'my',
    'nepali': 'ne',
    'norwegian': 'no',
    'odia': 'or',
    'pashto': 'ps',
    'persian': 'fa',
    'polish': 'pl',
    'portuguese': 'pt',
    'punjabi': 'pa',
    'romanian': 'ro',
    'russian': 'ru',
    'samoan': 'sm',
    'scots gaelic': 'gd',
    'serbian': 'sr',
    'sesotho': 'st',
    'shona': 'sn',
    'sindhi': 'sd',
    'sinhala': 'si',
    'slovak': 'sk',
    'slovenian': 'sl',
    'somali': 'so',
    'spanish': 'es',
    'sundanese': 'su',
    'swahili': 'sw',
    'swedish': 'sv',
    'tajik': 'tg',
    'tamil': 'ta',
    'telugu': 'te',
    'thai': 'th',
    'turkish': 'tr',
    'ukrainian': 'uk',
    'urdu': 'ur',
    'uyghur': 'ug',
    'uzbek': 'uz',
    'vietnamese': 'vi',
    'welsh': 'cy',
    'xhosa': 'xh',
    'yiddish': 'yi',
    'yoruba': 'yo',
    'zulu': 'zu'}

languages = list(LANGUAGES.keys())  # list of languages

class RegistrationScreen:
    def __init__(self, host, port):
        self.reg_screen = Tk()
        self.user = None
        self.host = host
        self.port = port
        self.reg_screen.title("Register")
        self.reg_screen.geometry("350x300")
        self.reg_screen.config(bg="#34495e")

        Label(self.reg_screen, text="Please enter register details", bg="#34495e", fg="white").pack()
        Label(self.reg_screen, text="", bg="#34495e").pack()

        # Username
        Label(self.reg_screen, text="Username", bg="#34495e", fg="white").pack()
        self.username = Entry(self.reg_screen)
        self.username.pack()

        # Email
        Label(self.reg_screen, text="Email", bg="#34495e", fg="white").pack()
        self.email = Entry(self.reg_screen)
        self.email.pack()

        # Password
        Label(self.reg_screen, text="", bg="#34495e").pack()
        Label(self.reg_screen, text="Password", bg="#34495e", fg="white").pack()
        self.password = Entry(self.reg_screen, show='*')
        self.password.pack()

        # Language
        Label(self.reg_screen, text="Language", bg="#34495e", fg="white").pack()
        self.variable = StringVar(self.reg_screen)
        self.variable.set("Select a language")  # default value
        lng_menu = OptionMenu(self.reg_screen, self.variable, *languages)
        lng_menu.config(bg="#2c3e50", fg="white")
        lng_menu["menu"].config(bg="#2c3e50", fg="white")
        lng_menu.pack(pady=5)

        Button(self.reg_screen, text="Register", width=10, height=1, command=self.redirect_chat, bg="#2c3e50", fg="white").pack()

    def valid_user(self):
        user = self.username.get()
        return user

    def valid_email(self):
        email = self.email.get()
        return email and "@" in email and "." in email.split('@')[-1]

    def valid_pswd(self):
        p = self.password.get()
        return p and len(p) >= 6

    def valid_lng(self):
        language = self.variable.get()
        return language != "Select a language"

    def get_db_connection(host="127.0.0.1", user="user", password="yourpassword", database="project"):
        try:
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            return mydb
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
    def email_exists(self, email):
        mydb = self.get_db_connection()
        mycursor = mydb.cursor()

        sql = "SELECT COUNT(*) FROM users WHERE email = %s"
        mycursor.execute(sql, (email,))
        count = mycursor.fetchone()[0]

        mycursor.close()
        mydb.close()

        return count > 0

    def redirect_chat(self):
        user_flag = self.valid_user()
        email_flag = self.valid_email()
        pswd_flag = self.valid_pswd()
        lng_flag = self.valid_lng()
        if lng_flag and pswd_flag and email_flag and user_flag:
            if not self.email_exists(self.email.get()):
                mydb = self.get_db_connection()
                mycursor = mydb.cursor()

                self.user = self.username.get()
                self.email = self.email.get()

                sql = "INSERT INTO users (username, password, language, email,chats) VALUES (%s, %s, %s, %s,%s)"
                values = (self.user, self.password.get(), LANGUAGES[self.variable.get()], self.email,"")
                mycursor.execute(sql, values)
                mydb.commit()

                self.reg_screen.destroy()
                mycursor.close()
                mydb.close()
                chat_app = ChatApp(self.host, self.port, self.email)
                chat_app.run()
            else:
                messagebox.showerror("Error","Email is already registered")

        else:
            msg = ""
            if not email_flag:
                msg+="Email not valid"
            if not user_flag:
                msg+=",Username not valid"
            if not lng_flag:
                msg+=",Choose a language"
            if not pswd_flag:
                msg+=",Password must be at least 6 character long "
            messagebox.showerror("Invalid input", msg)

    def get_user(self):
        return self.user

    def run(self):
        self.reg_screen.mainloop()


