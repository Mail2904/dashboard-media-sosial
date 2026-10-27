import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# KONFIGURASI
# ==================================================

st.set_page_config(
    page_title="Dashboard Media Sosial Mahaputra 2026",
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

# Urutan bulan agar grafik selalu kronologis.
URUTAN_BULAN = [
    "Jan-26", "Feb-26", "Mar-26", "Apr-26",
    "May-26", "Jun-26", "Jul-26", "Aug-26",
    "Sep-26", "Oct-26", "Nov-26", "Dec-26"
]


# ==================================================
# MEMBACA DATABASE GITHUB
# ==================================================

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)

    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom tidak ditemukan di data.csv: "
            + ", ".join(kolom_hilang)
        )

    df["Bulan"] = df["Bulan"].astype("string").str.strip()

    df = df[
        df["Bulan"].notna()
        & (df["Bulan"] != "")
    ].copy()

    for kolom in KOLOM_ANGKA:
        # Mendukung angka biasa dan angka dengan
        # pemisah ribuan titik, misalnya 1.103.
        nilai = df[kolom].astype("string").str.strip()
        nilai = nilai.str.replace(r"\s+", "", regex=True)
        nilai = nilai.str.replace(".", "", regex=False)
        nilai = nilai.str.replace(",", ".", regex=False)

        df[kolom] = pd.to_numeric(
            nilai,
            errors="coerce"
        )

    # Bulan tanpa data angka tidak dipakai
    # dalam grafik dan perhitungan.
    df = df.dropna(subset=KOLOM_ANGKA, how="all")

    df["_urutan"] = df["Bulan"].map(
        {bulan: i for i, bulan in enumerate(URUTAN_BULAN)}
    )

    df = df.sort_values(
        "_urutan",
        na_position="last"
    ).drop(columns="_urutan")

    return df


def fmt(nilai, plus=False):
    nilai = int(nilai)
    if plus:
        return f"{nilai:+,}".replace(",", ".")
    return f"{nilai:,}".replace(",", ".")


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📌 Menu Dashboard")
st.sidebar.write(
    "Dashboard Performa Media Sosial "
    "Bengkel Mahaputra."
)

if st.sidebar.button(
    "🔄 Muat Ulang Data",
    use_container_width=True
):
    load_data.clear()
    st.rerun()

st.sidebar.caption(
    "Sumber database: GitHub | Cache 60 detik"
)


# ==================================================
# LOAD DATA DAN PENANGANAN ERROR
# ==================================================

try:
    df = load_data()

except Exception as e:
    st.error(
        "Data gagal dimuat. Pastikan data.csv tersedia "
        "di branch main dan nama kolom sudah benar."
    )
    st.code(str(e))
    st.stop()


# ==================================================
# FILTER
# ==================================================

st.sidebar.divider()
st.sidebar.subheader("Filter Data")

bulan_terpilih = st.sidebar.multiselect(
    "Pilih Bulan",
    options=df["Bulan"].tolist(),
    default=df["Bulan"].tolist()
)

df_filter = df[
    df["Bulan"].isin(bulan_terpilih)
].copy()

st.title("📊 Dashboard Performa Media Sosial")

st.markdown(
    """
    Dashboard ini menyajikan perkembangan performa
    media sosial Bengkel Mahaputra berdasarkan data
    bulanan yang disimpan di GitHub.
    """
)

st.caption(
    f"Periode terpilih: {len(bulan_terpilih)} bulan"
)

st.divider()


# ==================================================
# KPI UTAMA
# ==================================================

total_tayangan = df_filter["Tayangan"].sum()
total_interaksi = df_filter["Total Interaksi"].sum()
total_kunjungan = df_filter["Kunjungan Profil"].sum()
total_tautan = df_filter["Ketukan Tautan Bio"].sum()
total_follower = df_filter["Net Follower"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("👁️ Total Tayangan", fmt(total_tayangan))

with k2:
    st.metric("💬 Total Interaksi", fmt(total_interaksi))

with k3:
    st.metric("👤 Kunjungan Profil", fmt(total_kunjungan))

with k4:
    st.metric("🔗 Ketukan Tautan", fmt(total_tautan))

with k5:
    st.metric(
        "📈 Net Follower",
        fmt(total_follower, plus=True)
    )

st.divider()


# ==================================================
# GRAFIK TAYANGAN
# ==================================================

st.subheader("📈 Perkembangan Tayangan")

if not df_filter.empty:
    fig = px.line(
        df_filter,
        x="Bulan",
        y="Tayangan",
        markers=True,
        text="Tayangan"
    )

    fig.update_traces(
        texttemplate="%{y:,.0f}",
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Tayangan",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pilih setidaknya satu bulan yang memiliki data.")


# ==================================================
# GRAFIK INTERAKSI DAN PROFIL
# ==================================================

kolom1, kolom2 = st.columns(2)

with kolom1:
    st.subheader("💬 Total Interaksi")

    if not df_filter.empty:
        fig = px.bar(
            df_filter,
            x="Bulan",
            y="Total Interaksi",
            text="Total Interaksi"
        )

        fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Jumlah Interaksi"
        )

        st.plotly_chart(fig, use_container_width=True)

