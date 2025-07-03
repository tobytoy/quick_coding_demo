# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 讀取你製作的指標資料，欄位格式同前
df = pd.read_csv("data.csv")
geo_path = "taiwan_counties.geojson"  # 下載的 g0v GeoJSON

st.set_page_config(layout="wide")
st.title("🌍 台灣縣市指標互動地圖")

selected_metric = st.selectbox("選擇指標", df.columns.drop("country"))

m = folium.Map(location=[23.7, 121], zoom_start=7)
folium.Choropleth(
    geo_data=geo_path,
    data=df,
    columns=["country", selected_metric],
    key_on="feature.properties.name",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=selected_metric
).add_to(m)

for _, row in df.iterrows():
    if "lat" in row and "lon" in row:
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color="black",
            fill=True, fill_color="white",
            popup=f"{row['county']}: {row[selected_metric]}"
        ).add_to(m)

st_folium(m, width=900, height=600)
