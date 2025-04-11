import streamlit as st
import mysql.connector
import bcrypt

from dotenv import load_dotenv
import os
import sys

with open("style.css") as f:
    css = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


print(sys.path) 

print(os.getenv("DB_HOST"))
load_dotenv()
def connect_db():
     try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
       
        return conn
     except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_genres():
    conn=connect_db()
    if conn:
         cursor = conn.cursor(dictionary=True)
         cursor.execute("SELECT DISTINCT genre FROM movies")
         genres = [row["genre"] for row in cursor.fetchall()]
         conn.close()
         return genres
    return []
def change_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()  

def get_movies(search_query=None, selected_genre=None):
    conn = connect_db() 
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM movies"
        params = []

        if search_query:
            query += " WHERE title LIKE %s"
            params.append(f"%{search_query}%")

        if selected_genre and selected_genre != "All":
            query += " AND genre = %s" if search_query else " WHERE genre = %s"
            params.append(selected_genre)

        cursor.execute(query, params)
        movies = cursor.fetchall()
        conn.close()
        return movies
    return []

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

    if st.button("Sign Up"):
        if username and email and password:
            try:
                conn = connect_db()
                cursor = conn.cursor()

                hashed_password = hash_password(password)
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                               (username, email, hashed_password))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                st.success("Account created successfully! Please log in.")
                st.session_state["authenticated"] = True
                change_page("Login")  

            except mysql.connector.Error as e:
                st.error(f"Database error: {e}")
        else:
            st.warning("Please fill in all fields.")

# Login Function
def login():
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password(password, user["password"]):
                st.success("Login successful!")
                st.session_state["logged_in"] = True
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user["id"]
                st.session_state["username"] = user["username"]
                st.session_state["user_role"] = "admin" if user["is_admin"] else "user"  
                st.session_state["page"] = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password.")
        except mysql.connector.Error as e:
            st.error(f"Database error: {e}")
def show_dashboard():
    st.title("🍿 Movie Dashboard")
    st.write("Choose an action:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🎬 View Movies", key="view_movies"):
            st.session_state["page"] = "Movies"
            st.rerun()
            
    with col2:
        if st.button("✍️ Write Review", key="write_review"):
            st.session_state["page"] = "Write Review"
            st.rerun()
            

    with col3:
        if st.button("⭐ Rate Movie", key="rate_movie"):
            st.session_state["page"] = "Rate Movie"
            st.rerun()
            

    if st.session_state["user_role"] == "admin":
        with col4:
            if st.button("⚙️ Admin Panel", key="admin_panel"):
                st.session_state["page"] = "Admin Panel"
                st.rerun()
                
