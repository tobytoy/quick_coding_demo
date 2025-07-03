import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 模擬 API 抓取資料
def fetch_updated_data():
    updated_data = {
        "country": [
            "台北市","新北市","桃園市","台中市","台南市","高雄市",
            "基隆市","新竹市","新竹縣","苗栗縣","彰化縣","南投縣",
            "雲林縣","嘉義市","嘉義縣","屏東縣","宜蘭縣","花蓮縣",
            "台東縣","澎湖縣","金門縣","連江縣"
        ],
        "pm25": [
            18, 20, 19, 22, 25, 23,
            21, 19, 18, 20, 22, 21,
            24, 20, 19, 23, 18, 17,
            19, 16, 17, 17
        ],
        "population": [
            2640000, 4020000, 2270000, 2800000, 1880000, 2700000,
            370000, 450000, 550000, 550000, 1300000, 500000,
            700000, 275000, 540000, 830000, 460000, 330000,
            220000, 105000, 140000, 12000
        ]
    }

    df_new = pd.DataFrame(updated_data)
    df_new.to_csv("data.csv", index=False)
    return df_new

st.set_page_config(layout="wide")
st.title("🌍 台灣縣市指標互動地圖")

# 加入更新按鈕
if st.button("🔄 更新資料"):
    df = fetch_updated_data()
    st.success("資料已更新！")
else:
    df = pd.read_csv("data.csv")

geo_path = "taiwan_counties.geojson"
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
            popup=f"{row['country']}: {row[selected_metric]}"
        ).add_to(m)

st_folium(m, width=900, height=600)
