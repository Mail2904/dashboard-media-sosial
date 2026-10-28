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

BASE_URL = (
    "https://raw.githubusercontent.com/"
    "Mail2904/dashboard-media-sosial/main/"
)

INSTAGRAM_URL = BASE_URL + "data.csv"
TIKTOK_URL = BASE_URL + "tiktok.csv"

INSTAGRAM_COLUMNS = [
    "Tayangan",
    "Total Interaksi",
    "Kunjungan Profil",
    "Ketukan Tautan Bio",
    "Net Follower"
]

TIKTOK_REQUIRED = [
    "Tayangan",
    "Net Follower"
]

TARGET = {
    "Instagram": {
        "bulanan": {
            "followers": 45,
            "viewers": 85000
        },
        "tahunan": {
            "followers": 500,
            "viewers": 1000000
        }
    },
    "TikTok": {
        "bulanan": {
            "followers": 85,
            "viewers": 42000
        },
        "tahunan": {
            "followers": 1000,
            "viewers": 500000
        }
    }
}

BULAN = [
    "Januari", "Februari", "Maret",
    "April", "Mei", "Juni",
    "Juli", "Agustus", "September",
    "Oktober", "November", "Desember"
]

BULAN_MAP = {
    nama.lower(): i + 1
    for i, nama in enumerate(BULAN)
}


# ==================================================
# FUNGSI FORMAT
# ==================================================

def format_angka(nilai):
    if pd.isna(nilai):
        return "-"
    return f"{int(nilai):,}".replace(",", ".")


def format_persen(nilai):
    return f"{nilai:.1f}%".replace(".", ",")


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


def status_kpi(aktual, target):
    if aktual >= target:
        return "🟢 Tercapai"
    return "🔴 Belum Tercapai"


