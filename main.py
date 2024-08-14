import streamlit as st
import pandas as pd

# Title of the app
st.title('IMDB Titles MOVIES')

# Load the CSV file
@st.cache_data
def load_data():
    return pd.read_csv('imdb_top_1000.csv')

data = load_data()

# Convert Poster_Link column to HTML for rendering images
def render_image(url):
    return f'<img src="{url}" width="100">'

# Apply the render_image function to the Poster_Link column
data['Poster'] = data['Poster_Link'].apply(render_image)

# Rename cast columns
data.rename(columns={'Star1': 'Cast 1', 'Star2': 'Cast 2', 'Star3': 'Cast 3', 'Star4': 'Cast 4'}, inplace=True)

# Step 1: Data Preparation
# Filter the relevant columns
relevant_columns = ['IMDB_Rating', 'Director', 'Cast 1', 'Cast 2', 'Cast 3', 'Cast 4', 'Runtime']
filtered_data = data[relevant_columns]

# Step 2: Identify Key Contributors

# (a) Top Director by Average Rating
top_director = filtered_data.groupby('Director')['IMDB_Rating'].mean().idxmax()
top_director_rating = filtered_data.groupby('Director')['IMDB_Rating'].mean().max()

# (a) Lowest Director by Average Rating
lowest_director = filtered_data.groupby('Director')['IMDB_Rating'].mean().idxmin()
lowest_director_rating = filtered_data.groupby('Director')['IMDB_Rating'].mean().min()

# (b) Top Cast Members by Highest and Lowest Average Rating
cast_columns = ['Cast 1', 'Cast 2', 'Cast 3', 'Cast 4']
top_cast = pd.DataFrame()

for cast in cast_columns:
    cast_avg_rating = filtered_data.groupby(cast)['IMDB_Rating'].mean().reset_index()
    cast_avg_rating.columns = ['Actor/Actress', 'Average_Rating']
    cast_avg_rating['Cast Position'] = cast
    top_cast = top_cast._append(cast_avg_rating, ignore_index=True)

# Pivot the data to get the required format
top_cast_pivot = top_cast.pivot_table(index='Actor/Actress', columns='Cast Position', values='Average_Rating').reset_index()

# Rename columns and fill NaN values with 0
top_cast_pivot = top_cast_pivot.fillna(0)
top_cast_pivot.columns.name = None
top_cast_pivot = top_cast_pivot.rename(columns={
    'Cast 1': 'Cast 1 Rating',
    'Cast 2': 'Cast 2 Rating',
    'Cast 3': 'Cast 3 Rating',
    'Cast 4': 'Cast 4 Rating'
})

# Compute the average rating for each cast member
top_cast_pivot['Average Rating'] = top_cast_pivot[['Cast 1 Rating', 'Cast 2 Rating', 'Cast 3 Rating', 'Cast 4 Rating']].mean(axis=1)

# Identify highest and lowest average rating
highest_avg_rating = top_cast_pivot[['Actor/Actress', 'Average Rating']].sort_values(by='Average Rating', ascending=False).iloc[0]
lowest_avg_rating = top_cast_pivot[['Actor/Actress', 'Average Rating']].sort_values(by='Average Rating').iloc[0]

# (c) Ideal Duration
optimal_duration = filtered_data.groupby('Runtime')['IMDB_Rating'].mean().idxmax()
optimal_duration_rating = filtered_data.groupby('Runtime')['IMDB_Rating'].mean().max()

# (c) Ideal Duration
worst_duration = filtered_data.groupby('Runtime')['IMDB_Rating'].mean().idxmin()
worst_duration_rating = filtered_data.groupby('Runtime')['IMDB_Rating'].mean().min()

# Step 3: Create Summary Table
summary = pd.DataFrame({
    'Category': ['Top Director', 'Optimal Duration'],
    'Name/Details': [top_director, f'{optimal_duration} minutes'],
    'Rating': [top_director_rating, optimal_duration_rating]
})

summary2 = pd.DataFrame({
    'Category': ['Lowest Director', 'Worst Duration'],
    'Name/Details': [lowest_director, f'{worst_duration} minutes'],
    'Rating': [lowest_director_rating, worst_duration_rating]
})
# Display the Summary Table
st.subheader("Summary of Best Ratings")
st.dataframe(summary)

st.subheader("Summary of Worst Ratings")
st.dataframe(summary2)

# Display the highest and lowest average rating for each cast member
st.subheader("Highest Average Rating for Each Cast Member")
st.dataframe(top_cast_pivot[['Actor/Actress', 'Average Rating']].sort_values(by='Average Rating', ascending=False).head(10))

st.subheader("Lowest Average Rating for Each Cast Member")
st.dataframe(top_cast_pivot[['Actor/Actress', 'Average Rating']].sort_values(by='Average Rating').head(10))


# Ensure the 'Gross' column is numeric (handle any non-numeric values)
data['Gross'] = pd.to_numeric(data['Gross'].str.replace(',', ''), errors='coerce')

# Drop rows with missing or invalid gross revenue
data = data.dropna(subset=['Gross'])

# Sort the data by the 'Gross' column in descending order
highest_grossing = data.sort_values(by='Gross', ascending=False)

# Display the top entries with the highest gross revenue
top_highest_grossing = highest_grossing.head(10)  # Show top 10 movies

# Display the highest-grossing movies
st.subheader("Top 10 Highest Grossing Movies")
st.table(top_highest_grossing[['Series_Title', 'Gross']])

# Display the data with images
columns = ['Poster', 'Series_Title', 'Released_Year', 'Runtime', 'IMDB_Rating', 'Genre', 'Director', 'Cast 1', 'Cast 2', 'Cast 3', 'Cast 4', 'No_of_Votes', 'Gross']
data = data[columns]
st.markdown(data.to_html(escape=False, index=False), unsafe_allow_html=True)
