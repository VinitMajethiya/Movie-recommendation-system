import streamlit as st
import pickle
import pandas as pd
import requests
from collections import deque

# Initialize queue in session state if not already present
if 'recent_recommendations' not in st.session_state:
    st.session_state.recent_recommendations = deque(maxlen=5)

# Function to recommend movies
def recommend(movie):
    index = movies[movies['Series_Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_details = []
    for i in distances[1:11]:  # Top 10 recommendations
        movie_title = movies.iloc[i[0]].Series_Title
        poster_url, overview, director, cast = fetch_movie_details(movie_title)
        recommended_movie_details.append({
            "title": movie_title,
            "poster": poster_url,
            "overview": overview,
            "director": director,
            "cast": cast
        })
    return recommended_movie_details

# Function to fetch movie details (poster, overview, director, and cast)
def fetch_movie_details(movie_title):
    api_key = "f100ac8e"  # Your OMDb API key
    base_url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "t": movie_title}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        poster_url = data.get("Poster", "https://via.placeholder.com/300x450?text=Poster+Not+Available")
        overview = data.get("Plot", "Overview not available")
        director = data.get("Director", "Director not available")
        cast = data.get("Actors", "Cast not available")
        return poster_url, overview, director, cast
    else:
        return (
            "https://via.placeholder.com/300x450?text=Error+Fetching+Poster",
            "Error fetching overview",
            "Error fetching director",
            "Error fetching cast"
        )

# Load movie data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Set up Streamlit page with custom background
st.set_page_config(page_title="Recommend.Me", page_icon="🎥", layout="wide")

# Add background CSS
def add_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://images.unsplash.com/photo-1542206395-9feb3edaa68c");
            background-size: cover;
        }
        .title {
            font-family: 'Courier New', Courier, monospace;
            font-size: 45px;
            color: #FFFFFF;
            text-align: center;
            text-shadow: 2px 2px 4px #000000;
        }
        .movie-title {
            font-family: 'Arial Black', sans-serif;
            font-size: 24px;
            color: #FFFFFF;
        }
        .movie-overview, .movie-director, .movie-cast {
            font-family: 'Arial', sans-serif;
            font-size: 16px;
            color: #DDDDDD;
        }
        .movie-section {
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_background()

# Title section
st.markdown('<p class="title">🎥 Recommend.Me</p>', unsafe_allow_html=True)
st.markdown(
    "<h4 style='text-align: center; color: white;'>Find your next favorite movie based on what you already love!</h4>",
    unsafe_allow_html=True,
)

# Movie selection
movie_list = movies['Series_Title'].values
selected_movie_name = st.selectbox("🎬 Select a Movie:", movie_list, key="movie_select")

if st.button('🔍 Get Recommendations'):
    with st.spinner('Fetching recommendations... 🎥'):
        recommendations = recommend(selected_movie_name)

    # Append selected movie to persistent queue
    st.session_state.recent_recommendations.append(selected_movie_name)

    st.markdown("### Recommendations 🎉")
    for movie in recommendations:
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(movie["poster"], width=150)
            with col2:
                st.markdown(f'<p class="movie-title">{movie["title"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="movie-overview"><b>Overview:</b> {movie["overview"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="movie-director"><b>Director:</b> {movie["director"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="movie-cast"><b>Cast:</b> {movie["cast"]}</p>', unsafe_allow_html=True)
                st.markdown("---")

# Show recently recommended movies using session-based queue
if st.session_state.recent_recommendations:
    st.markdown("### 🔁 Recently Recommended Movies")
    for movie_name in list(st.session_state.recent_recommendations):
        st.markdown(f"- {movie_name}")

# Footer with personalization
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        text-align: center;
        padding: 10px;
        color: white;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        <p>🎬 Made with ❤️ by Vinit Majethiya</p>
    </div>
    """,
    unsafe_allow_html=True,
)
