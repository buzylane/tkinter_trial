import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry
from database import fetch_customers, fetch_sources, fetch_services, fetch_order_ids, load_treeview_data

def clear_content(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

def load_content(button_name, content_frame):
    clear_content(content_frame)
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
    customer_dict = fetch_customers()
    source_dict = fetch_sources()
    service_dict = fetch_services()

    def update_contact(event):
        customer_name = customer_combobox.get()
        contact = customer_dict.get(customer_name, (None, ''))[1]
        customer_contact_label.config(text=f"Contact: {contact}")

    add_order_window = tk.Toplevel(root)
    add_order_window.title("Add Order")
    add_order_window.geometry("1800x900")
    add_order_window.configure(bg='white')

    # Fixed frame on top with Add New Customer and Add New Order buttons
    top_frame = tk.Frame(add_order_window, bg='gray', height=50)
    top_frame.pack(fill='x')

    top_label = tk.Label(top_frame, text="Order Management", bg='gray', fg='white', font=('Helvetica', 16))
    top_label.pack(side='left', pady=10, padx=20)

    add_customer_button = tk.Button(top_frame, text="Add New Customer", bg='blue', fg='white', command=None)
    add_customer_button.pack(side='left', padx=10, pady=5)

    add_order_button = tk.Button(top_frame, text="Add New Order", bg='blue', fg='white', command=None)
    add_order_button.pack(side='left', padx=10, pady=5)

    # Yellow section with customer dropdown and other fields
    yellow_frame = tk.Frame(add_order_window, bg='orange', height=50)
    yellow_frame.pack(fill='x', pady=5)

    customer_label = tk.Label(yellow_frame, text="Customer:", bg='orange', font=('Helvetica', 12))
    customer_label.pack(side='left', padx=10, pady=5)

    customer_combobox = ttk.Combobox(yellow_frame, values=list(customer_dict.keys()), width=30)
    customer_combobox.pack(side='left', padx=10, pady=5)
    customer_combobox.bind("<<ComboboxSelected>>", update_contact)

    customer_contact_label = tk.Label(yellow_frame, text="Contact: ", bg='orange', font=('Helvetica', 12))
    customer_contact_label.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Source ID:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    source_combobox = ttk.Combobox(yellow_frame, values=list(source_dict.keys()), width=15)
    source_combobox.set("Physical Store")
    source_combobox.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Service ID:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    service_combobox = ttk.Combobox(yellow_frame, values=list(service_dict.keys()), width=15)
    service_combobox.set("Product")
    service_combobox.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Order Date:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    order_date_entry = DateEntry(yellow_frame, width=15, background='darkblue', foreground='white', borderwidth=2)
    order_date_entry.set_date(datetime.now())
    order_date_entry.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Delivery Date:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    expected_delivery_date_entry = DateEntry(yellow_frame, width=15, background='darkblue', foreground='white', borderwidth=2)
    expected_delivery_date_entry.set_date(datetime.now())
    expected_delivery_date_entry.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Payment Status:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    payment_status_entry = ttk.Entry(yellow_frame, width=15)
    payment_status_entry.insert(0, "Pending Payment")
    payment_status_entry.pack(side='left', padx=10, pady=5)

    # Blue bordered section for the data table
    blue_border_frame = tk.Frame(add_order_window, bg='white', highlightbackground='blue', highlightthickness=2)
    blue_border_frame.pack(pady=10, padx=10, fill='both', expand=True)

    form_frame = tk.Frame(blue_border_frame, bg='white')
    form_frame.pack(pady=20, padx=10, fill='both', expand=True)

    # Create the Treeview (data table)
    columns = ("product_id", "product_name", "variant", "total_amount", "discount")
    tree = ttk.Treeview(form_frame, columns=columns, show='headings')

    # Define headings
    tree.heading("product_id", text="Product ID")
    tree.heading("product_name", text="Product Name")
    tree.heading("variant", text="Variant")
    tree.heading("total_amount", text="Total Amount")
    tree.heading("discount", text="Discount")

    tree.pack(fill='both', expand=True)

    def save_new_order():
        customer_name = customer_combobox.get()
        customer_id = customer_dict.get(customer_name, (None, ''))[0]
        order_date = order_date_entry.get_date()
        source_id = source_dict.get(source_combobox.get())
        service_id = service_dict.get(service_combobox.get())
        expected_delivery_date = expected_delivery_date_entry.get_date()
        payment_status = payment_status_entry.get()

        if customer_id is None or source_id is None or service_id is None:
            messagebox.showerror("Input Error", "Please make sure all fields are filled correctly.")
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
            INSERT INTO orders (customerid, orderdate, sourceid, serviceid, paymentstatus, expecteddeliverydate, userid, statusid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING orderid
            """
            cursor.execute(query, (customer_id, order_date, source_id, service_id, payment_status, expected_delivery_date, 1, 1))
            order_id = cursor.fetchone()[0]

            # Insert each product into orderdetails
            for row in tree.get_children():
                product_id, product_name, variant, total_amount, discount = tree.item(row)['values']
                cursor.execute(
                    "INSERT INTO orderdetails (orderid, productid, variant, totalamount, discount) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, product_id, variant, total_amount, discount)
                )

            conn.commit()
            cursor.close()
            conn.close()
            load_treeview_data(tree)
            add_order_window.destroy()
        except Exception as e:
            print(f"Database error: {e}")

    save_button = tk.Button(add_order_window, text="Save", bg='blue', fg='white', command=save_new_order)
    save_button.pack(pady=20)

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

    load_treeview_data(tree)
    poll_database(tree)

def poll_database(tree):
    global last_update
    if (datetime.now() - last_update).seconds >= 10:
        last_update = load_treeview_data(tree, last_update)
    tree.after(10000, lambda: poll_database(tree))

def filter_by_order_id(tree, order_id):
    try:
        conn = connect_db()
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
        conn = connect_db()
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
        conn = connect_db()
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
        conn = connect_db()
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
