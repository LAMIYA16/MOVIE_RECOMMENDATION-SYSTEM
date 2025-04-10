import streamlit as st
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Lamiya@2004",
        database="movie_db",
       
    )

# Fetch Movies from Database
def fetch_movies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, image_url, rating FROM movies")
    movies = cursor.fetchall()
    conn.close()
    return movies

# Movie Display Function
def display_movies():
    movies = fetch_movies()
    
    # Custom CSS for Styling Cards
    st.markdown("""
        <style>
        .movie-card {
            background-color: #111;
            color: white;
            padding: 15px;
            border-radius: 10px;
            width: 200px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(255, 255, 255, 0.2);
        }
        .movie-card img {
            width: 100%;
            border-radius: 10px;
        }
        .rating {
            color: gold;
            font-size: 18px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Display movies in a grid layout
    cols = st.columns(3)  # 3 movies per row
    for i, movie in enumerate(movies):
        with cols[i % 3]:  # Places movies in columns dynamically
            st.markdown(f"""
            <div class="movie-card">
                <img src="{movie['image_url']}" alt="Movie Poster">
                <h4>{movie['title']}</h4>
                <p class="rating">⭐ {movie['rating']}</p>
                <button>Watchlist</button>
            </div>
            """, unsafe_allow_html=True)

# Run display function if file is executed
if __name__ == "__main__":
    display_movies()
