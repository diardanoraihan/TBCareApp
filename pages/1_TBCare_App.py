from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import plotly.express as px
import streamlit as st
import duckdb as db
import pandas as pd
import numpy as np
import json
from openai import OpenAI
import time

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
k = 5
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
    color_scale = {'1': 'red', '2': 'green', '3': 'blue', '4': 'orange', '5': 'brown'}


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
    hovertemplate="<b>%{customdata[0]}</b><br>" + color_mode + " = %{customdata[1]}",
    customdata=df_base[["Provinsi", color_mode]].to_numpy()
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

if mode != 'Cluster':
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
    
else:
  
  df_cluster_means = df_base.groupby('Cluster')[features].mean()
  df_cluster_means.reset_index(inplace = True)
  
  col1, col2, col3, col4, col5 = st.columns(5)
  
  columns = ["Provinsi"] + features
  with col1:
    st.write('### Cluster 1')
    col1.metric(label='Avg. % Nakes per Penduduk', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% nakes/penduduk'], 3))
    col1.metric(label='Avg. % Pulmonologist per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% pulmonologist/kasus'], 3))
    col1.metric(label='Avg. % Dokter umum per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% dr umum/kasus'], 3))
    col1.metric(label='Avg. % Nakes Perawat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% Tenaga Kesehatan - Perawat/kasus'], 3))
    col1.metric(label='Avg. % Nakes Masyarakat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% Tenaga Kesehatan Masyarakat/kasus'], 3))
    col1.metric(label='Avg. % Nakes Lingkungan per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '1']['% Tenaga Kesehatan Lingkungan/kasus'], 3))
    st.write('Daftar Provinsi: ')
    col1_provinces = ', '.join(list(df_base[df_base['Cluster'] == '1']['Provinsi']))
    st.write(col1_provinces)
  with col2:
    st.write('### Cluster 2')
    col2.metric(label='Avg. % Nakes per Penduduk', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% nakes/penduduk'], 3))
    col2.metric(label='Avg. % Pulmonologist per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% pulmonologist/kasus'], 3))
    col2.metric(label='Avg. % Dokter umum per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% dr umum/kasus'], 3))
    col2.metric(label='Avg. % Nakes Perawat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% Tenaga Kesehatan - Perawat/kasus'], 3))
    col2.metric(label='Avg. % Nakes Masyarakat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% Tenaga Kesehatan Masyarakat/kasus'], 3))
    col2.metric(label='Avg. % Nakes Lingkungan per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '2']['% Tenaga Kesehatan Lingkungan/kasus'], 3))
    st.write('Daftar Provinsi: ')
    col2_provinces = ', '.join(list(df_base[df_base['Cluster'] == '2']['Provinsi']))
    st.write(col2_provinces)
  with col3:
    st.write('### Cluster 3')
    col3.metric(label='Avg. % Nakes per Penduduk', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% nakes/penduduk'], 3))
    col3.metric(label='Avg. % Pulmonologist per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% pulmonologist/kasus'], 3))
    col3.metric(label='Avg. % Dokter umum per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% dr umum/kasus'], 3))
    col3.metric(label='Avg. % Nakes Perawat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% Tenaga Kesehatan - Perawat/kasus'], 3))
    col3.metric(label='Avg. % Nakes Masyarakat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% Tenaga Kesehatan Masyarakat/kasus'], 3))
    col3.metric(label='Avg. % Nakes Lingkungan per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '3']['% Tenaga Kesehatan Lingkungan/kasus'], 3))
    st.write('Daftar Provinsi: ')
    col3_provinces = ', '.join(list(df_base[df_base['Cluster'] == '3']['Provinsi']))
    st.write(col3_provinces)
  with col4:
    st.write('### Cluster 4')
    col4.metric(label='Avg. % Nakes per Penduduk', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% nakes/penduduk'], 3))
    col4.metric(label='Avg. % Pulmonologist per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% pulmonologist/kasus'], 3))
    col4.metric(label='Avg. % Dokter umum per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% dr umum/kasus'], 3))
    col4.metric(label='Avg. % Nakes Perawat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% Tenaga Kesehatan - Perawat/kasus'], 3))
    col4.metric(label='Avg. % Nakes Masyarakat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% Tenaga Kesehatan Masyarakat/kasus'], 3))
    col4.metric(label='Avg. % Nakes Lingkungan per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '4']['% Tenaga Kesehatan Lingkungan/kasus'], 3))
    st.write('Daftar Provinsi: ')
    col4_provinces = ', '.join(list(df_base[df_base['Cluster'] == '4']['Provinsi']))
    st.write(col4_provinces)
  with col5:
    st.write('### Cluster 5')
    col5.metric(label='Avg. % Nakes per Penduduk', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% nakes/penduduk'], 3))
    col5.metric(label='Avg. % Pulmonologist per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% pulmonologist/kasus'], 3))
    col5.metric(label='Avg. % Dokter umum per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% dr umum/kasus'], 3))
    col5.metric(label='Avg. % Nakes Perawat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% Tenaga Kesehatan - Perawat/kasus'], 3))
    col5.metric(label='Avg. % Nakes Masyarakat per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% Tenaga Kesehatan Masyarakat/kasus'], 3))
    col5.metric(label='Avg. % Nakes Lingkungan per Kasus', value=np.round(df_cluster_means[df_cluster_means['Cluster'] == '5']['% Tenaga Kesehatan Lingkungan/kasus'], 3))
    st.write('Daftar Provinsi: ')
    col5_provinces = ', '.join(list(df_base[df_base['Cluster'] == '5']['Provinsi']))
    st.write(col5_provinces)

