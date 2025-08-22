
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Tombol reload data
st.markdown('## e-Pasar Kabupaten Sanggau')
reload = st.button('🔄 Reload Data dari Spreadsheet')
if reload:
    st.cache_data.clear()
    st.experimental_rerun()

# Logo dan Header
st.title('Pemantauan Harga Pasar dan Kebutuhan Pokok')
st.subheader('Kabupaten Sanggau')

@st.cache_data
def load_data():
    csv_export_url = "https://docs.google.com/spreadsheets/d/1mDvUZ2TMZHqAtXaWrgbLD5SOPv0cAcMrghGvXa1pC-c/export?format=csv&gid=0"
    df = pd.read_csv(csv_export_url)
    # Bersihkan header kolom dari spasi/karakter aneh
    df.columns = df.columns.str.strip().str.replace('\u200b', '').str.replace(' +', ' ', regex=True)
    df['Harga'] = pd.to_numeric(df['Harga'], errors='coerce')
    return df
try:
    df = load_data()
except KeyError as e:
    st.error(f"Kolom tidak ditemukan di data: {e}.\nCek header file CSV Anda.")
    st.stop()

    

    reload = st.button('🔄 Reload Data dari Spreadsheet')
# Filter interaktif
colTahun, colPeriode, colKategori, colBarang, colKec = st.columns(5)
with colTahun:
    tahun = st.selectbox('Tahun', sorted(df['Tahun'].unique(), reverse=True))
with colPeriode:
    periode = st.selectbox('Periode', sorted(df[df['Tahun']==tahun]['Periode'].unique()))
with colKategori:
    kategori = st.selectbox('Kategori Barang', ['Semua'] + sorted(df['Kategori Barang'].dropna().unique()))
with colBarang:
    if kategori != 'Semua':
        barang_opsi = sorted(df[df['Kategori Barang']==kategori]['Nama Barang'].unique())
    else:
        barang_opsi = sorted(df['Nama Barang'].unique())
    barang = st.selectbox('Nama Barang', barang_opsi)
with colKec:
    kecamatan = st.selectbox('Kecamatan', ['Semua'] + sorted(df['Kecamatan'].unique()))


# Filter untuk tabel detail (semua filter)
df_filtered = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
if kategori != 'Semua':
    df_filtered = df_filtered[df_filtered['Kategori Barang']==kategori]
if barang:
    df_filtered = df_filtered[df_filtered['Nama Barang']==barang]
if kecamatan != 'Semua':
    df_filtered = df_filtered[df_filtered['Kecamatan']==kecamatan]

# Filter untuk visualisasi agregat (tahun, periode, kategori)
df_viz = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
if kategori != 'Semua':
    df_viz = df_viz[df_viz['Kategori Barang']==kategori]


# Tabel Harga
st.markdown('### Tabel Harga')
st.dataframe(df_filtered, use_container_width=True)

# Bar Chart Harga per Komoditas
st.markdown('### Bar Chart Harga per Komoditas')
df_bar = df_viz.groupby('Nama Barang')['Harga'].mean().reset_index()
fig = px.bar(df_bar, x='Harga', y='Nama Barang', orientation='h',
            labels={'Harga':'Harga (Rp)', 'Nama Barang':'Komoditas'},
            hover_data={'Harga':':,.0f'}, text='Harga', height=max(400, 40*len(df_bar)))
fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig, use_container_width=True)

# Heatmap Harga per Komoditas dan Kecamatan
st.markdown('### Heatmap Harga per Komoditas dan Kecamatan')
heat_data = df_viz.pivot_table(index='Nama Barang', columns='Kecamatan', values='Harga', aggfunc='mean')
fig2 = px.imshow(heat_data, text_auto=True, aspect='auto', color_continuous_scale='YlOrRd',
                labels=dict(color='Harga (Rp)'),
                title='Harga per Komoditas dan Kecamatan')
st.plotly_chart(fig2, use_container_width=True)

# Pie Chart Distribusi Harga per Kategori
st.markdown('### Distribusi Rata-rata Harga per Kategori Barang')
df_pie = df[(df['Tahun']==tahun) & (df['Periode']==periode)].groupby('Kategori Barang')['Harga'].mean().reset_index()
fig3 = px.pie(df_pie, values='Harga', names='Kategori Barang', title='Distribusi Rata-rata Harga per Kategori Barang', hole=0.3)
st.plotly_chart(fig3, use_container_width=True)

# Tabel Harga
st.markdown('### Tabel Harga Tertinggi & Terendah')
st.dataframe(df, use_container_width=True)


