import streamlit as st
import pandas as pd
import sys
import os
from mongoengine import connect
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Path Setup: Tell Streamlit where your Django models live
sys.path.append(os.path.abspath('../backend/python'))
from django_app.entities.product import ProductDocument
from django_app.entities.category import CategoryDocument

# 2. Page Configuration (This MUST be the very first Streamlit command)
st.set_page_config(page_title="Inventory Dashboard", page_icon="📦", layout="wide")

st.title("📦 Live Inventory Dashboard")
st.write("Welcome to the Week 5 Interactive Analytics space!")

# 3. Database Connection
# @st.cache_resource tells Streamlit: "Only run this function ONCE. Do not reconnect every time the user clicks a button."
@st.cache_resource
def init_connection():
    return connect(host="mongodb://root:example@127.0.0.1:27019/?authSource=admin")

init_connection()

# 4. Data Fetching
# @st.cache_data tells Streamlit: "Remember this data for 60 seconds so the app is fast!"
@st.cache_data(ttl=60)
def fetch_inventory_data():
    raw_products = ProductDocument.objects()
    categories = {str(c.id): c.title for c in CategoryDocument.objects()}
    data = []
    for p in raw_products:
        data.append({
            "Name": p.name,
            "Category Name": categories.get(str(p.category.id), "Unknown") if p.category else "None",
            "Price": p.price,
            "Brand": p.brand,
            "Quantity": p.quantity
        })
    return pd.DataFrame(data)

# 5. Load the data
df = fetch_inventory_data()

# 6. Draw the UI
st.divider() # Draws a nice horizontal line
st.subheader("Raw Data View")

# Draw an interactive table that stretches across the whole screen
st.dataframe(df, width='stretch')

# --- VISUALIZATION SECTION ---
st.divider()
st.subheader("📈 Inventory Analytics")

# Streamlit Magic: We can split the screen into two columns!
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Products per Category**")
    # 1. Create a blank canvas
    fig_cat, ax_cat = plt.subplots(figsize=(6, 4))
    
    # 2. Ask Seaborn to draw a bar chart counting the 'Category Name' column
    sns.countplot(data=df, x="Category Name", palette="viridis", ax=ax_cat)
    
    # 3. Rotate the labels so they don't overlap
    plt.xticks(rotation=45) 
    
    # 4. Hand the finished canvas to Streamlit
    st.pyplot(fig_cat)

with col2:
    st.markdown("**Price Distribution**")
    # 1. Create another blank canvas
    fig_price, ax_price = plt.subplots(figsize=(6, 4))
    
    # 2. Ask Seaborn to draw a Histogram of the 'Price' column
    sns.histplot(data=df, x="Price", bins=10, kde=True, color="coral", ax=ax_price)
    
    # 3. Hand the canvas to Streamlit
    st.pyplot(fig_price)

