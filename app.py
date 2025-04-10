import streamlit as st
import mysql.connector
import bcrypt
from movies import display_movies

# Connect to MySQL Database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Lamiya@2004",  # Change this
        database="movie_db"
    )

# Hash Password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Check Password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Sign Up Function
def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        conn = connect_db()
        cursor = conn.cursor()
        hashed_password = hash_password(password)  

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, hashed_password))
            conn.commit()
            st.success("User registered successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

# Login Function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password(password, user["password"]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["user_id"] = user["id"]  # Correctly store user ID
            
            st.success("Logged in successfully!")
            st.rerun()
            
if "user_id" in st.session_state:
                st.header("🎬 Movies ")
                display_movies()
else:
            st.error("Invalid username or password.")
# Show Movies
def show_movies():
    st.title("Movies")
    search_query = st.text_input("Search Movies")
    genre_filter = st.selectbox("Filter by Genre", ["All", "Action", "Comedy", "Drama", "Thriller"])

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM movies WHERE title LIKE %s"
    params = [f"%{search_query}%"]
    
    if genre_filter != "All":
        query += " AND genre = %s"
        params.append(genre_filter)

    cursor.execute(query, tuple(params))
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    for movie in movies:
        st.image(movie["image_url"], width=200)
        st.write(f"**{movie['title']}** ({movie['genre']}) - ⭐ {movie['rating']}")
        show_reviews(movie["id"])

# Show Reviews
def show_reviews(movie_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reviews.review_text, users.username 
        FROM reviews 
        JOIN users ON reviews.user_id = users.id 
        WHERE movie_id = %s
    """, (movie_id,))
    
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()

    st.subheader("Reviews")
    for review in reviews:
        st.write(f"**{review['username']}**: {review['review_text']}")

# Write Review
def write_review():
    st.title("Write a Review")

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("You need to log in to write a review.")
        return
    
    movie_id = st.number_input("Movie ID", min_value=1, step=1)
    review_text = st.text_area("Your Review")
           
    if st.button("Submit Review"):
        user_id = st.session_state.get("user_id")
        if user_id is None:
            st.error("Error retrieving user ID. Try logging in again.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO reviews (user_id, movie_id, review_text) VALUES (%s, %s, %s)",
                           (user_id, movie_id, review_text))
            conn.commit()
            st.success("Review submitted successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

# Admin Panel
def admin_panel():
    st.title("Admin Panel")

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("You need to log in as admin to access this panel.")
        return

    new_movie_title = st.text_input("Movie Title")
    new_movie_genre = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Thriller"])
    new_movie_image = st.text_input("Movie Image URL")

    if st.button("Add Movie"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, genre, image_url) VALUES (%s, %s, %s)",
                       (new_movie_title, new_movie_genre, new_movie_image))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Movie added successfully!")

    delete_movie_id = st.number_input("Movie ID to Delete", min_value=1, step=1)
    if st.button("Delete Movie"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = %s", (delete_movie_id,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Movie deleted successfully!")

# Session Management
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Movies", "Write Review", "Admin Panel"])

if not st.session_state["logged_in"]:
    login()
    if st.button("Sign Up Instead"):
        signup()
else:
    if page == "Movies":
        show_movies()
    elif page == "Write Review":
        write_review()
    elif page == "Admin Panel":
        admin_panel()