def tampil_kpi(label, aktual, target):
    persen = (
        aktual / target * 100
        if target > 0 else 0
    )

    tercapai = aktual >= target

    warna = "#16803c" if tercapai else "#dc2626"
    background = "#e8f7ed" if tercapai else "#fdecec"
    status = "TERCAPAI" if tercapai else "BELUM TERCAPAI"

    st.markdown(
        f"""
        <div style="
            background:{background};
            border:1px solid {warna};
            border-radius:12px;
            padding:18px;
            margin-bottom:12px;
            color:#222;
        ">
            <div style="font-size:14px;font-weight:600;">
                {label}
            </div>
            <div style="
                font-size:25px;
                font-weight:700;
                margin-top:8px;
            ">
                {format_angka(aktual)}
            </div>
            <div style="font-size:13px;margin-top:5px;">
                Target: {format_angka(target)}
            </div>
            <div style="
                font-weight:700;
                color:{warna};
                margin-top:10px;
            ">
                {status} — {format_persen(persen)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        min(max(persen / 100, 0), 1)
    )


# ==================================================
# MEMUAT DATABASE
# ==================================================

@st.cache_data(ttl=60)
def load_csv(url, platform):
    df = pd.read_csv(url, dtype=str)

    df.columns = df.columns.str.strip()

    required = (
        INSTAGRAM_COLUMNS
        if platform == "Instagram"
        else TIKTOK_REQUIRED
    )

    missing = [
        kolom for kolom in ["Bulan"] + required
        if kolom not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Kolom {platform} tidak ditemukan: "
            + ", ".join(missing)
        )

    df = df.dropna(how="all").copy()

    df["Bulan"] = (
        df["Bulan"]
        .fillna("")
        .str.strip()
    )

    df = df[df["Bulan"] != ""].copy()

    # Mendukung Bulan: Januari, Januari 2026,
    # serta kolom Tahun terpisah.
    if "Tahun" in df.columns:
        df["Tahun"] = pd.to_numeric(
            df["Tahun"], errors="coerce"
        )

        df["_Bulan"] = (
            df["Bulan"].str.lower()
            .map(BULAN_MAP)
        )
    else:
        ekstrak = df["Bulan"].str.extract(
            r"^([A-Za-z]+)\s+(\d{4})$"
        )

        bulan_dengan_tahun = ekstrak[0].notna()

        df["Tahun"] = pd.to_numeric(
            ekstrak[1], errors="coerce"
        )

        df["_Bulan"] = (
            df["Bulan"].str.lower()
            .map(BULAN_MAP)
        )

        df.loc[bulan_dengan_tahun, "_Bulan"] = (
            ekstrak.loc[bulan_dengan_tahun, 0]
            .str.lower()
            .map(BULAN_MAP)
        )

    if df["_Bulan"].isna().any():
        raise ValueError(
            f"Format bulan {platform} tidak valid. "
            "Gunakan Januari, Februari, dan seterusnya."
        )

    # Jika tahun tidak tersedia, gunakan 2026.
    # Ubah nilai ini bila database berasal
    # dari tahun yang berbeda.
    df["Tahun"] = df["Tahun"].fillna(2026).astype(int)

    df["Bulan"] = df["_Bulan"].apply(
        lambda x: BULAN[int(x) - 1]
    )

    # Mengonversi kolom numerik.
    # Tidak mengalikan atau menambah nol.
    kolom_angka = [
        kolom for kolom in df.columns
        if kolom not in [
            "Bulan", "Tahun", "_Bulan"
        ]
    ]

    for kolom in kolom_angka:
        nilai = (
            df[kolom]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df[kolom] = pd.to_numeric(
            nilai.replace("", pd.NA),
            errors="coerce"
        )

    # Validasi metrik wajib
    if df[required].isna().any().any():
        raise ValueError(
            f"Data {platform} memiliki angka "
            "kosong atau tidak valid pada kolom wajib."
        )

    if df.duplicated(
        subset=["Tahun", "_Bulan"]
    ).any():
        raise ValueError(
            f"Terdapat bulan dan tahun ganda "
            f"pada database {platform}."
        )

    df = df.sort_values(
        ["Tahun", "_Bulan"]
    ).reset_index(drop=True)

    df["Periode"] = (
        df["Bulan"] + " "
        + df["Tahun"].astype(str)
    )

    return df


# ==================================================
# FUNGSI GRAFIK
# ==================================================

def grafik_line(df, kolom, judul):
    st.subheader(judul)

    fig = px.line(
        df,
        x="Periode",
        y=kolom,
        markers=True
    )

    fig.update_traces(
        mode="lines+markers+text",
        text=[
            format_angka(v)
            for v in df[kolom]
        ],
        textposition="top center",
        hovertemplate=(
            "Periode: %{x}<br>"
            "Nilai: %{y:,.0f}<extra></extra>"
        )
    )

    format_sumbu(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def grafik_bar(df, kolom, judul):
    st.subheader(judul)

    fig = px.bar(
        df,
        x="Periode",
        y=kolom,
        text=kolom
    )

    fig.update_traces(
        text=[
            format_angka(v)
            for v in df[kolom]
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Periode: %{x}<br>"
            "Nilai: %{y:,.0f}<extra></extra>"
        )
    )

    if kolom == "Net Follower":
        fig.update_traces(
            marker_color=[
                "#16a34a" if v >= 0 else "#dc2626"
                for v in df[kolom]
            ]
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_width=1
        )

    format_sumbu(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def grafik_perbandingan(df_ig, df_tt, kolom, judul):
    st.subheader(judul)

    gabungan = pd.concat([
        df_ig[["Periode", kolom]].assign(
            Platform="Instagram"
        ),
        df_tt[["Periode", kolom]].assign(
            Platform="TikTok"
        )
    ], ignore_index=True)

    if gabungan.empty:
        st.info("Belum ada data untuk dibandingkan.")
        return

    fig = px.bar(
        gabungan,
        x="Periode",
        y=kolom,
        color="Platform",
        barmode="group",
        text=kolom,
        color_discrete_map={
            "Instagram": "#d946ef",
            "TikTok": "#111827"
        }
    )

    fig.update_traces(
        texttemplate="%{y:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    format_sumbu(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📊 Menu Dashboard")
st.sidebar.caption("Bengkel Mahaputra")

st.sidebar.divider()

halaman = st.sidebar.radio(
    "Pilih Halaman",
    [
        "🏠 Dashboard Utama",
        "📸 Performa Instagram",
        "🎵 Performa TikTok"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Muat Ulang Data",
    use_container_width=True
):
    load_csv.clear()
    st.rerun()

st.sidebar.caption(
    "Database dibaca dari GitHub. "
    "Cache diperbarui otomatis setiap 60 detik."
)

st.sidebar.markdown("**Sumber Data**")

st.sidebar.markdown(
    "[Instagram - data.csv]"
    "(https://github.com/Mail2904/"
    "dashboard-media-sosial/blob/main/data.csv)"
)

st.sidebar.markdown(
    "[TikTok - tiktok.csv]"
    "(https://github.com/Mail2904/"
    "dashboard-media-sosial/blob/main/tiktok.csv)"
)


# ==================================================
# MEMUAT DATA INSTAGRAM DAN TIKTOK
# ==================================================

try:
    df_ig = load_csv(
        INSTAGRAM_URL,
        "Instagram"
    )

    df_tt = load_csv(
        TIKTOK_URL,
        "TikTok"
    )

except Exception as e:
    st.error("Database gagal dimuat.")

    st.warning(
        "Pastikan data.csv dan tiktok.csv tersedia "
        "di GitHub serta memiliki kolom yang sesuai."
    )

    st.code(str(e))
    st.stop()


# ==================================================
# FILTER TAHUN
# ==================================================

semua_tahun = sorted(
    set(df_ig["Tahun"].tolist())
    | set(df_tt["Tahun"].tolist())
)

tahun = st.sidebar.selectbox(
    "Pilih Tahun",
    options=semua_tahun,
    index=len(semua_tahun) - 1
)

ig_tahun = df_ig[
    df_ig["Tahun"] == tahun
].copy()

tt_tahun = df_tt[
    df_tt["Tahun"] == tahun
].copy()

bulan_tersedia = sorted(
    set(ig_tahun["_Bulan"].tolist())
    | set(tt_tahun["_Bulan"].tolist())
)

nama_bulan = [
    BULAN[int(b) - 1]
    for b in bulan_tersedia
]

bulan_filter = st.sidebar.multiselect(
    "Filter Bulan untuk Grafik",
    options=nama_bulan,
    default=nama_bulan
)

ig_show = ig_tahun[
    ig_tahun["Bulan"].isin(bulan_filter)
].copy()

tt_show = tt_tahun[
    tt_tahun["Bulan"].isin(bulan_filter)
].copy()


# ==================================================
# HALAMAN 1 - DASHBOARD UTAMA
# ==================================================

if halaman == "🏠 Dashboard Utama":

    st.title("📊 Dashboard Performa Media Sosial")

    st.markdown(
        "Ringkasan dan perbandingan performa "
        "**Instagram dan TikTok Bengkel Mahaputra**."
    )

    st.caption(f"Periode evaluasi: Tahun {tahun}")

    st.divider()

    # ----------------------------------------------
    # RINGKASAN TOTAL
    # ----------------------------------------------

    st.header("Ringkasan Performa Media Sosial")

    total_ig_view = ig_show["Tayangan"].sum()
    total_tt_view = tt_show["Tayangan"].sum()

    total_ig_follow = ig_show["Net Follower"].sum()
    total_tt_follow = tt_show["Net Follower"].sum()

    a, b = st.columns(2)

    with a:
        st.subheader("📸 Instagram")

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Tayangan",
            format_angka(total_ig_view)
        )

        c2.metric(
            "Net Follower",
            format_angka(total_ig_follow)
        )

    with b:
        st.subheader("🎵 TikTok")

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Tayangan",
            format_angka(total_tt_view)
        )

        c2.metric(
            "Net Follower",
            format_angka(total_tt_follow)
        )

    st.caption(
        "Ringkasan di atas mengikuti filter bulan. "
        "KPI tahunan di bawah menggunakan seluruh "
        "data pada tahun yang dipilih."
    )

    st.divider()

    # ----------------------------------------------
    # KPI TAHUNAN
    # ----------------------------------------------

    st.header("🎯 KPI Keberhasilan Tahunan")

    st.markdown(
        "Evaluasi pencapaian target tahunan "
        "Instagram dan TikTok."
    )

    ig_view_year = ig_tahun["Tayangan"].sum()
    tt_view_year = tt_tahun["Tayangan"].sum()

    ig_follow_year = ig_tahun["Net Follower"].sum()
    tt_follow_year = tt_tahun["Net Follower"].sum()

    kiri, kanan = st.columns(2)

    with kiri:
        st.subheader("📸 Instagram")

        tampil_kpi(
            "Followers Tahunan",
            ig_follow_year,
            TARGET["Instagram"]["tahunan"]["followers"]
        )

        tampil_kpi(
            "Viewers Tahunan",
            ig_view_year,
            TARGET["Instagram"]["tahunan"]["viewers"]
        )

    with kanan:
        st.subheader("🎵 TikTok")

        tampil_kpi(
            "Followers Tahunan",
            tt_follow_year,
            TARGET["TikTok"]["tahunan"]["followers"]
        )

        tampil_kpi(
            "Viewers Tahunan",
            tt_view_year,
            TARGET["TikTok"]["tahunan"]["viewers"]
        )

    st.divider()

    # ----------------------------------------------
    # KPI BULANAN
    # ----------------------------------------------

    st.header("🎯 KPI Keberhasilan Bulanan")

    st.markdown(
        "Pilih bulan untuk melihat pencapaian "
        "target masing-masing platform."
    )

    if nama_bulan:

        bulan_kpi = st.selectbox(
            "Pilih Bulan Evaluasi KPI",
            options=nama_bulan,
            index=len(nama_bulan) - 1
        )

        ig_bulan = ig_tahun[
            ig_tahun["Bulan"] == bulan_kpi
        ]

        tt_bulan = tt_tahun[
            tt_tahun["Bulan"] == bulan_kpi
        ]

        st.subheader(
            f"Hasil Evaluasi {bulan_kpi} {tahun}"
        )

        kiri, kanan = st.columns(2)

        with kiri:
            st.markdown("### 📸 Instagram")

            if not ig_bulan.empty:

                tampil_kpi(
                    "Followers Bulanan",
                    ig_bulan["Net Follower"].sum(),
                    TARGET["Instagram"]["bulanan"]["followers"]
                )

                tampil_kpi(
                    "Viewers Bulanan",
                    ig_bulan["Tayangan"].sum(),
                    TARGET["Instagram"]["bulanan"]["viewers"]
                )

            else:
                st.info(
                    "Data Instagram bulan ini belum tersedia."
                )

        with kanan:
            st.markdown("### 🎵 TikTok")

            if not tt_bulan.empty:

                tampil_kpi(
                    "Followers Bulanan",
                    tt_bulan["Net Follower"].sum(),
                    TARGET["TikTok"]["bulanan"]["followers"]
                )

                tampil_kpi(
                    "Viewers Bulanan",
                    tt_bulan["Tayangan"].sum(),
                    TARGET["TikTok"]["bulanan"]["viewers"]
                )

            else:
                st.info(
                    "Data TikTok bulan ini belum tersedia."
                )

    st.divider()

    # ----------------------------------------------
    # TABEL KPI BULANAN
    # ----------------------------------------------

    st.header("📋 Rekap Pencapaian KPI Bulanan")

    rekap = []

    for platform, data in [
        ("Instagram", ig_tahun),
        ("TikTok", tt_tahun)
    ]:

        for _, baris in data.iterrows():

            target_f = TARGET[platform]["bulanan"]["followers"]
            target_v = TARGET[platform]["bulanan"]["viewers"]

            rekap.append({
                "Platform": platform,
                "Bulan": baris["Bulan"],
                "Followers": baris["Net Follower"],
                "Target Followers": target_f,
                "Status Followers": status_kpi(
                    baris["Net Follower"], target_f
                ),
                "Viewers": baris["Tayangan"],
                "Target Viewers": target_v,
                "Status Viewers": status_kpi(
                    baris["Tayangan"], target_v
                )
            })

    tabel_rekap = pd.DataFrame(rekap)

    if not tabel_rekap.empty:

        st.dataframe(
            tabel_rekap,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Followers": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Viewers": st.column_config.NumberColumn(
                    format="%d"
                )
            }
        )

    st.divider()

    # ----------------------------------------------
    # GRAFIK PERBANDINGAN
    # ----------------------------------------------

    st.header("📊 Perbandingan Performa")

    grafik_perbandingan(
        ig_show,
        tt_show,
        "Tayangan",
        "Perbandingan Tayangan Instagram dan TikTok"
    )

    grafik_perbandingan(
        ig_show,
        tt_show,
        "Net Follower",
        "Perbandingan Pertumbuhan Followers"
    )

    st.divider()

    # ----------------------------------------------
    # RINGKASAN OTOMATIS
    # ----------------------------------------------

    st.header("💡 Ringkasan Perbandingan")

    if total_ig_view > total_tt_view:
        platform_view = "Instagram"
    elif total_tt_view > total_ig_view:
        platform_view = "TikTok"
    else:
        platform_view = "Keduanya seimbang"

    if total_ig_follow > total_tt_follow:
        platform_follow = "Instagram"
    elif total_tt_follow > total_ig_follow:
        platform_follow = "TikTok"
    else:
        platform_follow = "Keduanya seimbang"

    c1, c2 = st.columns(2)

    with c1:
        st.info(
            "**Platform dengan tayangan lebih tinggi**\n\n"
            + platform_view
        )

    with c2:
        st.info(
            "**Platform dengan pertumbuhan follower lebih tinggi**"
            "\n\n" + platform_follow
        )


# ==================================================
# HALAMAN 2 - INSTAGRAM
# ==================================================

elif halaman == "📸 Performa Instagram":

    st.title("📸 Dashboard Performa Instagram")

    st.markdown(
        "Monitoring dan analisis performa "
        "Instagram Bengkel Mahaputra."
    )

    st.caption(f"Periode: Tahun {tahun}")

    if ig_show.empty:
        st.info(
            "Tidak ada data Instagram untuk "
            "periode yang dipilih."
        )
        st.stop()

    st.divider()

    # ----------------------------------------------
    # KARTU METRIK
    # ----------------------------------------------

    total_tayangan = ig_show["Tayangan"].sum()
    total_interaksi = ig_show["Total Interaksi"].sum()
    total_kunjungan = ig_show["Kunjungan Profil"].sum()
    total_tautan = ig_show["Ketukan Tautan Bio"].sum()
    total_follower = ig_show["Net Follower"].sum()

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

    # ----------------------------------------------
    # GRAFIK
    # ----------------------------------------------

    grafik_line(
        ig_show,
        "Tayangan",
        "📈 Tren Tayangan Instagram"
    )

    kiri, kanan = st.columns(2)

    with kiri:
        grafik_bar(
            ig_show,
            "Total Interaksi",
            "💬 Total Interaksi"
        )

    with kanan:
        grafik_bar(
            ig_show,
            "Kunjungan Profil",
            "👤 Kunjungan Profil"
        )

    st.divider()

    grafik_line(
        ig_show,
        "Ketukan Tautan Bio",
        "🔗 Tren Ketukan Tautan Bio"
    )

    st.divider()

    grafik_bar(
        ig_show,
        "Net Follower",
        "📈 Pertumbuhan Net Follower"
    )

    # ----------------------------------------------
    # TABEL
    # ----------------------------------------------

    st.divider()

    st.subheader("📋 Tabel Data Instagram")

    tabel = ig_show[
        ["Periode"] + INSTAGRAM_COLUMNS
    ].copy()

    st.dataframe(
        tabel,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # RINGKASAN
    # ----------------------------------------------

    st.divider()

    st.subheader("💡 Ringkasan Performa Instagram")

    tayangan_max = ig_show.loc[
        ig_show["Tayangan"].idxmax()
    ]

    interaksi_max = ig_show.loc[
        ig_show["Total Interaksi"].idxmax()
    ]

    follower_max = ig_show.loc[
        ig_show["Net Follower"].idxmax()
    ]

    follower_min = ig_show.loc[
        ig_show["Net Follower"].idxmin()
    ]

    kiri, kanan = st.columns(2)

    with kiri:
        st.info(
            "**Tayangan tertinggi**\n\n"
            f"{tayangan_max['Periode']}: "
            f"{format_angka(tayangan_max['Tayangan'])}"
        )

        st.info(
            "**Interaksi tertinggi**\n\n"
            f"{interaksi_max['Periode']}: "
            f"{format_angka(interaksi_max['Total Interaksi'])}"
        )

    with kanan:
        st.info(
            "**Net follower tertinggi**\n\n"
            f"{follower_max['Periode']}: "
            f"{format_angka(follower_max['Net Follower'])}"
        )

        st.info(
            "**Net follower terendah**\n\n"
            f"{follower_min['Periode']}: "
            f"{format_angka(follower_min['Net Follower'])}"
        )


# ==================================================
# HALAMAN 3 - TIKTOK
# ==================================================

elif halaman == "🎵 Performa TikTok":

    st.title("🎵 Dashboard Performa TikTok")

    st.markdown(
        "Monitoring dan analisis performa "
        "TikTok Bengkel Mahaputra."
    )

    st.caption(f"Periode: Tahun {tahun}")

    if tt_show.empty:
        st.info(
            "Tidak ada data TikTok untuk "
            "periode yang dipilih."
        )
        st.stop()

    st.divider()

    # ----------------------------------------------
    # KARTU METRIK
    # ----------------------------------------------

    metrik_tiktok = [
        kolom for kolom in tt_show.columns
        if kolom not in [
            "Bulan", "Tahun", "_Bulan", "Periode"
        ]
    ]

    kolom_kartu = st.columns(
        min(len(metrik_tiktok), 5)
    )

    for i, kolom in enumerate(metrik_tiktok):
        with kolom_kartu[i % len(kolom_kartu)]:
            st.metric(
                kolom,
                format_angka(tt_show[kolom].sum())
            )

    st.divider()

    # ----------------------------------------------
    # GRAFIK UTAMA
    # ----------------------------------------------

    grafik_line(
        tt_show,
        "Tayangan",
        "📈 Tren Tayangan TikTok"
    )

    st.divider()

    grafik_bar(
        tt_show,
        "Net Follower",
        "📈 Pertumbuhan Net Follower TikTok"
    )

    # ----------------------------------------------
    # GRAFIK TAMBAHAN
    # ----------------------------------------------

    metrik_tambahan = [
        kolom for kolom in metrik_tiktok
        if kolom not in [
            "Tayangan", "Net Follower"
        ]
    ]

    if metrik_tambahan:

        st.divider()
        st.header("📊 Metrik Tambahan TikTok")

        for kolom in metrik_tambahan:
            grafik_bar(
                tt_show,
                kolom,
                f"Tren {kolom}"
            )

    # ----------------------------------------------
    # TABEL DATA
    # ----------------------------------------------

    st.divider()

    st.subheader("📋 Tabel Data TikTok")

    tabel = tt_show[
        ["Periode"] + metrik_tiktok
    ].copy()

    st.dataframe(
        tabel,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # RINGKASAN
    # ----------------------------------------------

    st.divider()

    st.subheader("💡 Ringkasan Performa TikTok")

    tayangan_max = tt_show.loc[
        tt_show["Tayangan"].idxmax()
    ]

    follower_max = tt_show.loc[
        tt_show["Net Follower"].idxmax()
    ]

    follower_min = tt_show.loc[
        tt_show["Net Follower"].idxmin()
    ]

    kiri, kanan = st.columns(2)

    with kiri:
        st.info(
            "**Tayangan tertinggi**\n\n"
            f"{tayangan_max['Periode']}: "
            f"{format_angka(tayangan_max['Tayangan'])}"
        )

    with kanan:
        st.info(
            "**Net follower tertinggi**\n\n"
            f"{follower_max['Periode']}: "
            f"{format_angka(follower_max['Net Follower'])}"
        )

    st.info(
        "**Net follower terendah**\n\n"
        f"{follower_min['Periode']}: "
        f"{format_angka(follower_min['Net Follower'])}"
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Dashboard Performa Media Sosial | Bengkel Mahaputra"
)

st.caption(
    "Sumber: data.csv (Instagram) dan "
    "tiktok.csv (TikTok) pada GitHub. "
    "Nilai ditampilkan sesuai data sumber."
)
