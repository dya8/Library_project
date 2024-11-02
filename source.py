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
        open_main_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

# Main Menu
def open_main_menu():
    main_menu = ctk.CTk()
    main_menu.title("Main Menu")
    main_menu.geometry("400x300")

    ctk.CTkLabel(main_menu, text="Select Table").pack(pady=10)
    ctk.CTkButton(main_menu, text="Books", command=open_books_window).pack(pady=5)
    ctk.CTkButton(main_menu, text="Students", command=open_students_window).pack(pady=5)
    ctk.CTkButton(main_menu, text="Current Status", command=open_current_status_window).pack(pady=5)
    ctk.CTkButton(main_menu, text="Librarians", command=open_librarians_window).pack(pady=5)
    ctk.CTkButton(main_menu, text="Fine Calculation", command=open_fine_window).pack(pady=5)

    main_menu.mainloop()




# Fine Table Management Functions
def open_fine_window():
    global bookid_entry, studentid_entry, no_of_days_delayed_entry, fine_id_entry

    fine_window = ctk.CTk()
    fine_window.title("Manage Fine")
    fine_window.geometry("400x400")

    # Fine Details
   
    ctk.CTkLabel(fine_window, text="Student ID").grid(row=1, column=0, padx=10, pady=10)
    studentid_entry = ctk.CTkEntry(fine_window)
    studentid_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(fine_window, text="Fine ID").grid(row=2, column=0, padx=10, pady=10)  # Changed row to 2
    fine_id_entry = ctk.CTkEntry(fine_window)
    fine_id_entry.grid(row=2, column=1, padx=10, pady=10)  # Changed row to 2
    
    # CRUD Buttons
    ctk.CTkButton(fine_window, text="Display Fines", command=display_fines).grid(row=5, column=0, padx=10, pady=10)
    ctk.CTkButton(fine_window, text="Insert Fine", command=insert_fine).grid(row=5, column=1, padx=10, pady=10)
    ctk.CTkButton(fine_window, text="Update Fine", command=update_fine).grid(row=6, column=0, padx=10, pady=10)
    ctk.CTkButton(fine_window, text="Delete Fine", command=delete_fine).grid(row=6, column=1, padx=10, pady=10)

    fine_window.mainloop()


def display_fines():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM Fine")
    data = cur.fetchall()
    con.close()
    output = tabulate(data, headers=['BOOKID', 'STUDENTID', 'NO_OF_DAYS_DELAYED', 'FINE_AMOUNT', 'FINE_STATUS'], tablefmt='plain')#REVIEW11
    messagebox.showinfo("Fines", output)

def insert_fine():
    global fine_id_entry
    con = connect_db()
    cur = con.cursor()

    # Only Student ID is entered manually
    studentid = int(studentid_entry.get())
    fine_id_entry = int(fine_id_entry.get())

    # Retrieve the Book ID and No of Days Delayed for the given Student ID
    fetch_sql = "SELECT Bookid, NO_OF_DAYS_DELAYED FROM Current_status WHERE Studid = %s"
    cur.execute(fetch_sql, (studentid,))
    result = cur.fetchone()

    if result:
        bookid, no_days_delayed = result
        
        # Fine calculation logic
        fine_per_day = 50
        fine_amount = fine_per_day + (no_days_delayed - 1) * 10 if no_days_delayed > 0 else 0
        
        # Set fine status based on fine amount
        if fine_amount > 0:
            fine_status = "Pending"
        else:
            fine_status = "No Fine"

        # Insert fine details into Fine table
        insert_sql = "INSERT INTO Fine (fine_id, bookid, studid, no_of_days_delayed, fine_amount, fine_status) VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            cur.execute(insert_sql, (fine_id_entry, bookid, studentid, no_days_delayed, fine_amount, fine_status))
            con.commit()
            messagebox.showinfo("Success", "Fine inserted successfully!")
        except Exception as e:
            con.rollback()
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "No record found for this Student ID in Current_status.")

    con.close()

