import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# KONFIGURASI DASHBOARD
# ==========================================

st.set_page_config(
    page_title="Dashboard Media Sosial Mahaputra",
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
    "Net Follower",
]

KOLOM_WAJIB = ["Bulan"] + KOLOM_ANGKA


# ==========================================
# FORMAT ANGKA
# ==========================================

def format_angka(nilai):
    """Menampilkan angka dengan titik sebagai pemisah ribuan."""
    return f"{int(nilai):,}".replace(",", ".")


# ==========================================
# MEMBACA DATA
# ==========================================

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)

    # Membersihkan spasi pada nama kolom
    df.columns = df.columns.str.strip()

    # Memastikan seluruh kolom wajib tersedia
    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom berikut tidak ditemukan: "
            + ", ".join(kolom_hilang)
        )

    # Menghapus spasi di kolom Bulan
    df["Bulan"] = df["Bulan"].astype(str).str.strip()

    # Konversi langsung tanpa menghapus titik atau menambah nol
    for kolom in KOLOM_ANGKA:
        df[kolom] = pd.to_numeric(
            df[kolom],
            errors="coerce"
        )

    # Memastikan data angka tidak kosong
    if df[KOLOM_ANGKA].isna().any().any():
        raise ValueError(
            "Ada data angka kosong atau tidak valid di data.csv. "
            "Periksa penulisan angka pada file CSV."
        )

    # Data bulan harus unik
    if df["Bulan"].duplicated().any():
        raise ValueError(
            "Ada nama bulan yang tercatat lebih dari satu kali."
        )

    return df


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📊 Dashboard Mahaputra")
st.sidebar.caption("Analisis Performa Media Sosial")

if st.sidebar.button(
    "🔄 Muat Ulang Data",
    use_container_width=True
):
    load_data.clear()
    st.rerun()


# ==========================================
# MEMUAT DATA DAN MENANGANI ERROR
# ==========================================

try:
    df = load_data()

except Exception as e:
    st.error(
        "Data gagal dimuat. Pastikan data.csv sudah tersedia "
        "di GitHub dan nama kolomnya sesuai."
    )
    st.code(str(e))
    st.stop()


# ==========================================
# FILTER BULAN
# ==========================================

st.sidebar.subheader("Filter Data")

daftar_bulan = df["Bulan"].tolist()

pilihan_bulan = st.sidebar.selectbox(
    "Pilih periode",
    ["Semua Bulan"] + daftar_bulan
)

if pilihan_bulan == "Semua Bulan":
    data_tampil = df.copy()
else:
    data_tampil = df[
        df["Bulan"] == pilihan_bulan
    ].copy()


# ==========================================
# JUDUL
# ==========================================

st.title("Dashboard Performa Media Sosial")
st.caption(
    "Bengkel Mahaputra | Monitoring tayangan, interaksi, "
    "kunjungan profil, tautan bio, dan pertumbuhan pengikut"
)

st.divider()


# ==========================================
# KPI
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
    title="Tayangan per Bulan",
    text="Tayangan"
)

fig_tayangan.update_traces(
    texttemplate="%{y:,.0f}",
    textposition="top center",
    hovertemplate=(
        "Bulan: %{x}<br>"
        "Tayangan: %{y:,.0f}<extra></extra>"
    )
)

fig_tayangan.update_layout(
    yaxis_title="Jumlah Tayangan",
    xaxis_title="Bulan",
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
        "Ketukan Tautan Bio",
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
    title="Interaksi, Kunjungan Profil, dan Ketukan Tautan Bio",
    text="Jumlah"
)

fig_interaksi.update_traces(
    texttemplate="%{y:,.0f}",
    textposition="outside",
    cliponaxis=False
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
    title="Net Follower per Bulan",
    text="Net Follower"
)

fig_follower.update_traces(
    texttemplate="%{y:,.0f}",
    textposition="outside",
    cliponaxis=False
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

# Memformat angka hanya untuk tampilan tabel.
# Nilai asli pada data_tampil tidak diubah.
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

if not data_tampil.empty:
    bulan_tertinggi = data_tampil.loc[
        data_tampil["Tayangan"].idxmax(),
        "Bulan"
    ]

    tayangan_tertinggi = data_tampil["Tayangan"].max()

    bulan_interaksi = data_tampil.loc[
        data_tampil["Total Interaksi"].idxmax(),
        "Bulan"
    ]

    interaksi_tertinggi = data_tampil["Total Interaksi"].max()

    c1, c2 = st.columns(2)

    c1.info(
        f"Tayangan tertinggi terjadi pada {bulan_tertinggi}, "
        f"sebanyak {format_angka(tayangan_tertinggi)}."
    )

    c2.info(
        f"Total interaksi tertinggi terjadi pada {bulan_interaksi}, "
        f"sebanyak {format_angka(interaksi_tertinggi)}."
    )

st.caption(
    "Sumber data: data.csv pada repositori GitHub. "
    "Data tersimpan sebagai angka asli dan hanya diformat "
    "ketika ditampilkan."
)
