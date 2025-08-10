
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Logo dan Header
st.title('Pemantauan Harga Pasar dan Kebutuhan Pokok')
st.subheader('Kabupaten Sanggau')

# Load data dari CSV
@st.cache_data
def load_data():
    df = pd.read_csv('data_harga_dummy.csv')
    return df
df = load_data()

# Filter interaktif
colTahun, colPeriode, colBarang, colKec = st.columns(4)
with colTahun:
    tahun = st.selectbox('Tahun', sorted(df['Tahun'].unique(), reverse=True))
with colPeriode:
    periode = st.selectbox('Periode', sorted(df[df['Tahun']==tahun]['Periode'].unique()))
with colBarang:
    barang = st.selectbox('Nama Barang', sorted(df['Nama Barang'].unique()))
with colKec:
    kecamatan = st.selectbox('Kecamatan', ['Semua'] + sorted(df['Kecamatan'].unique()))

df_filtered = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
if barang:
    df_filtered = df_filtered[df_filtered['Nama Barang']==barang]
if kecamatan != 'Semua':
    df_filtered = df_filtered[df_filtered['Kecamatan']==kecamatan]

# Tabel Harga
st.markdown('### Tabel Harga')
st.dataframe(df_filtered, use_container_width=True)


# Interaktif: Pilih beberapa komoditas untuk visualisasi
komoditas_multi = st.multiselect('Pilih Komoditas untuk Visualisasi:', sorted(df['Nama Barang'].unique()), default=[barang])

# Bar Chart Harga Tertinggi per Komoditas (Interaktif)
st.markdown('### Bar Chart Harga Tertinggi per Komoditas (Interaktif)')
df_bar = df[(df['Tahun']==tahun) & (df['Periode']==periode) & (df['Nama Barang'].isin(komoditas_multi))]
if not df_bar.empty:
    bar_data = df_bar.groupby('Nama Barang')['Tertinggi'].max().reset_index()
    fig = px.bar(bar_data, x='Tertinggi', y='Nama Barang', orientation='h',
                labels={'Tertinggi':'Harga Tertinggi (Rp)', 'Nama Barang':'Komoditas'},
                hover_data={'Tertinggi':':,.0f'}, text='Tertinggi', height=max(400, 40*len(bar_data)))
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Tidak ada data untuk bar chart.')

# Spacer agar heatmap tidak terhimpit
st.markdown('---')

# Heatmap Harga per Kecamatan (Multi Komoditas, Interaktif)
st.markdown('### Heatmap Harga per Kecamatan (Multi Komoditas, Interaktif)')
komoditas_heatmap_multi = st.multiselect('Pilih Komoditas untuk Heatmap:', sorted(df['Nama Barang'].unique()), default=[barang], key='heatmap_multi')
df_heat = df[(df['Tahun']==tahun) & (df['Periode']==periode) & (df['Nama Barang'].isin(komoditas_heatmap_multi))]
if not df_heat.empty:
    heat_data = df_heat.pivot(index='Nama Barang', columns='Kecamatan', values='Harga')
    fig2 = px.imshow(heat_data, text_auto=True, aspect='auto', color_continuous_scale='YlOrRd',
                    labels=dict(color='Harga (Rp)'),
                    title='Harga per Kecamatan')
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info('Tidak ada data untuk heatmap.')

# Tabel Harga
st.markdown('### Tabel Harga Tertinggi & Terendah')
st.dataframe(df, use_container_width=True)


# Responsive Layout: Bar Chart & Heatmap
col1, col2 = st.columns(2)
with col1:
    st.markdown('### Visualisasi Harga Tertinggi per Komoditas (Tahun & Periode)')
    df_top = df[(df['Tahun']==tahun) & (df['Periode']==periode)]
    top_komoditas = df_top.groupby('Nama Barang')['Tertinggi'].max().sort_values(ascending=False).head(10)
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
    top10 = df[(df['Tahun']==tahun) & (df['Periode']==periode)].groupby('Nama Barang')['Tertinggi'].max().sort_values(ascending=False).head(10)
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
