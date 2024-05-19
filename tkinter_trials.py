import tkinter as tk
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database connection parameters
DB_NAME = "Buzylane"
DB_USER = "postgres"
DB_PASSWORD = "1qazxsw2"
DB_HOST = "localhost"
DB_PORT = "5432"

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def load_content(button_name):
    clear_content()
    if button_name == "Orders/Transactions":
        setup_orders_transactions(content_frame)
    else:
        tk.Label(content_frame, text=f"Content for {button_name}", font=('Helvetica', 16), bg='white').pack(pady=20)

def setup_orders_transactions(frame):
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview",
                    background="#D3D3D3",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#D3D3D3")
    style.map('Treeview', background=[('selected', '#347083')])

    top_panel = tk.Frame(frame, bg='orange')
    top_panel.pack(fill='x', padx=10, pady=5)
    buttons_info = [
        ("Today's Orders", 'blue', filter_todays_orders),
        ("This Month Orders", 'blue', filter_this_month_orders),
        ("All Orders/Refresh", 'blue', load_treeview_data),
        ("All Cancelled Orders", 'blue', filter_cancelled_orders)
    ]
    for text, color, command in buttons_info:
        tk.Button(top_panel, text=text, bg=color, fg='white', command=lambda c=command: c(tree)).pack(side='left', padx=5, pady=5)

    middle_panel = tk.Frame(frame, bg='white')
    middle_panel.pack(fill='x', padx=10, pady=5)
    filters = ["ORDER ID", "PAYMENT STATUS", "DELIVERY DATE", "ORDER STATUS", "EXTERNAL PAYMENT"]

    order_ids = fetch_order_ids()
    for text in filters:
        ttk.Label(middle_panel, text=text).pack(side='left', padx=5)
        if text == "ORDER ID":
            order_id_combobox = ttk.Combobox(middle_panel, values=order_ids, width=15)
            order_id_combobox.pack(side='left', padx=5)
            order_id_combobox.bind("<<ComboboxSelected>>", lambda e: filter_by_order_id(tree, order_id_combobox.get()))
        else:
            ttk.Entry(middle_panel, width=15).pack(side='left', padx=5)

    setup_treeview(frame)

def fetch_order_ids():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT DISTINCT \"ID\" FROM {}").format(sql.Identifier('TBL_ORDERS')))
        ids = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return ids
    except Exception as e:
        print(f"Database error: {e}")
        return []

def setup_treeview(frame):
    style = ttk.Style()
    style.configure("Treeview",
                    background="#D3D3D3",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#E3E3E3")
    style.map('Treeview', background=[('selected', '#E3B043')])

    global tree
    tree = ttk.Treeview(frame, columns=(
        'ID', 'Date', 'Source', 'Type', 'Cust.Name', 'Cust.Contact', 'Order_Notes', 'Amount', 'Discount', 'Total',
        'Status', 'Payment', 'Ext. Payment'), show='headings', height=10)
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')

    for col in tree['columns']:
        tree.heading(col, text=col.replace('_', ' '))
        tree.column(col, anchor="center", width=100)

    load_treeview_data(tree)
    poll_database(tree)

def load_treeview_data(tree):
    global last_update
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT \"ID\", \"Transaction_DAte\", \"Source\", \"Service_Type\", \"Customer_Name\", \"Customer_Contact\", \"Order\", \"Amount\", \"Discount\", \"Total_Amount\", \"Status\", \"Payment\", \"External_Payment\" FROM {}").format(sql.Identifier('TBL_ORDERS')))
        rows = cursor.fetchall()
        if rows:
            tree.delete(*tree.get_children())
            for row in rows:
                formatted_row = [str(item) if item is not None else "" for item in row]
                tree.insert('', 'end', values=formatted_row)
        last_update = datetime.now()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def poll_database(tree):
    global last_update
    if (datetime.now() - last_update).seconds >= 10:
        load_treeview_data(tree)
    tree.after(10000, lambda: poll_database(tree))

