import streamlit as st
import sqlite3
import plotly.express as px
import pandas as pd
import warnings
import base64

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Social Media Dashboard", page_icon=":bar_chart:", layout="wide")


# Database connection
def connect_db():
    conn = sqlite3.connect("qwerty.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS qwertys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
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
     
    # Adding background image using custom CSS
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
    # Add the background image
    add_bg_from_local("static/image.jpg")  # Update with your image path

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


# Main Page (Dashboard)
def main_page():
    
    st.title("Social Media Dashboard")
    st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)

    fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
    if fl is not None:
        filename = fl.name
        st.write(filename)
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(fl, engine="openpyxl")
        else:
            df = pd.read_csv(fl, encoding="ISO-8859-1")
    else:
        df = pd.read_excel("C:\\Users\\jayapratha\\Desktop\\social\\sentimentdataset.xlsx", engine="openpyxl")

# Convert 'Timestamp' to datetime if necessary
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Filter by date range
    col1, col2 = st.columns((2))
    startDate = df["Timestamp"].min()
    endDate = df["Timestamp"].max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df = df[(df["Timestamp"] >= date1) & (df["Timestamp"] <= date2)].copy()

# Sidebar filters    
    st.sidebar.header("Choose your filter:")
    platform = st.sidebar.multiselect("Select Platform", df["Platform"].unique())
    country = st.sidebar.multiselect("Select Country", df["Country"].unique())
    hashtags = st.sidebar.multiselect("Select Hashtags", df["Hashtags"].unique())

    filtered_df = df.copy()
    if platform:
        filtered_df = filtered_df[filtered_df["Platform"].isin(platform)]
    if country:
        filtered_df = filtered_df[filtered_df["Country"].isin(country)]
    if hashtags:
        filtered_df = filtered_df[filtered_df["Hashtags"].isin(hashtags)]

# Sentiment analysis summary    
    sentiment_df = filtered_df.groupby("Sentiment", as_index=False)[["Retweets", "Likes"]].sum()

    with col1:
        st.subheader("Sentiment vs Retweets")
        fig = px.bar(sentiment_df, x="Sentiment", y="Retweets", text=sentiment_df["Retweets"], template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sentiment vs Likes")
        fig = px.pie(sentiment_df, values="Likes", names="Sentiment", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
 # Time series analysis
    filtered_df["month_year"] = filtered_df["Timestamp"].dt.to_period("M")
    st.subheader('Time Series Analysis of Engagement')

    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))[["Retweets", "Likes"]].sum()).reset_index()
    fig2 = px.line(linechart, x="month_year", y=["Retweets", "Likes"], labels={"value": "Engagement"}, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Data of TimeSeries:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# Hashtags-based analysis
    st.subheader("Hashtag Analysis")
    hashtag_df = filtered_df.groupby("Hashtags", as_index=False)[["Retweets", "Likes"]].sum()

    fig3 = px.treemap(hashtag_df, path=["Hashtags"], values="Likes", hover_data=["Retweets"], color="Likes")
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader('Country wise Retweets')
        fig = px.pie(filtered_df, values="Retweets", names="Country", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader('Platform wise Likes')
        fig = px.pie(filtered_df, values="Likes", names="Platform", template="gridon")
        st.plotly_chart(fig, use_container_width=True)

# Scatter plot for Retweets vs Likes
    data1 = px.scatter(filtered_df, x="Retweets", y="Likes", size="Retweets")
    data1['layout'].update(title="Relationship between Retweets and Likes",
                       titlefont=dict(size=20), xaxis=dict(title="Retweets", titlefont=dict(size=19)),
                       yaxis=dict(title="Likes", titlefont=dict(size=19)))
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("View Data"):
        st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download original dataset
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="SocialMediaData.csv", mime="text/csv")

# Logout logic
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
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
