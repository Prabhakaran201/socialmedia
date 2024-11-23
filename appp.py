import streamlit as st
import base64

def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Login Page
def login_page():
    st.title("Login")
    
    # Add the background image
    add_bg_from_local("C:/Users/jayapratha/Desktop/pro/static/image.jpg")  # Update with your image path

    # Login form content
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if username and password:
            # Authenticate user here (implement your authentication logic)
            st.success("Login successful!")
        else:
            st.error("Please fill in both fields.")

# Example app function to display login page
def app():
    login_page()

if __name__ == "__main__":
    app()
