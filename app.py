import streamlit as st
import pandas as pd

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "Mail2904/dashboard-media-sosial/main/data.csv"
)

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)

    kolom_angka = [
        "Tayangan",
        "Total Interaksi",
        "Kunjungan Profil",
        "Ketukan Tautan Bio",
        "Net Follower"
    ]

    for kolom in kolom_angka:
        df[kolom] = pd.to_numeric(
            df[kolom], errors="coerce"
        )

    return df

df = load_data()
