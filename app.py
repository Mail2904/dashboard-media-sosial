    if show.empty:
        st.info('Pilih minimal satu bulan untuk melihat performa.')
        return
    cols = ['Tayangan', 'Net Follower']
    if platform == 'Instagram':
        cols = ['Tayangan', 'Total Interaksi', 'Kunjungan Profil', 'Ketukan Tautan Bio', 'Net Follower']
    else:
        cols = ['Tayangan'] + [c for c in df.columns if c not in ['Bulan','Tahun','Nomor Bulan','Tayangan','Net Follower']] + ['Net Follower']
    metrics = st.columns(min(len(cols), 5))
    for i, c in enumerate(cols):
        metrics[i % len(metrics)].metric(c, fmt(show[c].sum()))
    st.divider()
    series_chart(show, 'Tayangan', '📈 Tren Tayangan', 'line')
    others = [c for c in cols if c not in ['Tayangan','Net Follower']]
    for start in range(0, len(others), 2):
        pair = st.columns(2)
        for j, c in enumerate(others[start:start+2]):
            with pair[j]:
                series_chart(show, c, c)
    series_chart(show, 'Net Follower', '📈 Pertumbuhan Net Follower')
    st.subheader('📋 Tabel Data Performa')
    st.dataframe(show[['Bulan']+cols].style.format({c:'{:,.0f}' for c in cols}), use_container_width=True, hide_index=True)
    st.subheader('💡 Ringkasan Otomatis')
    for c in ['Tayangan','Net Follower']:
        best = show.loc[show[c].idxmax()]
        st.info(f'**{c} tertinggi:** {best["Bulan"]} — {fmt(best[c])}')
    worst = show.loc[show['Net Follower'].idxmin()]
    st.info(f'**Net Follower terendah:** {worst["Bulan"]} — {fmt(worst["Net Follower"])}')

st.sidebar.title('📌 Menu Dashboard')
st.sidebar.caption('Bengkel Mahaputra')
page = st.sidebar.radio('Pilih halaman', ['🏠 Halaman Utama', '📸 Performa Instagram', '🎵 Performa TikTok'])
if st.sidebar.button('🔄 Muat Ulang Data', use_container_width=True):
    read_csv.clear()
    st.rerun()
st.sidebar.caption('Sumber data GitHub · cache 60 detik')
st.sidebar.markdown('[data.csv (Instagram)](https://github.com/Mail2904/dashboard-media-sosial/blob/main/data.csv)')
st.sidebar.markdown('[tiktok.csv (TikTok)](https://github.com/Mail2904/dashboard-media-sosial/blob/main/tiktok.csv)')
try:
    ig = load_platform('data.csv', IG_COLS)
    tt = load_platform('tiktok.csv', TT_COLS)
except Exception as exc:
    st.error('Gagal membaca data CSV. Periksa nama file, nama kolom, dan angka pada GitHub.')
    st.code(str(exc))
    st.stop()
years = sorted(set(ig['Tahun']).union(set(tt['Tahun'])), reverse=True)
year = st.sidebar.selectbox('Tahun', years)
ig_year = ig[ig['Tahun'] == year].copy()
tt_year = tt[tt['Tahun'] == year].copy()

if page == '📸 Performa Instagram':
    platform_page('Instagram', ig_year)
elif page == '🎵 Performa TikTok':
    platform_page('TikTok', tt_year)
else:
    st.title('🏠 Ringkasan Performa Media Sosial')
    st.caption(f'Bengkel Mahaputra · Tahun {year} · Instagram vs TikTok')
    a, b = st.columns(2)
    with a:
        st.subheader('📸 Instagram')
        st.metric('Total Tayangan', fmt(ig_year['Tayangan'].sum()))
        st.metric('Net Follower', fmt(ig_year['Net Follower'].sum()))
    with b:
        st.subheader('🎵 TikTok')
        st.metric('Total Tayangan', fmt(tt_year['Tayangan'].sum()))
        st.metric('Net Follower', fmt(tt_year['Net Follower'].sum()))
    st.divider()
    st.subheader('🎯 KPI Tahunan')
    st.caption('Dihitung dari total data yang tersedia pada tahun terpilih. Jika belum 12 bulan, status bersifat sementara.')
    for metric, field in [('Followers','Net Follower'),('Viewers','Tayangan')]:
        c1,c2 = st.columns(2)
        with c1: kpi_card('TikTok','Tahunan',metric,int(tt_year[field].sum()))
        with c2: kpi_card('Instagram','Tahunan',metric,int(ig_year[field].sum()))
    st.divider()
    st.subheader('🎯 KPI Bulanan')
    common_months = sorted(set(ig_year['Nomor Bulan']).union(set(tt_year['Nomor Bulan'])))
    if common_months:
        selected_num = st.selectbox('Pilih bulan untuk evaluasi KPI', common_months, format_func=lambda n: next(k.capitalize() for k,v in MONTHS.items() if v == n))
        for metric, field in [('Followers','Net Follower'),('Viewers','Tayangan')]:
            c1,c2 = st.columns(2)
            for c, platform, data in [(c1,'TikTok',tt_year),(c2,'Instagram',ig_year)]:
                row = data[data['Nomor Bulan'] == selected_num]
                with c:
                    if row.empty: st.info(f'{platform}: data bulan ini belum tersedia.')
                    else: kpi_card(platform,'Bulanan',metric,int(row[field].iloc[0]))
    else:
        st.info('Belum ada data pada tahun ini.')
    st.divider()
    st.subheader('📊 Perbandingan Performa Bulanan')
    comparison = pd.DataFrame({'Nomor Bulan':range(1,13)})
    for platform, data in [('Instagram',ig_year),('TikTok',tt_year)]:
        part = data[['Nomor Bulan','Tayangan','Net Follower']].rename(columns={'Tayangan':f'Tayangan {platform}','Net Follower':f'Follower {platform}'})
        comparison = comparison.merge(part, on='Nomor Bulan', how='left')
    comparison = comparison[comparison[['Tayangan Instagram','Tayangan TikTok','Follower Instagram','Follower TikTok']].notna().any(axis=1)].copy()
    comparison['Bulan'] = comparison['Nomor Bulan'].map({v:k.capitalize() for k,v in MONTHS.items()})
    if not comparison.empty:
        for fields,title in [(['Tayangan Instagram','Tayangan TikTok'],'Perbandingan Tayangan'),(['Follower Instagram','Follower TikTok'],'Perbandingan Net Follower')]:
            st.subheader(title)
            long = comparison.melt(id_vars=['Bulan'],value_vars=fields,var_name='Platform',value_name='Jumlah').dropna()
            fig = px.bar(long,x='Bulan',y='Jumlah',color='Platform',barmode='group',text='Jumlah')
            fig.update_traces(texttemplate='%{text:,.0f}',textposition='outside',cliponaxis=False)
            fig.update_xaxes(categoryorder='array',categoryarray=comparison['Bulan'].tolist())
            st.plotly_chart(chart_style(fig),use_container_width=True)
        st.subheader('📋 Tabel Perbandingan')
        st.dataframe(comparison.drop(columns=['Nomor Bulan']).style.format(na_rep='—',precision=0,thousands='.'),hide_index=True,use_container_width=True)
    st.caption('Viewers menggunakan Tayangan sebagai indikator. Net Follower merupakan perubahan bersih, bukan total follower akun.')
st.divider()
st.caption('Dashboard Performa Media Sosial | Bengkel Mahaputra · Sumber: data.csv & tiktok.csv')
