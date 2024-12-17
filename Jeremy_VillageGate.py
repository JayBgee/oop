import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk

# Main Application Window
root = Tk()
root.title("Village Gate System")
root.geometry("760x700")
root.resizable(True, True)
root.configure(bg="#e9f7fa")

# Database Connection
conn = sqlite3.connect('village_gate.db')
c = conn.cursor()

# Database Table with time_in and time_out columns
c.execute('''CREATE TABLE IF NOT EXISTS "gate_access" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "full_name" TEXT,
    "contact_number" INTEGER,
    "access_purpose" TEXT,
    "access_status" TEXT,
    "time_in" TEXT,
    "time_out" TEXT
)''')
conn.commit()

# Add a new record
def add_record():
    # Input validation for empty fields
    if full_name.get() == "" or contact_number.get() == "" or access_purpose.get() == "" or access_status.get() == "":
        return  # Prevent adding empty records

    # Input validation for contact number (must be all digits)
    if not contact_number.get().isdigit():
        error_label.config(text="Error: Contact number must contain only numbers", fg="red")
        return

    # Determine the time to insert based on the access status
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_in = timestamp if access_status.get() == "Enter" else None
    time_out = timestamp if access_status.get() == "Exit" else None

    # If the contact number is valid, proceed to add the record
    conn = sqlite3.connect('village_gate.db')
    c = conn.cursor()
    c.execute("INSERT INTO gate_access (full_name, contact_number, access_purpose, access_status, time_in, time_out) VALUES (?, ?, ?, ?, ?, ?)", 
              (full_name.get(), contact_number.get(), access_purpose.get(), access_status.get(), time_in, time_out))
    conn.commit()

    # Clear input fields
    full_name.delete(0, END)
    contact_number.delete(0, END)
    access_purpose.delete(0, END)
    access_status.set("")  # Clear combobox

    conn.close()

    # Clear error label if any
    error_label.config(text="")

# View all records
def view_records():
    conn = sqlite3.connect('village_gate.db')
    c = conn.cursor()
    c.execute("SELECT * FROM gate_access")
    records = c.fetchall()

    # Clear Treeview
    for record in tree.get_children():
        tree.delete(record)

    # Insert records into Treeview
    for record in records:
        tree.insert("", END, values=record)

    conn.close()

# Delete a record
def delete_record():
    try:
        record_id = int(delete_id.get())
    except ValueError:
        return

    # Delete the record from the database
    conn = sqlite3.connect('village_gate.db')
    c = conn.cursor()
    c.execute("DELETE FROM gate_access WHERE id=?", (record_id,))
    conn.commit()

    # Reset AUTOINCREMENT value to avoid gaps (this resets the counter to the last used id + 1)
    c.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM gate_access) WHERE name = 'gate_access'")
    conn.commit()

    conn.close()
    view_records()
    delete_id.delete(0, END)

# Update a record
def edit_record():
    try:
        record_id = int(edit_id.get())
    except ValueError:
        return

    editor = Toplevel(root)
    editor.title("Update Record")
    editor.geometry("400x400")
    editor.configure(bg="#f2f2f2")

    conn = sqlite3.connect('village_gate.db')
    c = conn.cursor()
    c.execute("SELECT * FROM gate_access WHERE id=?", (record_id,))
    record = c.fetchone()

    if not record:
        editor.destroy()
        return

    Label(editor, text="Full Name", font=("Arial", 12), bg="#f2f2f2").grid(row=0, column=0, padx=20, pady=10, sticky=W)
    full_name_editor = Entry(editor, width=30)
    full_name_editor.grid(row=0, column=1, pady=10)
    full_name_editor.insert(0, record[1])

    Label(editor, text="Contact Number", font=("Arial", 12), bg="#f2f2f2").grid(row=1, column=0, padx=20, pady=10, sticky=W)
    contact_number_editor = Entry(editor, width=30)
    contact_number_editor.grid(row=1, column=1, pady=10)
    contact_number_editor.insert(0, record[2])

    Label(editor, text="Access Purpose", font=("Arial", 12), bg="#f2f2f2").grid(row=2, column=0, padx=20, pady=10, sticky=W)
    access_purpose_editor = Entry(editor, width=30)
    access_purpose_editor.grid(row=2, column=1, pady=10)
    access_purpose_editor.insert(0, record[3])

    Label(editor, text="Access Status", font=("Arial", 12), bg="#f2f2f2").grid(row=3, column=0, padx=20, pady=10, sticky=W)
    access_status_editor = ttk.Combobox(editor, values=["Enter", "Exit"], width=28)  # Combobox for Access Status
    access_status_editor.grid(row=3, column=1, pady=10)
    access_status_editor.set(record[4])  # Set existing status

    # Validation function for contact number
    def validate_contact_number():
        contact_number = contact_number_editor.get()
        if not contact_number.isdigit():
            error_label.config(text="Error: Contact number must contain only numbers", fg="red")
            return False
        return True

    # Save updates after validation
    def save_update():
        if validate_contact_number():  # Only save if the contact number is valid
            # Update the correct time_in or time_out field based on access status
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time_in = record[5]  # Preserve the existing time_in value
            time_out = None

            if access_status_editor.get() == "Enter" and not record[5]:  # If the record doesn't have a time_in yet
                time_in = timestamp
            elif access_status_editor.get() == "Exit" and record[5]:  # If the record already has a time_in
                time_out = timestamp

            c.execute("""UPDATE gate_access SET
                            full_name = ?, contact_number = ?, access_purpose = ?, access_status = ?, time_in = ?, time_out = ?
                            WHERE id = ?""",
                        (full_name_editor.get(), contact_number_editor.get(), access_purpose_editor.get(), access_status_editor.get(), time_in, time_out, record_id))
            conn.commit()
            conn.close()
            editor.destroy()
            view_records()

    Button(editor, text="Save Changes", command=save_update, bg="#007bff", fg="white", font=("Arial", 10), relief=RAISED).grid(row=4, column=0, columnspan=2, pady=20, ipadx=50)

    editor.mainloop()


