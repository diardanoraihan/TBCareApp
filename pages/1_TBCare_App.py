from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import plotly.express as px
import streamlit as st
import duckdb as db
import pandas as pd
import numpy as np
import json
import os

# ---- Set Page Configuration ----
st.set_page_config(page_title="TBCare App",
                   layout="wide",
                   page_icon='./images/app.png')

# ---- App Title ----
st.markdown(
    """
    <div style="text-align: center;">
        <h1>🫁 TBCare 1.0</h1>
        <h4><em>An AI-Powered Web App to Track the Spread of TBC and Healthcare Resources in Indonesia</em></h4>
        <p><i>by Avektive (Turnamen Sains Data Nasional 2024)</i></p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Read dataset GeoJSON
with open('dataset/indonesia-province.json') as file:
    indo_provinces = json.load(file)

province_id_map = {}
for feature in indo_provinces['features']:
    # add id
    feature['id'] = feature['properties']['kode']
    # map province name to its id
    province_id_map[feature['properties']['Propinsi']] = feature['id']

# Read dataset master
df_base = pd.read_csv('dataset/dataset.csv')
df_base['Provinsi'] = df_base['Provinsi'].apply(lambda x: x.upper())
df_base['id'] = df_base['Provinsi'].apply(lambda x: province_id_map[x])

col1, col2 = st.columns(2)

with col1:
  modes = [
    'Jumlah Kasus TBC',
    'Jumlah Penduduk',
    '% Tenaga Kesehatan (Semua Kategori) per Penduduk',
    '% Pulmonologist per Kasus',
    '% Dokter Umum per Kasus',
    '% Tenaga Kesehatan Perawat per Kasus',
    '% Tenaga Kesehatan Masyarakat per Kasus',
    '% Tenaga Kesehatan Lingkungan per Kasus'
  ]
  mode = st.selectbox(f'Pilih Mode Peta : ', options=modes, index=0)
  if mode == 'Jumlah Penduduk':
    color_mode = 'Jumlah Penduduk'
    color_scale = "Greens"
  elif mode == '% Tenaga Kesehatan per Penduduk':
    color_mode = '% nakes/penduduk'
    color_scale = "Blues"
  elif mode == 'Jumlah Kasus TBC':
    color_mode = 'Jumlah Kasus Penyakit - TB Paru'
    color_scale = "YlOrRd"
  else:
    color_mode = 'Jumlah Penduduk'
  
with col2:
  provinces = list(df_base['Provinsi'].unique())
  provinces.sort()
  provinsi = st.multiselect(f'Pilih Provinsi: ', options = provinces)
  
  if provinsi:
    df_base = df_base[df_base['Provinsi'].isin(provinsi)]

fig = px.choropleth_mapbox(data_frame = df_base,
                           locations = "id", # feature identifier inside data frame df_ind
                           geojson = indo_provinces,
                           featureidkey = "id", # feature identifier inside geojson indo_provinces
                           color = color_mode,
                           color_continuous_scale = color_scale,
                           mapbox_style = "white-bg",
                           opacity = 0.7,
                           zoom = 3.9,
                           center = {"lat": -2.548926, "lon": 118.0148634})

fig.update_traces(
    hovertemplate="<b>%{customdata[0]}</b><br>" +
                  "Jumlah Penduduk = %{customdata[1]}<br>" +
                  "Jumlah Tenaga Kesehatan / Jumlah Penduduk (%) = %{customdata[2]:.2f}%<br>" +
                  "Jumlah Kasus Penyakit TBC = %{customdata[3]}",
    customdata=df_base[["Provinsi", "Jumlah Penduduk", "% nakes/penduduk", "Jumlah Kasus Penyakit - TB Paru"]].to_numpy()
)

fig.update_layout(
  margin={"r":150,"t":0,"l":150,"b":0},
  coloraxis_colorbar = dict(
    orientation="h",  # Horizontal legend
    y=-0.1,  # Posisi Vertikal (negatif: di bawah grafik)
  )
)

# fig.show()
st.plotly_chart(fig, use_container_width=True)

columns = ['Provinsi']
columns.append(color_mode)
# st.write(columns)
df_gen_ai = df_base[columns] # Untuk Bakti

st.dataframe(df_gen_ai)

# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)