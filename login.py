import os

import mysql.connector
from tkinter import *
from client import ChatApp
from register import RegistrationScreen
from tkinter import messagebox
class LoginScreen:
    def __init__(self, host, port):
        self.login_screen = Tk()
        self.user = None
        self.host = host
        self.port = port

        self.login_screen.title("Login")
        self.login_screen.geometry("300x250")
        self.login_screen.config(bg="#34495e")

        Label(self.login_screen, text="Please enter login details", bg="#34495e", fg="white").pack()
        Label(self.login_screen, text="", bg="#34495e").pack()

        Label(self.login_screen, text="Email", bg="#34495e", fg="white").pack()
        self.email_var = StringVar()
        self.email_input = Entry(self.login_screen, textvariable=self.email_var)
        self.email_input.pack()

        Label(self.login_screen, text="Password", bg="#34495e", fg="white").pack()
        self.password_var = StringVar()
        self.password = Entry(self.login_screen, textvariable=self.password_var, show='*')
        self.password.pack()

        Button(self.login_screen, text="Login", width=10, height=1, command=self.redirect_chat, bg="#2c3e50", fg="white").pack(pady=5)
        Button(self.login_screen, text="Register", width=10, height=1, command=self.redirect_register, bg="#2c3e50", fg="white").pack(pady=5)

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

    def redirect_chat(self):
        pswd_flag = self.valid_pswd()
        email_flag = self.valid_email()
        if email_flag and pswd_flag:
            mydb = self.get_db_connection()
            self.email = self.email_var.get()
            pswd = self.password_var.get()
            mycursor = mydb.cursor()

            sql = f"SELECT * FROM users WHERE email = '{self.email}' AND password = '{pswd}'"
            mycursor.execute(sql)

            result = mycursor.fetchall()
            mycursor.close()
            mydb.close()
            if result:
                self.login_screen.destroy()
                chat_app = ChatApp(self.host, self.port, self.email)
                chat_app.run()
        else:
            if not pswd_flag:
                messagebox.showerror("Invalid Password", "The password needs to contain at least 6 characters")

            if not email_flag:
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")

    def valid_email(self):
        user = self.email_var.get()
        # checks for email format
        return user and "@" in user and "." in user.split('@')[-1]

    def valid_pswd(self):#validate password
        p = self.password_var.get()
        return p and len(p) >= 6


    def redirect_register(self):#redirect user to register page
        self.login_screen.destroy()
        register_screen = RegistrationScreen(self.host,self.port)
        register_screen.run()

    def get_user(self):
        return self.user
    def run(self):
        self.login_screen.mainloop()

if __name__ == "__main__":
    host = os.getenv("CHAT_HOST", "localhost")
    port = int(os.getenv("CHAT_PORT", 8080))
    login_screen = LoginScreen(host, port)
    login_screen.run()
