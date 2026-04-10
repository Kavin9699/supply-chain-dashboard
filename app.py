import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("📦 Supply Chain Analytics Dashboard")


df = pd.read_csv("supply_chain_data.csv")

st.subheader("📊 Dataset Preview")
st.write(df.head())

st.subheader("📁 Dataset Info")
st.write("Shape:", df.shape)
st.write("Columns:", df.columns)

st.subheader("📌 Key Metrics")

col1, col2 = st.columns(2)

col1.metric("Total Revenue", f"${df['Revenue generated'].sum():,.2f}")
col2.metric("Total Orders", int(df["Number of products sold"].sum()))

st.subheader("🚚 Shipping Time Analysis")

fig, ax = plt.subplots()
sns.histplot(df['Shipping times'], kde=True, ax=ax)
ax.set_title("Distribution of Shipping Times")

st.pyplot(fig)

# Location Analysis
st.subheader("📍 Orders by Location")

location_data = df['Location'].value_counts()

fig2, ax2 = plt.subplots()
location_data.plot(kind='bar', ax=ax2)
ax2.set_title("Orders by Location")

st.pyplot(fig2)

# Footer
st.write("✅ Project by Kavin")