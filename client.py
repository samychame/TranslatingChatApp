import socket
from threading import Thread
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from googletrans import Translator
import mysql.connector
import os
import time

class Group:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.messages = []


class ChatApp:
    def __init__(self, host, port,email):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.email = email
        self.lng = None
        self.translator = Translator()
        self.group_dict = {}
        self.all_users = []
        self.user_in_chat = []
        self.user_listbox = None
        self.file_listbox = None
        self.window = Tk()
        self.window.title("Chat Application")
        self.window.configure(bg="#2c3e50")
        self.window.geometry("800x350")

        self.groups = []
        self.current_group = None

        self.create_widgets()

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        self.initialize_database()
        self.update_group_list()
        self.get_messagedb()

        self.window.mainloop()

    def create_widgets(self):
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=3)

        # Group listbox frame
        group_frame = tk.Frame(self.window, bg="#34495e")
        group_frame.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=5, pady=5)
        group_frame.grid_rowconfigure(1, weight=1)

        tk.Label(group_frame, text="Groups", bg="#34495e", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        self.group_listbox = tk.Listbox(group_frame, height=20, width=20, bg="white")
        self.group_listbox.pack(fill=tk.BOTH, expand=True)
        self.group_listbox.bind("<<ListboxSelect>>", self.select_group)

        # Message display frame
        message_display_frame = tk.Frame(self.window, bg="#34495e")
        message_display_frame.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)
        message_display_frame.grid_rowconfigure(0, weight=1)
        message_display_frame.grid_columnconfigure(0, weight=1)

        tk.Label(message_display_frame, text="Messages", bg="#34495e", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        self.message_frame = tk.Frame(message_display_frame, bg='white')
        self.message_frame.pack(fill=tk.BOTH, expand=True)

        self.scroll_bar = tk.Scrollbar(self.message_frame)
        self.msg_list = tk.Listbox(self.message_frame, bg="white", yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Entry frame for message input and buttons
        entry_frame = tk.Frame(self.window, bg="#2c3e50")
        entry_frame.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        entry_frame.grid_columnconfigure(0, weight=1)

        self.my_msg = tk.StringVar()
        self.entry_field = tk.Entry(entry_frame, textvariable=self.my_msg, fg="black", font=("Arial", 10))
        self.entry_field.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.send_button = tk.Button(entry_frame, text="Send", font=("Arial", 10, "bold"), fg="white", bg="#3498db",
                                     command=lambda: self.send(False))

        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        self.file_button = tk.Button(entry_frame, text="Send File", font=("Arial", 10, "bold"), fg="white", bg="#3498db",
                                     command=self.select_file)
        self.file_button.grid(row=0, column=2, padx=5, pady=5)

        self.download_button = tk.Button(entry_frame, text="Download File", font=("Arial", 10, "bold"), fg="white", bg="#3498db",
                                         command=self.request_file_list)
        self.download_button.grid(row=0, column=3, padx=5, pady=5)

        self.group_info_button = tk.Button(entry_frame, text="Group Info", font=("Arial", 10, "bold"), fg="white", bg="#2ecc71",
                                           command=self.info_window)
        self.group_info_button.grid(row=0, column=4, padx=5, pady=5)

        self.add_group_button = tk.Button(entry_frame, text="Add Group", font=("Arial", 10, "bold"), fg="white", bg="#3498db",
                                          command=self.group_window)
        self.add_group_button.grid(row=0, column=5, padx=5, pady=5)
    def initialize_database(self):
        # Initialize the database and retrieve user's language
        try:
            mydb = self.get_db_connection()

            if mydb.is_connected():
                mycursor = mydb.cursor()
                sql = f"SELECT language,chats FROM users WHERE email ='{ self.email }'"
                mycursor.execute(sql)
                result = mycursor.fetchone()

                if result is not None:
                    self.lng = result[0]
                    if result[1] != '':
                        chats = result[1].split(",")
                        for i in chats:
                            if i != "":
                                self.groups.append(Group(i[:len(i) - 5], i[len(i) - 5:len(i)]))

                else:
                    print("User not found or language not specified in the database.")
                    # Set a default language or handle the situation accordingly.

                sql = "SELECT username,email FROM users"
                mycursor.execute(sql)
                result = mycursor.fetchall()
                for i in result:
                    self.all_users.append(f"{i[0]}({i[1]})")
                mycursor.close()
            else:
                print("Error: Database connection failed.")

        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")

        finally:
            if mydb.is_connected():
                mydb.close()

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
    def get_messagedb(self):
        # Retrieve messages from the database
        try:
            mydb = self.get_db_connection()

            if mydb.is_connected():
                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM messages")
                result = mycursor.fetchall()
                for i in result:
                    message = i[3]
                    if i[1] != self.email and message != "":
                        message = self.translator.translate(i[3], dest=self.lng).text
                    if i[0] in self.group_dict:
                        self.group_dict[i[0]].messages.append(f"[{i[1]}]{message}")

            else:
                print("Problem with database")
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")

        finally:
            if mydb.is_connected():
                mydb.close()

    def update_group_list(self):
        # Update the group list
        if self.groups:
            for group in self.groups:
                self.group_dict[group.id] = group
                self.group_listbox.insert(tk.END, f"{group.name}[{group.id}]")

    def select_group(self, event):
        # Select a group from the listbox
        selected_index = self.group_listbox.curselection()
        if selected_index:
            selected_group_name = self.group_listbox.get(selected_index)
            self.current_group = next(
                (group for group in self.groups if f"{group.name}[{group.id}]" == selected_group_name), None)
            self.display_messages()

    def display_messages(self):
        # Display messages in the message listbox
        self.msg_list.delete(0, tk.END)
        if self.current_group:
            for message in self.current_group.messages:
                self.msg_list.insert(tk.END, message)

    def get_lng(self):
        return self.lng

    def update_groups(self):
        try:
            mydb = self.get_db_connection()

            if mydb.is_connected():
                mycursor = mydb.cursor()
                sql = f"SELECT chats FROM users WHERE email = '{self.email}'"
                mycursor.execute(sql)
                result = mycursor.fetchone()
                if result is not None:
                    if result[0] != '':
                        chats = result[0].split(",")
                        remove = True #see if a group needs to be removed
                        for chat in chats:
                            if chat != "":
                                flag = False
                                id = chat[-5:]
                                name = chat[:-5]
                                for group in self.groups:
                                    if id == group.id:
                                        flag = True
                                        if name != group.name:
                                            #means that the name was changed
                                            remove = False
                                            group.name = name
                                            for index in range(self.group_listbox.size()):
                                                item_text = self.group_listbox.get(index)
                                                if id in item_text:
                                                    self.group_listbox.delete(index)
                                                    self.group_listbox.insert(index, f"{name}[{id}]")
                                                    break
                                if not flag:
                                    #means that the group is new
                                    remove = False
                                    self.groups.append(Group(name,id))
                                    self.group_listbox.insert(tk.END, f"{name}[{id}]")
                        if remove:
                            #remove a group from the group list
                            for group in self.groups:
                                flag = False
                                for chat in chats:
                                    if chat != "":
                                        id = chat[-5:]
                                        name = chat[:-5]
                                        if group.id == id:
                                            flag = True
                                if not flag:
                                    #the current group is the one we need to remove
                                    #remove from group array
                                    self.groups.remove(group)
                                    #remove from the list of groups
                                    for index in range(self.group_listbox.size()):
                                        item_text = self.group_listbox.get(index)
                                        if group.id in item_text:
                                            # Replace the item if it contains the specific 5-digit number
                                            self.group_listbox.delete(index)
                                            break
                else:
                    print("Problem with connecting to database")
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()

    def receive(self):
        while True:
            try:
                header = self.s.recv(1).decode('utf-8')
                if not header:
                    break

                if header == 'T':
                    message_length = int(self.s.recv(4).decode('utf-8'))
                    msg = self.s.recv(message_length).decode('utf-8')
                    print(msg)
                    list_msg = msg.split(",")
                    group_id = list_msg[1][-5:]

                    if group_id != "00000":
                        for i in self.groups:
                            if i.id == group_id:
                                msg_group = i
                                while self.lng is None:
                                    time.sleep(0.1)

                                message = self.translator.translate(list_msg[0], dest=self.lng).text
                                msg_group.messages.append(message)
                                self.display_messages()
                    else:
                        self.update_groups()
                elif header == 'F':
                    file_name_length = int(self.s.recv(4).decode('utf-8'))
                    file_name = self.s.recv(file_name_length).decode('utf-8')
                    file_size = int(self.s.recv(10).decode('utf-8'))
                    name_group_size = int(self.s.recv(4).decode('utf-8'))
                    name_group = self.s.recv(name_group_size).decode('utf-8')
                    values = name_group.split("]")
                    email = values[0].replace("[","")
                    group_name = values[1].replace("[","")
                    id = values[2].replace("[","")
                    file_data = b""
                    while len(file_data) < file_size:
                        chunk = self.s.recv(1024)
                        if not chunk:
                            break
                        file_data += chunk

                    for group in self.groups:
                        if group.id == id:
                            self.save_file(file_name, file_data,email,group_name,id)
                elif header == 'L':
                    try:
                        message_length = int(self.s.recv(4).decode('utf-8'))
                        msg = self.s.recv(message_length).decode('utf-8')
                        print(msg)
                        print("Received message:", msg)
                        self.open_request_window(msg)
                    except ValueError as ve:
                        print("Error: Invalid message length format:", ve)
                    except UnicodeDecodeError as ude:
                        print("Error: Unable to decode message:", ude)
                    except Exception as e:
                        print("Error receiving message:", e)


            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Error during translation: {e}")

    def open_request_window(self,msg):
        self.request_files_window(msg)

    def add_msg(self, name, id, message):
        # Add a message to the database
        mydb = self.get_db_connection()

        mycursor = mydb.cursor()
        current_time = time.time()

        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
        sql = "INSERT INTO messages (chatid, chatname, time, data) VALUES (%s, %s, %s, %s)"
        values = (id, name, formatted_time, message)
        try:
            mycursor.execute(sql, values)
            mydb.commit()
        except mysql.connector.Error as err:
            print("Error executing SQL query:", err)
        mycursor.close()
        mydb.close()

    def send(self,refresh):
        # Send a text message
        if self.current_group and self.my_msg.get() and not refresh:
            message = f"[{self.email}] {self.my_msg.get()}"
            self.add_msg(self.email, self.current_group.id, self.my_msg.get())
            self.current_group.messages.append(message)
            self.display_messages()
            self.my_msg.set("")
            message_with_group = f"{message},{self.current_group.id}".encode('utf-8')
            message_length = len(message_with_group)
            header = f"T{message_length:04d}".encode('utf-8')
            self.s.sendall(header + message_with_group)

        elif refresh:
            message = f"refresh message"
            message_with_group = message + ",00000"
            message_length = len(message_with_group)
            header = f"T{message_length:04d}"
            self.s.send(bytes(header + message_with_group, "utf8"))
        else:
            messagebox.showerror("","Choose a group before sending a message")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.send_file(file_path)
    def save_file(self, file_name, file_data,email,group_name,id):
        directory = os.path.join("received_files", id)
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_path = os.path.join(directory, file_name)
            with open(file_path, "wb") as file:
                file.write(file_data)
            for group in self.groups:
                if group.id == id:
                    trans = self.translator.translate("file sent", dest=self.lng).text
                    message = f"[{email}]{trans}: {file_name}"
                    group.messages.append(message)
                    self.display_messages()
            messagebox.showinfo("", f"File '{file_name}' received in group {group_name} from user:{email}")
        except Exception as e:
            print("Error saving or broadcasting file:", e)


    def send_file(self, file_path):
        if self.current_group:
            try:
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                file_name_bytes = file_name.encode('utf-8')
                file_name_length = len(file_name_bytes)
                name_and_group = f"[{self.email}][{self.current_group.name}][{self.current_group.id}]".encode('utf-8')
                header = f"F{file_name_length:04d}".encode('utf-8') + file_name_bytes + f"{file_size:010d}".encode('utf-8') + f"{len(name_and_group):04d}".encode('utf-8') + name_and_group
                self.s.sendall(header)

                with open(file_path, 'rb') as file:
                    while (file_data := file.read(1024)):
                        self.s.sendall(file_data)
                trans = self.translator.translate("file sent", dest=self.lng).text
                message = f"[{self.email}]{trans}: {file_name}"
                self.add_msg(self.email, self.current_group.id, message)
                self.current_group.messages.append(message)
                self.display_messages()
                messagebox.showinfo("","File sent successfully!")
            except Exception as e:
                messagebox.showerror("",f"Failed to send file: {e}")
        else:
            messagebox.showerror("","Choose a group before sendind a file")

    def request_file_list(self):
        if self.current_group:
            try:
                message = self.current_group.id
                message_length = len(message)
                header = f"L{message_length:04d}"
                self.s.send(header.encode("utf-8") + message.encode("utf-8"))
            except Exception as e:
                print("Error sending message to client:", e)
        else:
            messagebox.showinfo("","Choose a group to download a file from")

    def request_files_window(self, file_str):
        request_files_window = tk.Toplevel(self.window)
        self.file_listbox = tk.Listbox(request_files_window, width=30)
        self.file_listbox.pack(padx=10, pady=10)
        delimiter = '\0'
        file_list = file_str.split(delimiter)
        for file in file_list:
            if file != "":
                self.file_listbox.insert(tk.END, file)
        self.file_listbox.bind("<Double-Button-1>", lambda event: self.request_file(event, request_files_window))

    def request_file(self, event, request_files_window):
        selected_file_index = self.file_listbox.curselection()
        if selected_file_index:
            file_name = self.file_listbox.get(selected_file_index) + self.current_group.id
            try:
                message_length = len(file_name.encode('utf-8'))
                header = f"L{message_length:04d}"
                self.s.send(bytes(header + file_name, "utf8"))
            except Exception as e:
                print("couldn't send the message because of:", e)
        request_files_window.destroy()

    def run(self):
        self.window.mainloop()

    def group_window(self):
        # Create a window to add a new group
        users_add = []  # users that will be added to group
        global group_popup
        group_popup = tk.Toplevel(self.window)
        Label(group_popup, text="Group name").pack()
        group_name_input = Entry(group_popup)
        group_name_input.pack()

        Label(group_popup, text="Users:").pack()
        print(self.all_users)
        for i, user in enumerate(self.all_users):
            var = tk.BooleanVar()
            users_add.append((user, var))  #  username and associated boolean variable
            checkbox = Checkbutton(group_popup, text=user, variable=var)
            checkbox.pack()

        create_button = Button(group_popup, text="Create Group",
                               command=lambda: self.create_group(group_name_input.get(), users_add))
        create_button.pack(pady=10)

    def create_group(self, group_name, users_add):
        # Create a new group
        selected_users = []
        for user, var in users_add:  # through each user and  boolean variable
            if var.get():  # If the boolean variable is True (checkbox is checked)
                selected_users.append(user)
        emails = []
        for user in selected_users:
            emails.append(user[user.find("(") + 1:len(user) - 1])
        try:
            mydb = self.get_db_connection()

            if mydb.is_connected():
                mycursor = mydb.cursor()
                mycursor.execute("SELECT COUNT(*) FROM chats")
                result = mycursor.fetchone()
                count = result[0]
                id = str(count + 1)
                while len(id) < 5:
                    id = "0" + id
                group_name = group_name
                email_str = ""
                for email in emails:
                    email_str += f"{email},"
                    sql = f"UPDATE users SET chats = CONCAT(chats,',','{group_name + id}') WHERE email = '{email}'"
                    mycursor.execute(sql)

                mycursor.execute(f'''
                            INSERT INTO chats (code,name,emails,admins)
                            VALUES (%s, %s, %s,%s)
                        ''', (id, group_name, email_str, self.email))
                new_group = Group(group_name, id)
                self.groups.append(new_group)
                self.group_listbox.insert(tk.END, f"{group_name}[{id}]")
                mydb.commit()
                group_popup.destroy()
                self.send(True)
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()

    def info_window(self):
        if self.current_group:
            # Open the info window for the current group chat
            mydb = self.get_db_connection()

            curr_id = self.current_group.id
            mycursor = mydb.cursor()
            mycursor.execute(f'''
                SELECT emails,admins FROM chats WHERE code = '{curr_id}'
            ''')
            result = mycursor.fetchone()
            self.user_in_chat = []
            if result is not None:
                print(result)
                if result[0] and result[1]:
                    result_emails = result[0].split(",")
                    result_admins = result[1].split(",")
                    for user in result_emails:
                        if user in result_admins:
                            self.user_in_chat.append(f"{user}[ADMIN]")
                        else:
                            self.user_in_chat.append(user)
                    if self.email not in result_admins:
                        info_popup = tk.Toplevel(self.window)
                        Label(info_popup, text=f"Group name: {self.current_group.name}").pack()
                        Label(info_popup, text="Users:").pack()
                        for user in self.user_in_chat:
                            label = tk.Label(info_popup, text=user)
                            label.pack()

                    else:  # if user is admin
                        admin_window = tk.Toplevel(self.window)
                        group_name_input = Entry(admin_window)
                        group_name_input.pack()
                        change_name_button = Button(admin_window, text="Update Name",
                                                    command=lambda: self.change_group_name(group_name_input.get()))
                        change_name_button.pack(pady=10)
                        self.user_listbox = tk.Listbox(admin_window, width=30)
                        self.user_listbox.pack(padx=10, pady=10)

                        for user in self.user_in_chat:
                            self.user_listbox.insert(tk.END, user)

                        self.user_listbox.bind("<Double-Button-1>", self.show_admin_options)

            mydb.close()
        else:
            messagebox.showinfo("", "Choose a group")


    def show_admin_options(self,event):
        # Show admin options
        selected_user = ""
        selected_user_index = self.user_listbox.curselection()
        if selected_user_index:
            selected_user = self.user_in_chat[selected_user_index[0]]
        if self.email not in selected_user:
            options_window = Toplevel(self.window)
            options_window.geometry("100x100")
            # Button to remove user
            remove_button = Button(options_window, text="Remove", command=lambda: self.remove_user(selected_user))
            remove_button.pack(pady=5)
            if "[ADMIN]" in selected_user:
                admin_button = Button(options_window, text="Remove Admin", command=lambda: self.remove_admin(selected_user))
                admin_button.pack(pady=5)
            else:
                # Button to give admin privileges
                admin_button = Button(options_window, text="Give Admin", command=lambda: self.give_admin(selected_user))
                admin_button.pack(pady=5)
        else:
            messagebox.showinfo("Sorry", "you can't edit yourself")

    def remove_user(self, selected_user):
        # Remove a user from the group chat
        try:
            mydb = self.get_db_connection()

            mycursor = mydb.cursor()
            email = selected_user[selected_user.find('(') + 1:selected_user.find(')')]
            # Take chat name from table users
            mycursor.execute(f"SELECT chats FROM users WHERE email = '{email}'")
            result = mycursor.fetchone()
            chats = result[0]
            chats = chats.replace(f"{self.current_group.name}{self.current_group.id}", "")
            mycursor.execute(f"UPDATE users SET chats = '{chats}' WHERE email = '{email}'")

            # Take user from table chats
            mycursor.execute(f"SELECT emails,admins FROM chats WHERE code = '{self.current_group.id}'")
            result2 = mycursor.fetchone()
            emails = result2[0]
            admins = result2[1]
            emails = emails.replace(f"{email},", "")
            admins = admins.replace(f"{email},", "")
            mycursor.execute(f"UPDATE chats SET emails = '{emails}',admins = '{admins}' WHERE code = '{self.current_group.id}'")
            mydb.commit()
            mycursor.close()

            # send broaddcast message with id being 00000 so it updates the group list
            self.send(True)

            # remove user from group user list
            self.user_in_chat.remove(selected_user)
            self.update_user_listbox()
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()
            tk.messagebox.showinfo("Success", f"{selected_user} has been removed from the group.")

    def give_admin(self, selected_user):
        # Give admin privileges to a user
        try:
            mydb = self.get_db_connection()

            email = selected_user[selected_user.find('(') + 1:selected_user.find(')')]
            mycursor = mydb.cursor()
            mycursor.execute(f"UPDATE chats SET admins = CONCAT(admins,',','{email}') WHERE code = '{self.current_group.id}'")
            for index, user in enumerate(self.user_in_chat):
                if user == selected_user:
                    self.user_in_chat[index] += "[ADMIN]"
                    break
            mycursor.close()
            mydb.commit()
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()
            tk.messagebox.showinfo("Success", f"{selected_user} is now an admin.")

    def remove_admin(self, selected_user):
        # Remove admin privileges from a user
        try:
            mydb = self.get_db_connection()

            email = selected_user[selected_user.find('(') + 1:selected_user.find(')')]
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT admins FROM chats WHERE code = '{self.current_group.id}'")
            result = mycursor.fetchone()
            admins = result[0].split(",")
            admins.remove(email)
            admins = ','.join(admins)
            mycursor.execute(f"UPDATE chats SET admins = '{admins}' WHERE code = '{self.current_group.id}'")
            for index, user in enumerate(self.user_in_chat):
                if user == selected_user:
                    self.user_in_chat[index] = selected_user.replace("[ADMIN]", "")
                    break
            mycursor.close()
            mydb.commit()
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()
            tk.messagebox.showinfo("Success", f"{selected_user} is no longer an admin.")

    def update_user_listbox(self):
        # Update the user listbox
        self.user_listbox.delete(0, tk.END)
        for user in self.user_in_chat:
            self.user_listbox.insert(tk.END, user)

    def change_group_name(self, new_group_name):
        # Change the name of the current group
        try:
            mydb = self.get_db_connection()
            mycursor = mydb.cursor()
            mycursor.execute(f"UPDATE chats SET name = '{new_group_name}' WHERE code = '{self.current_group.id}'")
            emails = []
            for user in self.all_users:
                emails.append(user[user.find("(") + 1:len(user) - 1])
            for email in emails:
                mycursor.execute(f"SELECT chats FROM users WHERE email ='{email}'")
                result = mycursor.fetchone()
                chats = result[0].split(",")
                id = self.current_group.id
                for i in range(len(chats)):
                    if id in chats[i]:
                        chats[i] = f"{new_group_name}{id}"
                        updated_chats = ",".join(chats)
                        mycursor.execute(f"UPDATE users SET chats = '{updated_chats}' WHERE email = '{email}'")

            mycursor.close()
            mydb.commit()
            self.current_group.name = new_group_name
            for index in range(self.group_listbox.size()):
                item_text = self.group_listbox.get(index)
                if id in item_text:
                    # Replace the item if it contains the specific 5-digit number
                    self.group_listbox.delete(index)
                    self.group_listbox.insert(index, f"{new_group_name}[{id}]")
                    break
            self.send(True)
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
        finally:
            if mydb.is_connected():
                mydb.close()
            tk.messagebox.showinfo("Success", "Group name updated successfully.")



