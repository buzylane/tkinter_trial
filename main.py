import subprocess
import os
import tkinter as tk
from tkinter import ttk
import psycopg2
from psycopg2 import sql
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime


# Global variable to store user ID and username
global_user_id = None
global_username = None


# Function to update the script from the GitHub repository
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

# Database connection parameters
DB_NAME = "BuzylaneMainDB"
DB_USER = "postgres"
DB_PASSWORD = "1qazxsw2"
DB_HOST = "192.168.8.179"
DB_PORT = "5432"


last_update = datetime.now()  # Initialize last_update

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None


def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()


def load_content(button_name):
    clear_content()
    if button_name == "Login":
        setup_login(content_frame)
    elif button_name == "Orders/Transactions":
        setup_orders_transactions(content_frame)
    elif button_name == "Revenue":
        setup_orders_transactions(content_frame)
    else:
        tk.Label(content_frame, text=f"Content for {button_name}", font=('Helvetica', 16), bg='white').pack(pady=20)


def setup_login(frame):
    # Clear any existing content and hide navigation
    clear_content()
    nav_frame.grid_remove()  # Ensure nav_frame is not visible

    # Main login frame centered in the content frame
    login_frame = tk.Frame(frame, bg='white')
    login_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Styling for the entries and buttons
    style = ttk.Style()
    style.configure('TLabel', background='white', font=('Arial', 12))
    style.configure('TEntry', font=('Arial', 12), padding=5)
    style.configure('Login.TButton', font=('Arial', 12), background='white', padding=5)
    style.map('Login.TButton',
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '!disabled', '#0073e6'), ('active', '#0056b3')])

    # Title Label
    title_label = ttk.Label(login_frame, text="Login to Your Account", font=('Arial', 16, 'bold'), background='white')
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Username and password labels and entries
    username_label = ttk.Label(login_frame, text="Username:", style='TLabel')
    username_label.grid(row=1, column=0, sticky='e', padx=10, pady=10)
    username_entry = ttk.Entry(login_frame, width=30)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    password_label = ttk.Label(login_frame, text="Password:", style='TLabel')
    password_label.grid(row=2, column=0, sticky='e', padx=10, pady=10)
    password_entry = ttk.Entry(login_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    # Login button
    login_button = ttk.Button(login_frame, text="Login", style='Login.TButton',
                              command=lambda: login(username_entry.get(), password_entry.get()))
    login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="ew")  # Make it fill the space

    # Bind the Enter key to the login function when focused on either entry field
    username_entry.bind('<Return>', lambda event: login(username_entry.get(), password_entry.get()))
    password_entry.bind('<Return>', lambda event: login(username_entry.get(), password_entry.get()))

    # Adjust column configuration for better alignment
    login_frame.columnconfigure(0, weight=1)
    login_frame.columnconfigure(1, weight=2)
    username_entry.focus()

