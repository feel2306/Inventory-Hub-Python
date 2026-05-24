import streamlit as st
import sqlite3 as sql
from datetime import date
import pandas as pd
import time
import plotly.express as pl
import re

dbname = "inv_hub.db"

st.markdown("""
    <style>
    
    /*Inputs default*/
    .stTextInput>div, .stNumberInput>div, .stDateInput>div>div{
        border-radius: 8px;
    }
    
    /*Inputs on focus*/
    .stTextInput>div:focus-within, 
    .stNumberInput>div:focus-within, 
    .stDateInput>div>div:focus-within {
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 0 5px rgba(0, 174, 239, 0.9) !important;
        transform: translateY(-1px); /* Very slight lift on focus */
    }
    
    /*Button default*/
    .stButton>button, div[data-testid="stFormSubmitButton"] > button{
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    /*Button on hover*/
    .stButton>button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover{
        background-color: #0E1117 !important; 
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 0 8px rgba(0, 174, 239, 0.9) !important;
            
    }
    
    /*Header*/
    .main-header {
        text-align: center;
        color: var(--text-color);
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# Database -- Table creation
def db():
    with sql.connect(dbname) as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            u_id INTEGER PRIMARY KEY AUTOINCREMENT,
            u_name TEXT UNIQUE NOT NULL,
            pass TEXT NOT NULL,
            mobile TEXT NOT NULL)""")
        
        cur.execute("""CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            sell_price REAL NOT NULL,
            buying_price REAL NOT NULL,
            exp_date DATE NOT NULL,
            arrival_date DATE NOT NULL,
            profit REAL NOT NULL,
            UNIQUE(user_id, item_name),
            FOREIGN KEY (user_id) REFERENCES users(u_id))""")

        cur.execute("""CREATE TABLE IF NOT EXISTS sales(
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            date_sold DATE NOT NULL,
            net_profit INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(u_id))""")
        conn.commit()

# login
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    with st.form("login"):
        mobile = st.text_input("Mobile Number", max_chars=10)
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if mobile == "" or not mobile.isdigit() or len(mobile) != 10:
                st.warning("Enter a valid Mobile Number !!")
            elif password == "":
                st.warning("Password cannot be empty !!")
            else:
                with sql.connect(dbname) as con:
                    cursor = con.cursor()
                    cursor.execute(
                        """SELECT u_id, mobile, pass FROM users WHERE mobile = ? AND pass = ?""",
                        (mobile, password),
                    )
                    result = cursor.fetchone()
                    if result:
                        with st.spinner("Logging you in..."):
                            time.sleep(2)
                            st.success("Login successful!")
                            st.session_state.logged_in = True
                            st.session_state.user_id = result[0]
                            st.rerun()
                    else:
                        st.error("Invalid username or password.") 

# register user
def register():
    with st.form("register"):
        name = st.text_input("Enter Username : ")
        password = st.text_input("Enter Password : ", type="password")
        mobile = st.text_input("Enter Mobile No. : ")
        
        if st.form_submit_button("Register"):
            if not name or not password or not mobile:
                st.error("All fields are required !")
            elif not mobile.isdigit() or len(mobile) != 10:
                st.error("Invalid mobile number !")
            elif len(password) < 6 or not re.match("^[A-Za-z](?=.*\d)(?=.*[^A-Za-z0-9]).{5,}$", password):
                st.warning("Enter a valid Password !!")
                st.info("Password must start with a letter, contain a digit, a special character, and be at least 6 characters long.")
            else:
                try:
                    with sql.connect(dbname) as con:
                        cursor = con.cursor()
                        cursor.execute("""INSERT INTO users (u_name, pass, mobile) VALUES (?, ?, ?)""",(name, password, mobile),)
                        con.commit()
                        st.success("Registration successful! Go to log in tab")
                except sql.IntegrityError:
                        st.error("Username already exists !!")

