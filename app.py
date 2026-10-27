import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# KONFIGURASI DASHBOARD
# ==========================================

st.set_page_config(
    page_title="Dashboard Performa Media Sosial Mahaputra",
    page_icon="📊",
    layout="wide"
)

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "Mail2904/dashboard-media-sosial/main/data.csv"
)

KOLOM_ANGKA = [
    "Tayangan",
    "Total Interaksi",
    "Kunjungan Profil",
    "Ketukan Tautan Bio",
    "Net Follower"
]

KOLOM_WAJIB = ["Bulan"] + KOLOM_ANGKA


# ==========================================
# FORMAT ANGKA
# ==========================================

def format_angka(nilai):
    if pd.isna(nilai):
        return "-"
    return f"{int(nilai):,}".replace(",", ".")


# ==========================================
# MEMBACA DAN MEMVALIDASI DATA
# ==========================================

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL, dtype=str)

    # Membersihkan spasi nama kolom
    df.columns = df.columns.str.strip()

    # Memastikan kolom tersedia
    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom tidak ditemukan: "
            + ", ".join(kolom_hilang)
        )

    # Membersihkan spasi pada data
    df["Bulan"] = df["Bulan"].fillna("").str.strip()

    # Mengabaikan baris yang benar-benar kosong
    df = df.dropna(how="all").copy()

    # Mengabaikan baris tanpa nama bulan
    df = df[df["Bulan"] != ""].copy()

    # Mengonversi kolom angka
    for kolom in KOLOM_ANGKA:
        nilai = df[kolom].fillna("").str.strip()

        # Nilai harus berupa angka biasa tanpa pemisah ribuan
        df[kolom] = pd.to_numeric(
            nilai.replace("", pd.NA),
            errors="coerce"
        )

    # Mendeteksi angka kosong atau tidak valid
    data_invalid = df[KOLOM_ANGKA].isna()

    if data_invalid.any().any():
        masalah = []

        for kolom in KOLOM_ANGKA:
            baris_salah = df.index[
                data_invalid[kolom]
            ].tolist()

            for indeks in baris_salah:
                masalah.append(
                    f"Baris CSV {indeks + 2}, "
                    f"kolom '{kolom}', "
                    f"bulan '{df.loc[indeks, 'Bulan']}'"
                )

        raise ValueError(
            "Terdapat data angka kosong atau tidak valid: "
            + "; ".join(masalah)
            + ". Periksa data.csv di GitHub."
        )

    # Memastikan tidak ada nama bulan ganda
    if df["Bulan"].duplicated().any():
        bulan_ganda = df.loc[
            df["Bulan"].duplicated(keep=False),
            "Bulan"
        ].tolist()

        raise ValueError(
            "Terdapat bulan yang tercatat lebih dari sekali: "
            + ", ".join(bulan_ganda)
        )

    return df.reset_index(drop=True)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Dashboard Mahaputra")
st.sidebar.caption("Monitoring Performa Media Sosial")

if st.sidebar.button(
    "Muat Ulang Data",
    use_container_width=True
):
    load_data.clear()
    st.rerun()


# ==========================================
# MEMUAT DATA
# ==========================================

try:
    df = load_data()

except Exception as e:
    st.error("Data gagal dimuat.")
    st.warning(
        "Pastikan data.csv tersedia di GitHub, "
        "nama kolom benar, dan setiap baris bulan "
        "memiliki nilai angka yang lengkap."
    )
    st.code(str(e))
    st.stop()


# ==========================================
# FILTER BULAN
# ==========================================

st.sidebar.subheader("Filter Periode")

pilihan_bulan = st.sidebar.selectbox(
    "Pilih bulan",
    ["Semua Bulan"] + df["Bulan"].tolist()
)

if pilihan_bulan == "Semua Bulan":
    data_tampil = df.copy()
else:
    data_tampil = df[
        df["Bulan"] == pilihan_bulan
    ].copy()


# ==========================================
# JUDUL DASHBOARD
# ==========================================

st.title("Dashboard Performa Media Sosial")
st.caption(
    "Bengkel Mahaputra | Analisis tayangan, interaksi, "
    "kunjungan profil, tautan bio, dan pertumbuhan pengikut"
)

st.divider()