# Responsive Layout: Bar Chart & Heatmap
col1, col2 = st.columns(2)
with col1:
    st.markdown('### Visualisasi Harga Tertinggi per Komoditas (Tahun & Periode)')
    df_top = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
    top_komoditas = df_top.groupby('Nama Barang')['Harga'].max().sort_values(ascending=False).head(10)
    # (sudah diganti Plotly, kode plt dihapus)

with col2:
    st.markdown('### Heatmap Harga per Kecamatan')
    komoditas_heatmap = st.selectbox('Pilih Komoditas untuk Heatmap:', sorted(df['Nama Barang'].unique()), key='heatmap_select')
    df_heat = df[(df['Tahun']==tahun) & (df['Periode']==periode) & (df['Nama Barang']==komoditas_heatmap)]
    heat_data = df_heat.pivot(index='Nama Barang', columns='Kecamatan', values='Harga')
    # (sudah diganti Plotly, kode plt/sns dihapus)

# Insight & Analisis
st.markdown('---')
st.markdown('## Insight & Analisis')

# Visualisasi Tambahan

# Responsive Layout: Pie Chart & Boxplot
col3, col4 = st.columns(2)
with col3:
    st.markdown('### Distribusi Harga Tertinggi 10 Komoditas')
    top10 = df[(df['Tahun']==tahun) & (df['Periode']==periode)].groupby('Nama Barang')['Harga'].max().sort_values(ascending=False).head(10)
    # (sudah diganti Plotly, kode plt dihapus)
with col4:
    st.markdown('### Sebaran Harga Tertinggi dan Terendah (Boxplot)')
    df_box = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
    # (sudah diganti Plotly, kode plt dihapus)

# Responsive Line Chart: Tren Harga Tahunan per Kecamatan (Plotly)
st.markdown('### Tren Harga Tahunan (Interaktif)')
komoditas_line = st.multiselect('Pilih Komoditas untuk Tren:', sorted(df['Nama Barang'].unique()), default=[barang], key='tren')
kec_line = st.multiselect('Pilih Kecamatan untuk Tren:', sorted(df['Kecamatan'].unique()), default=sorted(df['Kecamatan'].unique()))
df_tren = df[df['Nama Barang'].isin(komoditas_line) & df['Kecamatan'].isin(kec_line)]
if not df_tren.empty:
    fig5 = px.line(df_tren, x='Tahun', y='Harga', color='Nama Barang', line_dash='Kecamatan',
                  markers=True, hover_name='Kecamatan',
                  labels={'Harga':'Harga Rata-rata (Rp)', 'Tahun':'Tahun'},
                  title='Tren Harga Tahunan per Kecamatan')
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info('Tidak ada data untuk tren harga.')

# Insight dinamis
with st.expander('Lihat Insight Otomatis'):
    st.markdown('#### Insight Otomatis')
    if not df_filtered.empty:
        harga_max = df_filtered['Harga'].max()
        harga_min = df_filtered['Harga'].min()
        st.write(f"Harga tertinggi pada filter saat ini: Rp{harga_max:,.0f}")
        st.write(f"Harga terendah pada filter saat ini: Rp{harga_min:,.0f}")
        st.write(f"Rata-rata harga: Rp{df_filtered['Harga'].mean():,.0f}")
        st.write(f"Jumlah data: {len(df_filtered)}")
    else:
        st.info('Tidak ada data untuk insight.')

# st.markdown('''
# - **Komoditas dengan harga terendah:** Garam Halus (Bungkus) Rp.1.800.
# - **Komoditas dengan fluktuasi harga terbesar:** Cabe Keriting (Rp.150.000 - Rp.40.000), Daging Sapi (Rp.180.000 - Rp.88.000), Gas Elpiji (12 KG) (Rp.390.000 - Rp.130.000).
# - **Komoditas dengan harga stabil (selisih kecil):** Beras Medium Cap AAA, Beras Cap medium Lainnya, Gula Pasir.
# - **Beberapa kecamatan belum tersedia data harga (0), terutama pada komoditas tertentu.**
# - **Rekomendasi:**
#     - Perlu perhatian pada komoditas dengan fluktuasi tinggi seperti cabe dan daging.
#     - Pengumpulan data lebih lengkap di kecamatan yang masih kosong.
#     - Harga Gas Elpiji perlu dipantau karena selisih harga sangat besar antar kecamatan.
# ''')

# st.markdown('''
# **Dashboard ini dapat digunakan masyarakat dan pemangku kebijakan untuk memantau harga kebutuhan pokok, mengidentifikasi potensi gejolak harga, serta mengambil langkah antisipasi jika diperlukan.**
# ''')