def update_fine():
    global fine_id_entry
    con = connect_db()
    cur = con.cursor()

    # Retrieve values from entries
    studentid = int(studentid_entry.get())
    fine_id = int(fine_id_entry.get())  # Get fine ID from the entry

    # Fetch the fine amount to determine the status
    fetch_fine_sql = "SELECT fine_amount FROM Fine WHERE fine_id = %s AND studid = %s"
    cur.execute(fetch_fine_sql, (fine_id, studentid))
    result = cur.fetchone()

    if result:
        fine_amount = result[0]

        # Determine fine status based on fine amount
        if fine_amount > 0:
            fine_status = "PAID"
        else:
            fine_status = "No Fine"

        # Update fine status
        update_sql = "UPDATE Fine SET fine_status = %s WHERE fine_id = %s AND studid = %s"
        try:
            cur.execute(update_sql, (fine_status, fine_id, studentid))
            con.commit()
            
            # Check if any row was updated
            if cur.rowcount > 0:
                messagebox.showinfo("Success", f"Fine updated to '{fine_status}' successfully!")
            else:
                messagebox.showwarning("Warning", "No fine found for the given Fine ID and Student ID.")
        except Exception as e:
            con.rollback()
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "No fine found for the given Fine ID and Student ID.")

    con.close()