# ==========================================
# RINGKASAN KPI
# ==========================================

total_tayangan = data_tampil["Tayangan"].sum()
total_interaksi = data_tampil["Total Interaksi"].sum()
total_kunjungan = data_tampil["Kunjungan Profil"].sum()
total_tautan = data_tampil["Ketukan Tautan Bio"].sum()
total_follower = data_tampil["Net Follower"].sum()

k1, k2, k3 = st.columns(3)
k4, k5 = st.columns(2)

k1.metric(
    "Total Tayangan",
    format_angka(total_tayangan)
)

k2.metric(
    "Total Interaksi",
    format_angka(total_interaksi)
)

k3.metric(
    "Kunjungan Profil",
    format_angka(total_kunjungan)
)

k4.metric(
    "Ketukan Tautan Bio",
    format_angka(total_tautan)
)

k5.metric(
    "Net Follower",
    format_angka(total_follower)
)

st.divider()


# ==========================================
# GRAFIK TAYANGAN
# ==========================================

st.subheader("Tren Tayangan")

fig_tayangan = px.line(
    data_tampil,
    x="Bulan",
    y="Tayangan",
    markers=True,
    title="Tayangan per Bulan"
)

fig_tayangan.update_traces(
    text=data_tampil["Tayangan"].map(format_angka),
    textposition="top center",
    mode="lines+markers+text",
    hovertemplate=(
        "Bulan: %{x}<br>"
        "Tayangan: %{y:,.0f}<extra></extra>"
    )
)

fig_tayangan.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Jumlah Tayangan",
    hovermode="x unified"
)

st.plotly_chart(
    fig_tayangan,
    use_container_width=True
)


# ==========================================
# GRAFIK INTERAKSI
# ==========================================

st.subheader("Performa Interaksi")

data_interaksi = data_tampil.melt(
    id_vars="Bulan",
    value_vars=[
        "Total Interaksi",
        "Kunjungan Profil",
        "Ketukan Tautan Bio"
    ],
    var_name="Metrik",
    value_name="Jumlah"
)

fig_interaksi = px.bar(
    data_interaksi,
    x="Bulan",
    y="Jumlah",
    color="Metrik",
    barmode="group",
    title="Interaksi, Kunjungan Profil, dan Ketukan Tautan Bio"
)

fig_interaksi.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Jumlah",
    legend_title="Indikator"
)

st.plotly_chart(
    fig_interaksi,
    use_container_width=True
)


# ==========================================
# GRAFIK NET FOLLOWER
# ==========================================

st.subheader("Pertumbuhan Net Follower")

fig_follower = px.bar(
    data_tampil,
    x="Bulan",
    y="Net Follower",
    title="Net Follower per Bulan"
)

fig_follower.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Net Follower"
)

st.plotly_chart(
    fig_follower,
    use_container_width=True
)


# ==========================================
# TABEL DATA
# ==========================================

st.subheader("Tabel Data Performa")

tabel = data_tampil.copy()

for kolom in KOLOM_ANGKA:
    tabel[kolom] = tabel[kolom].map(format_angka)

st.dataframe(
    tabel,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# RINGKASAN OTOMATIS
# ==========================================

st.subheader("Ringkasan Performa")

bulan_tayangan_tertinggi = data_tampil.loc[
    data_tampil["Tayangan"].idxmax()
]

bulan_interaksi_tertinggi = data_tampil.loc[
    data_tampil["Total Interaksi"].idxmax()
]

c1, c2 = st.columns(2)

c1.info(
    f"Tayangan tertinggi terjadi pada "
    f"{bulan_tayangan_tertinggi['Bulan']}, "
    f"sebanyak "
    f"{format_angka(bulan_tayangan_tertinggi['Tayangan'])}."
)

c2.info(
    f"Interaksi tertinggi terjadi pada "
    f"{bulan_interaksi_tertinggi['Bulan']}, "
    f"sebanyak "
    f"{format_angka(bulan_interaksi_tertinggi['Total Interaksi'])}."
)


# ==========================================
# INFORMASI SUMBER DATA
# ==========================================

st.caption(
    "Sumber data: data.csv pada repositori GitHub. "
    "Angka ditampilkan sesuai nilai yang tersimpan "
    "tanpa pengalian otomatis."
)