columns = ['Provinsi', 'Cluster']
if mode != "Cluster":
  columns.append(color_mode)
else:
  columns = columns + features
# st.write(columns)
df_gen_ai = df_base[columns] # Untuk Bakti

# ---- AI-Powered Insights ----
st.markdown("---")
st.header("AI-Powered Insights")


client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"],
)
# Prepare the data for the AI prompt
data_string = df_gen_ai.to_csv(index=False)
# data_string = df_gen_ai.head(10).to_csv(index=False)


# Construct the prompt
if mode != 'Cluster':
  prompt = (
      "Sebagai Asisten AI, analisis data berikut dan berikan insight yang baik.\n\n"
      f"Data:\n{data_string}\n\n"
      f"Berikan Insight dengan mempertimbangkan rekomendasi WHO berikut : rasio nakes / jumlah penduduk = 0.445%, rasio dokter paru & dokter umum / pasien = 0.4%, rasio perawat / pasien =2%"
  )
else:
  prompt = (
      "Sebagai Asisten AI, analisis karakteristik setiap cluster  beserta daftar provinsinya pada data berikut dengan mempertimbangkan 6 parameter diantaranya: \n"
      f"{features}\n"
      f"Data:\n{data_string}\n\n"
      f"Berikan Insight rekomendasi cluster mana yang perlu diprioritaskan dari prioritas tinggi, menengah, dan rendah, beserta daftar provinsinya untuk penanganan segera dengan mempertimbangkan rekomendasi WHO berikut : rasio nakes / jumlah penduduk = 0.445%, rasio dokter paru & dokter umum / pasien = 0.4%, rasio perawat / pasien =2%"
  )

# Call the OpenAI GPT-4 model
with st.spinner("Generating insights..."):
    try:
        # Create a placeholder for the AI response
        # st.write("### AI Response:")
        response_placeholder = st.empty()

        # Initialize an empty string to hold the AI's response
        ai_response = ""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Kamu adalah Asisten AI yang mampu menganalisa data dan memberikan insight yang baik",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            stream=True,  # Enable streaming
        )

        # Iterate over the streamed response
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content or ""
            ai_response += chunk_message
            # Update the placeholder with the latest AI response
            response_placeholder.markdown(ai_response)
            time.sleep(0.01)  # Optional: control typing speed
    except Exception as e:
        st.error(f"An error occurred: {e}")

# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)