def login(username, password):
    conn = connect_db()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT userid, username FROM users WHERE username = %s AND password = %s", (username, password))
            user_record = cursor.fetchone()
            cursor.close()
            conn.close()
            if user_record:
                global global_user_id, global_username
                global_user_id, global_username = user_record
                header_label.config(text=f"STORE MANAGEMENT SYSTEM - Logged in as: {global_username}")
                display_navigation_buttons()
                nav_frame.grid(row=1, column=0, sticky="ns")
                load_content("Dashboard")
            else:
                messagebox.showerror("Login Failed", "Incorrect username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            if conn is not open:
                conn.close()
    else:
        messagebox.showerror("Connection Error", "Failed to connect to the database.")



def logout():
    clear_content()
    nav_frame.grid_remove()  # Hide navigation on logout
    setup_login(content_frame)
    header_label.config(text=f"STORE MANAGEMENT SYSTEM - Please login")

def display_navigation_buttons():
    # Navigation buttons are displayed only after successful login
    buttons = ["Dashboard", "Orders/Transactions", "Revenue", "Inventory", "Expenditure", "Hairstylists"]
    for idx, button in enumerate(buttons):
        action = lambda b=button: load_content(b)
        tk.Button(nav_frame, text=button, bg='orange', fg='black', height=2, width=20, command=action).grid(row=idx, column=0, padx=10, pady=10, sticky="ew")
    logout_button = tk.Button(nav_frame, text="Logout", bg='red', fg='white', height=2, width=20, command=logout)
    logout_button.grid(row=len(buttons), column=0, padx=10, pady=10, sticky="ew")


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

    # Add Order button and other buttons
    tk.Button(top_panel, text="Add Order", bg='blue', fg='white', command=add_order).pack(side='left', padx=5, pady=5)

    buttons_info = [
        ("Today's Orders", 'blue', filter_todays_orders),
        ("This Month Orders", 'blue', filter_this_month_orders),
        ("All Orders/Refresh", 'blue', load_treeview_data),
        ("All Cancelled Orders", 'blue', filter_cancelled_orders)
    ]
    for text, color, command in buttons_info:
        tk.Button(top_panel, text=text, bg=color, fg='white', command=lambda c=command: c(tree)).pack(side='left', padx=5, pady=5)

    # Filters
    filters = ["ORDER ID", "PAYMENT STATUS", "DELIVERY DATE", "ORDER STATUS", "EXTERNAL PAYMENT"]
    order_ids = fetch_order_ids()
    for text in filters:
        ttk.Label(top_panel, text=text).pack(side='left', padx=5)
        if text == "ORDER ID":
            order_id_combobox = ttk.Combobox(top_panel, values=order_ids, width=15)
            order_id_combobox.pack(side='left', padx=5)
            order_id_combobox.bind("<<ComboboxSelected>>", lambda e: filter_by_order_id(tree, order_id_combobox.get()))
        else:
            ttk.Entry(top_panel, width=15).pack(side='left', padx=5)

    # Add Order button
    tk.Button(top_panel, text="Add Order", bg='blue', fg='white', command=add_order).pack(side='right', padx=5, pady=5)

    # Assuming the yellow frame has a specific height and padding, replicate those values here
    separator_frame = tk.Frame(frame, bg='light blue',
                               height=50)  # Adjust height as per the yellow frame's actual height
    separator_frame.pack(fill='x', padx=10, pady=5)  # Adjust padding to match the yellow frame's padding

    setup_treeview(frame)

# Fetch customers, sources, and services for dropdowns
def fetch_customers():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT customerid, firstname || ' ' || lastname AS customer_name, phone FROM customers")
        customers = cursor.fetchall()
        cursor.close()
        conn.close()
        return {f"{row[1]} (ID: {row[0]})": (row[0], row[2]) for row in customers}
    except Exception as e:
        print(f"Database error: {e}")
        return {}



def fetch_sources():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT sourceid, sourcename FROM ordersource")
        sources = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[1]: row[0] for row in sources}
    except Exception as e:
        print(f"Database error: {e}")
        return {}

def fetch_services():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT serviceid, servicename FROM servicetype")
        services = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[1]: row[0] for row in services}
    except Exception as e:
        print(f"Database error: {e}")
        return {}

def fetch_products():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT productid, name FROM products")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[0]: row[1] for row in products}
    except Exception as e:
        print(f"Database error: {e}")
        return {}
def fetch_payment_methods():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT method_name FROM payment_methods")  # Adjust the table and column names based on your schema
        methods = cursor.fetchall()
        cursor.close()
        conn.close()
        return [method[0] for method in methods]  # Assuming methodname is stored in the first column
    except Exception as e:
        print(f"Database error: {e}")
        return []

