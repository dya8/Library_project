import mysql.connector as mc
import customtkinter as ctk
from tkinter import messagebox, Toplevel, PhotoImage, Tk, Canvas
import tkinter.font as tkfont
from PIL import Image, ImageTk
from tabulate import tabulate


# Database connection function
def connect_db():
    return mc.connect(host='localhost', user='root', password='', database='lms')
def display_fines():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM Fine")
        data = cur.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return
    finally:
        con.close()

    # Create a new window for displaying the fine table
    fines_window = ctk.CTkToplevel()
    fines_window.title("Fines List")
    fines_window.geometry("600x400")

    # Prepare the table output
    output = tabulate(data, headers=['BOOKID', 'STUDENTID', 'NO_OF_DAYS_DELAYED', 'FINE_AMOUNT', 'FINE_STATUS'], tablefmt='grid')

    # Create a Textbox to display the output
    text_box = ctk.CTkTextbox(fines_window, width=580, height=350, fg_color="#061132", border_color="#cccccc")
    text_box.pack(pady=10)

    # Insert the table output into the textbox
    text_box.insert("1.0", output)  
    text_box.configure(state="disabled")  # Disable editing of the textbox

    # Add a close button
    close_button = ctk.CTkButton(fines_window, text="Close", command=fines_window.destroy)
    close_button.pack(pady=(0, 10))

    fines_window.mainloop()

def insert_fine(studentid_entry, fine_id_entry):
    try:
        # Get student ID and fine ID from entry widgets
        studentid = int(studentid_entry.get())
        fine_id = int(fine_id_entry.get())

        con = connect_db()
        cur = con.cursor()

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
            fine_status = "Pending" if fine_amount > 0 else "No Fine"

            # Insert fine details into Fine table
            insert_sql = "INSERT INTO Fine (fine_id, bookid, studid, no_of_days_delayed, fine_amount, fine_status) VALUES (%s, %s, %s, %s, %s, %s)"
            try:
                cur.execute(insert_sql, (fine_id, bookid, studentid, no_days_delayed, fine_amount, fine_status))
                con.commit()
                messagebox.showinfo("Success", "Fine inserted successfully!")
            except Exception as e:
                con.rollback()
                messagebox.showerror("Error", f"Error inserting fine: {str(e)}")
        else:
            messagebox.showerror("Error", "No record found for this Student ID in Current_status.")
    
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values for Student ID and Fine ID.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    finally:
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
    

