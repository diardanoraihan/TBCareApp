import streamlit as st

st.set_page_config(page_title="Home",
                   layout="wide",
                   page_icon='./images/home.png')
st.sidebar.header('')

# Content
st.markdown(
  """
    <style>
    .btn-3d {
        background-color: red;  /* Red background */
        color: white;           /* White text */
        font-size: 16px;        /* Font size */
        padding: 12px 24px;     /* Padding around the text */
        border: none;           /* Remove border */
        border-radius: 8px;     /* Rounded corners */
        cursor: pointer;       /* Change cursor to pointer on hover */
        text-align: center;     /* Center align the text */
        text-decoration: none;  /* Remove underline */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.12); /* 3D shadow effect */
        transition: transform 0.1s ease, box-shadow 0.1s ease; /* Smooth transition for effects */
        outline: none;          /* Remove outline on focus */
    }

    .btn-3d:active {
        transform: translateY(4px);  /* Button moves down when clicked */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.12); /* Shadow effect when button is pressed */
    }

    .btn-3d:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.12); /* Increase shadow on hover */
        transform: translateY(-2px);  /* Lift button slightly when hovered */
    }
    </style>

  # 🫁 TBCare 1.0
  ### *An AI-Powered Web App to Track the Spread of TBC and Healthcare Resources in Indonesia*
  <a href="/TBCare_App">
      <button class="btn-3d">
          Buka Aplikasi
      </button>
  </a>

  ---
  Aplikasi <b>TBCare 1.0</b> ini dikembangkan oleh Tim <b>Avektive</b> yang beranggotakan 4 orang dalam rangka mengikuti <b>Turnamen Sains Data Nasional 2024</b>

  - Nama Tim: Avektive
  - Ketua: Diardano Raihan
  - Anggota:
    - Syaiful Andy
    - Bakti Satria
    - Arfie Nugraha

  ---
  """,
  unsafe_allow_html=True
)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)