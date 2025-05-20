import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import json


#Load data ipm
ipm_df = pd.read_csv("data/ipm_indonesia.csv")
ipm_df.columns = [col.strip() for col in ipm_df.columns]
ipm_df['Provinsi'] = ipm_df['Provinsi'].str.strip()

# Load geojson
with open("geojson/indonesia-prov.geojson", "r", encoding="utf-8") as geo:
    geojson_data = json.load(geo)

# Sidebar
tahun_list = sorted(ipm_df['Tahun'].unique())
tahun_pilihan = st.sidebar.selectbox("Pilih Tahun", tahun_list)
data_tahun = ipm_df[ipm_df['Tahun'] == tahun_pilihan]

# Header
st.title("Pemetaan Indeks Pembangunan Manusia (IPM) Indonesia")
st.markdown(f"**Tahun: {tahun_pilihan}**")

# Statistik
avg_ipm = data_tahun['IPM'].mean()
max_row = data_tahun.loc[data_tahun['IPM'].idxmax()]
min_row = data_tahun.loc[data_tahun['IPM'].idxmin()]

st.markdown(f"**Rata-rata IPM Nasional:** {avg_ipm:.2f}")
st.markdown(f"**Provinsi Tertinggi:** {max_row['Provinsi']} ({max_row['IPM']})")
st.markdown(f"**Provinsi Terendah:** {min_row['Provinsi']} ({min_row['IPM']})")

# Radar Chart
st.subheader("Radar Chart IPM per Provinsi")
radar_data = data_tahun.sort_values("IPM", ascending=False).head(5)
fig_radar = px.line_polar(radar_data, r='IPM', theta='Provinsi', line_close=True,
                          title='Top 5 Provinsi dengan IPM Tertinggi',
                          color='Provinsi', markers=True)
st.plotly_chart(fig_radar)

# Peta
st.subheader("Peta Interaktif IPM")
m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="CartoDB positron")

#Data untuk peta
for feature in geojson_data['features']:
    prov = feature['properties']['Provinsi'].strip()
    nilai = data_tahun[data_tahun['Provinsi'] == prov]['IPM']
    if not nilai.empty:
        feature['properties']['IPM'] = float(nilai)
    else:
        feature['properties']['IPM'] = None

folium.Choropleth(
    geo_data=geojson_data,
    name="choropleth",
    data=data_tahun,
    columns=["Provinsi", "IPM"],
    key_on="feature.properties.Provinsi",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Indeks Pembangunan Manusia (IPM)"
).add_to(m)

folium.LayerControl().add_to(m)
st_folium(m, width=700, height=500)

# Tabel data
st.subheader("Tabel Data IPM")
st.dataframe(data_tahun.reset_index(drop=True))

# Footer
st.markdown("---")
st.markdown("Sumber: Badan Pusat Statistik (BPS) Indonesia")