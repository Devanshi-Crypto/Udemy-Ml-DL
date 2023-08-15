import streamlit as st
import pandas as pd
import difflib

# Load data
movie_titles_df = pd.read_csv("Movie_Id_Titles")
movies_rating_df = pd.read_csv('u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])

# Merge dataframes
movies_rating_df = pd.merge(movies_rating_df, movie_titles_df, on='item_id')

# Calculate correlations
userid_movietitle_matrix = movies_rating_df.pivot_table(index='user_id', columns='title', values='rating')
movie_correlations = userid_movietitle_matrix.corr(method='pearson', min_periods=80)

# Streamlit UI
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
)

# Color palette
primary_color = "#c9b492"
secondary_color = "plum"
background_color = "#F9F9F9"

# Page styling
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {background_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {primary_color};
    }}
    .Widget>label {{
        color: {secondary_color};
        font-weight: bold;
    }}
    .sidebar .sidebar-content .stButton {{
        background-color: {secondary_color};
        color: white;
    }}
    .st-bb {{
        background-color: {secondary_color};
    }}
    .st-at {{
        background-color: {secondary_color};
    }}
    .st-cc {{
        background-color: {secondary_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Movie Recommender System")

# User input for ratings
st.sidebar.header("Rate Movies")
myRatings = []
for i in range(3):  # Change the number to the desired number of movies to rate
    movie_input = st.sidebar.text_input(f"Movie {i + 1} Title")
    movie_name = difflib.get_close_matches(movie_input, movie_titles_df['title'], n=1)
    if movie_name:
        movie_name = movie_name[0]
        if movie_name in movie_correlations.columns:
            rating = st.sidebar.slider(f"Your Rating for {movie_name}", 1, 5, key=f"rating_{i}")
            myRatings.append((movie_name, rating))
        else:
            st.sidebar.warning(f"Movie '{movie_name}' not found. Please enter a valid movie name.")

# Calculate similar movies
similar_movies_list = pd.Series()
for movie_name, rating in myRatings:
    similar_movie = movie_correlations[movie_name].dropna()
    similar_movie = similar_movie.map(lambda x: x * rating)
    similar_movies_list = similar_movies_list.append(similar_movie)

similar_movies_list = similar_movies_list.groupby(similar_movies_list.index).sum()
similar_movies_list = similar_movies_list.sort_values(ascending=False)

# Display recommended movies
st.header("Recommended Movies")
if similar_movies_list.empty:
    st.info("No recommendations yet. Please rate some movies.")
else:
    for movie_name, correlation in similar_movies_list.head(10).iteritems():
        st.write(f"{movie_name}: Correlation - {correlation:.2f}")

# Footer
st.markdown("---")
st.write("Developed by Devanshi Doshi")
