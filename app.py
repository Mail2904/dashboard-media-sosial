
import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Dashboard Media Sosial Mahaputra 2026",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# DATABASE GITHUB
# ==================================================

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
# FUNGSI MEMBACA DATABASE
# ==================================================

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)

    # Validasi kolom
    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom berikut tidak ditemukan di data.csv: "
            + ", ".join(kolom_hilang)
        )

    # Membersihkan data
    df["Bulan"] = df["Bulan"].astype("string").str.strip()

    df = df[
        df["Bulan"].notna() & (df["Bulan"] != "")
    ].copy()

    for kolom in KOLOM_ANGKA:
        df[kolom] = pd.to_numeric(
            df[kolom].astype("string")
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )

    # Baris tanpa angka tetap boleh ada di database,
    # tetapi tidak digunakan dalam perhitungan.
    return df


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
    "Data dibaca dari GitHub. "
    "Cache otomatis diperbarui setiap 60 detik."
)

# ==================================================
# MEMUAT DATABASE
# ==================================================

try:
    df = load_data()

except Exception as e:
    st.error(
        "Data gagal dimuat. Periksa file data.csv, "
        "URL GitHub, nama kolom, dan koneksi internet."
    )
    st.code(str(e))
    st.stop()

# ==================================================
# FILTER BULAN
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

# Hanya data yang memiliki angka untuk grafik
df_valid = df_filter.dropna(subset=KOLOM_ANGKA, how="all")

# ==================================================
# JUDUL DASHBOARD
# ==================================================

st.title("📊 Dashboard Performa Media Sosial")

st.markdown(
    """
    Dashboard ini menampilkan perkembangan performa
    media sosial Bengkel Mahaputra berdasarkan data bulanan
    yang tersimpan di GitHub.
    """
)

st.caption(
    f"Jumlah periode dipilih: {len(bulan_terpilih)} bulan"
)

st.divider()

# ==================================================
# FORMAT ANGKA
# ==================================================

def format_angka(nilai, tanda_plus=False):
    nilai = int(nilai)
    if tanda_plus:
        return f"{nilai:+,}".replace(",", ".")
    return f"{nilai:,}".replace(",", ".")


# ==================================================
# KPI UTAMA
# ==================================================

total_tayangan = df_filter["Tayangan"].sum()
total_interaksi = df_filter["Total Interaksi"].sum()
total_kunjungan = df_filter["Kunjungan Profil"].sum()
total_tautan = df_filter["Ketukan Tautan Bio"].sum()
total_follower = df_filter["Net Follower"].sum()

kolom1, kolom2, kolom3, kolom4, kolom5 = st.columns(5)

with kolom1:
    st.metric(
        "👁️ Total Tayangan",
        format_angka(total_tayangan)
    )

with kolom2:
    st.metric(
        "💬 Total Interaksi",
        format_angka(total_interaksi)
    )

with kolom3:
    st.metric(
        "👤 Kunjungan Profil",
        format_angka(total_kunjungan)
    )

with kolom4:
    st.metric(
        "🔗 Ketukan Tautan",
        format_angka(total_tautan)
    )

with kolom5:
    st.metric(
        "📈 Net Follower",
        format_angka(total_follower, tanda_plus=True)
    )

st.divider()

# ==================================================
# GRAFIK
# ==================================================

if df_valid.empty:
    st.warning(
        "Belum ada data angka untuk periode yang dipilih."
    )

