import mysql.connector as mc
import customtkinter as ctk
from tkinter import messagebox
from tabulate import tabulate

# Database connection function
def connect_db():
    return mc.connect(host='localhost', user='root', password='', database='lms')

# Function for Login Validation
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "ADMIN" and password == "ADMIN123":
        messagebox.showinfo("Login Successful", "Welcome to the Library Management System!")
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

# CRUD operations
def display_books():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    con.close()
    output = tabulate(data, headers=['BOOKID', 'BOOKNAME', 'AUTHOR', 'CATEGORY'], tablefmt='plain')
    messagebox.showinfo("Books", output)

def insert_book():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    bookname = bookname_entry.get()
    author = author_entry.get()
    category = category_entry.get()
    sql = "INSERT INTO books (bookid, bookname, author, category) VALUES (%s, %s, %s, %s)"
    try:
        cur.execute(sql, (bookid, bookname, author, category))
        con.commit()
        messagebox.showinfo("Success", "Book inserted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def update_book():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    new_name = bookname_entry.get()
    sql = "UPDATE books SET bookname = %s WHERE bookid = %s"
    try:
        cur.execute(sql, (new_name, bookid))
        con.commit()
        messagebox.showinfo("Success", "Book updated successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def delete_book():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    sql = "DELETE FROM books WHERE bookid = %s"
    try:
        cur.execute(sql, (bookid,))
        con.commit()
        messagebox.showinfo("Success", "Book deleted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

# GUI Windows
def open_main_window():
    global bookid_entry, bookname_entry, author_entry, category_entry
    
    main_window = ctk.CTk()
    main_window.title("Library Management System")
    main_window.geometry("400x400")

    # Book Details
    ctk.CTkLabel(main_window, text="Book ID").grid(row=0, column=0, padx=10, pady=10)
    bookid_entry = ctk.CTkEntry(main_window)
    bookid_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(main_window, text="Book Name").grid(row=1, column=0, padx=10, pady=10)
    bookname_entry = ctk.CTkEntry(main_window)
    bookname_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(main_window, text="Author").grid(row=2, column=0, padx=10, pady=10)
    author_entry = ctk.CTkEntry(main_window)
    author_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(main_window, text="Category").grid(row=3, column=0, padx=10, pady=10)
    category_entry = ctk.CTkEntry(main_window)
    category_entry.grid(row=3, column=1, padx=10, pady=10)

    # CRUD Buttons
    ctk.CTkButton(main_window, text="Display Books", command=display_books).grid(row=4, column=0, padx=10, pady=10)
    ctk.CTkButton(main_window, text="Insert Book", command=insert_book).grid(row=4, column=1, padx=10, pady=10)
    ctk.CTkButton(main_window, text="Update Book", command=update_book).grid(row=5, column=0, padx=10, pady=10)
    ctk.CTkButton(main_window, text="Delete Book", command=delete_book).grid(row=5, column=1, padx=10, pady=10)

    main_window.mainloop()

# Login Window
login_window = ctk.CTk()
login_window.title("Login")
login_window.geometry("300x200")

ctk.CTkLabel(login_window, text="Username").grid(row=0, column=0, padx=10, pady=10)
username_entry = ctk.CTkEntry(login_window)
username_entry.grid(row=0, column=1, padx=10, pady=10)

ctk.CTkLabel(login_window, text="Password").grid(row=1, column=0, padx=10, pady=10)
password_entry = ctk.CTkEntry(login_window, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

ctk.CTkButton(login_window, text="Login", command=login).grid(row=2, column=1, padx=10, pady=10)

login_window.mainloop()