with kolom2:
    st.subheader("👤 Kunjungan Profil")

    if not df_filter.empty:
        fig = px.bar(
            df_filter,
            x="Bulan",
            y="Kunjungan Profil",
            text="Kunjungan Profil"
        )

        fig.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Jumlah Kunjungan"
        )

        st.plotly_chart(fig, use_container_width=True)


# ==================================================
# GRAFIK KETUKAN TAUTAN BIO
# ==================================================

st.subheader("🔗 Perkembangan Ketukan Tautan Bio")

if not df_filter.empty:
    fig = px.line(
        df_filter,
        x="Bulan",
        y="Ketukan Tautan Bio",
        markers=True,
        text="Ketukan Tautan Bio"
    )

    fig.update_traces(
        texttemplate="%{y:,.0f}",
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Ketukan"
    )

    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# GRAFIK PERTUMBUHAN FOLLOWER
# ==================================================

st.subheader("📊 Pertumbuhan Pengikut")

if not df_filter.empty:
    fig = px.bar(
        df_filter,
        x="Bulan",
        y="Net Follower",
        text="Net Follower"
    )

    fig.update_traces(
        texttemplate="%{y:+,.0f}",
        textposition="outside"
    )

    fig.add_hline(
        y=0,
        line_dash="dash"
    )

    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Pertumbuhan Pengikut"
    )

    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# TABEL DATA
# ==================================================

st.divider()
st.subheader("📋 Tabel Performa Media Sosial")

tabel = df_filter.copy()

for kolom in KOLOM_ANGKA:
    tabel[kolom] = tabel[kolom].apply(
        lambda x: fmt(x) if pd.notna(x) else "-"
    )

st.dataframe(
    tabel,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# INSIGHT OTOMATIS
# ==================================================

st.divider()
st.subheader("💡 Insight Otomatis")

if not df_filter.empty:

    tayangan = df_filter.dropna(subset=["Tayangan"])
    interaksi = df_filter.dropna(subset=["Total Interaksi"])
    follower = df_filter.dropna(subset=["Net Follower"])

    if not tayangan.empty:
        baris = tayangan.loc[tayangan["Tayangan"].idxmax()]

        st.success(
            f"**Tayangan tertinggi:** {baris['Bulan']} "
            f"dengan {fmt(baris['Tayangan'])} tayangan."
        )

    if not interaksi.empty:
        baris = interaksi.loc[
            interaksi["Total Interaksi"].idxmax()
        ]

        st.info(
            f"**Interaksi tertinggi:** {baris['Bulan']} "
            f"dengan {fmt(baris['Total Interaksi'])} interaksi."
        )

    if not follower.empty:
        baris_max = follower.loc[
            follower["Net Follower"].idxmax()
        ]

        st.success(
            f"**Pertumbuhan pengikut tertinggi:** "
            f"{baris_max['Bulan']} dengan net follower "
            f"{fmt(baris_max['Net Follower'], plus=True)}."
        )

        baris_min = follower.loc[
            follower["Net Follower"].idxmin()
        ]

        if baris_min["Net Follower"] < 0:
            st.warning(
                f"**Penurunan pengikut terbesar:** "
                f"{baris_min['Bulan']} dengan net follower "
                f"{fmt(baris_min['Net Follower'], plus=True)}. "
                "Periode ini perlu dievaluasi."
            )

else:
    st.info("Belum ada data untuk menghasilkan insight.")


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Dashboard Performa Media Sosial Bengkel Mahaputra "
    "| Data bersumber dari GitHub"
)