# Input Fields for Record Details
Label(root, text="Full Name", font=("Arial", 12), bg="#e9f7fa").grid(row=0, column=0, padx=20, pady=10, sticky=W)
full_name = Entry(root, width=90)
full_name.grid(row=0, column=1, pady=10)

Label(root, text="Contact Number", font=("Arial", 12), bg="#e9f7fa").grid(row=1, column=0, padx=20, pady=10, sticky=W)
contact_number = Entry(root, width=90)
contact_number.grid(row=1, column=1, pady=10)

Label(root, text="Access Purpose", font=("Arial", 12), bg="#e9f7fa").grid(row=2, column=0, padx=20, pady=10, sticky=W)
access_purpose = Entry(root, width=90)
access_purpose.grid(row=2, column=1, pady=10)

# Combobox for Access Status
Label(root, text="Access Status (Enter/Exit)", font=("Arial", 12), bg="#e9f7fa").grid(row=3, column=0, padx=20, pady=10, sticky=W)
access_status = ttk.Combobox(root, values=["Enter", "Exit"], width=87)  # Set predefined values
access_status.grid(row=3, column=1, pady=10)

# ID Fields for Editing and Deleting
Label(root, text="Enter ID to Delete", font=("Arial", 12), bg="#e9f7fa").grid(row=4, column=0, padx=20, pady=10, sticky=W)
delete_id = Entry(root, width=90)
delete_id.grid(row=4, column=1, pady=10)

Label(root, text="Enter ID to Edit", font=("Arial", 12), bg="#e9f7fa").grid(row=5, column=0, padx=20, pady=10, sticky=W)
edit_id = Entry(root, width=90)
edit_id.grid(row=5, column=1, pady=10)

# Error label for validation messages
error_label = Label(root, text="", font=("Arial", 10), bg="#e9f7fa", fg="red")
error_label.grid(row=4, column=2, pady=10, padx=20, sticky=W)

# Buttons
Button(root, text="Add Information", command=add_record, bg="#007bff", fg="white", font=("Arial", 12), relief=RAISED).grid(row=6, column=0, columnspan=2, pady=10, ipadx=80)
Button(root, text="View Information", command=view_records, bg="#007bff", fg="white", font=("Arial", 12), relief=RAISED).grid(row=7, column=0, columnspan=2, pady=10, ipadx=78)
Button(root, text="Delete Information", command=delete_record, bg="#007bff", fg="white", font=("Arial", 12), relief=RAISED).grid(row=8, column=0, columnspan=2, pady=10, ipadx=72)
Button(root, text="Edit Information", command=edit_record, bg="#007bff", fg="white", font=("Arial", 12), relief=RAISED).grid(row=9, column=0, columnspan=2, pady=10, ipadx=81)

# Treeview for Displaying Records
columns = ("ID", "Full Name", "Contact Number", "Access Purpose", "Access Status", "Time In", "Time Out")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.grid(row=10, column=0, columnspan=2, padx=20, pady=20)

# Configure Treeview Columns with anchor set to CENTER
tree.heading("ID", text="ID")
tree.heading("Full Name", text="Full Name")
tree.heading("Contact Number", text="Contact Number")
tree.heading("Access Purpose", text="Access Purpose")
tree.heading("Access Status", text="Access Status")
tree.heading("Time In", text="Time In")
tree.heading("Time Out", text="Time Out")

tree.column("ID", width=50, anchor=CENTER)
tree.column("Full Name", width=120, anchor=CENTER)
tree.column("Contact Number", width=120, anchor=CENTER)
tree.column("Access Purpose", width=150, anchor=CENTER)
tree.column("Access Status", width=100, anchor=CENTER)
tree.column("Time In", width=180, anchor=CENTER)
tree.column("Time Out", width=180, anchor=CENTER)


root.mainloop()