class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self._hits = []  # Initialize _hits here to ensure it's always defined
        self.bind('<KeyRelease>', self.handle_key_release)
        self.bind('<Return>', self.select_value)
        self.bind('<<ComboboxSelected>>', self.on_combobox_selected)
        self.bind('<Button-1>', self.on_mouse_click)  # Bind mouse click event

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # Ensure list is sorted
        self['values'] = self._completion_list  # Set the values immediately

    def handle_key_release(self, event):
        # Ignore navigation keys that should be processed by the combobox itself.
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Down', 'Up', 'Escape', 'Tab'):
            return

        # Update dropdown to reflect current text input
        self.update_dropdown()

    def update_dropdown(self):
        sub = self.get()
        self._hits = [x for x in self._completion_list if x.lower().startswith(sub.lower())] if sub else self._completion_list
        self['values'] = self._hits if self._hits else ['No match found']
        self.show_dropdown()

    def show_dropdown(self):
        if self._hits:  # Only show dropdown if there are hits
            self.event_generate('<Down>')
        self.focus()  # Set focus back to the combobox
        self.icursor(tk.END)  # Ensure cursor stays at the end of input

    def on_mouse_click(self, event):
        """Handle mouse click to potentially display all items if dropdown arrow is clicked."""
        if self['state'] != 'readonly':  # Check if the combobox is in editable state
            width = self.winfo_width()
            if event.x > width - 20:  # Assuming the dropdown arrow is about 20 pixels wide
                self['values'] = self._completion_list  # Reset to show all values
                self.show_dropdown()

    def select_value(self, event=None):
        if self.get() in self._completion_list:
            self.icursor(tk.END)  # Move cursor to the end if the value is selected
        else:
            self.set('')
            self['values'] = self._completion_list

    def on_combobox_selected(self, event=None):
        self.icursor(tk.END)  # Move cursor to the end upon selection
        self.selection_clear()