else:
    # Grafik tayangan
    st.subheader("📈 Perkembangan Tayangan")

    data_tayangan = df_valid.dropna(subset=["Tayangan"])

    if not data_tayangan.empty:
        fig_tayangan = px.line(
            data_tayangan,
            x="Bulan",
            y="Tayangan",
            markers=True,
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
            xaxis_title="Bulan",
            yaxis_title="Jumlah Tayangan",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_tayangan,
            use_container_width=True
        )

    # Grafik interaksi dan profil
    kolom_grafik1, kolom_grafik2 = st.columns(2)

    with kolom_grafik1:
        st.subheader("💬 Total Interaksi")

        data_interaksi = df_valid.dropna(
            subset=["Total Interaksi"]
        )

        if not data_interaksi.empty:
            fig_interaksi = px.bar(
                data_interaksi,
                x="Bulan",
                y="Total Interaksi",
                text="Total Interaksi"
            )

            fig_interaksi.update_traces(
                texttemplate="%{y:,.0f}",
                textposition="outside"
            )

            fig_interaksi.update_layout(
                xaxis_title="Bulan",
                yaxis_title="Jumlah Interaksi"
            )

            st.plotly_chart(
                fig_interaksi,
                use_container_width=True
            )

    with kolom_grafik2:
        st.subheader("👤 Kunjungan Profil")

        data_profil = df_valid.dropna(
            subset=["Kunjungan Profil"]
        )

        if not data_profil.empty:
            fig_profil = px.bar(
                data_profil,
                x="Bulan",
                y="Kunjungan Profil",
                text="Kunjungan Profil"
            )

            fig_profil.update_traces(
                texttemplate="%{y:,.0f}",
                textposition="outside"
            )

            fig_profil.update_layout(
                xaxis_title="Bulan",
                yaxis_title="Jumlah Kunjungan"
            )

            st.plotly_chart(
                fig_profil,
                use_container_width=True
            )

    # Grafik tautan bio
    st.subheader("🔗 Perkembangan Ketukan Tautan Bio")

    data_tautan = df_valid.dropna(
        subset=["Ketukan Tautan Bio"]
    )

    if not data_tautan.empty:
        fig_tautan = px.line(
            data_tautan,
            x="Bulan",
            y="Ketukan Tautan Bio",
            markers=True,
            text="Ketukan Tautan Bio"
        )

        fig_tautan.update_traces(
            texttemplate="%{y:,.0f}",
            textposition="top center"
        )

        fig_tautan.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Jumlah Ketukan"
        )

        st.plotly_chart(
            fig_tautan,
            use_container_width=True
        )

    # Grafik follower
    st.subheader("📊 Pertumbuhan Pengikut")

    data_follower = df_valid.dropna(
        subset=["Net Follower"]
    )

    if not data_follower.empty:
        fig_follower = px.bar(
            data_follower,
            x="Bulan",
            y="Net Follower",
            text="Net Follower"
        )

        fig_follower.update_traces(
            texttemplate="%{y:+,.0f}",
            textposition="outside"
        )

        fig_follower.add_hline(
            y=0,
            line_dash="dash"
        )

        fig_follower.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Pertumbuhan Pengikut"
        )

        st.plotly_chart(
            fig_follower,
            use_container_width=True
        )

# ==================================================
# TABEL DATA
# ==================================================

st.divider()
st.subheader("📋 Tabel Performa Media Sosial")

st.dataframe(
    df_filter,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# INSIGHT OTOMATIS
# ==================================================

st.divider()
st.subheader("💡 Insight Otomatis")

if not df_valid.empty:

    data_tayangan = df_valid.dropna(subset=["Tayangan"])
    data_interaksi = df_valid.dropna(subset=["Total Interaksi"])
    data_follower = df_valid.dropna(subset=["Net Follower"])

    if not data_tayangan.empty:
        idx = data_tayangan["Tayangan"].idxmax()
        bulan = data_tayangan.loc[idx, "Bulan"]
        nilai = data_tayangan.loc[idx, "Tayangan"]

        st.success(
            f"**Tayangan tertinggi:** {bulan}, "
            f"sebanyak {format_angka(nilai)} tayangan."
        )

    if not data_interaksi.empty:
        idx = data_interaksi["Total Interaksi"].idxmax()
        bulan = data_interaksi.loc[idx, "Bulan"]
        nilai = data_interaksi.loc[idx, "Total Interaksi"]

        st.info(
            f"**Interaksi tertinggi:** {bulan}, "
            f"sebanyak {format_angka(nilai)} interaksi."
        )

    if not data_follower.empty:
        idx_max = data_follower["Net Follower"].idxmax()
        idx_min = data_follower["Net Follower"].idxmin()

        bulan_max = data_follower.loc[idx_max, "Bulan"]
        nilai_max = data_follower.loc[idx_max, "Net Follower"]

        bulan_min = data_follower.loc[idx_min, "Bulan"]
        nilai_min = data_follower.loc[idx_min, "Net Follower"]

        st.success(
            f"**Pertumbuhan pengikut tertinggi:** {bulan_max}, "
            f"dengan net follower {format_angka(nilai_max, True)}."
        )

        if nilai_min < 0:
            st.warning(
                f"**Penurunan pengikut terbesar:** {bulan_min}, "
                f"dengan net follower {format_angka(nilai_min, True)}. "
                "Periode ini perlu dievaluasi lebih lanjut."
            )
        else:
            st.info(
                f"**Net follower terendah:** {bulan_min}, "
                f"dengan {format_angka(nilai_min, True)} pengikut."
            )

else:
    st.info("Insight akan muncul setelah data tersedia.")

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Dashboard Performa Media Sosial Bengkel Mahaputra | "
    "Data bersumber dari GitHub"
)