def filter_by_order_id(tree, order_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT \"ID\", \"Transaction_DAte\", \"Source\", \"Service_Type\", \"Customer_Name\", \"Customer_Contact\", \"Order\", \"Amount\", \"Discount\", \"Total_Amount\", \"Status\", \"Payment\", \"External_Payment\" FROM {} WHERE \"ID\" = %s").format(sql.Identifier('TBL_ORDERS')), [order_id])
        rows = cursor.fetchall()
        if rows:
            tree.delete(*tree.get_children())
            for row in rows:
                formatted_row = [str(item) if item is not None else "" for item in row]
                tree.insert('', 'end', values=formatted_row)
            open_transaction_details(order_id, rows[0])  # Open the modal form with the order details
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def filter_todays_orders(tree):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT \"ID\", \"Transaction_DAte\", \"Source\", \"Service_Type\", \"Customer_Name\", \"Customer_Contact\", \"Order\", \"Amount\", \"Discount\", \"Total_Amount\", \"Status\", \"Payment\", \"External_Payment\" FROM {} WHERE \"Transaction_DAte\"::date = CURRENT_DATE").format(sql.Identifier('TBL_ORDERS')))
        rows = cursor.fetchall()
        if rows:
            tree.delete(*tree.get_children())
            for row in rows:
                formatted_row = [str(item) if item is not None else "" for item in row]
                tree.insert('', 'end', values=formatted_row)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def filter_this_month_orders(tree):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        first_day_of_month = datetime.now().replace(day=1)
        cursor.execute(sql.SQL(
            "SELECT \"ID\", \"Transaction_DAte\", \"Source\", \"Service_Type\", \"Customer_Name\", \"Customer_Contact\", \"Order\", \"Amount\", \"Discount\", \"Total_Amount\", \"Status\", \"Payment\", \"External_Payment\" FROM {} WHERE \"Transaction_DAte\"::date >= %s").format(sql.Identifier('TBL_ORDERS')), [first_day_of_month])
        rows = cursor.fetchall()
        if rows:
            tree.delete(*tree.get_children())
            for row in rows:
                formatted_row = [str(item) if item is not None else "" for item in row]
                tree.insert('', 'end', values=formatted_row)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def filter_cancelled_orders(tree):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT \"ID\", \"Transaction_DAte\", \"Source\", \"Service_Type\", \"Customer_Name\", \"Customer_Contact\", \"Order\", \"Amount\", \"Discount\", \"Total_Amount\", \"Status\", \"Payment\", \"External_Payment\" FROM {} WHERE \"Status\" = %s").format(sql.Identifier('TBL_ORDERS')), ['Cancelled'])
        rows = cursor.fetchall()
        if rows:
            tree.delete(*tree.get_children())
            for row in rows:
                formatted_row = [str(item) if item is not None else "" for item in row]
                tree.insert('', 'end', values=formatted_row)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")


def open_transaction_details(order_id, transaction_data):
    details_window = tk.Toplevel(root)
    details_window.title(f"Transaction Details for Order ID: {order_id}")
    details_window.geometry("600x400")  # Set a fixed size for the details window
    details_window.configure(bg='white')  # Set background color to match the main form

    container = tk.Frame(details_window, bg='white')
    container.pack(expand=True)

    labels = ["Transaction Date", "Source", "Service Type", "Customer Name", "Customer Contact", "Order Notes",
              "Amount", "Discount", "Total Amount", "Status", "Payment", "External Payment"]
    entries = {}

    # Define custom styles
    label_font = ('Helvetica', 12, 'bold')
    entry_font = ('Helvetica', 12)
    label_bg = 'white'
    label_fg = 'black'
    entry_bg = 'lightgrey'
    entry_fg = 'black'
    button_bg = 'blue'
    button_fg = 'white'

    for idx, (label, value) in enumerate(zip(labels, transaction_data[1:])):  # Skip the first item (ID)
        tk.Label(container, text=label, font=label_font, bg=label_bg, fg=label_fg).grid(row=idx, column=0, padx=10,
                                                                                        pady=5, sticky='e')
        entry = tk.Entry(container, font=entry_font, bg=entry_bg, fg=entry_fg, width=30)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entry.insert(0, str(value))  # Ensure value is converted to string
        entries[label] = entry

    def save_changes():
        updated_data = {label: entry.get() for label, entry in entries.items()}
        update_transaction_in_database(order_id, updated_data)
        details_window.destroy()

    tk.Button(container, text="Save", font=label_font, bg=button_bg, fg=button_fg, command=save_changes).grid(
        row=len(labels), column=0, columnspan=2, pady=10)

    # Center the window on the screen
    details_window.update_idletasks()
    width = details_window.winfo_width()
    height = details_window.winfo_height()
    x = (details_window.winfo_screenwidth() // 2) - (width // 2)
    y = (details_window.winfo_screenheight() // 2) - (height // 2)
    details_window.geometry(f'{width}x{height}+{x}+{y}')


def update_transaction_in_database(order_id, updated_data):
    columns = ["Transaction_DAte", "Source", "Service_Type", "Customer_Name", "Customer_Contact", "Order", "Amount",
               "Discount", "Total_Amount", "Status", "Payment", "External_Payment"]
    set_clause = ", ".join([f"\"{col}\" = %s" for col in columns])
    values = [updated_data[col] for col in columns]
    values.append(order_id)

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            f"UPDATE {{}} SET {set_clause} WHERE \"ID\" = %s").format(sql.Identifier('TBL_ORDERS')), values)
        conn.commit()
        cursor.close()
        conn.close()
        load_treeview_data(tree)  # Refresh the Treeview data after updating the database
    except Exception as e:
        print(f"Database error: {e}")

root = tk.Tk()
root.title("Business Dashboard")
root.geometry("1800x900")

header_frame = tk.Frame(root, bg='gray')
header_frame.grid(row=0, column=0, sticky="ew", columnspan=2)
header_label = tk.Label(header_frame, text="STORE MANAGEMENT SYSTEM", bg='gray', fg='white', font=('Helvetica', 20))
header_label.pack(pady=20, fill='x')

nav_frame = tk.Frame(root, width=200, bg='blue')
nav_frame.grid(row=1, column=0, sticky="ns")
content_frame = tk.Frame(root, bg='white')
content_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

buttons = ["Orders/Transactions", "Revenue", "Inventory", "Expenditure", "Hairstylists"]
for idx, button in enumerate(buttons):
    action = lambda b=button: load_content(b)
    tk.Button(nav_frame, text=button, bg='orange', fg='black', height=2, width=20, command=action).grid(row=idx, column=0, padx=10, pady=10, sticky="ew")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

root.mainloop()