def add_order(order_id=None):
    customer_dict = fetch_customers()
    source_dict = fetch_sources()
    service_dict = fetch_services()
    products_dict = fetch_products()

    def save_order():
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
            conn = connect_db()
            cursor = conn.cursor()
            new_order_id = None

            if order_id:
                query = """
                UPDATE orders SET customerid=%s, orderdate=%s, sourceid=%s, serviceid=%s, paymentstatus=%s, expecteddeliverydate=%s
                WHERE orderid=%s
                """
                cursor.execute(query, (
                customer_id, order_date, source_id, service_id, payment_status, expected_delivery_date, order_id))
                cursor.execute("DELETE FROM orderdetails WHERE orderid = %s", (order_id,))
                new_order_id = order_id
            else:
                query = """
                INSERT INTO orders (customerid, orderdate, sourceid, serviceid, paymentstatus, expecteddeliverydate, userid, statusid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING orderid
                """
                cursor.execute(query, (
                customer_id, order_date, source_id, service_id, payment_status, expected_delivery_date, 1, 1))
                new_order_id = cursor.fetchone()[0]

            for row in tree.get_children():
                product_info = tree.item(row)['values']
                product_id = product_info[0]
                variant = product_info[2]
                quantity = int(product_info[3])
                unit_price = float(product_info[4])
                cursor.execute(
                    "INSERT INTO orderdetails (orderid, productid, variant, quantity, unitprice) VALUES (%s, %s, %s, %s, %s)",
                    (new_order_id, product_id, variant, quantity, unit_price)
                )

            conn.commit()
            cursor.close()
            conn.close()
            load_treeview_data(tree)
            add_order_window.destroy()
        except Exception as e:
            print(f"Database error: {e}")


    # Only use product IDs for the dropdown
    product_ids = [str(pid) for pid in products_dict.keys()]

    # Fetch all product names and variants
    def fetch_all_product_details():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT productid, name, variant, retailprice FROM products")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            return products
        except Exception as e:
            print(f"Database error: {e}")
            return []

    def fetch_variants_by_product_name(product_name):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT variant FROM products WHERE name = %s ORDER BY variant", (product_name,))
            variants = cursor.fetchall()
            cursor.close()
            conn.close()
            return [variant[0] for variant in variants]
        except Exception as e:
            print(f"Database error: {e}")
            return []

    def fetch_product_id_by_name_and_variant(product_name, variant):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT productid FROM products WHERE name = %s AND variant = %s", (product_name, variant))
            product_id = cursor.fetchone()
            cursor.close()
            conn.close()
            return product_id[0] if product_id else None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def fetch_unit_price(product_name, variant):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT retailprice FROM products WHERE name = %s AND variant = %s", (product_name, variant))
            retail_price = cursor.fetchone()
            cursor.close()
            conn.close()
            return retail_price[0] if retail_price else None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    all_products = fetch_all_product_details()

    product_names = {product[1]: product[0] for product in all_products}
    product_variants = {product[2]: product[0] for product in all_products}
    product_prices = {product[0]: product[3] for product in all_products}

    order_details, product_details = fetch_order_details(order_id) if order_id else (None, [])
    print(order_id)

    def update_contact(event):
        customer_name = customer_combobox.get()
        contact = customer_dict.get(customer_name, (None, ''))[1]
        customer_contact_label.config(text=f"Contact: {contact}")

    def fetch_product_details(product_id):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name, variant, retailprice FROM products WHERE productid = %s", (product_id,))
            product_details = cursor.fetchone()
            cursor.close()
            conn.close()
            return product_details
        except Exception as e:
            print(f"Database error: {e}")
            return None, None, None

    def update_product_details(event):
        product_id = product_id_combobox.get()
        product_details = fetch_product_details(product_id)
        if product_details:
            product_name, variant, retail_price = product_details
            product_name_combobox.set(product_name)
            variant_combobox.set(variant)
            unit_price_entry.delete(0, tk.END)
            unit_price_entry.insert(0, retail_price)
            calculate_amount(None)

    def update_variants(event):
        product_name = product_name_combobox.get()
        variants = fetch_variants_by_product_name(product_name)
        variant_combobox.set_completion_list(variants)
        if variants:
            variant_combobox.set(variants[0])
            update_product_id(None)

    def update_product_id(event):
        product_name = product_name_combobox.get()
        variant = variant_combobox.get()
        product_id = fetch_product_id_by_name_and_variant(product_name, variant)
        product_id_combobox.set(product_id)
        unit_price = fetch_unit_price(product_name, variant)
        unit_price_entry.delete(0, tk.END)
        unit_price_entry.insert(0, unit_price)
        calculate_amount(None)

    def calculate_total_bill():
        total = 0.0
        for child in tree.get_children():
            total += float(tree.item(child)['values'][5])  # Assumes total amount is in the sixth column (index 5)
        total_bill_entry.delete(0, tk.END)
        total_bill_entry.insert(0, f"{total:.2f}")

    add_order_window = tk.Toplevel(root)
    add_order_window.title(f"Edit Order #{order_id}" if order_id else "Add New Order")
    add_order_window.geometry("1800x900")
    add_order_window.configure(bg='white')

    top_frame = tk.Frame(add_order_window, bg='gray', height=50)
    top_frame.pack(fill='x')

    top_label = tk.Label(top_frame, text="Order Management", bg='gray', fg='white', font=('Helvetica', 16))
    top_label.pack(side='left', pady=10, padx=20)

    add_customer_button = tk.Button(top_frame, text="Add New Customer", bg='blue', fg='white', command=None)
    add_customer_button.pack(side='left', padx=10, pady=5)

    add_order_button = tk.Button(top_frame, text="Add New Order", bg='blue', fg='white', command=None)
    add_order_button.pack(side='left', padx=10, pady=5)

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
    source_combobox.pack(side='left', padx=10, pady=5)

    tk.Label(yellow_frame, text="Service ID:", bg='orange', font=('Helvetica', 12)).pack(side='left', padx=10, pady=5)
    service_combobox = ttk.Combobox(yellow_frame, values=list(service_dict.keys()), width=15)
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

    if order_id:
        customer_combobox.set(next((k for k, v in customer_dict.items() if v[0] == order_details[0]), ''))
        source_combobox.set(next((k for k, v in source_dict.items() if v == order_details[1]), ''))
        service_combobox.set(next((k for k, v in service_dict.items() if v == order_details[2]), ''))
        order_date_entry.set_date(order_details[3])
        expected_delivery_date_entry.set_date(order_details[4])
        payment_status_entry.delete(0, tk.END)
        payment_status_entry.insert(0, order_details[5])

    product_entry_frame = tk.Frame(add_order_window, bg='lightblue')
    product_entry_frame.pack(fill='x', pady=5)

    # Product ID
    product_id_frame = tk.Frame(product_entry_frame, bg='lightblue')
    product_id_frame.pack(side='left', padx=5, pady=5)
    tk.Label(product_id_frame, text="Product ID:", bg='lightblue').pack(anchor='w')
    product_id_combobox = AutocompleteCombobox(product_id_frame, width=30)
    product_id_combobox.set_completion_list(product_ids)
    product_id_combobox.pack()
    product_id_combobox.bind("<<ComboboxSelected>>", update_product_details)

    # Product Name
    product_name_frame = tk.Frame(product_entry_frame, bg='lightblue')
    product_name_frame.pack(side='left', padx=5, pady=5)
    tk.Label(product_name_frame, text="Product Name:", bg='lightblue').pack(anchor='w')
    product_name_combobox = AutocompleteCombobox(product_name_frame, width=30)
    product_name_combobox.set_completion_list(list(product_names.keys()))
    product_name_combobox.pack()
    product_name_combobox.bind("<<ComboboxSelected>>", update_variants)

    # Variant
    variant_frame = tk.Frame(product_entry_frame, bg='lightblue')
    variant_frame.pack(side='left', padx=5, pady=5)
    tk.Label(variant_frame, text="Variant:", bg='lightblue').pack(anchor='w')
    variant_combobox = AutocompleteCombobox(variant_frame, width=30)
    variant_combobox.set_completion_list([])
    variant_combobox.pack()
    variant_combobox.bind("<<ComboboxSelected>>", update_product_id)

    # Unit Price
    unit_price_frame = tk.Frame(product_entry_frame, bg='lightblue')
    unit_price_frame.pack(side='left', padx=5, pady=5)
    tk.Label(unit_price_frame, text="Unit Price:", bg='lightblue').pack(anchor='w')
    unit_price_entry = ttk.Entry(unit_price_frame, width=10)
    unit_price_entry.pack()

    # Quantity
    quantity_frame = tk.Frame(product_entry_frame, bg='lightblue')
    quantity_frame.pack(side='left', padx=5, pady=5)
    tk.Label(quantity_frame, text="Quantity:", bg='lightblue').pack(anchor='w')
    quantity_entry = ttk.Entry(quantity_frame, width=10)
    quantity_entry.insert(0, "1")  # Set default quantity to 1
    quantity_entry.pack()

    # Total Amount
    amount_frame = tk.Frame(product_entry_frame, bg='lightblue')
    amount_frame.pack(side='left', padx=5, pady=5)
    tk.Label(amount_frame, text="Total Amount:", bg='lightblue').pack(anchor='w')
    amount_entry = ttk.Entry(amount_frame, width=15)
    amount_entry.pack()

    def calculate_amount(event):
        try:
            quantity = int(quantity_entry.get())
            unit_price = float(unit_price_entry.get())
            amount = quantity * unit_price
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, f"{amount:.2f}")
        except ValueError:
            amount_entry.delete(0, tk.END)

    quantity_entry.bind("<KeyRelease>", calculate_amount)
    unit_price_entry.bind("<KeyRelease>", calculate_amount)

    button_frame = tk.Frame(product_entry_frame, bg='lightblue')
    button_frame.pack(side='left', padx=10, pady=5)

    add_product_button = tk.Button(button_frame, text="Add Product", bg='green', fg='white',
                                   command=lambda: add_product_to_tree(product_id_combobox.get(),
                                                                       product_name_combobox.get(),
                                                                       variant_combobox.get(), quantity_entry.get(),
                                                                       unit_price_entry.get(), amount_entry.get()))
    add_product_button.pack(side='left', padx=10)

    delete_button = tk.Button(button_frame, text="Delete Product", bg='red', fg='white',
                              command=lambda: delete_product(tree))
    delete_button.pack(side='left', padx=10)

    save_button = tk.Button(button_frame, text="Save", bg='blue', fg='white', command=save_order)
    save_button.pack(side='left', padx=10)

    receive_payment_button = tk.Button(button_frame, text="Receive Payment", bg='blue', fg='white',
                                       command=lambda: receive_payment(order_id, add_order_window))
    receive_payment_button.pack(side='left', padx=10, pady=10)



    def add_product_to_tree(product_id, product_name, variant, quantity, unit_price, totalamount):
        tree.insert('', 'end', values=(product_id, product_name, variant, quantity, unit_price, totalamount))
        calculate_total_bill()

    blue_border_frame = tk.Frame(add_order_window, bg='white', highlightbackground='blue', highlightthickness=2)
    blue_border_frame.pack(pady=10, padx=10, fill='both', expand=True)

    form_frame = tk.Frame(blue_border_frame, bg='white')
    form_frame.pack(pady=20, padx=10, fill='both', expand=True)

    columns = ("product_id", "product_name", "variant", "quantity", "unit_price", "totalamount")
    tree = ttk.Treeview(form_frame, columns=columns, show='headings')

    tree.heading("product_id", text="Product ID")
    tree.heading("product_name", text="Product Name")
    tree.heading("variant", text="Variant")
    tree.heading("quantity", text="Quantity")
    tree.heading("unit_price", text="Unit Price")
    tree.heading("totalamount", text="Total Amount")

    tree.pack(fill='both', expand=True)
    bill_frame = tk.Frame(add_order_window, bg='lightblue', height=200)  # Set a fixed height for more prominent display
    bill_frame.pack(fill='x', padx=20, pady=10, side='bottom')  # Ensure it's at the bottom or another strategic location

    # Empty space Label to push the Bill label and entry to the right
    spacer_label = tk.Label(bill_frame, text="", bg='lightblue')
    spacer_label.pack(side='left', expand=True)

    bill_label = tk.Label(bill_frame, text="Bill:", bg='lightblue', font=('Helvetica', 12))
    bill_label.pack(side='left', padx=20, pady=10)

    total_bill_entry = tk.Entry(bill_frame, width=20, font=('Helvetica', 12))
    total_bill_entry.pack(side='left', padx=10, pady=5)

    def delete_product(tree):
        selected_item = tree.selection()
        if selected_item:
            tree.delete(selected_item)
            # Optionally, set focus back to the tree or a specific part of the form
            tree.focus_set()
            calculate_total_bill()
    # Initialize the total bill calculation
    calculate_total_bill()

    for product in product_details:
        product_id = product[0]
        product_name = fetch_product_name(product_id)
        variant = product[1]
        quantity = product[2]
        unit_price = product[3]
        total_amount = product[4]
        add_product_to_tree(product_id, product_name, variant, quantity, unit_price, total_amount)

