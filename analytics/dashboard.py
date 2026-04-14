import streamlit as st
import pandas as pd
import sys
import os
from mongoengine import connect
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

#Path Setup
sys.path.append(os.path.abspath('../backend/python'))
from django_app.entities.product import ProductDocument
from django_app.entities.category import CategoryDocument

#Page Configuration
st.set_page_config(page_title="Inventory Dashboard", page_icon="📦", layout="wide")
st.title("📦 Live Interactive Inventory")

# Database Connection
@st.cache_resource
def init_connection():
    return connect(host="mongodb://root:example@127.0.0.1:27019/?authSource=admin")

init_connection()

#Data Fetching
@st.cache_data(ttl=60)
def fetch_inventory_data():
    raw_products = ProductDocument.objects()
    data = []
    for p in raw_products:
        data.append({
            "Name": p.name,
            "Category": p.category.title if p.category else "None", # Fetching category title for readability
            "Price": p.price,
            "Brand": p.brand,
            "Quantity": p.quantity
        })
    return pd.DataFrame(data)

df = fetch_inventory_data()

# ==========================================
# 🛡️ SIDEBAR & ALERTS
# ==========================================
st.sidebar.header("Controls & Filters")

# Advanced 1: Sidebar Filtering
categories = df['Category'].unique().tolist()
categories.insert(0, "All Categories") # Add a default 'All' option
selected_category = st.sidebar.selectbox("Filter by Category", categories)

# Apply the filter to our Pandas DataFrame
if selected_category != "All Categories":
    df = df[df['Category'] == selected_category]

# Advanced 2: Stock Alerts (Dynamic Threshold)
st.sidebar.divider()
threshold = st.sidebar.slider("Low Stock Threshold", min_value=1, max_value=500, value=100, step=10)

# Filter Pandas for items below the threshold
low_stock_df = df[df['Quantity'] < threshold]

if not low_stock_df.empty:
    # st.error creates a bright red warning box!
    st.sidebar.error(f"⚠️ ALERT: {len(low_stock_df)} items are low on stock!")
    st.sidebar.dataframe(low_stock_df[['Name', 'Quantity']], hide_index=True)
else:
    st.sidebar.success("✅ All stock levels look healthy.")

# ==========================================
# 📊 THE MAIN DASHBOARD
# ==========================================
st.subheader("Current Inventory")
st.dataframe(df, width='stretch')

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Products per Category**")
    fig_cat, ax_cat = plt.subplots(figsize=(6, 4))
    sns.countplot(data=df, x="Category", palette="viridis", ax=ax_cat)
    plt.xticks(rotation=45) 
    st.pyplot(fig_cat)

with col2:
    st.markdown("**Price Distribution**")
    fig_price, ax_price = plt.subplots(figsize=(6, 4))
    sns.histplot(data=df, x="Price", bins=10, kde=True, color="coral", ax=ax_price)
    st.pyplot(fig_price)

# ==========================================
# ➕ ADD PRODUCTS VIA UI
# ==========================================
st.divider()
st.subheader("➕ Add New Product")

# Create the Form
with st.form("add_product_form", clear_on_submit=True):
    st.write("Enter product details below:")
    
    colA, colB = st.columns(2)
    with colA:
        new_name = st.text_input("Product Name*")
        new_brand = st.text_input("Brand Name*")
        
        # Get real categories from the database for the dropdown
        real_categories = CategoryDocument.objects()
        cat_options = {c.title: c for c in real_categories}
        new_category_title = st.selectbox("Category*", list(cat_options.keys()))
        
    with colB:
        new_price = st.number_input("Price ($)*", min_value=0.01, value=10.00)
        new_quantity = st.number_input("Starting Quantity*", min_value=0, value=50)
        new_description = st.text_area("Description")

    # The magic submit button
    submitted = st.form_submit_button("Save to Database")
    
    if submitted:
        if not new_name or not new_brand:
            st.error("Name and Brand are required!")
        else:
            try:
                # 1. Create the Mongo Document directly
                new_doc = ProductDocument(
                    product_id=str(uuid.uuid4()),
                    name=new_name,
                    brand=new_brand,
                    category=cat_options[new_category_title],
                    price=new_price,
                    quantity=new_quantity,
                    description=new_description
                )
                new_doc.save() # Save it to MongoDB!
                
                # 2. Tell Streamlit to forget the old data
                fetch_inventory_data.clear() 
                
                # 3. Show success and refresh the page to show the new item!
                st.success(f"Successfully added {new_name}!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save: {str(e)}")