def open_fine_window():
    global bookid_entry, studentid_entry, no_of_days_delayed_entry, fine_amount_entry, fine_status_entry, fine_status_label

    # Create the main window
    fine_window = ctk.CTk()
    fine_window.title("Manage Fine")
    fine_window.geometry("1000x600")
    fine_window.configure(fg_color="#061132")

    # Frame for Fine Details
    details_frame = ctk.CTkFrame(fine_window, width=800, height=450, fg_color="#FFFFFF", corner_radius=10)
    details_frame.pack(padx=20, pady=20)

    # Label and Entry styling
    label_style = {
        "text_color": "#000000",
        "font": ("Arial", 18, "bold")
    }
    entry_style = {
        "width": 350,
        "height": 40,
        "fg_color": "#f0f0f0",
        "border_color": "#cccccc",
        "border_width": 2,
        "corner_radius": 5,
        "text_color":"black"
    }

    # Book ID
    ctk.CTkLabel(details_frame, text="Book ID", **label_style).grid(row=0, column=0, padx=20, pady=15, sticky="e")
    bookid_entry = ctk.CTkEntry(details_frame, **entry_style)
    bookid_entry.grid(row=0, column=1, padx=20, pady=15, sticky="w")

    # Student ID
    ctk.CTkLabel(details_frame, text="Student ID", **label_style).grid(row=1, column=0, padx=20, pady=15, sticky="e")
    studentid_entry = ctk.CTkEntry(details_frame, **entry_style)
    studentid_entry.grid(row=1, column=1, padx=20, pady=15, sticky="w")

    # No of Days Delayed
    ctk.CTkLabel(details_frame, text="No of Days Delayed", **label_style).grid(row=2, column=0, padx=20, pady=15, sticky="e")
    no_of_days_delayed_entry = ctk.CTkEntry(details_frame, **entry_style)
    no_of_days_delayed_entry.grid(row=2, column=1, padx=20, pady=15, sticky="w")

    # Fine Status (Initially hidden)
    fine_status_label = ctk.CTkLabel(details_frame, text="Fine Status", **label_style)
    fine_status_label.grid(row=4, column=0, padx=20, pady=15, sticky="e")
    fine_status_entry = ctk.CTkEntry(details_frame, **entry_style)
    fine_status_entry.grid(row=4, column=1, padx=20, pady=15, sticky="w")

    fine_status_label.grid_forget()  # Hide the label initially
    fine_status_entry.grid_forget()  # Hide the entry initially

    # Frame for CRUD Buttons
    buttons_frame = ctk.CTkFrame(fine_window, fg_color="#5CE1E6")
    buttons_frame.pack(pady=(10, 20))

    # Button styling
    button_style = {
        "width": 150,
        "height": 60,
        "fg_color": "#2a9d8f",
        "hover_color": "#21867a",
        "border_color": "#f55b96",
        "text_color": "white",
        "font": ("Arial", 16, "bold")
    }

    # CRUD Buttons
    ctk.CTkButton(buttons_frame, text="Display Fines", command=display_fines, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Insert Fine", command=insert_fine, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Update Fine", command=lambda: toggle_fine_status_field(True), **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Delete Fine", command=delete_fine, **button_style).pack(side="left", padx=10, pady=10)

    fine_window.mainloop()

# Function to toggle visibility of Fine Status label and entry field when updating fine
def toggle_fine_status_field(show):
    if show:
        fine_status_label.grid(row=4, column=0, padx=20, pady=15, sticky="e")  # Show the label
        fine_status_entry.grid(row=4, column=1, padx=20, pady=15, sticky="w")  # Show the entry
    else:
        fine_status_label.grid_forget()  # Hide the label
        fine_status_entry.grid_forget()  # Hide the entry
        
def display_librarians():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM librarian")
        data = cur.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return
    finally:
        con.close()

    # Create a new window for displaying the table
    librarians_window = ctk.CTkToplevel()
    librarians_window.title("Librarians List")
    librarians_window.geometry("600x400")

    # Prepare the table output
    output = tabulate(data, headers=['LIBRARIAN_ID', 'LIBRARIAN_NAME', 'EMAIL'], tablefmt='grid')

    # Create a Textbox to display the output
    text_box = ctk.CTkTextbox(librarians_window, width=580, height=350, fg_color="#061132", border_color="#cccccc")
    text_box.pack(pady=10)

    # Insert the table output into the textbox
    text_box.insert("1.0", output)  
    text_box.configure(state="disabled")  # Disable editing of the textbox

    # Add a close button
    close_button = ctk.CTkButton(librarians_window, text="Close", command=librarians_window.destroy)
    close_button.pack(pady=(0, 10))

    librarians_window.mainloop()

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

def open_librarians_window():
    global librarian_id_entry, librarian_name_entry, email_entry

    # Create the main window
    librarians_window = ctk.CTk()
    librarians_window.title("Manage Librarians")
    librarians_window.geometry("1000x600")
    librarians_window.configure(fg_color="#061132")

    # Frame for Librarian Details
    details_frame = ctk.CTkFrame(librarians_window, width=800, height=450, fg_color="#FFFFFF", corner_radius=10)
    details_frame.pack(padx=20, pady=20)

    # Label and Entry styling
    label_style = {
        "text_color": "#000000",
        "font": ("Arial", 18, "bold")
    }
    entry_style = {
        "width": 350,
        "height": 40,
        "fg_color": "#f0f0f0",
        "border_color": "#cccccc",
        "border_width": 2,
        "corner_radius": 5,
        "text_color":"black"
    }

    # Librarian ID
    ctk.CTkLabel(details_frame, text="Librarian ID", **label_style).grid(row=0, column=0, padx=20, pady=15, sticky="e")
    librarian_id_entry = ctk.CTkEntry(details_frame, **entry_style)
    librarian_id_entry.grid(row=0, column=1, padx=20, pady=15, sticky="w")

    # Librarian Name
    ctk.CTkLabel(details_frame, text="Librarian Name", **label_style).grid(row=1, column=0, padx=20, pady=15, sticky="e")
    librarian_name_entry = ctk.CTkEntry(details_frame, **entry_style)
    librarian_name_entry.grid(row=1, column=1, padx=20, pady=15, sticky="w")

    # Email
    ctk.CTkLabel(details_frame, text="Email", **label_style).grid(row=2, column=0, padx=20, pady=15, sticky="e")
    email_entry = ctk.CTkEntry(details_frame, **entry_style)
    email_entry.grid(row=2, column=1, padx=20, pady=15, sticky="w")

    # Frame for CRUD Buttons
    buttons_frame = ctk.CTkFrame(librarians_window, fg_color="#5CE1E6")
    buttons_frame.pack(pady=(10, 20))

    # Button styling
    button_style = {
        "width": 150,
        "height": 60,
        "fg_color": "#2a9d8f",
        "hover_color": "#21867a",
        "border_color": "#f55b96",
        "text_color": "white",
        "font": ("Arial", 16, "bold")
    }

    # CRUD Buttons
    ctk.CTkButton(buttons_frame, text="Display Librarians", command=display_librarians, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Insert Librarian", command=insert_librarian, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Update Librarian", command=update_librarian, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Delete Librarian", command=delete_librarian, **button_style).pack(side="left", padx=10, pady=10)

    librarians_window.mainloop()

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
def display_students():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM student")
        data = cur.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return
    finally:
        con.close()

    # Create a new window for displaying the table
    students_window = ctk.CTkToplevel()
    students_window.title("Students List")
    students_window.geometry("600x400")

    # Prepare the table output
    output = tabulate(data, headers=['STUDID', 'STUDNAME', 'CLASS'], tablefmt='grid')

    # Create a Textbox to display the output
    text_box = ctk.CTkTextbox(students_window, width=580, height=350, fg_color="#061132", border_color="#cccccc")
    text_box.pack(pady=10)

    # Insert the table output into the textbox
    text_box.insert("1.0", output)  
    text_box.configure(state="disabled")  # Disable editing of the textbox

    # Add a close button
    close_button = ctk.CTkButton(students_window, text="Close", command=students_window.destroy)
    close_button.pack(pady=(0, 10))

    students_window.mainloop()

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



def open_students_window():
    global studid_entry, studname_entry, class_entry

    # Create the main window
    students_window = ctk.CTk()
    students_window.title("Manage Students")
    students_window.geometry("1000x600")
    students_window.configure(fg_color="#061132")

    # Create a frame for the student details section
    details_frame = ctk.CTkFrame(students_window, width=900, height=500, fg_color="#FFFFFF", corner_radius=10)
    details_frame.grid(row=0, column=0, padx=210, pady=50, sticky="nsew")

    # Heading
    heading_label = ctk.CTkLabel(
        details_frame,
        text="Enter Student Details",
        font=("Arial", 24, "bold"),
        text_color="#000000"
    )
    heading_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

    # Label and Entry style
    label_style = {
        "text_color": "#000000",
        "font": ("Arial", 18, "bold")
    }
    entry_style = {
        "width": 400,
        "height": 40,
        "fg_color": "#f0f0f0",
        "border_color": "#cccccc",
        "border_width": 2,
        "corner_radius": 5,
        "text_color":"black"
    }

    # Labels and Entries for Student Details
    ctk.CTkLabel(details_frame, text="Student ID", **label_style).grid(row=1, column=0, padx=20, pady=15, sticky="e")
    studid_entry = ctk.CTkEntry(details_frame, **entry_style)
    studid_entry.grid(row=1, column=1, padx=20, pady=15, sticky="w")

    ctk.CTkLabel(details_frame, text="Student Name", **label_style).grid(row=2, column=0, padx=20, pady=15, sticky="e")
    studname_entry = ctk.CTkEntry(details_frame, **entry_style)
    studname_entry.grid(row=2, column=1, padx=20, pady=15, sticky="w")

    ctk.CTkLabel(details_frame, text="Class", **label_style).grid(row=3, column=0, padx=20, pady=15, sticky="e")
    class_entry = ctk.CTkEntry(details_frame, **entry_style)
    class_entry.grid(row=3, column=1, padx=20, pady=15, sticky="w")

    # Frame for CRUD buttons in a row
    buttons_frame = ctk.CTkFrame(students_window, fg_color="#5CE1E6")
    buttons_frame.grid(row=1, column=0, padx=230, pady=30)

    # Button styling
    button_style = {
        "width": 150,
        "height": 60,
        "fg_color": "#2a9d8f",
        "hover_color": "#21867a",
        "border_color": "#f55b96",
        "text_color": "white",
        "font": ("Arial", 16, "bold")
    }

    # CRUD Buttons
    ctk.CTkButton(buttons_frame, text="Display Students", command=display_students, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Insert Student", command=insert_student, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Update Student", command=update_student, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Delete Student", command=delete_student, **button_style).pack(side="left", padx=10, pady=10)

    students_window.mainloop()# CRUD functions for Student
# CRUD operation window for Books
def open_books_window():
    global bookid_entry, bookname_entry, author_entry, category_entry
    
    books_window = ctk.CTk()
    books_window.title("Manage Books")
    books_window.geometry("1000x600")
    books_window.configure(fg_color="#061132")

    # Frame for book details
    details_frame = ctk.CTkFrame(books_window, width=900, height=500, fg_color="#FFFFFF", corner_radius=10)
    details_frame.grid(row=0, column=0, padx=210, pady=50, sticky="nsew")

    # Custom configuration for entry fields
    entry_config = {
        "width": 400,
        "height": 40,
        "fg_color": "#f0f0f0",
        "border_color": "#cccccc",
        "border_width": 2,
        "corner_radius": 5,
        "text_color":"black"
    }

    # Label and Entry fields with improved style
    ctk.CTkLabel(details_frame, text="Book ID", text_color="#000000", font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="e")
    bookid_entry = ctk.CTkEntry(details_frame, **entry_config)
    bookid_entry.grid(row=0, column=1, padx=20, pady=20)

    ctk.CTkLabel(details_frame, text="Book Name", text_color="#000000", font=("Arial", 24, "bold")).grid(row=1, column=0, padx=20, pady=20, sticky="e")
    bookname_entry = ctk.CTkEntry(details_frame, **entry_config)
    bookname_entry.grid(row=1, column=1, padx=20, pady=20)

    ctk.CTkLabel(details_frame, text="Author", text_color="#000000", font=("Arial", 24, "bold")).grid(row=2, column=0, padx=20, pady=20, sticky="e")
    author_entry = ctk.CTkEntry(details_frame, **entry_config)
    author_entry.grid(row=2, column=1, padx=20, pady=20)

    ctk.CTkLabel(details_frame, text="Category", text_color="#000000", font=("Arial", 24, "bold")).grid(row=3, column=0, padx=20, pady=20, sticky="e")
    category_entry = ctk.CTkEntry(details_frame, **entry_config)
    category_entry.grid(row=3, column=1, padx=20, pady=20)
   # Frame for CRUD buttons arranged in a row
    buttons_frame = ctk.CTkFrame(books_window, fg_color="#5CE1E6")
    buttons_frame.grid(row=1, column=0, padx=230, pady=30)

# Button styling
    button_config = {
        "width": 150,
        "height": 60,
        "fg_color": "#2a9d8f",  # Button color
        "hover_color": "#21867a",
        "border_color": "#f55b96",
        "text_color": "white",
        "font": ("Arial", 14, "bold")  # Font styling
    }

# Adding buttons with improved appearance
    ctk.CTkButton(buttons_frame, text="Display Books", command=display_books, **button_config).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Insert Book", command=insert_book, **button_config).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Update Book", command=update_book, **button_config).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Delete Book", command=delete_book, **button_config).pack(side="left", padx=10, pady=10)

    books_window.mainloop()

def open_main_menu():
    main_menu = ctk.CTk()
    main_menu.title("Library Management System")
    main_menu.geometry("1000x600")
    main_menu.configure(bg="#222831")
    #check me
    bg_image = PhotoImage(file=r"C:\Users\diyad\OneDrive\Desktop - Copy\lib\starting.png")  # Replace 'background.png' with your image file

    # Create a Canvas to hold the background image
    canvas = Canvas(main_menu, width=700, height=300)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Create a Frame for buttons and place it in the center
    button_frame = ctk.CTkFrame(main_menu, fg_color="#061132", width=1000, height=180)  # Transparent frame
    button_frame.place(relx=0.5, rely=0.14, anchor="center") 
    # Add a title label


    # Enhanced buttons
    ctk.CTkButton(button_frame, border_color="#7a7ed8",border_width=1,text="📚 Manage Books", fg_color="#000000",hover_color="#f55b96",command=open_books_window, width=167).pack(side="left", padx=18, pady=10)
    ctk.CTkButton(button_frame, border_color="#7a7ed8",border_width=1,text="👩‍🎓 Manage Students",fg_color="#000000",hover_color="#f55b96",command=open_students_window, width=167).pack(side="left", padx=18, pady=10)
    ctk.CTkButton(button_frame, border_color="#7a7ed8",border_width=1,text="📊 Current Status",fg_color="#000000",hover_color="#f55b96", command=open_current_status_window, width=167).pack(side="left", padx=18, pady=10)
    ctk.CTkButton(button_frame, border_color="#7a7ed8",border_width=1,text="👨‍💼 Manage Librarians",fg_color="#000000", hover_color="#f55b96", command=open_librarians_window, width=167).pack(side="left", padx=18, pady=10)
    ctk.CTkButton(button_frame, border_color="#7a7ed8",border_width=1,text="💰 Fine Calculation", fg_color="#000000",hover_color="#f55b96", command=open_fine_window, width=167).pack(side="left", padx=18, pady=10)

    canvas.image = bg_image

    main_menu.mainloop()



# CRUD operations for Books
def display_books():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    con.close()

    # Create a new window for displaying the table
    books_window = ctk.CTkToplevel()  # Use CTkToplevel for a secondary window
    books_window.title("Books List")
    books_window.geometry("600x400")

    # Prepare the table output
    output = tabulate(data, headers=['BOOKID', 'BOOKNAME', 'AUTHOR', 'CATEGORY'], tablefmt='grid')

    # Create a Textbox to display the output
    text_box = ctk.CTkTextbox(books_window, width=580, height=350, fg_color="#061132", border_color="#cccccc")
    text_box.pack(pady=10)
    text_box.insert("1.0", output)  # Insert the table output into the textbox
    text_box.configure(state="disabled")  # Disable editing of the textbox

    # Add a close button
    close_button = ctk.CTkButton(books_window, text="Close", command=books_window.destroy)
    close_button.pack(pady=(0, 10))

    books_window.mainloop()
    

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







def open_started():
    get_started_window = ctk.CTk()  # Create a new window
    get_started_window.title("Get Started")
    get_started_window.geometry("1000x600")
    get_started_window.configure(bg="#222831")

    # Load the background image (check me)
    bg_image = PhotoImage(file=r"C:\Users\diyad\OneDrive\Desktop - Copy\lib\landing.png")  # Update the path to your image file

    # Create a Canvas to hold the background image
    canvas = Canvas(get_started_window, width=1000, height=600)
    canvas.pack(fill="both", expand=True)
    
    # Create the background image on the canvas
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Create a button that calls open_main_menu when clicked
    get_started_button = ctk.CTkButton(get_started_window, text="Get Started", width=200, height=60 ,fg_color="#f55b9d", hover_color="#5ce1e6",
    font=("Helvetica", 16, "bold"),
    command=lambda: [get_started_window.destroy(), open_main_menu()])
    get_started_button.place(relx=0.43, rely=0.69, anchor="center")  # Center the button

    # Keep a reference to the image to prevent garbage collection
    get_started_window.bg_image = bg_image

    get_started_window.mainloop()
    
bg_image=None   

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "ADMIN" and password == "ADMIN123":
        
        login_window.destroy()
        open_started()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

# Login Window Setup
login_window = ctk.CTk()
login_window.title("Login")
login_window.geometry("1000x600")  # Set window to full screen
login_window.configure(fg_color="#061132")



# Left and Right Images (check me)
left_image = Image.open(r"C:\Users\diyad\OneDrive\Desktop - Copy\lib\01.png")
left_image = left_image.resize((400, 400), Image.LANCZOS)
left_img = ImageTk.PhotoImage(left_image)

right_image = Image.open(r"C:\Users\diyad\OneDrive\Desktop - Copy\lib\02.png")
right_image = right_image.resize((400, 400), Image.LANCZOS)
right_img = ImageTk.PhotoImage(right_image)

# Left Box with Image
left_frame = ctk.CTkFrame(login_window, width=400, height=400, corner_radius=40)
left_frame.place(relx=0.12, rely=0.5, anchor='w')
left_label = ctk.CTkLabel(left_frame, image=left_img)
left_label.pack(expand=True, fill='both')

# Right Box with Image
right_frame = ctk.CTkFrame(login_window, width=400, height=400, corner_radius=15)
right_frame.place(relx=0.88, rely=0.5, anchor='e')
right_label = ctk.CTkLabel(right_frame, image=right_img)
right_label.pack(expand=True, fill='both')

# Center Box for Login Details
center_frame = ctk.CTkFrame(login_window, corner_radius=15, width=250, height=400, fg_color="#121212")
center_frame.place(relx=0.5, rely=0.5, anchor='center')
center_frame.pack_propagate(False) 

ctk.CTkLabel(center_frame, text="Username", text_color="#ffffff",font=("Arial", 20,"bold")).pack(pady=12)
username_entry = ctk.CTkEntry(center_frame)
username_entry.pack(pady=12)

ctk.CTkLabel(center_frame, text="Password", text_color="#ffffff",font=("Arial", 20,"bold")).pack(pady=12)
password_entry = ctk.CTkEntry(center_frame, show="*")
password_entry.pack(pady=12)


ctk.CTkButton(center_frame, text="Login", font=("Arial", 20,"bold"), command=login, fg_color="#f55b96", hover_color="#5ce1e6", width=180, height=40).pack(pady=30)

# Start the application
login_window.mainloop()


#Landing Page



 
 #main menu






# CRUD operation functions for Students, Current Status, Librarians, and Fines (similar to open_books_window)
def open_students_window():
    global studid_entry, studname_entry, class_entry

    # Create the main window
    students_window = ctk.CTk()
    students_window.title("Manage Students")
    students_window.geometry("1000x600")
    students_window.configure(fg_color="#061132")

    # Create a frame for the student details section
    details_frame = ctk.CTkFrame(students_window, width=900, height=500, fg_color="#FFFFFF", corner_radius=10)
    details_frame.grid(row=0, column=0, padx=210, pady=50, sticky="nsew")

    # Heading
    heading_label = ctk.CTkLabel(
        details_frame,
        text="Enter Student Details",
        font=("Arial", 24, "bold"),
        text_color="#000000"
    )
    heading_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

    # Label and Entry style
    label_style = {
        "text_color": "#000000",
        "font": ("Arial", 18, "bold")
    }
    entry_style = {
        "width": 400,
        "height": 40,
        "fg_color": "#f0f0f0",
        "border_color": "#cccccc",
        "border_width": 2,
        "corner_radius": 5,
        "text_color":"black"
    }

    # Labels and Entries for Student Details
    ctk.CTkLabel(details_frame, text="Student ID", **label_style).grid(row=1, column=0, padx=20, pady=15, sticky="e")
    studid_entry = ctk.CTkEntry(details_frame, **entry_style)
    studid_entry.grid(row=1, column=1, padx=20, pady=15, sticky="w")

    ctk.CTkLabel(details_frame, text="Student Name", **label_style).grid(row=2, column=0, padx=20, pady=15, sticky="e")
    studname_entry = ctk.CTkEntry(details_frame, **entry_style)
    studname_entry.grid(row=2, column=1, padx=20, pady=15, sticky="w")

    ctk.CTkLabel(details_frame, text="Class", **label_style).grid(row=3, column=0, padx=20, pady=15, sticky="e")
    class_entry = ctk.CTkEntry(details_frame, **entry_style)
    class_entry.grid(row=3, column=1, padx=20, pady=15, sticky="w")

    # Frame for CRUD buttons in a row
    buttons_frame = ctk.CTkFrame(students_window, fg_color="#5CE1E6")
    buttons_frame.grid(row=1, column=0, padx=230, pady=30)

    # Button styling
    button_style = {
        "width": 150,
        "height": 60,
        "fg_color": "#2a9d8f",
        "hover_color": "#21867a",
        "border_color": "#f55b96",
        "text_color": "white",
        "font": ("Arial", 16, "bold")
    }

    # CRUD Buttons
    ctk.CTkButton(buttons_frame, text="Display Students", command=display_students, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Insert Student", command=insert_student, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Update Student", command=update_student, **button_style).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(buttons_frame, text="Delete Student", command=delete_student, **button_style).pack(side="left", padx=10, pady=10)

    students_window.mainloop()# CRUD functions for Student








 