# forgot password
def forgot():
    with st.form("forgot_password"):
        mo = st.text_input("Enter your registered Mobile Number", max_chars=10)
        new_pass = st.text_input("Enter New Password", type="password")
        if st.form_submit_button("Submit"):
            if mo == "" or not mo.isdigit() or len(mo) != 10:
                st.warning("Enter a valid Mobile Number !!")
            elif len(new_pass) < 6 or not re.match("^[A-Za-z](?=.*\d)(?=.*[^A-Za-z0-9]).{5,}$", new_pass):
                st.warning("Enter a valid Password !!")
                st.info("Password must start with a letter, contain a digit, a special character, and be at least 6 characters long.")  
            else:
                with sql.connect(dbname) as con:
                    cur = con.cursor()
                    cur.execute(
                        "SELECT u_name, pass FROM users WHERE mobile = ?",
                        (mo,)
                    )
                    result = cur.fetchone()
                    if result:
                        cur.execute(
                            "UPDATE users SET pass = ? WHERE mobile = ?",
                            (new_pass, mo),
                        )
                        st.success("Password updated successfully! Go to log in tab")
                        con.commit()
                    else:
                        st.error("Mobile Number not found.")

# For checking available stock
def check():
    user_id = st.session_state.user_id
    with sql.connect(dbname) as con:
        cur = con.cursor()
        cur.execute("SELECT item_name, quantity, sell_price, exp_date FROM inventory WHERE user_id = ?", (user_id,))
        data = cur.fetchall()
        if data:
            st.markdown("")
            st.header("⚠️ Expiry alerts")
            st.markdown("")
            for item in data:
                exp = date.fromisoformat(str(item[3]))
                days_left = (exp - date.today()).days
                if days_left < 0:
                    st.error(f"{item[0]} has expired !")
                elif days_left == 0:
                    st.error(f"{item[0]} is expiring today !")
                elif days_left <= 7:
                    st.warning(f"{item[0]} is expiring in {days_left} day(s) !")
            st.header("⚠️ Low Stock Alerts")
            st.markdown("")
            for item in data:
                if item[1] <= 15:
                    st.warning(f"{item[0]} -- only {item[1]} left in stock !")
            st.subheader("")
            st.header("📦 Available Stock")
            st.markdown("")          
            df = pd.DataFrame(data,columns = ["Item Name", "Quantity", "Selling Price", "Expiry Date"])
            st.dataframe(df, use_container_width=True)     
        else:
            st.warning("No items available in inventory.")


