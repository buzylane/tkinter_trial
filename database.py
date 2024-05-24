import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database connection parameters
DB_NAME = "BuzylaneMainDB"
DB_USER = "postgres"
DB_PASSWORD = "1qazxsw2"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

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

def fetch_order_ids():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT DISTINCT orderid FROM orders"))
        ids = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return ids
    except Exception as e:
        print(f"Database error: {e}")
        return []

def load_treeview_data(tree, last_update):
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
    return last_update
