import streamlit as st

st.set_page_config(page_title="Home",
                   layout="wide",
                   page_icon='./images/home.png')
st.sidebar.header('')

# Content
st.markdown(
"""
# 🫁 TBCare 1.0
### *An AI-Powered Web App to Track the Spread of TBC and Healthcare Resources in Indonesia*
#### Turnamen Sains Data Nasional 2024 [Klik di sini untuk menjalankan App](/TBCare_App/)

Dibuat oleh:
- Nama Tim: Avektive
- Ketua: Diardano Raihan	
- Anggota: 
  - Syaiful Andy	
  - Bakti Satria	
  - Arfie Nugraha
---
### 
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