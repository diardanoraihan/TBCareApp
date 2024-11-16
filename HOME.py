import streamlit as st

st.set_page_config(page_title="Home",
                   layout="wide",
                   page_icon='./images/home.png')
st.sidebar.header('')
st.sidebar.image("./images/TSDN_logo.png", use_column_width=True)

# Content
st.markdown(
"""
# 🔍 Vulprio 1.0
### *Risk Based Vulnerability Prioritization App using Machine Learning Model*
Aplikasi web untuk memprioritaskan temuan kerentanan CVE berbasis risiko. [Klik di sini untuk menjalankan App](/Vulprio_App/)

---
### Deskripsi
App ini dapat mendeteksi kerentanan pada suatu situs web sekaligus memberikan rekomendasi daftar kerentanan utama yang perlu diprioritaskan. 

### Flow Webapp
- Pengguna menginputkan daftar host (i.e. IP address) beserta 5 parameter diantaranya:
  - Akses Publik
  - Informasi Data Pribadi
  - Klasifikasi Data
  - Potensi Kerugian
  - Jumlah Pengguna
  baik melalui fitur input manual atau unggah file dalam format .xlsx atau .csv
- Webapp akan melakukan pencarian kerentanan (CVE ID) pada daftar host yang telah diinputkan.
  Daftar kerentanan yang berhasil ditemukan merupakan hasil pencarian pada database webapp yang mana datanya sudah dikumpulkan menggunakan scanner kerentanan publik (contoh Shodan).
- Untuk setiap kerentanan tersebut lalu webapp akan menghimpun informasi skor untuk kerentanan tersebut yaitu:
  - CVSS
  - ESPP
  - Ransomware
  - CISA Kev
- Dari 4 atribut tersebut, webapp akan menghitung _risk score_ dan _asset score_ dengan formula sebagai berikut:
  - Risk Score
    - Likelihood = (EPSS + Ransomware + CISA Kev) * 100 / 3
    - Impact = CVSS * 10
    - Risk Score = (Likelihood + Impact) / 2
  - Asset Score
    - Akses publik
      - Ya (2)
      - Tidak (1)
    - Data pribadi
      - Ya (2)
      - Tidak (1)
    - Klasifikasi data
      - Sangat Rahasia (2)
      - Rahasia/Terbatas (1.5)
      - Biasa (1)
    - Potensi kerugian
      - Tinggi (2)
      - Sedang (1.5)
      - Rendah (1)
    - Jumlah pengguna
      - Banyak (2)
      - Sedang (1.5)
      - Sedikit (1)
    - Asset score = (Akses publik + Data Pribadi + Klasifikasi data + Potensi Kerugian + Jumlah Pengguna) * 10 
- Setelah menghitung _Risk Score_ dan _Asset Score_, webapp akan menghitung Priority Score sebagai berikut:
  - Priority Score = (Risk Score + Asset Score) / 2
- Dengan _priority score_ ini, webapp akan secara otomatis menjalankan univariate clustering model menggunakan Kmeans untuk mensegmentasikan setiap temuan kerentanan ke dalam suatu grup dengan karakteristik yang relatif sama.
- Setelah cluster temuan kerentanan berhasil dibuat, webapp akan secara otomatis menampilkan overview dan statistika deskriptif untuk menjelaskan persebaran data temuan kerentanan tersebut.
- Di akhir, webapp akan secara pintar memberikan rekomendasi prioritas cluster temuan kerentanan yang harus segera diatasi. 
""")

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)