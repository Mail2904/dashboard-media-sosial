import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Dashboard Performa Media Sosial",
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


# ==================================================
# FUNGSI FORMAT ANGKA
# ==================================================

def format_angka(nilai):
    if pd.isna(nilai):
        return "-"
    return f"{int(nilai):,}".replace(",", ".")


def format_sumbu(fig):
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=15, r=15, t=55, b=15),
        legend_title_text="",
        font=dict(size=12),
        autosize=True
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(
        title=None,
        separatethousands=True
    )
    return fig


# ==================================================
# MEMUAT DAN MEMVALIDASI DATA
# ==================================================

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL, dtype=str)

    df.columns = df.columns.str.strip()

    # Memastikan kolom wajib tersedia
    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom tidak ditemukan: "
            + ", ".join(kolom_hilang)
        )

    # Menghapus baris yang sepenuhnya kosong
    df = df.dropna(how="all").copy()

    # Membersihkan nama bulan
    df["Bulan"] = df["Bulan"].fillna("").str.strip()

    # Mengabaikan baris kosong yang tidak memiliki bulan
    df = df[df["Bulan"] != ""].copy()

    # Mengonversi angka tanpa mengalikan atau menambah nol
    for kolom in KOLOM_ANGKA:
        nilai = df[kolom].fillna("").str.strip()

        df[kolom] = pd.to_numeric(
            nilai.replace("", pd.NA),
            errors="coerce"
        )

    # Memeriksa angka kosong atau tidak valid
    data_invalid = df[KOLOM_ANGKA].isna()

    if data_invalid.any().any():
        masalah = []

        for kolom in KOLOM_ANGKA:
            indeks_salah = df.index[
                data_invalid[kolom]
            ].tolist()

            for indeks in indeks_salah:
                masalah.append(
                    f"Baris CSV {indeks + 2}, "
                    f"bulan {df.loc[indeks, 'Bulan']}, "
                    f"kolom {kolom}"
                )

        raise ValueError(
            "Data kosong atau tidak valid: "
            + "; ".join(masalah)
            + ". Periksa data.csv."
        )

    # Memeriksa bulan yang tercatat ganda
    if df["Bulan"].duplicated().any():
        bulan_ganda = df.loc[
            df["Bulan"].duplicated(keep=False),
            "Bulan"
        ].tolist()

        raise ValueError(
            "Nama bulan tercatat lebih dari sekali: "
            + ", ".join(bulan_ganda)
        )

    return df.reset_index(drop=True)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📌 Menu Dashboard")
st.sidebar.caption("Bengkel Mahaputra")

st.sidebar.markdown("---")

st.sidebar.markdown("**Sumber Data**")
st.sidebar.markdown(
    "[Lihat data.csv di GitHub]"
    "(https://github.com/Mail2904/dashboard-media-sosial/blob/main/data.csv)"
)

if st.sidebar.button(
    "🔄 Muat Ulang Data",
    use_container_width=True
):
    load_data.clear()
    st.rerun()

st.sidebar.caption(
    "Data diperbarui dari GitHub. "
    "Cache otomatis diperbarui setiap 60 detik."
)

st.sidebar.markdown("---")


# ==================================================
# MEMUAT DATA
# ==================================================

try:
    df = load_data()

except Exception as e:
    st.error("Data gagal dimuat.")
    st.warning(
        "Pastikan data.csv tersedia di GitHub, "
        "kolom sesuai, dan setiap bulan memiliki "
        "nilai angka yang lengkap."
    )
    st.code(str(e))
    st.stop()


# ==================================================
# FILTER BULAN
# ==================================================

st.sidebar.markdown("**Filter Periode**")

semua_bulan = df["Bulan"].tolist()

bulan_dipilih = st.sidebar.multiselect(
    "Pilih bulan yang ingin ditampilkan",
    options=semua_bulan,
    default=semua_bulan
)

if bulan_dipilih:
    data_tampil = df[
        df["Bulan"].isin(bulan_dipilih)
    ].copy()
else:
    data_tampil = df.iloc[0:0].copy()


# ==================================================
# JUDUL DASHBOARD
# ==================================================

st.title("📊 Dashboard Performa Media Sosial")

st.markdown(
    "Monitoring dan analisis performa media sosial "
    "Bengkel Mahaputra berdasarkan data bulanan."
)

st.caption(
    f"Menampilkan {len(data_tampil)} dari {len(df)} periode data."
)

st.divider()


if data_tampil.empty:
    st.info(
        "Pilih minimal satu bulan pada sidebar "
        "untuk menampilkan data dashboard."
    )
    st.stop()


# ==================================================
# KARTU KPI
# ==================================================

total_tayangan = data_tampil["Tayangan"].sum()
total_interaksi = data_tampil["Total Interaksi"].sum()
total_kunjungan = data_tampil["Kunjungan Profil"].sum()
total_tautan = data_tampil["Ketukan Tautan Bio"].sum()
total_follower = data_tampil["Net Follower"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "👁️ Total Tayangan",
    format_angka(total_tayangan)
)

k2.metric(
    "💬 Total Interaksi",
    format_angka(total_interaksi)
)

k3.metric(
    "👤 Kunjungan Profil",
    format_angka(total_kunjungan)
)

k4.metric(
    "🔗 Ketukan Tautan",
    format_angka(total_tautan)
)

k5.metric(
    "📈 Net Follower",
    format_angka(total_follower)
)

st.divider()


# ==================================================
# GRAFIK TAYANGAN
# ==================================================

st.subheader("📈 Tren Tayangan")

