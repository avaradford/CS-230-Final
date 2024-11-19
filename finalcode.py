import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration 
st.set_page_config(page_title="Airbnb Data Analysis", layout="wide")


# Clean the data with lambda function
@st.cache_data
def load_data(listings_path, reviews_path, neighborhoods_path):
    try:
        # Load datasets
        listings = pd.read_csv(listings_path)
        reviews = pd.read_csv(reviews_path)
        neighborhoods = pd.read_csv(neighborhoods_path)

        # Clean data
        listings['price'] = listings['price'].replace(r'\$|,', '', regex=True).astype(float)
        listings['reviews_per_month'] = listings['reviews_per_month'].fillna(0)

        # Create new column
        listings['price_per_night'] = listings['price'] / listings['minimum_nights']

        return listings, reviews, neighborhoods
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None


# Load data
listings, reviews, neighborhoods = load_data(
    'listings.csv',
    'reviews.csv',
    'neighbourhoods.csv'
)

# Sidebar navigation
section = st.sidebar.radio("Choose a Section",
                           ("Boston Airbnb Overview", "Listings and Neighborhoods", "Map and Visualizations"))


# Function to filter listings by neighborhood and price
def filter_listings(neighborhood, price_range=(50, 300)):
    return listings[(listings['neighbourhood'] == neighborhood) &
                    (listings['price'].between(price_range[0], price_range[1]))]


# Display different content based on the selected section
if section == "Boston Airbnb Overview":
    st.title("Boston Airbnb Overview")
    st.write("This section provides an overview of Boston's Airbnb data and key insights.")

    # Display basic info about the data
    st.subheader("Listings Data Overview")
    st.write("Listings data preview:", listings.head())

    # Key insights
    mean_price = listings['price'].mean()
    max_price = listings['price'].max()
    st.metric(label="Average Price", value=f"${mean_price:.2f}")
    st.metric(label="Maximum Price", value=f"${max_price:.2f}")

elif section == "Listings and Neighborhoods":
    st.title("Top Listings and Neighborhood in Boston Summary")

    # Sidebar filters for neighborhood and price
    neighborhood = st.sidebar.selectbox("Select a Neighborhood", listings['neighbourhood'].unique())
    price_range = st.sidebar.slider("Select Price Range", int(listings['price'].min()), int(listings['price'].max()),
                                    (50, 300))
    filtered_listings = filter_listings(neighborhood, price_range)

    # Top 10 Listings based on price_per_night
    st.subheader("Top 10 Listings")
    top_listings = filtered_listings.nlargest(10, 'price_per_night')[
        ['name', 'price_per_night', 'neighbourhood', 'number_of_reviews']]
    st.write(top_listings)

    # Neighborhood Summary
    st.subheader("Neighborhood Summary")
    neighborhood_summary = listings.groupby('neighbourhood').agg({
        'price': 'mean',
        'number_of_reviews': 'sum',
        'availability_365': 'count'
    }).rename(columns={
        'price': 'Average Price',
        'number_of_reviews': 'Total Reviews',
        'availability_365': 'Available Listings Count'
    })
    st.write(neighborhood_summary)

elif section == "Map and Visualizations":
    st.title("Map and Visualizations")

    # Sidebar filters for map visualization
    neighborhood = st.sidebar.selectbox("Select a Neighborhood", listings['neighbourhood'].unique())
    price_range = st.sidebar.slider("Select Price Range", int(listings['price'].min()), int(listings['price'].max()),
                                    (50, 300))
    filtered_listings = filter_listings(neighborhood, price_range)

    # Map visualization with pydeck
    st.subheader("Map of Filtered Listings")
    map_layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_listings,
        get_position='[longitude, latitude]',
        get_radius=150,
        get_color='[255, 0, 0, 160]',
        pickable=True
    )
    view_state = pdk.ViewState(
        latitude=filtered_listings['latitude'].mean(),
        longitude=filtered_listings['longitude'].mean(),
        zoom=13,
        pitch=45
    )
    map = pdk.Deck(
        layers=[map_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}: ${price_per_night}"}
    )
    st.pydeck_chart(map)

    # Price distribution visualization
    st.subheader("Price Distribution in Selected Neighborhood")
    sorted_listings = filtered_listings.sort_values(by='price', ascending=False)
    plt.figure(figsize=(14, 6))
    sns.barplot(data=sorted_listings.head(20), x='name', y='price', palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 20 Listings by Price')
    plt.xlabel('Listing Name')
    plt.ylabel('Price ($)')
    st.pyplot(plt)
