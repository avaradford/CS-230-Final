import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
def comment_doc_string():
    """
    Name: Ava Radford
    CS230: Section 6
    Data: Airbnb Listings, Reviews, Neighborhoods
    Streamlit URL: https://cs-230-final-htuyy9gf8ikpfszhpprecd.streamlit.app/
    Local Host URL: http://localhost:8501/
    
    Description:
    This program analyzes Boston's Airbnb data, offering insights into pricing, availability, and reviews by neighborhood.
    It features interactive widgets, detailed charts, and a map visualization.
    """
    pass #preventing docstring from being displayed when running
# [ST4] Page configuration 
st.set_page_config(page_title="Airbnb Data Analysis", layout="wide")


# [DA1] Clean the data with lambda function, and [PY2] Function returning multiple values 
@st.cache_data
def load_data(listings_path, reviews_path, neighborhoods_path):
    try:
        # Load datasets
        listings = pd.read_csv(listings_path)
        reviews = pd.read_csv(reviews_path)
        neighborhoods = pd.read_csv(neighborhoods_path)

        # Clean data (remove $, and fills missing reviews with 0)
        listings['price'] = listings['price'].replace(r'\$|,', '', regex=True).astype(float)
        listings['reviews_per_month'] = listings['reviews_per_month'].fillna(0)

        # Create new column for price per night 
        listings['price_per_night'] = listings['price'] / listings['minimum_nights']

        return listings, reviews, neighborhoods
    except Exception as e: # [PY3] Error handling with try/except
        st.error(f"Error loading data: {e}")
        return None, None, None


# Load data
listings, reviews, neighborhoods = load_data(
    'listings.csv',
    'reviews.csv',
    'neighbourhoods.csv'
)

# [ST4] Sidebar navigation
section = st.sidebar.radio("Choose a Section",
                           ("Boston Airbnb Overview", "Statistics By Neighborhood", "Listing Map and Price Distribution By Neighborhood"))


# [PY1] Function to filter listings by neighborhood and price
def filter_listings(neighborhood, price_range=(50, 300)):
    return listings[(listings['neighbourhood'] == neighborhood) &
                    (listings['price'].between(price_range[0], price_range[1]))]


# [ST1] Display different content based on the selected section
if section == "Boston Airbnb Overview":
    st.title("Boston Airbnb Overview")
    st.write("This section provides an overview of Boston's Airbnb data and key insights.")

    # [VIZ1] Display basic info about the data
    st.subheader("Listings Data Overview")
    st.write("Listings data preview:", listings.head())

    # [DA3] Calculate and disply average and max prices 
    mean_price = listings['price'].mean()
    max_price = listings['price'].max()
    st.metric(label="Average Price", value=f"${mean_price:.2f}")
    st.metric(label="Maximum Price", value=f"${max_price:.2f}")

elif section == "Statistics By Neighborhood":
    # Neighborhood Summary
    st.subheader("Neighborhood Summary")

    # [DA6] Group and aggregate data by neighborhood
    neighborhood_summary = listings.groupby('neighbourhood').agg({
        'price': 'mean',
        'number_of_reviews': 'sum',
        'availability_365': 'count'
    }).rename(columns={
        'price': 'Average Price',
        'number_of_reviews': 'Total Reviews',
        'availability_365': 'Available Listings Count'
    }).reset_index()

    # [VIZ2] Display chart for Average Price by Neighborhood
    st.subheader("Average Price by Neighborhood")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=neighborhood_summary, x='neighbourhood', y='Average Price', palette='Blues_d')
    plt.xticks(rotation=45, ha='right')
    plt.title("Average Price by Neighborhood")
    plt.xlabel("Neighborhood")
    plt.ylabel("Average Price ($)")
    st.pyplot(plt)

    # [VIZ3] Display chart for Total Reviews by Neighborhood
    st.subheader("Total Reviews by Neighborhood")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=neighborhood_summary, x='neighbourhood', y='Total Reviews', palette='Greens_d')
    plt.xticks(rotation=45, ha='right')
    plt.title("Total Reviews by Neighborhood")
    plt.xlabel("Neighborhood")
    plt.ylabel("Total Reviews")
    st.pyplot(plt)

    # [VIZ4] Display chart for Available Listings by Neighborhood
    st.subheader("Available Listings by Neighborhood")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=neighborhood_summary, x='neighbourhood', y='Available Listings Count', palette='Oranges_d')
    plt.xticks(rotation=45, ha='right')
    plt.title("Available Listings by Neighborhood")
    plt.xlabel("Neighborhood")
    plt.ylabel("Available Listings")
    st.pyplot(plt)
   
    # [PY4] Create a list of dictionaries for neighborhood data
    neighborhood_dict_list = [
        {
            'Neighborhood': row['neighbourhood'],
            'Average Price': round(row['Average Price'], 2),
            'Total Reviews': row['Total Reviews'],
            'Available Listings Count': row['Available Listings Count']
        }
        for _, row in neighborhood_summary.iterrows()
    ]

    neighborhood_df = pd.DataFrame(neighborhood_dict_list)

    # Display it as a styled data frame
    st.subheader("Neighborhood Data Summary")
    st.dataframe(neighborhood_df.style.format({
    "Average Price": "${:.2f}", 
    "Total Reviews": "{:,}", 
    "Available Listings Count": "{:,}"
    }))

elif section == "Listing Map and Price Distribution By Neighborhood":
    st.title("Listing Map and Price Distribution By Neighborhood")

    # [ST2] Sidebar filters for map visualization
    neighborhood = st.sidebar.selectbox("Select a Neighborhood", listings['neighbourhood'].unique())
    price_range = st.sidebar.slider("Select Price Range", int(listings['price'].min()), int(listings['price'].max()),
                                    (50, 300))
    filtered_listings = filter_listings(neighborhood, price_range)

    # [MAP] Interactive map visualization using pydeck
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

    # [VIZ5] Price distribution bar chart
    st.subheader("Price Distribution in Selected Neighborhood")
    sorted_listings = filtered_listings.sort_values(by='price', ascending=False)
    plt.figure(figsize=(14, 6))
    sns.barplot(data=sorted_listings.head(20), x='name', y='price', palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 20 Listings by Price')
    plt.xlabel('Listing Name')
    plt.ylabel('Price ($)')
    st.pyplot(plt)