def receive_payment(order_id, parent_window):
    payment_methods = fetch_payment_methods()  # Fetch payment methods from the database

    payment_window = tk.Toplevel(parent_window)
    payment_window.title("Receive Payment")
    payment_window.geometry("400x250")

    # Calculate position to center the window on the parent window
    window_width = payment_window.winfo_reqwidth()
    window_height = payment_window.winfo_reqheight()
    position_right = int(parent_window.winfo_x() + (parent_window.winfo_width() / 2 - window_width / 2))
    position_down = int(parent_window.winfo_y() + (parent_window.winfo_height() / 2 - window_height / 2))
    payment_window.geometry("+{}+{}".format(position_right, position_down))

    tk.Label(payment_window, text="Receive Payment", font=('Helvetica', 16)).pack(pady=(20, 10))

    # Payment Amount
    tk.Label(payment_window, text="Payment Amount:", font=('Helvetica', 12)).pack()
    payment_amount_entry = ttk.Entry(payment_window, width=20)
    payment_amount_entry.pack(pady=(0, 20))

    # Payment Method
    tk.Label(payment_window, text="Payment Method:", font=('Helvetica', 12)).pack()
    payment_method_combobox = ttk.Combobox(payment_window, values=payment_methods, width=18)
    payment_method_combobox.pack(pady=(0, 20))



    # Confirm and Cancel Buttons
    confirm_button = tk.Button(payment_window, text="Confirm", bg='blue', fg='white',
                               command=lambda: confirm_payment(order_id, payment_amount_entry.get(), payment_method_combobox.get(), payment_window, parent_window))
    confirm_button.pack(side='left', padx=(50, 10), pady=20)

    cancel_button = tk.Button(payment_window, text="Cancel", bg='red', fg='white', command=payment_window.destroy)
    cancel_button.pack(side='right', padx=(10, 50), pady=20)



