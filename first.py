import streamlit as st
import sqlite3

# Database connection
def connect_db():
    conn = sqlite3.connect("qwerty.db")
    return conn

# Add user to database
def add_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO qwertys (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        st.success("User registered successfully!")
    except sqlite3.IntegrityError:
        st.error("Username already exists. Try a different one.")
    conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qwertys WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Register Page
def register_page():
    st.title("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        if username and password:
            add_user(username, password)
        else:
            st.error("Please fill in both fields.")

# Login Page
def login_page():
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user:
                st.success("Login successful!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Please fill in both fields.")

# Main Page
def main_page():
    st.title("Welcome to the Main Page")
    st.write(f"Hello, {st.session_state['username']}!")
    # Logout logic
    if st.button("Logout"):
        # Clear session state to log out the user
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        
        # Trigger a rerun using st.experimental_set_query_params
        st.stop()


# App Logic
def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""

    if st.session_state["logged_in"]:
        main_page()
    else:
        choice = st.sidebar.selectbox("Choose Action", ["Login", "Register"])
        if choice == "Login":
            login_page()
        elif choice == "Register":
            register_page()

if __name__ == "__main__":
    app()