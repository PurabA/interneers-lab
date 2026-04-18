import streamlit as st
import pandas as pd
import sys
import os
from mongoengine import connect
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

#Path Setup
sys.path.append(os.path.abspath('../backend/python'))
from django_app.entities.product import ProductDocument
from django_app.entities.category import CategoryDocument

# --- PYDANTIC SHIELDS FOR AI ---
class SyntheticProduct(BaseModel):
    name: str
    brand: str
    price: float = Field(ge=0.0)
    quantity: int = Field(ge=0)
    description: str
    category_title: str # AI will invent a category name for us too!

class ProductList(BaseModel):
    products: list[SyntheticProduct]

#Page Configuration
st.set_page_config(page_title="Inventory Dashboard", page_icon="📦", layout="wide")
st.title("📦 Live Interactive Inventory + AI Engine")

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
st.sidebar.header("Controls & API")

# --- SECURE AI KEY INPUT ---
gemini_key = st.sidebar.text_input("🔑 Gemini API Key", type="password", help="Paste your AI Studio key here to enable the Simulation Engine.")

st.sidebar.divider()
st.sidebar.subheader("Filters")

# Advanced 1: Sidebar Filtering
categories = df['Category'].unique().tolist()
categories.insert(0, "All Categories") # Add a default 'All' option
selected_category = st.sidebar.selectbox("Filter by Category", categories)

if selected_category != "All Categories":
    df = df[df['Category'] == selected_category]

# Advanced 2: Stock Alerts (Dynamic Threshold)
st.sidebar.divider()
threshold = st.sidebar.slider("Low Stock Threshold", min_value=1, max_value=500, value=100, step=10)

low_stock_df = df[df['Quantity'] < threshold]

if not low_stock_df.empty:
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
# 🤖 ADVANCED TASK: AI SCENARIO SIMULATOR
# ==========================================
st.divider()
st.subheader("🤖 AI Scenario Simulator")
st.write("Inject massive amounts of synthetic data into your database to test scaling and UI response.")

# The Scenario Selector
scenarios = {
    "Black Friday Tech Rush": "Generate high-end electronics and gadgets with huge quantities (500+).",
    "Summer Outdoor Clearance": "Generate cheap summer water toys and sports gear with very low quantities (under 20).",
    "Luxury Holiday Gifts": "Generate extremely expensive luxury items (watches, jewelry) with low stock.",
    "Zombie Apocalypse Prep": "Generate survival gear, canned food, and medical kits."
}

colS1, colS2 = st.columns([3, 1])
with colS1:
    selected_scenario = st.selectbox("Choose a Business Scenario", list(scenarios.keys()))
with colS2:
    num_to_generate = st.slider("Items to Generate", min_value=1, max_value=20, value=5)

if st.button("Generate & Populate Database", type="primary"):
    if not gemini_key:
        st.error("🚨 Please enter your Gemini API Key in the sidebar first!")
    else:
        with st.spinner(f"🧠 Gemini is hallucinating {num_to_generate} products for '{selected_scenario}'..."):
            try:
                # 1. Setup API
                os.environ["GEMINI_API_KEY"] = gemini_key
                client = genai.Client()
                
                # 2. Build the Prompt
                scenario_instructions = scenarios[selected_scenario]
                prompt = f"You are a realistic data generator. Generate {num_to_generate} unique products. Scenario rules: {scenario_instructions}"
                
                # 3. Call Gemini with Structured Outputs
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=1.2, # Extra creative
                        response_mime_type="application/json",
                        response_schema=ProductList, 
                    )
                )
                
                ai_data = json.loads(response.text)
                
                # 4. Save to Database
                docs_to_save = []
                for item in ai_data.get("products", []):
                    # Find or create the category Gemini invented
                    cat = CategoryDocument.objects(title=item["category_title"]).first()
                    if not cat:
                        cat = CategoryDocument(category_id=str(uuid.uuid4()), title=item["category_title"]).save()
                        
                    doc = ProductDocument(
                        product_id=str(uuid.uuid4()),
                        name=item["name"],
                        brand=item["brand"],
                        price=item["price"],
                        quantity=item["quantity"],
                        description=item["description"],
                        category=cat
                    )
                    docs_to_save.append(doc)
                
                if docs_to_save:
                    ProductDocument.objects.insert(docs_to_save)
                    fetch_inventory_data.clear() # Clear Streamlit's memory
                    st.success(f"✅ Boom! {len(docs_to_save)} items injected into the database.")
                    st.rerun() # Refresh the page immediately
                    
            except Exception as e:
                st.error(f"❌ AI Generation Failed: {str(e)}")

# ==========================================
# ➕ MANUAL ADD PRODUCTS VIA UI
# ==========================================
st.divider()
with st.expander("➕ Manually Add New Product"):
    with st.form("add_product_form", clear_on_submit=True):
        st.write("Enter product details below:")
        colA, colB = st.columns(2)
        with colA:
            new_name = st.text_input("Product Name*")
            new_brand = st.text_input("Brand Name*")
            real_categories = CategoryDocument.objects()
            cat_options = {c.title: c for c in real_categories}
            # Fallback if no categories exist
            cat_keys = list(cat_options.keys()) if cat_options else ["None"]
            new_category_title = st.selectbox("Category*", cat_keys)
            
        with colB:
            new_price = st.number_input("Price ($)*", min_value=0.01, value=10.00)
            new_quantity = st.number_input("Starting Quantity*", min_value=0, value=50)
            new_description = st.text_area("Description")
        submitted = st.form_submit_button("Save to Database")
        if submitted:
            if not new_name or not new_brand:
                st.error("Name and Brand are required!")
            elif new_category_title == "None":
                st.error("Please create a category first!")
            else:
                try:
                    new_doc = ProductDocument(
                        product_id=str(uuid.uuid4()),
                        name=new_name,
                        brand=new_brand,
                        category=cat_options[new_category_title],
                        price=new_price,
                        quantity=new_quantity,
                        description=new_description
                    )
                    new_doc.save() 
                    fetch_inventory_data.clear() 
                    st.success(f"Successfully added {new_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save: {str(e)}")