fig_tayangan = px.line(
    data_tampil,
    x="Bulan",
    y="Tayangan",
    markers=True,
    text="Tayangan"
)

fig_tayangan.update_traces(
    mode="lines+markers+text",
    text=[
        format_angka(v)
        for v in data_tampil["Tayangan"]
    ],
    textposition="top center",
    hovertemplate=(
        "Bulan: %{x}<br>"
        "Tayangan: %{y:,.0f}<extra></extra>"
    )
)

format_sumbu(fig_tayangan)

st.plotly_chart(
    fig_tayangan,
    use_container_width=True
)


# ==================================================
# GRAFIK INTERAKSI DAN KUNJUNGAN PROFIL
# ==================================================

kolom_kiri, kolom_kanan = st.columns(2)

with kolom_kiri:
    st.subheader("💬 Total Interaksi")

    fig_interaksi = px.bar(
        data_tampil,
        x="Bulan",
        y="Total Interaksi",
        text="Total Interaksi"
    )

    fig_interaksi.update_traces(
        text=[
            format_angka(v)
            for v in data_tampil["Total Interaksi"]
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Bulan: %{x}<br>"
            "Interaksi: %{y:,.0f}<extra></extra>"
        )
    )

    format_sumbu(fig_interaksi)

    st.plotly_chart(
        fig_interaksi,
        use_container_width=True
    )


with kolom_kanan:
    st.subheader("👤 Kunjungan Profil")

    fig_kunjungan = px.bar(
        data_tampil,
        x="Bulan",
        y="Kunjungan Profil",
        text="Kunjungan Profil"
    )

    fig_kunjungan.update_traces(
        text=[
            format_angka(v)
            for v in data_tampil["Kunjungan Profil"]
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Bulan: %{x}<br>"
            "Kunjungan: %{y:,.0f}<extra></extra>"
        )
    )

    format_sumbu(fig_kunjungan)

    st.plotly_chart(
        fig_kunjungan,
        use_container_width=True
    )


# ==================================================
# GRAFIK KETUKAN TAUTAN BIO
# ==================================================

st.divider()
st.subheader("🔗 Tren Ketukan Tautan Bio")

fig_tautan = px.line(
    data_tampil,
    x="Bulan",
    y="Ketukan Tautan Bio",
    markers=True,
    text="Ketukan Tautan Bio"
)

fig_tautan.update_traces(
    mode="lines+markers+text",
    text=[
        format_angka(v)
        for v in data_tampil["Ketukan Tautan Bio"]
    ],
    textposition="top center",
    hovertemplate=(
        "Bulan: %{x}<br>"
        "Ketukan tautan: %{y:,.0f}<extra></extra>"
    )
)

format_sumbu(fig_tautan)

st.plotly_chart(
    fig_tautan,
    use_container_width=True
)


# ==================================================
# GRAFIK NET FOLLOWER
# ==================================================

st.divider()
st.subheader("📈 Pertumbuhan Net Follower")

fig_follower = px.bar(
    data_tampil,
    x="Bulan",
    y="Net Follower",
    text="Net Follower"
)

fig_follower.update_traces(
    text=[
        format_angka(v)
        for v in data_tampil["Net Follower"]
    ],
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "Bulan: %{x}<br>"
        "Net Follower: %{y:,.0f}<extra></extra>"
    )
)

fig_follower.add_hline(
    y=0,
    line_dash="dash",
    line_width=1
)

format_sumbu(fig_follower)

st.plotly_chart(
    fig_follower,
    use_container_width=True
)


# ==================================================
# TABEL DATA
# ==================================================

st.divider()
st.subheader("📋 Tabel Data Performa")

tabel = data_tampil.copy()

for kolom in KOLOM_ANGKA:
    tabel[kolom] = tabel[kolom].map(format_angka)

st.dataframe(
    tabel,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# RINGKASAN OTOMATIS
# ==================================================

st.divider()
st.subheader("💡 Ringkasan Performa")

indeks_tayangan = data_tampil["Tayangan"].idxmax()
indeks_interaksi = data_tampil["Total Interaksi"].idxmax()
indeks_follower_naik = data_tampil["Net Follower"].idxmax()
indeks_follower_turun = data_tampil["Net Follower"].idxmin()

baris_tayangan = data_tampil.loc[indeks_tayangan]
baris_interaksi = data_tampil.loc[indeks_interaksi]
baris_follower_naik = data_tampil.loc[indeks_follower_naik]
baris_follower_turun = data_tampil.loc[indeks_follower_turun]

r1, r2 = st.columns(2)

with r1:
    st.info(
        f"**Tayangan tertinggi**\n\n"
        f"{baris_tayangan['Bulan']}: "
        f"{format_angka(baris_tayangan['Tayangan'])} tayangan."
    )

    st.info(
        f"**Interaksi tertinggi**\n\n"
        f"{baris_interaksi['Bulan']}: "
        f"{format_angka(baris_interaksi['Total Interaksi'])} interaksi."
    )

with r2:
    st.info(
        f"**Net follower tertinggi**\n\n"
        f"{baris_follower_naik['Bulan']}: "
        f"{format_angka(baris_follower_naik['Net Follower'])}."
    )

    st.info(
        f"**Net follower terendah**\n\n"
        f"{baris_follower_turun['Bulan']}: "
        f"{format_angka(baris_follower_turun['Net Follower'])}."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Dashboard Performa Media Sosial | Bengkel Mahaputra"
)

st.caption(
    "Sumber data: data.csv pada repositori GitHub. "
    "Angka ditampilkan sesuai nilai sumber tanpa "
    "pengalian otomatis."
)
