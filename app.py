import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================

st.set_page_config(
    page_title="Dashboard Performa Media Sosial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = (
    "https://raw.githubusercontent.com/"
    "Mail2904/dashboard-media-sosial/main/"
)

INSTAGRAM_URL = BASE_URL + "data.csv"
TIKTOK_URL = BASE_URL + "tiktok.csv"

BULAN = [
    "Januari", "Februari", "Maret", "April",
    "Mei", "Juni", "Juli", "Agustus",
    "September", "Oktober", "November", "Desember"
]

MAP_BULAN = {
    "jan": 1, "januari": 1,
    "feb": 2, "februari": 2,
    "mar": 3, "maret": 3,
    "apr": 4, "april": 4,
    "mei": 5, "may": 5,
    "jun": 6, "juni": 6,
    "jul": 7, "juli": 7,
    "agu": 8, "agt": 8, "aug": 8, "agustus": 8,
    "sep": 9, "sept": 9, "september": 9,
    "okt": 10, "oct": 10, "oktober": 10,
    "nov": 11, "november": 11,
    "des": 12, "dec": 12, "desember": 12
}

KOLOM_IG = [
    "Tayangan",
    "Total Interaksi",
    "Kunjungan Profil",
    "Ketukan Tautan Bio",
    "Net Follower"
]

KOLOM_TIKTOK = [
    "Tayangan",
    "Net Follower"
]

TARGET = {
    "Instagram": {
        "Bulanan": {
            "Followers": 45,
            "Viewers": 30000
        },
        "Tahunan": {
            "Followers": 500,
            "Viewers": 100000
        }
    },
    "TikTok": {
        "Bulanan": {
            "Followers": 85,
            "Viewers": 65000
        },
        "Tahunan": {
            "Followers": 1000,
            "Viewers": 500000
        }
    }
}


