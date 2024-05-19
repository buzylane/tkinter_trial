import subprocess
import os

def update_script():
    try:
        # Change directory to the script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_dir)

        # Pull the latest changes from the repository
        subprocess.check_call(['git', 'pull'])
        print("Successfully updated the script from GitHub repository.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update the script. Error: {e}")

# Call the update function at the beginning
update_script()

import tkinter as tk
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database connection parameters
DB_NAME = "BuzylaneMainDB"
DB_USER = "postgres"
DB_PASSWORD = "1qazxsw2"
DB_HOST = "localhost"
DB_PORT = "5432"

last_update = datetime.now()  # Initialize last_update

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
        tk.Button(top_panel, text=text, bg=color, fg='white', command=lambda c=command: c(tree)).pack(side='left',
                                                                                                      padx=5, pady=5)

    # Add Order button
    tk.Button(top_panel, text="Add Order", bg='blue', fg='white', command=add_order).pack(side='right', padx=5, pady=5)

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


def add_order():
    # Fetch customer names and IDs for the combobox
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT customerid, firstname || ' ' || lastname AS customer_name, phone FROM customers")
        customers = cursor.fetchall()
        customer_dict = {f"{row[1]} (ID: {row[0]})": (row[0], row[2]) for row in customers}
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return

    def update_contact(event):
        customer_name = customer_combobox.get()
        contact = customer_dict.get(customer_name, (None, ''))[1]
        customer_contact_label.config(text=f"Contact: {contact}")

    add_order_window = tk.Toplevel(root)
    add_order_window.title("Add Order")
    add_order_window.geometry("800x600")
    add_order_window.configure(bg='white')

    # Fixed frame on top
    top_frame = tk.Frame(add_order_window, bg='gray', height=50)
    top_frame.pack(fill='x')
    top_label = tk.Label(top_frame, text="Add New Order", bg='gray', fg='white', font=('Helvetica', 16))
    top_label.pack(pady=10)

    # Yellow section with customer dropdown and "Add New Customer" button
    yellow_frame = tk.Frame(add_order_window, bg='orange', height=50)
    yellow_frame.pack(fill='x', pady=5)

    customer_label = tk.Label(yellow_frame, text="Customer:", bg='orange', font=('Helvetica', 12))
    customer_label.pack(side='left', padx=10, pady=5)

    customer_combobox = ttk.Combobox(yellow_frame, values=list(customer_dict.keys()), width=30)
    customer_combobox.pack(side='left', padx=10, pady=5)
    customer_combobox.bind("<<ComboboxSelected>>", update_contact)

    customer_contact_label = tk.Label(yellow_frame, text="Contact: ", bg='orange', font=('Helvetica', 12))
    customer_contact_label.pack(side='left', padx=10, pady=5)


    tk.Button(yellow_frame, text="Add New Customer", bg='blue', fg='white', command=None).pack(side='right', padx=10, pady=5)

    # Blue bordered section for the form fields
    blue_border_frame = tk.Frame(add_order_window, bg='white', highlightbackground='blue', highlightthickness=2)
    blue_border_frame.pack(pady=10, padx=10, fill='both', expand=True)

    form_frame = tk.Frame(blue_border_frame, bg='white')
    form_frame.pack(pady=20, padx=10, fill='both', expand=True)

    tk.Label(form_frame, text="Product ID dropdown", bg='white', font=('Helvetica', 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(form_frame, text="Product Name dropdown", bg='white', font=('Helvetica', 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(form_frame, text="Variant dropdown", bg='white', font=('Helvetica', 12)).grid(row=0, column=2, padx=10, pady=10)

    # Placeholder entries for other fields (you can add appropriate dropdowns or entries as needed)
    product_id_entry = ttk.Entry(form_frame)
    product_id_entry.grid(row=1, column=0, padx=10, pady=10)

    product_name_entry = ttk.Entry(form_frame)
    product_name_entry.grid(row=1, column=1, padx=10, pady=10)

    variant_entry = ttk.Entry(form_frame)
    variant_entry.grid(row=1, column=2, padx=10, pady=10)

    tk.Label(form_frame, text="Order Date", bg='white', font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=10)
    order_date_entry = ttk.Entry(form_frame)
    order_date_entry.grid(row=3, column=0, padx=10, pady=10)

    tk.Label(form_frame, text="Source ID", bg='white', font=('Helvetica', 12)).grid(row=2, column=1, padx=10, pady=10)
    source_id_entry = ttk.Entry(form_frame)
    source_id_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Service ID", bg='white', font=('Helvetica', 12)).grid(row=2, column=2, padx=10, pady=10)
    service_id_entry = ttk.Entry(form_frame)
    service_id_entry.grid(row=3, column=2, padx=10, pady=10)

    tk.Label(form_frame, text="Total Amount", bg='white', font=('Helvetica', 12)).grid(row=4, column=0, padx=10, pady=10)
    total_amount_entry = ttk.Entry(form_frame)
    total_amount_entry.grid(row=5, column=0, padx=10, pady=10)

    tk.Label(form_frame, text="Discount", bg='white', font=('Helvetica', 12)).grid(row=4, column=1, padx=10, pady=10)
    discount_entry = ttk.Entry(form_frame)
    discount_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Payment Status", bg='white', font=('Helvetica', 12)).grid(row=4, column=2, padx=10, pady=10)
    payment_status_entry = ttk.Entry(form_frame)
    payment_status_entry.grid(row=5, column=2, padx=10, pady=10)

    tk.Label(form_frame, text="Expected Delivery Date", bg='white', font=('Helvetica', 12)).grid(row=6, column=0, padx=10, pady=10)
    expected_delivery_date_entry = ttk.Entry(form_frame)
    expected_delivery_date_entry.grid(row=7, column=0, padx=10, pady=10)

    def save_new_order():
        customer_name = customer_combobox.get()
        customer_id = customer_dict.get(customer_name, (None, ''))[0]
        order_date = order_date_entry.get()
        source_id = source_id_entry.get()
        service_id = service_id_entry.get()
        total_amount = total_amount_entry.get()
        discount = discount_entry.get()
        payment_status = payment_status_entry.get()
        expected_delivery_date = expected_delivery_date_entry.get()

        if customer_id is None:
            print("Invalid customer selected.")
            return

        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = conn.cursor()
            query = """
            INSERT INTO orders (customerid, orderdate, sourceid, serviceid, totalamount, discount, paymentstatus, expecteddeliverydate, userid, statusid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # For this example, we assume userid and statusid are fixed values
            cursor.execute(query, (customer_id, order_date, source_id, service_id, total_amount, discount, payment_status, expected_delivery_date, 1, 1))
            conn.commit()
            cursor.close()
            conn.close()
            load_treeview_data(tree)
            add_order_window.destroy()
        except Exception as e:
            print(f"Database error: {e}")

    tk.Button(add_order_window, text="Save", bg='blue', fg='white', command=save_new_order).pack(pady=20)



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
        cursor.execute(sql.SQL("SELECT DISTINCT orderid FROM orders"))
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
        'ID', 'Date', 'Source', 'Type', 'Cust.Name', 'Cust.Contact', 'Amount', 'Discount', 'Total',
        'Status', 'Payment', 'Delivery Date', 'User'), show='headings', height=10)
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
        query = """
        SELECT
            o.orderid,
            o.orderdate,
            os.sourcename,
            st.servicename,
            c.firstname || ' ' || c.lastname AS customer_name,
            c.phone AS customer_contact,
            o.totalamount,
            o.discount,
            (o.totalamount - o.discount) AS total,
            ost.statusname,
            o.paymentstatus,
            o.expecteddeliverydate,
            u.username
        FROM
            orders o
        JOIN
            customers c ON o.customerid = c.customerid
        JOIN
            ordersource os ON o.sourceid = os.sourceid
        JOIN
            servicetype st ON o.serviceid = st.serviceid
        JOIN
            orderstatus ost ON o.statusid = ost.statusid
        JOIN
            users u ON o.userid = u.userid
        """
        cursor.execute(query)
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
        query = """
        SELECT
            o.orderid,
            o.orderdate,
            os.sourcename,
            st.servicename,
            c.firstname || ' ' || c.lastname AS customer_name,
            c.phone AS customer_contact,
            o.totalamount,
            o.discount,
            (o.totalamount - o.discount) AS total,
            ost.statusname,
            o.paymentstatus,
            o.expecteddeliverydate,
            u.username
        FROM
            orders o
        JOIN
            customers c ON o.customerid = c.customerid
        JOIN
            ordersource os ON o.sourceid = os.sourceid
        JOIN
            servicetype st ON o.serviceid = st.serviceid
        JOIN
            orderstatus ost ON o.statusid = ost.statusid
        JOIN
            users u ON o.userid = u.userid
        WHERE
            o.orderid = %s
        """
        cursor.execute(query, [order_id])
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
        query = """
        SELECT
            o.orderid,
            o.orderdate,
            os.sourcename,
            st.servicename,
            c.firstname || ' ' || c.lastname AS customer_name,
            c.phone AS customer_contact,
            o.totalamount,
            o.discount,
            (o.totalamount - o.discount) AS total,
            os.statusname,
            o.paymentstatus,
            o.expecteddeliverydate,
            u.username
        FROM
            orders o
        JOIN
            customers c ON o.customerid = c.customerid
        JOIN
            ordersource os ON o.sourceid = os.sourceid
        JOIN
            servicetype st ON o.serviceid = st.serviceid
        JOIN
            users u ON o.userid = u.userid
        WHERE
            o.orderdate::date = CURRENT_DATE
        """
        cursor.execute(query)
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
        query = """
        SELECT
            o.orderid,
            o.orderdate,
            os.sourcename,
            st.servicename,
            c.firstname || ' ' || c.lastname AS customer_name,
            c.phone AS customer_contact,
            o.totalamount,
            o.discount,
            (o.totalamount - o.discount) AS total,
            ost.statusname,
            o.paymentstatus,
            o.expecteddeliverydate,
            u.username
        FROM
            orders o
        JOIN
            customers c ON o.customerid = c.customerid
        JOIN
            ordersource os ON o.sourceid = os.sourceid
        JOIN
            servicetype st ON o.serviceid = st.serviceid
        JOIN
            orderstatus ost ON o.statusid = ost.statusid
        JOIN
            users u ON o.userid = u.userid
        WHERE
            DATE_TRUNC('month', o.orderdate) = DATE_TRUNC('month', CURRENT_DATE)
        """
        cursor.execute(query)
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
        query = """
        SELECT
            o.orderid,
            o.orderdate,
            os.sourcename,
            st.servicename,
            c.firstname || ' ' || c.lastname AS customer_name,
            c.phone AS customer_contact,
            o.totalamount,
            o.discount,
            (o.totalamount - o.discount) AS total,
            ost.statusname,
            o.paymentstatus,
            o.expecteddeliverydate,
            u.username
        FROM
            orders o
        JOIN
            customers c ON o.customerid = c.customerid
        JOIN
            ordersource os ON o.sourceid = os.sourceid
        JOIN
            servicetype st ON o.serviceid = st.serviceid
        JOIN
            orderstatus ost ON o.statusid = ost.statusid
        JOIN
            users u ON o.userid = u.userid
        WHERE
            o.statusid = (SELECT statusid FROM orderstatus WHERE statusname = 'Cancelled')
        """
        cursor.execute(query)
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


def open_transaction_details(order_id, order_details):
    details_window = tk.Toplevel(root)
    details_window.title(f"Order Details for {order_id}")
    details_window.geometry("600x400")

    details_frame = tk.Frame(details_window, padx=10, pady=10)
    details_frame.pack(fill="both", expand=True)

    labels = [
        "Order ID", "Order Date", "Order Source", "Service Type", "Customer Name",
        "Customer Contact", "Total Amount", "Discount", "Total",
        "Status", "Payment Status", "Expected Delivery Date", "User"
    ]
    for i, label in enumerate(labels):
        tk.Label(details_frame, text=f"{label}:", font=('Helvetica', 12, 'bold')).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        tk.Label(details_frame, text=f"{order_details[i]}", font=('Helvetica', 12)).grid(row=i, column=1, sticky="w", padx=5, pady=2)

    def close_window():
        details_window.destroy()

    tk.Button(details_frame, text="Close", command=close_window).grid(row=len(labels), column=0, columnspan=2, pady=10)

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

buttons = ["Dashboard","Orders/Transactions", "Revenue", "Inventory", "Expenditure", "Hairstylists"]
for idx, button in enumerate(buttons):
    action = lambda b=button: load_content(b)
    tk.Button(nav_frame, text=button, bg='orange', fg='black', height=2, width=20, command=action).grid(row=idx, column=0, padx=10, pady=10, sticky="ew")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

root.mainloop()