# Entry of stocks arrived today
def stock_arrived():
    
    with st.form("stock"):
        
        st.header("📋 Stock Arrived")
        name = st.text_input("Item Name").strip()
        qty = st.number_input("Quantity", min_value=1, step=1)
        sell = st.number_input("Selling Price", min_value=0.5, step=0.01)
        buy = st.number_input("Buying Price", min_value=0.5, step=0.01)
        exp = st.date_input("Expiry Date", min_value=date.today())
        user_id = st.session_state.user_id
        if st.form_submit_button("Add to stock"):
            if not name or not qty or qty <= 0 or not sell or sell <= 0 or not buy or buy <= 0 or exp < date.today():
                st.warning("Please fill all fields with valid values !!")
                return
            if buy > sell:
                st.warning("Buying price cannot be greater than selling price !!")
            else:
                with sql.connect(dbname) as con:
                    cursor = con.cursor()
                    cursor.execute("SELECT item_name FROM inventory WHERE item_name = ? AND user_id = ?", (name, user_id))
                    if cursor.fetchone():
                        st.error("Please choose a different item name !!")
                    else:
                        # Inserting stock into inventory table
                        cursor.execute(
                        """INSERT INTO inventory(user_id, item_name, quantity, sell_price, exp_date, arrival_date, buying_price, profit)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (user_id, name, qty, sell, exp, date.today(), buy, (sell - buy)))
                        st.success("Added to inventory successfully!")
                        con.commit()
                        time.sleep(1)
                        st.rerun()

# selling
def sell():
    with st.form("selling"):
        user_id = st.session_state.user_id
        with sql.connect(dbname) as con:
            cursor = con.cursor()
            cursor.execute("SELECT item_name, quantity, exp_date, sell_price, buying_price FROM inventory WHERE user_id = ?", (user_id,))
            items = cursor.fetchall()
            if items:
                st.markdown("")
                st.header("🛒 Sell Items")
                st.markdown("")
                item_dict = {
                    i[0]: (i[1], i[2], i[3], i[4]) 
                    for i in items
                }
                item = st.selectbox(
                    "Select item to sell",
                    list(item_dict.keys()),
                    index=None,
                    placeholder="Select an item"
                )
                qty_to_sell = st.number_input("Quantity to sell", min_value=1, step=1)
                if st.form_submit_button("Sell"):
                    if not item:
                        st.warning("Please select an item to sell !!")
                        return
                    quantity, expiry_date, sell_price, buy_price = item_dict[item]
                    expiry_date = date.fromisoformat(str(expiry_date))
                    if date.today() > expiry_date:
                        st.error("This item is expired and cannot be sold!")
                        return
                    if qty_to_sell > quantity:
                        st.warning("Insufficient stock to sell !!")
                        return
                    cursor.execute(
                        "UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_name = ?",
                        (qty_to_sell, user_id, item)
                    )
                    cursor.execute(
                        "SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?",
                        (user_id, item)
                    )
                    row = cursor.fetchone()
                    if row and row[0] <= 0:
                        cursor.execute(
                            "DELETE FROM inventory WHERE user_id = ? AND item_name = ?",
                            (user_id, item)
                        )
                    net_profit = (sell_price - buy_price) * qty_to_sell
                    cursor.execute(
                        "INSERT INTO sales (user_id, item_name, quantity, date_sold, net_profit) VALUES (?, ?, ?, ?, ?)",
                        (user_id, item, qty_to_sell, date.today(), net_profit)
                    )
                    con.commit()
                    st.success(f"Successfully sold {qty_to_sell} of {item}.")
                    time.sleep(1)
                    st.rerun()

# Update  
def update():
    with st.form("update item"):
        user_id = st.session_state.user_id
        st.markdown("")
        st.header("📝 Update Price")
        st.markdown("")
        iname = st.text_input("Enter item name to update : ").strip()
        new_price = st.number_input("Enter new Sell Price",min_value=0.5,step=0.01)
        if st.form_submit_button("Update"):
            with sql.connect(dbname) as con:
                cur = con.cursor()
                cur.execute("""
                            SELECT buying_price 
                            FROM inventory 
                            WHERE item_name = ? AND user_id = ?
                        """, (iname, user_id,))
                result = cur.fetchone()
                if result:
                    buy_price = result[0]
                    if new_price <= buy_price:
                        st.error("Sell price must be greater than Buy price !!")
                    else:
                        cur.execute("""
                            UPDATE inventory 
                            SET sell_price = ? 
                            WHERE item_name = ? AND user_id = ?
                        """, (new_price, iname, user_id))
                        con.commit()
                        st.success("Price updated successfully !!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error(f'Item with name "{iname}" doesn\'t exist !!')

# delete item
def delete():
    with st.form("delete"):
        with sql.connect(dbname) as con:
            user_id = st.session_state.user_id
            cursor = con.cursor()
            cursor.execute("SELECT item_name FROM inventory WHERE user_id = ?", (user_id,))
            items = [row[0] for row in cursor.fetchall()]
            if items:
                st.markdown("")
                st.header("🗑️ Delete Item")
                st.markdown("")
                item_to_delete = st.selectbox(
                    "Select item to delete",
                    items,
                    index=None,
                    placeholder="Select an item"
                )
                if st.form_submit_button("Delete"):
                    if not item_to_delete:
                        st.warning("Please select an item to delete !!")
                    else:
                        cursor.execute(
                            "DELETE FROM inventory WHERE user_id = ? AND item_name = ?",
                            (user_id, item_to_delete)
                        )
                        con.commit()
                        st.success(f"{item_to_delete} deleted from inventory.")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("No items available to delete.")


# daily analysis of selling and profit
def analysis():
    user_id = st.session_state.user_id
    with sql.connect(dbname) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT item_name, quantity, date_sold, net_profit FROM sales WHERE user_id = ? AND date_sold = ?",
            (user_id, date.today()),
        )
        sales = cur.fetchall()
        if not sales:
            st.info("No sales data available for analysis.")
        else:
            df = pd.DataFrame(sales, columns=["Item", "Quantity ( Sold )", "Date ( Sold )", "Profit"])
            col1,col2 = st.columns(2)
            with col1:
                fig = pl.bar(
                    df,
                    x="Item",
                    y="Quantity ( Sold )",
                    orientation="v",
                    text="Quantity ( Sold )",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    yaxis_title="Quantity ( Sold )",
                    xaxis_title="Items",
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                fig.update_traces(textposition="inside")
            st.markdown("")
            st.subheader("📈 Today's sales overview")
            st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = pl.bar(
                    df,
                    x="Item",
                    y="Profit",
                    orientation="v",
                    text="Profit",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    yaxis_title="Profit",
                    xaxis_title="Items",
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                fig.update_traces(textposition="inside")
            st.markdown("")
            st.subheader("📈 Today's Profit overview")
            st.markdown("")
            total_profit = df["Profit"].sum()
            st.markdown(f"""
                <div style="
                    background-color: rgba(0, 174, 239, 0.1); 
                    padding: 10px; 
                    border-radius: 20px; 
                    border-left: 3px solid #00AEEF;
                    margin-bottom: 10px;">
                    <h4 style="margin:0; opacity: 0.8;">Net Profit</h4>
                    <h4 style="margin:0; color: #00AEEF;">₹ {total_profit:,.2f}</h4>
                </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            
# Profile settings, change pass,name, mobile
def profile():  
    user_id = st.session_state.user_id
    with sql.connect(dbname) as con:
        cur = con.cursor()
        cur.execute("SELECT u_name, mobile FROM users WHERE u_id = ?",(user_id,))
        user = cur.fetchone()
        name, mobile = user[0], user[1]
        
        st.header("👤 Profile")
        st.markdown("")
        st.markdown("")
        st.write("Name : " + name)
        st.write("Phone no : " + mobile)
        st.markdown("")
        
        opt = st.selectbox(
            "What You want to update ? ",
            ["Select", "Name", "Mobile"],
            index=0
        )
        if opt == "Name":
            new_name = st.text_input("Enter new name : ").strip()
            if st.button("Update Name"):
                if not new_name or new_name == None:
                    st.error("Please enter a valid username !")
                else:
                    cur.execute("SELECT u_name FROM users WHERE u_name = ?",(new_name,))
                    if cur.fetchone() : 
                        st.warning("Username already Exists !!")
                    else:
                        cur.execute("UPDATE users SET u_name = ? WHERE u_id = ?",(new_name, user_id))
                        con.commit()
                        st.success("Name updated successfully !")
                        time.sleep(1)
                        st.rerun()  
        elif opt == "Mobile":
            num = st.text_input("Enter Mobile No : ") 
            if st.button("Update Mobile No"):
                if not num or not num.isdigit() or len(num) != 10:
                    st.error("Invalid mobile number !")
                else :
                    cur.execute("SELECT mobile FROM users WHERE mobile = ?",(num,))
                    if cur.fetchone():
                        st.warning("Mobile number already exists !!")
                    else:
                        cur.execute("UPDATE users SET mobile = ? WHERE u_id = ?",(num,user_id))
                        st.success("Mobile number updated successfully !")
                        con.commit()
                        time.sleep(1)
                        st.rerun()
        st.markdown("")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_page = None
            st.rerun()
                             
# <<<----------- MAIN ----------->>>

st.set_page_config(
    page_title="Inventory Hub",
    page_icon="Inhub.png",
    layout="wide")
db()
st.session_state.setdefault("logged_in", False)
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>📦 Inventory Hub</h1>", unsafe_allow_html=True)
    st.markdown('<div style="border-bottom: 2px solid #00AEEF; margin: 10px 0 40px 0;"></div>',unsafe_allow_html=True,)
    t1, t2, t3 = st.tabs(["Login", "Register", "Forgot"])
    with t1: 
        login()
    with t2: 
        register()
    with t3: 
        forgot()
else:
    st.markdown("<h1 style='text-align:center; padding-bottom:50px'>📦 Inventory Hub</h1>", unsafe_allow_html=True)

    tabs = st.tabs([
        "Available stock",
        "Stock entry",
        "Sell",
        "Update",
        "Delete item(s)",
        "Analysis",
        "Profile"
    ])
    with tabs[0]:
        check()
    with tabs[1]:
        stock_arrived()
    with tabs[2]:
        sell()
    with tabs[3]:
        update()
    with tabs[4]:
        delete()
    with tabs[5]:
        analysis()
    with tabs[6]:
        profile()