def delete_fine():

    con = connect_db()
    cur = con.cursor()

    studentid = int(studentid_entry.get())
    sql = "DELETE FROM Fine WHERE studid = %s"
    try:
        
        cur.execute(sql, (studentid,))
        con.commit()
        messagebox.showinfo("Success", "Fine deleted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()


    # Confirmation message
    messagebox.showinfo("Fine Calculation", "Fine records have been updated in the database.")
    con.close()

# CRUD operation window for Books
def open_books_window():
    global bookid_entry, bookname_entry, author_entry, category_entry
    
    books_window = ctk.CTk()
    books_window.title("Manage Books")
    books_window.geometry("400x400")

    # Book Details
    ctk.CTkLabel(books_window, text="Book ID").grid(row=0, column=0, padx=10, pady=10)
    bookid_entry = ctk.CTkEntry(books_window)
    bookid_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(books_window, text="Book Name").grid(row=1, column=0, padx=10, pady=10)
    bookname_entry = ctk.CTkEntry(books_window)
    bookname_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(books_window, text="Author").grid(row=2, column=0, padx=10, pady=10)
    author_entry = ctk.CTkEntry(books_window)
    author_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(books_window, text="Category").grid(row=3, column=0, padx=10, pady=10)
    category_entry = ctk.CTkEntry(books_window)
    category_entry.grid(row=3, column=1, padx=10, pady=10)

    # CRUD Buttons
    ctk.CTkButton(books_window, text="Display Books", command=display_books).grid(row=4, column=0, padx=10, pady=10)
    ctk.CTkButton(books_window, text="Insert Book", command=insert_book).grid(row=4, column=1, padx=10, pady=10)
    ctk.CTkButton(books_window, text="Update Book", command=update_book).grid(row=5, column=0, padx=10, pady=10)
    ctk.CTkButton(books_window, text="Delete Book", command=delete_book).grid(row=5, column=1, padx=10, pady=10)

    books_window.mainloop()

# CRUD operation functions for Students, Current Status, Librarians, and Fines (similar to open_books_window)
def open_students_window():

    global studid_entry, studname_entry, class_entry
    
    students_window = ctk.CTk()
    students_window.title("Manage Students")
    students_window.geometry("400x400")

    # Student Details
    ctk.CTkLabel(students_window, text="Student ID").grid(row=0, column=0, padx=10, pady=10)
    studid_entry = ctk.CTkEntry(students_window)
    studid_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(students_window, text="Student Name").grid(row=1, column=0, padx=10, pady=10)
    studname_entry = ctk.CTkEntry(students_window)
    studname_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(students_window, text="Class").grid(row=2, column=0, padx=10, pady=10)
    class_entry = ctk.CTkEntry(students_window)
    class_entry.grid(row=2, column=1, padx=10, pady=10)

    # CRUD Buttons
    ctk.CTkButton(students_window, text="Display Students", command=display_students).grid(row=3, column=0, padx=10, pady=10)
    ctk.CTkButton(students_window, text="Insert Student", command=insert_student).grid(row=3, column=1, padx=10, pady=10)
    ctk.CTkButton(students_window, text="Update Student", command=update_student).grid(row=4, column=0, padx=10, pady=10)
    ctk.CTkButton(students_window, text="Delete Student", command=delete_student).grid(row=4, column=1, padx=10, pady=10)

    students_window.mainloop()

# CRUD functions for Student
def display_students():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM student")
    data = cur.fetchall()
    con.close()
    output = tabulate(data, headers=['STUDID', 'STUDNAME', 'CLASS'], tablefmt='plain')
    messagebox.showinfo("Student", output)

def insert_student():
    con = connect_db()
    cur = con.cursor()
    studid = int(studid_entry.get())
    studname = studname_entry.get()
    class_value = class_entry.get()
    sql = "INSERT INTO student (studid, studname, class) VALUES (%s, %s, %s)"
    try:
        cur.execute(sql, (studid, studname, class_value))
        con.commit()
        messagebox.showinfo("Success", "Student inserted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def update_student():
    con = connect_db()
    cur = con.cursor()
    studid = int(studid_entry.get())
    new_name = studname_entry.get()
    new_class = class_entry.get()
    sql = "UPDATE student SET studname = %s, class = %s WHERE studid = %s"
    try:
        cur.execute(sql, (new_name, new_class, studid))
        con.commit()
        messagebox.showinfo("Success", "Student updated successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def delete_student():
    con = connect_db()
    cur = con.cursor()
    studid = int(studid_entry.get())
    sql = "DELETE FROM student WHERE studid = %s"
    try:
        cur.execute(sql, (studid,))
        con.commit()
        messagebox.showinfo("Success", "Student deleted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()





# CRUD operations for Books
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
# Functions for Librarian Management
def open_librarians_window():
    global librarian_id_entry, librarian_name_entry, email_entry
    
    librarians_window = ctk.CTk()
    librarians_window.title("Manage Librarians")
    librarians_window.geometry("400x400")

    # Librarian Details
    ctk.CTkLabel(librarians_window, text="Librarian ID").grid(row=0, column=0, padx=10, pady=10)
    librarian_id_entry = ctk.CTkEntry(librarians_window)
    librarian_id_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(librarians_window, text="Librarian Name").grid(row=1, column=0, padx=10, pady=10)
    librarian_name_entry = ctk.CTkEntry(librarians_window)
    librarian_name_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(librarians_window, text="Email").grid(row=2, column=0, padx=10, pady=10)
    email_entry = ctk.CTkEntry(librarians_window)
    email_entry.grid(row=2, column=1, padx=10, pady=10)

    # CRUD Buttons
    ctk.CTkButton(librarians_window, text="Display Librarians", command=display_librarians).grid(row=3, column=0, padx=10, pady=10)
    ctk.CTkButton(librarians_window, text="Insert Librarian", command=insert_librarian).grid(row=3, column=1, padx=10, pady=10)
    ctk.CTkButton(librarians_window, text="Update Librarian", command=update_librarian).grid(row=4, column=0, padx=10, pady=10)
    ctk.CTkButton(librarians_window, text="Delete Librarian", command=delete_librarian).grid(row=4, column=1, padx=10, pady=10)

    librarians_window.mainloop()

def display_librarians():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM librarian")
    data = cur.fetchall()
    con.close()
    output = tabulate(data, headers=['LIBRARIAN_ID', 'LIBRARIAN_NAME', 'EMAIL'], tablefmt='plain')
    messagebox.showinfo("Librarian", output)

def insert_librarian():
    con = connect_db()
    cur = con.cursor()
    librarian_id = int(librarian_id_entry.get())
    librarian_name = librarian_name_entry.get()
    email = email_entry.get()
    sql = "INSERT INTO librarian (librarian_id, librarian_name, email) VALUES (%s, %s, %s)"
    try:
        cur.execute(sql, (librarian_id, librarian_name, email))
        con.commit()
        messagebox.showinfo("Success", "Librarian inserted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def update_librarian():
    con = connect_db()
    cur = con.cursor()
    librarian_id = int(librarian_id_entry.get())
    new_name = librarian_name_entry.get()
    new_email = email_entry.get()
    sql = "UPDATE librarian SET librarian_name = %s, email = %s WHERE librarian_id = %s"
    try:
        cur.execute(sql, (new_name, new_email, librarian_id))
        con.commit()
        messagebox.showinfo("Success", "Librarian updated successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def delete_librarian():
    con = connect_db()
    cur = con.cursor()
    librarian_id = int(librarian_id_entry.get())
    sql = "DELETE FROM librarian WHERE librarian_id = %s"
    try:
        cur.execute(sql, (librarian_id,))
        con.commit()
        messagebox.showinfo("Success", "Librarian deleted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()


 # Functions for Current Status Management
def open_current_status_window():
    global bookid_entry, studid_entry, bookname_entry, issued_date_entry, received_date_entry, current_status_entry, no_of_days_delayed_entry
    
    current_status_window = ctk.CTk()
    current_status_window.title("Manage Current Status")
    current_status_window.geometry("500x500")

    # Current Status Details
    ctk.CTkLabel(current_status_window, text="Book ID").grid(row=0, column=0, padx=10, pady=10)
    bookid_entry = ctk.CTkEntry(current_status_window)
    bookid_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="Student ID").grid(row=1, column=0, padx=10, pady=10)
    studid_entry = ctk.CTkEntry(current_status_window)
    studid_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="Book Name").grid(row=2, column=0, padx=10, pady=10)
    bookname_entry = ctk.CTkEntry(current_status_window)
    bookname_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="Issued Date").grid(row=3, column=0, padx=10, pady=10)
    issued_date_entry = ctk.CTkEntry(current_status_window)
    issued_date_entry.grid(row=3, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="Received Date").grid(row=4, column=0, padx=10, pady=10)
    received_date_entry = ctk.CTkEntry(current_status_window)
    received_date_entry.grid(row=4, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="Current Status").grid(row=5, column=0, padx=10, pady=10)
    current_status_entry = ctk.CTkEntry(current_status_window)
    current_status_entry.grid(row=5, column=1, padx=10, pady=10)

    ctk.CTkLabel(current_status_window, text="No. of Days Delayed").grid(row=6, column=0, padx=10, pady=10)
    no_of_days_delayed_entry = ctk.CTkEntry(current_status_window)
    no_of_days_delayed_entry.grid(row=6, column=1, padx=10, pady=10)

    # CRUD Buttons
    ctk.CTkButton(current_status_window, text="Display Current Status", command=display_current_status).grid(row=7, column=0, padx=10, pady=10)
    ctk.CTkButton(current_status_window, text="Insert Status", command=insert_current_status).grid(row=7, column=1, padx=10, pady=10)
    ctk.CTkButton(current_status_window, text="Update Status", command=update_current_status).grid(row=8, column=0, padx=10, pady=10)
    ctk.CTkButton(current_status_window, text="Delete Status", command=delete_current_status).grid(row=8, column=1, padx=10, pady=10)

    current_status_window.mainloop()

def display_current_status():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM current_status")
    data = cur.fetchall()
    con.close()
    output = tabulate(data, headers=['BOOKID', 'STUDID', 'BOOKNAME', 'ISSUED_DATE', 'RECEIVED_DATE', 'CURRENT_STATUS', 'NO_OF_DAYS_DELAYED'], tablefmt='plain')
    messagebox.showinfo("Current Status", output)

def insert_current_status():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    studid = int(studid_entry.get())
    bookname = bookname_entry.get()
    issued_date = issued_date_entry.get()
    received_date = received_date_entry.get()
    current_status = current_status_entry.get()
    no_of_days_delayed = int(no_of_days_delayed_entry.get())
    sql = "INSERT INTO current_status (bookid, studid, bookname, issued_date, received_date, current_status, no_of_days_delayed) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(sql, (bookid, studid, bookname, issued_date, received_date, current_status, no_of_days_delayed))
        con.commit()
        messagebox.showinfo("Success", "Status inserted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def update_current_status():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    studid = int(studid_entry.get())
    new_status = current_status_entry.get()
    new_received_date = received_date_entry.get()
    new_no_of_days_delayed = int(no_of_days_delayed_entry.get())
    sql = "UPDATE current_status SET current_status = %s, received_date = %s, no_of_days_delayed = %s WHERE bookid = %s AND studid = %s"
    try:
        cur.execute(sql, (new_status, new_received_date, new_no_of_days_delayed, bookid, studid))
        con.commit()
        messagebox.showinfo("Success", "Status updated successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

def delete_current_status():
    con = connect_db()
    cur = con.cursor()
    bookid = int(bookid_entry.get())
    studid = int(studid_entry.get())
    sql = "DELETE FROM current_status WHERE bookid = %s AND studid = %s"
    try:
        cur.execute(sql, (bookid, studid))
        con.commit()
        messagebox.showinfo("Success", "Status deleted successfully!")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", str(e))
    con.close()

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