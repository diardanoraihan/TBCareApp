from sklearn.preprocessing import StandardScaler
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

# Select the relevant columns for clustering
features = [
    '% nakes/penduduk',
    '% pulmonologist/kasus',
    '% dr umum/kasus',
    '% Tenaga Kesehatan - Perawat/kasus',
    '% Tenaga Kesehatan Masyarakat/kasus',
    '% Tenaga Kesehatan Lingkungan/kasus'
]

# Extract the data and standardize it
X = df_base[features].fillna(0)  # Handle missing values by filling with 0
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means Clustering (with K=3)
k = 3
kmeans = KMeans(n_clusters=k, random_state=0)
kmeans.fit(X_scaled)

# Add cluster labels to the DataFrame
df_base['Cluster'] = [str(cluster + 1) for cluster in kmeans.labels_]

col1, col2 = st.columns(2)

with col1:
  modes = [
    'Cluster',
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
    color_box = "green"
  elif mode == '% Tenaga Kesehatan (Semua Kategori) per Penduduk':
    color_mode = '% nakes/penduduk'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == 'Jumlah Kasus TBC':
    color_mode = 'Jumlah Kasus Penyakit - TB Paru'
    color_scale = "YlOrRd"
    color_box = "red"
  elif mode == '% Pulmonologist per Kasus':
    color_mode = '% pulmonologist/kasus'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == '% Dokter Umum per Kasus':
    color_mode = '% dr umum/kasus'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == '% Tenaga Kesehatan Perawat per Kasus':
    color_mode = '% Tenaga Kesehatan - Perawat/kasus'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == '% Tenaga Kesehatan Masyarakat per Kasus':
    color_mode = '% Tenaga Kesehatan Masyarakat/kasus'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == '% Tenaga Kesehatan Lingkungan per Kasus':
    color_mode = '% Tenaga Kesehatan Lingkungan/kasus'
    color_scale = "Blues"
    color_box = "blue"
  elif mode == 'Cluster':
    color_mode = 'Cluster'
    color_scale = {'1': 'green', '2': 'blue', '3': 'orange'}
    
  
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
    thickness=15,
    len = 0.8
  )
)

# fig.show()
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
  bar_title = mode + " di Setiap Provinsi"
  bar_chart = px.bar(
    df_base.sort_values(color_mode, ascending=True),
    x=color_mode,
    y="Provinsi",
    orientation="h",
    title=bar_title,
    # labels={"Jumlah Kasus TBC": "Jumlah Kasus Penyakit - TB Paru", "Provinsi": "Provinsi"}, 
    color= color_mode,
    color_continuous_scale = color_scale
  )
  
  bar_chart.update_layout(
    title={'text': bar_title, 'x': 0.5, 'xanchor': 'center'},  # Judul di tengah
    xaxis_title='',  # Menghapus judul axis x
    yaxis_title='',  # Menghapus judul axis y
    showlegend=False,  # Menonaktifkan legend jika tidak diperlukan
    coloraxis_showscale=False,
    plot_bgcolor='rgba(255, 255, 255, 0.1)',  # Warna latar belakang plot lebih terang (putih dengan transparansi)
    paper_bgcolor='rgba(255, 255, 255, 0.05)',  # Warna latar belakang keseluruhan area lebih transparan
    xaxis=dict(
        gridcolor='rgba(169, 169, 169, 0.5)'  # Warna abu-abu untuk garis grid pada sumbu x
    )
  )
  bar_chart.update_xaxes(showline=True, linewidth=1, linecolor='black')
  bar_chart.update_yaxes(showline=True, linewidth=1, linecolor='black')
  st.plotly_chart(bar_chart)
  
with col2:
  
  box_title = "Distribusi " + mode + " di Setiap Provinsi"
  
  box_plot = px.box(
      df_base,
      y=color_mode,
      title=box_title,
      color_discrete_sequence = [color_box],
      hover_name = "Provinsi",
      hover_data={
        color_mode: True
      }
  )
  
  box_plot.update_layout(
    title={'text': box_title, 'x': 0.5, 'xanchor': 'center'},  # Judul di tengah
    xaxis_title='',  # Menghapus judul axis x
    yaxis_title='',  # Menghapus judul axis y
    showlegend=False,  # Menonaktifkan legend jika tidak diperlukan
    plot_bgcolor='rgba(255, 255, 255, 0.1)',  # Warna latar belakang plot lebih terang (putih dengan transparansi)
    paper_bgcolor='rgba(255, 255, 255, 0.05)',  # Warna latar belakang keseluruhan area lebih transparan
    xaxis=dict(
        gridcolor='rgba(169, 169, 169, 0.5)'  # Warna abu-abu untuk garis grid pada sumbu x
    )
  )
  box_plot.update_xaxes(showline=True, linewidth=1, linecolor='black')
  box_plot.update_yaxes(showline=True, linewidth=1, linecolor='black')
  st.plotly_chart(box_plot, use_container_width=True)

columns = ['Provinsi']
columns.append(color_mode)
# st.write(columns)
df_gen_ai = df_base[columns] # Untuk Bakti

# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)