# Show Movies
def show_movies():
    st.title("🎬 Movie List with Ratings & Reviews")

    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()
        search_query = st.text_input("Search for a movie", "")
        genres = ["All"] + get_genres()
        selected_genre = st.selectbox("Filter by Genre", genres)
    
        movies = get_movies(search_query, selected_genre)
    
        if not movies:
          st.write("No movies found.")
        for movie in movies:
            # Fetch average rating from the ratings table
            cursor.execute("SELECT AVG(rating) as avg_rating FROM ratings WHERE movie_id = %s", (movie["id"],))
            avg_rating = cursor.fetchone()["avg_rating"]
            avg_rating = round(avg_rating, 1) if avg_rating else "No ratings yet"

            # Fetch reviews from the reviews table
            cursor.execute("""
                SELECT u.username, r.review_text
                FROM reviews r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.movie_id = %s
            """, (movie["id"],))
            reviews = cursor.fetchall()

     
            image_url = movie.get("image_url", "")
           


            # Display movie details
            with st.container():
                st.markdown(f"""
                    <div style="border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: white; display: flex; align-items: center;">
                        {'<img src="' + image_url + '" width="200" height="220" style="margin-right: 15px; border-radius: 8px;">' if image_url else ""}
                        <div>
                            st.markdown(f'<h1 class="movie-title">{movie["title"]}</h1>', unsafe_allow_html=True)
                            st.markdown(f'<h2 class="movie-title">{movie["genre"]}</h2>', unsafe_allow_html=True)
                            st.markdown(f'<h2 style="color: black; text-shadow: 2px 2px 4px black;">⭐ {avg_rating}</h2>', unsafe_allow_html=True)

                            

                        
                    </div>
                """, unsafe_allow_html=True)

                # Display user reviews
                if reviews:
                    st.subheader("User Reviews:")
                    for review in reviews:
                        st.markdown(f"""
                            <div style="border-left: 5px solid #2E86C1; padding-left: 10px; margin-bottom: 10px;">
                                <p>{review['username']}</p> :
                                <b>{review['review_text']}</b>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No reviews yet.")

                st.write("---")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


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

def rate_movie():
    st.title("⭐ Rate a Movie")

    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch movies
        cursor.execute("SELECT id, title FROM movies")
        movies = cursor.fetchall()

        if not movies:
            st.warning("No movies available to rate.")
            return

        # Movie selection
        movie_options = {movie["title"]: movie["id"] for movie in movies}
        movie_name = st.selectbox("Select a movie", list(movie_options.keys()))

        # Select rating
        rating = st.slider("Rate the movie (1-5 stars)", min_value=1, max_value=5, value=3)

        if st.button("Submit Rating"):
            movie_id = movie_options[movie_name]

            # Check if the user has already rated this movie
            cursor.execute("SELECT * FROM ratings WHERE user_id = %s AND movie_id = %s", (user_id, movie_id))
            existing_rating = cursor.fetchone()

            if existing_rating:
                # Update rating if it exists
                cursor.execute("UPDATE ratings SET rating = %s WHERE user_id = %s AND movie_id = %s",
                               (rating, user_id, movie_id))
                st.success(f"Updated your rating for {movie_name} to {rating} ⭐")
            else:
                # Insert new rating
                cursor.execute("INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)",
                               (user_id, movie_id, rating))
                st.success(f"Thank you for rating {movie_name}! ⭐ {rating}")

            conn.commit()

    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")

    finally:
        cursor.close()
        conn.close()

# Admin Panel
def admin_panel():
    st.title("Admin Panel")
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("You need to log in to access this panel.")
        return
    
    if st.session_state.get("user_role") != "admin":  
        st.error("You need to log in as an admin to access this panel.")
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
        
    st.subheader("Manage Reviews")
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, movie_id, review_text FROM reviews")
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()

    if reviews:
         for review in reviews:
            st.write(f"**Review ID:** {review['id']} | **Movie ID:** {review['movie_id']} | **User ID:** {review['user_id']}")
            st.write(f"📝 {review['review_text']}")
            if st.button(f"Delete Review {review['id']}", key=f"delete_btn_{review['id']}"):
                delete_review(review['id'])
            
def delete_review(review_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success(f"Review {review_id} deleted successfully!")
        st.rerun()
    else:
        st.error("Database connection failed.")



user_id = st.session_state.get("user_id")
if "page" not in st.session_state:
    st.session_state["page"] = "Home"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if st.session_state["page"] == "Home":
    st.title("📽️MovieSearch📽️")
    st.write("Welcome to Movie Search – your ultimate gateway to the world of cinema!")
    st.write("Dive into a vast collection of movies, explore trending blockbusters, and uncover hidden gems. " )
    st.write("Rate, review, and build your watchlist, all in one place. Whether you're a casual viewer or a hardcore cinephile, your next favorite film is just a search away! 🍿")
    if st.button("Get Started",key="get_started"):
        change_page("Auth")
elif st.session_state["page"] == "Auth":
    st.title("🔐 Login or Sign Up")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login",key="auth_login"):
            change_page("Login")  
    with col2:
        if st.button("Sign Up",key="auth_signup"):
            change_page("Sign Up")
elif st.session_state["page"] == "Login":
    login()
    if st.button("Go Back",key="login_back"):
        change_page("Auth")
elif st.session_state["page"] == "Sign Up":
    st.title("🆕 Create an Account")
    signup()
    if st.button("Go Back",key="signup_back"):
        change_page("Auth")
elif st.session_state["page"] == "Dashboard":
    show_dashboard()
    if st.button("Go Back",key="dash_back"):
            change_page("Home")
elif st.session_state["page"] == "Movies":
    show_movies()
    if st.button("Go Back",key="showmovies_back"):
            change_page("Dashboard")
elif st.session_state["page"] == "Write Review":
    write_review()
    if st.button("Go Back",key="writereview_back"):
            change_page("Dashboard")
elif st.session_state["page"] == "Rate Movie":
    rate_movie()
    if st.button("Go Back",key="ratemovies_back"):
            change_page("Dashboard")
elif st.session_state["page"] == "Admin Panel":
    admin_panel()
    if st.button("Go Back",key="showmovies_back"):
            change_page("Dashboard")
elif st.session_state["page"] == "Logout":
    
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["is_admin"] = False
    st.success("You have logged out successfully!")
    st.rerun() 
