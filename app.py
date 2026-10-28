import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Dashboard Performa Media Sosial', page_icon='📊', layout='wide')

BASE_URL = 'https://raw.githubusercontent.com/Mail2904/dashboard-media-sosial/main/'
SOURCES = {'Instagram': BASE_URL + 'data.csv', 'TikTok': BASE_URL + 'tiktok.csv'}
IG_REQUIRED = ['Tayangan', 'Total Interaksi', 'Kunjungan Profil', 'Ketukan Tautan Bio', 'Net Follower']
TT_REQUIRED = ['Tayangan', 'Net Follower']
MONTHS = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
MONTH_MAP = {m.lower(): i for i, m in enumerate(MONTHS, start=1)}
TARGETS = {'Instagram': {'bulanan': {'Net Follower': 45, 'Tayangan': 85000}, 'tahunan': {'Net Follower': 500, 'Tayangan': 1000000}}, 'TikTok': {'bulanan': {'Net Follower': 85, 'Tayangan': 42000}, 'tahunan': {'Net Follower': 1000, 'Tayangan': 500000}}}


def fmt(value):
    return f'{value:,.0f}'.replace(',', '.')


@st.cache_data(ttl=60)
def load_data(platform):
    url = SOURCES[platform]
    df = pd.read_csv(url, dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()
    required = IG_REQUIRED if platform == 'Instagram' else TT_REQUIRED
    missing = [col for col in ['Bulan'] + required if col not in df.columns]
    if missing:
        raise ValueError(f'{platform}: kolom wajib tidak ditemukan: {", ".join(missing)}')
    df = df.loc[df['Bulan'].astype(str).str.strip().ne('')].copy()
    if df.empty:
        raise ValueError(f'{platform}: CSV tidak memiliki data bulan.')

    raw_month = df['Bulan'].astype(str).str.strip()
    parts = raw_month.str.extract(r'^([A-Za-z]+)(?:\s+(\d{4}))?$', expand=True)
    month_num = parts[0].str.lower().map(MONTH_MAP)
    if month_num.isna().any():
        bad = raw_month.loc[month_num.isna()].tolist()
        raise ValueError(f'{platform}: nama bulan tidak dikenali: {bad}')
    df['_month'] = month_num.astype(int)

    year_from_name = pd.to_numeric(parts[1], errors='coerce')
    if 'Tahun' in df.columns:
        year_from_column = pd.to_numeric(df['Tahun'].replace('', pd.NA), errors='coerce')
        year = year_from_column.combine_first(year_from_name)
    else:
        year = year_from_name
    df['Tahun'] = year.fillna(2026).astype(int)
    df['Bulan'] = df['_month'].map(lambda x: MONTHS[x - 1])

    # Metrik opsional TikTok ikut dibaca, tetapi tidak wajib diisi.
    ignored = {'Bulan', 'Tahun', '_month'}
    metric_columns = [col for col in df.columns if col not in ignored]
    for col in metric_columns:
        raw = df[col].astype(str).str.strip()
        # Gunakan angka CSV tanpa mengalikan ribuan.
        # Format angka yang didukung: 1000, -25, 1000.5.
        converted = pd.to_numeric(raw.replace('', float('nan')), errors='coerce')
        if col in required and converted.isna().any():
            bad_rows = (converted.isna()).to_numpy().nonzero()[0] + 2
            raise ValueError(f'{platform}: kolom {col} berisi nilai kosong/tidak valid pada baris CSV {bad_rows.tolist()}. Gunakan 1000, bukan 1.000.')
        df[col] = converted

    if df.duplicated(['Tahun', '_month']).any():
        raise ValueError(f'{platform}: terdapat bulan dan tahun duplikat.')
    df = df.sort_values(['Tahun', '_month']).reset_index(drop=True)
    df['Periode'] = df['Bulan'] + ' ' + df['Tahun'].astype(str)
    return df


def chart_style(fig):
    fig.update_layout(margin=dict(l=12, r=12, t=45, b=12), hovermode='x unified', legend_title_text='', font=dict(size=12))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None, separatethousands=True)
    return fig


def plot_line(df, col, title):
    st.subheader(title)
    fig = px.line(df, x='Periode', y=col, markers=True, text=col)
    fig.update_traces(text=[fmt(v) if pd.notna(v) else '' for v in df[col]], textposition='top center', hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>')
    st.plotly_chart(chart_style(fig), use_container_width=True)


def plot_bar(df, col, title):
    st.subheader(title)
    fig = px.bar(df, x='Periode', y=col, text=col)
    fig.update_traces(text=[fmt(v) if pd.notna(v) else '' for v in df[col]], textposition='outside', cliponaxis=False)
    if col == 'Net Follower':
        fig.update_traces(marker_color=['#16a34a' if v >= 0 else '#dc2626' for v in df[col].fillna(0)])
        fig.add_hline(y=0, line_dash='dash', line_width=1)
    st.plotly_chart(chart_style(fig), use_container_width=True)


def kpi_card(label, actual, target):
    reached = actual >= target
