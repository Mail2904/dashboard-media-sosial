import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Dashboard Media Sosial Bengkel Mahaputra 2026",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# DATA
# ==================================================

data = {
    "Bulan": [
        "Januari 2026",
        "Februari 2026",
        "Maret 2026",
        "April 2026",
        "Mei 2026",
        "Juni 2026",
        "Juli 2026"
    ],
    
    "Tayangan": [
        90000,
        11134,
        35106,
        27098,
        36113,
        29386,
        57827
    ],
    
    "Total Interaksi": [
        822,
        105,
        235,
        237,
        224,
        248,
        502
    ],
    
    "Kunjungan Profil": [
        2100,
        400,
        772,
        968,
        944,
        995,
        1103
    ],
    
    "Ketukan Tautan Bio": [
        180,
        50,
        118,
        240,
        200,
        231,
        166
    ],
    
    "Net Follower": [
        100,
        5,
        13,
        7,
        -526,
        39,
        68
    ]
}

df = pd.DataFrame(data)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📌 Menu Dashboard")

st.sidebar.write(
    "Gunakan filter di bawah untuk memilih "
    "periode data yang ingin ditampilkan."
)

bulan_terpilih = st.sidebar.multiselect(
    "Pilih Bulan",
    options=df["Bulan"].tolist(),
    default=df["Bulan"].tolist()
)

# Filter data
df_filter = df[
    df["Bulan"].isin(bulan_terpilih)
]

# ==================================================
# JUDUL
# ==================================================

st.title("📊 Dashboard Performa Media Sosial")

st.markdown(
    """
    Dashboard ini menampilkan perkembangan performa
    media sosial selama periode **Januari–Juli 2026**.
    """
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

kolom1, kolom2, kolom3, kolom4, kolom5 = st.columns(5)

with kolom1:
    st.metric(
        label="👁️ Total Tayangan",
        value=f"{total_tayangan:,.0f}".replace(",", ".")
    )

with kolom2:
    st.metric(
        label="💬 Total Interaksi",
        value=f"{total_interaksi:,.0f}".replace(",", ".")
    )

with kolom3:
    st.metric(
        label="👤 Kunjungan Profil",
        value=f"{total_kunjungan:,.0f}".replace(",", ".")
    )

with kolom4:
    st.metric(
        label="🔗 Ketukan Tautan",
        value=f"{total_tautan:,.0f}".replace(",", ".")
    )

with kolom5:
    st.metric(
        label="📈 Net Follower",
        value=f"{total_follower:+,.0f}".replace(",", ".")
    )

st.divider()

# ==================================================
# GRAFIK TAYANGAN
# ==================================================

st.subheader("📈 Perkembangan Tayangan")

grafik_tayangan = px.line(
    df_filter,
    x="Bulan",
    y="Tayangan",
    markers=True,
    text="Tayangan"
)

grafik_tayangan.update_traces(
    textposition="top center"
)

grafik_tayangan.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Jumlah Tayangan",
    hovermode="x unified"
)

st.plotly_chart(
    grafik_tayangan,
    use_container_width=True
)

# ==================================================
# GRAFIK INTERAKSI DAN PROFIL
# ==================================================

kolom_grafik1, kolom_grafik2 = st.columns(2)

with kolom_grafik1:

    st.subheader("💬 Total Interaksi")

    grafik_interaksi = px.bar(
        df_filter,
        x="Bulan",
        y="Total Interaksi",
        text="Total Interaksi"
    )

    grafik_interaksi.update_traces(
        textposition="outside"
    )

    grafik_interaksi.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Interaksi"
    )

    st.plotly_chart(
        grafik_interaksi,
        use_container_width=True
    )


with kolom_grafik2:

    st.subheader("👤 Kunjungan Profil")

    grafik_profil = px.bar(
        df_filter,
        x="Bulan",
        y="Kunjungan Profil",
        text="Kunjungan Profil"
    )

    grafik_profil.update_traces(
        textposition="outside"
    )

    grafik_profil.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Kunjungan"
    )

    st.plotly_chart(
        grafik_profil,
        use_container_width=True
    )

# ==================================================
# GRAFIK KETUKAN TAUTAN
# ==================================================

st.subheader("🔗 Perkembangan Ketukan Tautan Bio")

grafik_tautan = px.line(
    df_filter,
    x="Bulan",
    y="Ketukan Tautan Bio",
    markers=True,
    text="Ketukan Tautan Bio"
)

grafik_tautan.update_traces(
    textposition="top center"
)

grafik_tautan.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Jumlah Ketukan"
)

st.plotly_chart(
    grafik_tautan,
    use_container_width=True
)

# ==================================================
# GRAFIK PERTUMBUHAN FOLLOWER
# ==================================================

st.subheader("📊 Pertumbuhan Pengikut")

grafik_follower = px.bar(
    df_filter,
    x="Bulan",
    y="Net Follower",
    text="Net Follower"
)

grafik_follower.update_traces(
    texttemplate="%{y:+}",
    textposition="outside"
)

grafik_follower.add_hline(
    y=0,
    line_dash="dash"
)

grafik_follower.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Pertumbuhan Pengikut"
)

st.plotly_chart(
    grafik_follower,
    use_container_width=True
)

# ==================================================
# TABEL DATA
# ==================================================

st.subheader("📋 Tabel Performa Media Sosial")

st.dataframe(
    df_filter,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# INSIGHT OTOMATIS
# ==================================================

st.subheader("💡 Insight Otomatis")

if len(df_filter) > 0:

    bulan_tayangan_tertinggi = (
        df_filter.loc[
            df_filter["Tayangan"].idxmax(),
            "Bulan"
        ]
    )

    nilai_tayangan_tertinggi = (
        df_filter["Tayangan"].max()
    )

    bulan_interaksi_tertinggi = (
        df_filter.loc[
            df_filter["Total Interaksi"].idxmax(),
            "Bulan"
        ]
    )

    bulan_follower_tertinggi = (
        df_filter.loc[
            df_filter["Net Follower"].idxmax(),
            "Bulan"
        ]
    )

    bulan_penurunan_follower = (
        df_filter.loc[
            df_filter["Net Follower"].idxmin(),
            "Bulan"
        ]
    )

    st.success(
        f"""
        **Tayangan tertinggi** terjadi pada
        **{bulan_tayangan_tertinggi}**
        dengan total
        **{nilai_tayangan_tertinggi:,.0f} tayangan**.
        """.replace(",", ".")
    )

    st.info(
        f"""
        **Interaksi tertinggi** terjadi pada
        **{bulan_interaksi_tertinggi}**.
        """
    )

    st.success(
        f"""
        **Pertumbuhan pengikut tertinggi**
        terjadi pada **{bulan_follower_tertinggi}**.
        """
    )

    st.warning(
        f"""
        Penurunan pengikut terbesar terjadi pada
        **{bulan_penurunan_follower}**.
        Periode tersebut perlu dievaluasi lebih lanjut.
        """
    )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Dashboard Performa Media Sosial | "
    "Periode Januari–Juli 2026"
)