def confirm_payment(order_id, amount, payment_method, payment_window, add_order_window):
    # Process the payment here (mocked as successful for example)
    print("Processing payment...")  # Replace with actual payment processing logic
    # Assuming payment was successful
    messagebox.showinfo("Payment Successful", f"Payment of {amount} using {payment_method} has been processed successfully for order number {order_id}")

    # Close the payment window and the add order window
    payment_window.destroy()
    add_order_window.destroy()



def on_treeview_double_click(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        order_id = item['values'][0]
        add_order(order_id)


def fetch_product_name(product_id):
    try:
        conn = connect_db()  # Ensure that this function uses your existing database connection logic
        cursor = conn.cursor()
        # Execute the query to get the product name using the product_id
        cursor.execute("SELECT name FROM products WHERE productid = %s", (product_id,))
        product_name = cursor.fetchone()
        if product_name:
            return product_name[0]  # Return the name part of the fetched tuple
        else:
            return "Unknown Product"  # Return a default name if the product ID is not found
    except Exception as e:
        print(f"Error fetching product name: {e}")
        return "Error fetching name"  # Return an error message if something goes wrong
    finally:
        cursor.close()
        conn.close()


def fetch_order_details(order_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch main order details
        cursor.execute("""
            SELECT customerid, sourceid, serviceid, orderdate, expecteddeliverydate, paymentstatus
            FROM orders
            WHERE orderid = %s
        """, (order_id,))
        order = cursor.fetchone()

        # If the order exists, fetch the associated products
        if order:
            cursor.execute("""
                SELECT productid, variant, quantity, unitprice, totalamount
                FROM orderdetails
                WHERE orderid = %s
            """, (order_id,))
            products = cursor.fetchall()
        else:
            order = None
            products = []

        cursor.close()
        conn.close()

        return order, products
    except Exception as e:
        print(f"Database error while fetching order details: {e}")
        return None, []

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
        cursor.execute(sql.SQL("SELECT DISTINCT orderid FROM orders ORDER BY orderid DESC"))
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

    tree.bind("<Double-1>", on_treeview_double_click)

    load_treeview_data(tree)
    # poll_database(tree)

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

# def poll_database(tree):
#     global last_update
#     if (datetime.now() - last_update).seconds >= 10:
#         load_treeview_data(tree)
#     tree.after(10000, lambda: poll_database(tree))

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
            # open_transaction_details(order_id, rows[0])  # Open the modal form with the order details
            add_order(order_id)
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


root = tk.Tk()
root.title("Business Dashboard")
root.geometry("1800x900")

# Maximize the window when it opens
root.state('zoomed')

header_frame = tk.Frame(root, bg='gray')
header_frame.grid(row=0, column=0, sticky="ew", columnspan=2)
header_label = tk.Label(header_frame, text=f"STORE MANAGEMENT SYSTEM - Please Login", bg='gray', fg='white', font=('Helvetica', 20))
header_label.pack(pady=20, fill='x')

nav_frame = tk.Frame(root, width=200, bg='blue')
nav_frame.grid(row=1, column=0, sticky="ns")
content_frame = tk.Frame(root, bg='white')
content_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

# buttons = ["Login","Dashboard","Orders/Transactions", "Revenue", "Inventory", "Expenditure", "Hairstylists"]
# for idx, button in enumerate(buttons):
#     action = lambda b=button: load_content(b)
#     tk.Button(nav_frame, text=button, bg='orange', fg='black', height=2, width=20, command=action).grid(row=idx, column=0, padx=10, pady=10, sticky="ew")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

def auto_login():
    global global_user_id, global_username
    global_user_id = 1  # Default user ID for development
    global_username = "Developer"
    header_label.config(text=f"STORE MANAGEMENT SYSTEM - Logged in as: {global_username}")
    display_navigation_buttons()
    nav_frame.grid(row=1, column=0, sticky="ns")
    load_content("Dashboard")

# Uncomment the following line to enable auto-login
auto_login()
# setup_login(content_frame)

root.mainloop()