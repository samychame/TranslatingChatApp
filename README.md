# Chat Translation App

This is a chat application built with Python that allows users to send messages, which are automatically translated into their preferred language.

## Features
- Real-time messaging
- Automatic language translation using Google Translate API
- Group chat support
- File sharing
- User authentication (Login/Register)

## Requirements
Ensure you have the following installed:

- Python 3.x
- MySQL Database
- Required Python libraries (install using the command below)

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Running the Application

### 1. Start the Server
```sh
python server.py
```

### 2. Run the Login/Register Interface
```sh
python login.py
```

Once a user logs in, they will be redirected to the chat application.

## Database Setup
Create a MySQL database and execute the following SQL commands:
```sql
CREATE DATABASE project;
USE project;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    chats TEXT
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chatid VARCHAR(10),
    chatname VARCHAR(255),
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data TEXT
);
```



## Author
Developed by Samy Chame