# ==================================================
# CSS TAMPILAN
# ==================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.kpi-card {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
    color: #111827;
}
.kpi-success {
    background-color: #ecfdf5;
    border-color: #16a34a;
}
.kpi-failed {
    background-color: #fef2f2;
    border-color: #dc2626;
}
.kpi-title {
    font-size: 14px;
    font-weight: 600;
}
.kpi-value {
    font-size: 27px;
    font-weight: 750;
    margin-top: 8px;
}
.kpi-target {
    font-size: 13px;
    margin-top: 5px;
}
.kpi-status {
    font-size: 14px;
    font-weight: 700;
    margin-top: 10px;
}
.success-text {
    color: #15803d;
}
.failed-text {
    color: #b91c1c;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# FUNGSI FORMAT
# ==================================================

def format_angka(nilai):
    if pd.isna(nilai):
        return "-"
    return f"{int(nilai):,}".replace(",", ".")


def format_persen(nilai):
    return f"{nilai:.1f}%".replace(".", ",")


def status_kpi(aktual, target):
    if aktual >= target:
        return "🟢 Tercapai"
    return "🔴 Belum Tercapai"


def kartu_kpi(judul, aktual, target):

    capaian = aktual / target * 100 if target else 0
    berhasil = aktual >= target

    kelas = "kpi-success" if berhasil else "kpi-failed"
    warna = "success-text" if berhasil else "failed-text"
    status = "TERCAPAI" if berhasil else "BELUM TERCAPAI"

    st.markdown(
        f"""
        <div class="kpi-card {kelas}">
            <div class="kpi-title">{judul}</div>
            <div class="kpi-value">{format_angka(aktual)}</div>
            <div class="kpi-target">
                Target: {format_angka(target)}
            </div>
            <div class="kpi-status {warna}">
                {status} | {format_persen(capaian)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(min(max(capaian / 100, 0), 1))


# ==================================================
# FUNGSI MEMBACA BULAN
# ==================================================

def parse_bulan(teks, tahun_kolom=""):

    teks = str(teks).strip()

    cocok = re.fullmatch(
        r"([A-Za-z]+)[\s\-/]*(\d{2,4})?",
        teks
    )

    if not cocok:
        raise ValueError(
            f"Format bulan tidak valid: {teks}"
        )

    nama_bulan = cocok.group(1).lower()
    tahun_teks = cocok.group(2)

    if nama_bulan not in MAP_BULAN:
        raise ValueError(
            f"Nama bulan tidak dikenal: {teks}"
        )

    nomor_bulan = MAP_BULAN[nama_bulan]

    if str(tahun_kolom).strip():
        tahun_teks = str(tahun_kolom).strip()

    if not tahun_teks:
        tahun = 2026
    else:
        tahun = int(tahun_teks)
        if len(tahun_teks) == 2:
            tahun += 2000

    return nomor_bulan, tahun


# ==================================================
# FUNGSI MEMBACA DATABASE GITHUB
# ==================================================

@st.cache_data(ttl=60)
def load_data(url, platform):

    df = pd.read_csv(
        url,
        dtype=str,
        keep_default_na=False
    )

    df.columns = df.columns.str.strip()

    wajib = (
        KOLOM_IG
        if platform == "Instagram"
        else KOLOM_TIKTOK
    )

    kolom_hilang = [
        k for k in ["Bulan"] + wajib
        if k not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            f"Kolom {platform} tidak ditemukan: "
            + ", ".join(kolom_hilang)
        )

    df = df[
        df["Bulan"].astype(str).str.strip() != ""
    ].copy()

    if df.empty:
        raise ValueError(
            f"Database {platform} kosong."
        )

    nomor_bulan = []
    daftar_tahun = []

    for _, row in df.iterrows():

        tahun_kolom = (
            row["Tahun"]
            if "Tahun" in df.columns
            else ""
        )

        nomor, tahun = parse_bulan(
            row["Bulan"],
            tahun_kolom
        )

        nomor_bulan.append(nomor)
        daftar_tahun.append(tahun)

    df["_Bulan"] = pd.Series(
        nomor_bulan,
        index=df.index,
        dtype="int64"
    )

    df["Tahun"] = pd.Series(
        daftar_tahun,
        index=df.index,
        dtype="int64"
    )

    df["Bulan"] = [
        BULAN[i - 1]
        for i in nomor_bulan
    ]

    kolom_angka = [
        k for k in df.columns
        if k not in ["Bulan", "Tahun", "_Bulan"]
    ]

    for kolom in kolom_angka:

        nilai_bersih = []

        for nilai in df[kolom]:

            teks = str(nilai).strip()
            teks = teks.replace(" ", "")

            if teks == "":
                nilai_bersih.append(None)
                continue

            if "." in teks and "," in teks:
                teks = teks.replace(".", "").replace(",", ".")

            elif "," in teks:
                teks = teks.replace(",", ".")

            elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", teks):
                teks = teks.replace(".", "")

            try:
                nilai_bersih.append(float(teks))
            except ValueError:
                nilai_bersih.append(None)

        df[kolom] = pd.to_numeric(
            pd.Series(nilai_bersih, index=df.index),
            errors="coerce"
        )

    if df[wajib].isna().any().any():
        raise ValueError(
            f"Data {platform} memiliki nilai kosong "
            "atau angka tidak valid."
        )

    if df.duplicated(["Tahun", "_Bulan"]).any():
        raise ValueError(
            f"Terdapat bulan ganda pada {platform}."
        )

    df = df.sort_values(
        ["Tahun", "_Bulan"]
    ).reset_index(drop=True)

    df["Periode"] = (
        df["Bulan"] + " " + df["Tahun"].astype(str)
    )

    return df


# ==================================================
# FUNGSI GRAFIK
# ==================================================

def format_grafik(fig):

    fig.update_layout(
        margin=dict(l=15, r=15, t=45, b=15),
        hovermode="x unified",
        legend_title_text="",
        font=dict(size=12)
    )

    fig.update_xaxes(title=None, type="category")
    fig.update_yaxes(title=None, separatethousands=True)

    return fig


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
        text=[format_angka(v) for v in df[kolom]],
        textposition="top center"
    )

    format_grafik(fig)

    st.plotly_chart(fig, use_container_width=True)


def grafik_bar(df, kolom, judul):

    st.subheader(judul)

    fig = px.bar(
        df,
        x="Periode",
        y=kolom,
        text=kolom
    )

    fig.update_traces(
        text=[format_angka(v) for v in df[kolom]],
        textposition="outside",
        cliponaxis=False
    )

    if kolom == "Net Follower":

        fig.update_traces(
            marker_color=[
                "#16a34a" if v >= 0 else "#dc2626"
                for v in df[kolom]
            ]
        )

        fig.add_hline(y=0, line_dash="dash")

    format_grafik(fig)

    st.plotly_chart(fig, use_container_width=True)


def grafik_perbandingan(ig, tt, kolom, judul):

    st.subheader(judul)

    data = pd.concat([
        ig[["Periode", kolom]].assign(
            Platform="Instagram"
        ),
        tt[["Periode", kolom]].assign(
            Platform="TikTok"
        )
    ], ignore_index=True)

    if data.empty:
        st.info("Belum ada data untuk dibandingkan.")
        return

    fig = px.bar(
        data,
        x="Periode",
        y=kolom,
        color="Platform",
        barmode="group",
        text=kolom,
        color_discrete_map={
            "Instagram": "#d946ef",
            "TikTok": "#06b6d4"
        }
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    format_grafik(fig)

    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📊 Dashboard Mahaputra")
st.sidebar.caption("Monitoring Performa Media Sosial")
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
    load_data.clear()
    st.rerun()

st.sidebar.markdown("**Database GitHub**")

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
# MEMUAT DATA
# ==================================================

st.title("📊 Dashboard Performa Media Sosial")
st.caption("Bengkel Mahaputra | Instagram & TikTok")

try:

    df_ig = load_data(INSTAGRAM_URL, "Instagram")
    df_tt = load_data(TIKTOK_URL, "TikTok")

except Exception as e:

    st.error("Database gagal dimuat.")

    st.warning(
        "Periksa data.csv dan tiktok.csv pada GitHub. "
        "Pastikan kolom dan format data sesuai."
    )

    st.code(str(e))
    st.stop()


# ==================================================
# FILTER TAHUN DAN BULAN
# ==================================================

semua_tahun = sorted(
    set(df_ig["Tahun"]) | set(df_tt["Tahun"])
)

tahun = st.sidebar.selectbox(
    "Pilih Tahun",
    semua_tahun,
    index=len(semua_tahun) - 1
)

ig_tahun = df_ig[df_ig["Tahun"] == tahun].copy()
tt_tahun = df_tt[df_tt["Tahun"] == tahun].copy()

nomor_bulan = sorted(
    set(ig_tahun["_Bulan"]) | set(tt_tahun["_Bulan"])
)

semua_bulan = [BULAN[i - 1] for i in nomor_bulan]

bulan_dipilih = st.sidebar.multiselect(
    "Filter Bulan",
    semua_bulan,
    default=semua_bulan
)

ig_show = ig_tahun[
    ig_tahun["Bulan"].isin(bulan_dipilih)
].copy()

tt_show = tt_tahun[
    tt_tahun["Bulan"].isin(bulan_dipilih)
].copy()


# ==================================================
# HALAMAN 1 - DASHBOARD UTAMA
# ==================================================

if halaman == "🏠 Dashboard Utama":

    st.header("🏠 Ringkasan Performa Media Sosial")

    st.markdown(
        f"Perbandingan performa Instagram dan TikTok "
        f"Bengkel Mahaputra pada tahun **{tahun}**."
    )

    st.divider()

    # RINGKASAN

    kiri, kanan = st.columns(2)

    with kiri:

        st.subheader("📸 Instagram")

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Tayangan",
            format_angka(ig_show["Tayangan"].sum())
        )

        c2.metric(
            "Net Follower",
            format_angka(ig_show["Net Follower"].sum())
        )

    with kanan:

        st.subheader("🎵 TikTok")

        c1, c2 = st.columns(2)

        c1.metric(
            "Total Tayangan",
            format_angka(tt_show["Tayangan"].sum())
        )

        c2.metric(
            "Net Follower",
            format_angka(tt_show["Net Follower"].sum())
        )

    st.caption(
        "Ringkasan mengikuti filter bulan. "
        "KPI tahunan menggunakan seluruh data "
        "pada tahun yang dipilih."
    )

    st.divider()

    # KPI TAHUNAN

    st.header("🎯 KPI Keberhasilan Tahunan")

    kiri, kanan = st.columns(2)

    with kiri:

        st.subheader("📸 Instagram")

        kartu_kpi(
            "Followers Tahunan",
            ig_tahun["Net Follower"].sum(),
            TARGET["Instagram"]["Tahunan"]["Followers"]
        )

        kartu_kpi(
            "Viewers Tahunan",
            ig_tahun["Tayangan"].sum(),
            TARGET["Instagram"]["Tahunan"]["Viewers"]
        )

    with kanan:

        st.subheader("🎵 TikTok")

        kartu_kpi(
            "Followers Tahunan",
            tt_tahun["Net Follower"].sum(),
            TARGET["TikTok"]["Tahunan"]["Followers"]
        )

        kartu_kpi(
            "Viewers Tahunan",
            tt_tahun["Tayangan"].sum(),
            TARGET["TikTok"]["Tahunan"]["Viewers"]
        )

    st.divider()

    # KPI BULANAN

    st.header("🎯 KPI Keberhasilan Bulanan")

    if semua_bulan:

        bulan_kpi = st.selectbox(
            "Pilih Bulan Evaluasi",
            semua_bulan,
            index=len(semua_bulan) - 1
        )

        ig_bulan = ig_tahun[
            ig_tahun["Bulan"] == bulan_kpi
        ]

        tt_bulan = tt_tahun[
            tt_tahun["Bulan"] == bulan_kpi
        ]

        kiri, kanan = st.columns(2)

        with kiri:

            st.subheader("📸 Instagram")

            if not ig_bulan.empty:

                kartu_kpi(
                    "Followers Bulanan",
                    ig_bulan["Net Follower"].sum(),
                    TARGET["Instagram"]["Bulanan"]["Followers"]
                )

                kartu_kpi(
                    "Viewers Bulanan",
                    ig_bulan["Tayangan"].sum(),
                    TARGET["Instagram"]["Bulanan"]["Viewers"]
                )

            else:
                st.info("Data bulan ini belum tersedia.")

        with kanan:

            st.subheader("🎵 TikTok")

            if not tt_bulan.empty:

                kartu_kpi(
                    "Followers Bulanan",
                    tt_bulan["Net Follower"].sum(),
                    TARGET["TikTok"]["Bulanan"]["Followers"]
                )

                kartu_kpi(
                    "Viewers Bulanan",
                    tt_bulan["Tayangan"].sum(),
                    TARGET["TikTok"]["Bulanan"]["Viewers"]
                )

            else:
                st.info("Data bulan ini belum tersedia.")

    st.divider()

    # REKAP KPI

    st.header("📋 Rekap Pencapaian KPI Bulanan")

    rekap = []

    for platform, data in [
        ("Instagram", ig_tahun),
        ("TikTok", tt_tahun)
    ]:

        for _, row in data.iterrows():

            tf = TARGET[platform]["Bulanan"]["Followers"]
            tv = TARGET[platform]["Bulanan"]["Viewers"]

            rekap.append({
                "Platform": platform,
                "Bulan": row["Bulan"],
                "Followers": int(row["Net Follower"]),
                "Target Followers": tf,
                "Status Followers": status_kpi(
                    row["Net Follower"], tf
                ),
                "Viewers": int(row["Tayangan"]),
                "Target Viewers": tv,
                "Status Viewers": status_kpi(
                    row["Tayangan"], tv
                )
            })

    if rekap:

        tabel_kpi = pd.DataFrame(rekap)

        def warna_status(nilai):

            if "🟢" in str(nilai):
                return (
                    "background-color:#dcfce7;"
                    "color:#166534;"
                )

            return (
                "background-color:#fee2e2;"
                "color:#991b1b;"
            )

        st.dataframe(
            tabel_kpi.style.map(
                warna_status,
                subset=[
                    "Status Followers",
                    "Status Viewers"
                ]
            ),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # GRAFIK PERBANDINGAN

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

    # RINGKASAN OTOMATIS

    st.header("💡 Ringkasan Perbandingan")

    ig_view = ig_show["Tayangan"].sum()
    tt_view = tt_show["Tayangan"].sum()

    ig_follow = ig_show["Net Follower"].sum()
    tt_follow = tt_show["Net Follower"].sum()

    if ig_view > tt_view:
        unggul_view = "Instagram"
    elif tt_view > ig_view:
        unggul_view = "TikTok"
    else:
        unggul_view = "Seimbang"

    if ig_follow > tt_follow:
        unggul_follow = "Instagram"
    elif tt_follow > ig_follow:
        unggul_follow = "TikTok"
    else:
        unggul_follow = "Seimbang"

    c1, c2 = st.columns(2)

    c1.info(
        "**Platform dengan tayangan tertinggi**\n\n"
        + unggul_view
    )

    c2.info(
        "**Platform dengan pertumbuhan follower tertinggi**\n\n"
        + unggul_follow
    )


# ==================================================
# HALAMAN 2 - INSTAGRAM
# ==================================================

elif halaman == "📸 Performa Instagram":

    st.header("📸 Dashboard Performa Instagram")

    if ig_show.empty:

        st.info(
            "Tidak ada data Instagram untuk periode ini."
        )

    else:

        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric(
            "👁️ Total Tayangan",
            format_angka(ig_show["Tayangan"].sum())
        )

        k2.metric(
            "💬 Total Interaksi",
            format_angka(ig_show["Total Interaksi"].sum())
        )

        k3.metric(
            "👤 Kunjungan Profil",
            format_angka(ig_show["Kunjungan Profil"].sum())
        )

        k4.metric(
            "🔗 Ketukan Tautan",
            format_angka(ig_show["Ketukan Tautan Bio"].sum())
        )

        k5.metric(
            "📈 Net Follower",
            format_angka(ig_show["Net Follower"].sum())
        )

        st.divider()

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

        st.divider()

        st.header("📋 Tabel Data Instagram")

        st.dataframe(
            ig_show[["Periode"] + KOLOM_IG],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.header("💡 Ringkasan Instagram")

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

    st.header("🎵 Dashboard Performa TikTok")

    if tt_show.empty:

        st.info(
            "Tidak ada data TikTok untuk periode ini."
        )

    else:

        metrik = [
            k for k in tt_show.columns
            if k not in [
                "Bulan", "Tahun", "_Bulan", "Periode"
            ]
        ]

        kartu = st.columns(min(len(metrik), 5))

        for i, kolom in enumerate(metrik):

            with kartu[i % len(kartu)]:

                st.metric(
                    kolom,
                    format_angka(tt_show[kolom].sum())
                )

        st.divider()

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

        tambahan = [
            k for k in metrik
            if k not in ["Tayangan", "Net Follower"]
        ]

        if tambahan:

            st.divider()
            st.header("📊 Metrik Tambahan TikTok")

            for kolom in tambahan:

                grafik_bar(
                    tt_show,
                    kolom,
                    f"Tren {kolom}"
                )

        st.divider()

        st.header("📋 Tabel Data TikTok")

        st.dataframe(
            tt_show[["Periode"] + metrik],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.header("💡 Ringkasan TikTok")

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
    "Sumber data: data.csv (Instagram) dan "
    "tiktok.csv (TikTok) dari GitHub."
)
