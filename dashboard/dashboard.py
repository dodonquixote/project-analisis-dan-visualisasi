import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # Library visualisasi interaktif

# ================= KONFIGURASI HALAMAN =================
# Mengatur judul halaman dan layout agar tampilan visualisasi menjadi lebar (wide)
st.set_page_config(page_title="E-commerce Analysis Dashboard", layout="wide")
st.title("Analisis Data E-commerce")

# ================= PEMUATAN DATA =================
# Fungsi load_data() bertugas membaca file CSV dari folder 'data' dan mengembalikan tiga dataset.
# @st.cache_data digunakan untuk menyimpan cache data agar tidak perlu membaca ulang file setiap kali terjadi interaksi.
@st.cache_data
def load_data():
    customers = pd.read_csv("data/customers_dataset.csv")
    geolocation = pd.read_csv("data/geolocation_dataset.csv")
    products = pd.read_csv("data/products_dataset.csv")
    return customers, geolocation, products

# Memanggil fungsi untuk memuat data dan menyimpannya ke dalam variabel
customers, geolocation, products = load_data()

# ================= PENGATURAN INTERAKTIF DI SIDEBAR =================
# Sidebar akan menyediakan kontrol utama dan kontrol lanjutan untuk menentukan jenis analisis yang ingin dilakukan.
st.sidebar.header("Pengaturan Analisis")
analysis_type = st.sidebar.selectbox(
    "Pilih Jenis Analisis",
    ["Distribusi Pelanggan", "Karakteristik Produk"]
)

# Panel kontrol tambahan dengan opsi berbeda sesuai dengan jenis analisis yang dipilih
with st.sidebar.expander("⚙️ Pengaturan Lanjutan"):
    # Inisialisasi variabel show_raw_data agar selalu terdefinisi (default False)
    show_raw_data = False  
    if analysis_type == "Distribusi Pelanggan":
        # Checkbox untuk menampilkan data mentah pada bagian Distribusi Pelanggan
        show_raw_data = st.checkbox("Tampilkan Data Mentah", value=True)
        # Slider untuk mengatur ukuran cluster pada peta (digunakan untuk mengatur radius pada heatmap)
        cluster_size = st.slider("Ukuran Cluster Peta", 100, 1000, 500)
    elif analysis_type == "Karakteristik Produk":
        # Radio button untuk memilih jenis metrik analisis pada produk
        metric_choice = st.radio(
            "Metrik Analisis",
            ["Berat", "Dimensi", "Korelasi"]
        )
        # Checkbox untuk menentukan apakah akan menampilkan outlier pada histogram
        show_outliers = st.checkbox("Tampilkan Outlier")

# Menambahkan pertanyaan bisnis dan informasi tambahan pada sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Pertanyaan Bisnis")
st.sidebar.write("1. Bagaimana pengaruh lokasi pelanggan terhadap preferensi belanja mereka?")
st.sidebar.write("2. Bagaimana distribusi berat dan dimensi mempengaruhi preferensi pelanggan?")
st.sidebar.markdown("---")
st.sidebar.info(
    "Dashboard ini menampilkan analisis data e-commerce Brazil mencakup:\n"
    "- Distribusi geografis pelanggan\n"
    "- Karakteristik produk\n"
    "- Data mentah terkait"
)

# ================= ANALISIS BERDASARKAN JENIS =================
if analysis_type == "Distribusi Pelanggan":
    # ---------------- ANALISIS DISTRIBUSI PELANGGAN ----------------
    
    # 1. Interactive City Selector
    # Widget multiselect memungkinkan pengguna memilih kota-kota yang ingin difilter.
    selected_cities = st.multiselect(
        "Pilih Kota untuk Filter",
        options=customers['customer_city'].unique(),
        default=["sao paulo", "rio de janeiro"],
        format_func=lambda x: x.title()  # Format agar tampilan nama kota menjadi capitalized
    )
    
    # 2. Dynamic Filtering
    # Filter data pelanggan berdasarkan kota yang dipilih oleh pengguna.
    if selected_cities:
        filtered_data = customers[customers['customer_city'].isin(selected_cities)]
    else:
        filtered_data = customers.copy()
    
    # 3. Tampilkan Statistik Real-time
    # Menampilkan metrik kunci seperti total pelanggan, jumlah kota unik, dan negara bagian unik.
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pelanggan", filtered_data.shape[0])
    with col2:
        st.metric("Kota Unik", filtered_data['customer_city'].nunique())
    with col3:
        st.metric("Negara Bagian", filtered_data['customer_state'].nunique())
    
    # 4. Peta Interaktif
    # Menampilkan peta interaktif menggunakan data geolokasi. Pilihan antara heatmap dan point map diberikan kepada pengguna.
    st.subheader("Peta Interaktif Pelanggan")
    # Untuk performa, ambil sample 1000 data geolokasi dan ubah nama kolom lat/lon agar sesuai dengan Plotly.
    map_data = geolocation.sample(1000).rename(columns={
        'geolocation_lat': 'lat', 
        'geolocation_lng': 'lon'
    })
    
    # Pilihan tipe peta melalui radio button
    layer_choice = st.radio("Tipe Peta", ["Heatmap", "Point Map"], horizontal=True)
    if layer_choice == "Heatmap":
        # Plot density map dengan radius disesuaikan dari nilai cluster_size (dibagi 100 untuk skala yang sesuai)
        fig = px.density_mapbox(
            map_data,
            lat='lat',
            lon='lon',
            radius=cluster_size / 100,
            zoom=3,
            height=500
        )
    else:
        # Plot scatter map untuk menampilkan titik individu dengan informasi nama kota sebagai hover text.
        fig = px.scatter_mapbox(
            map_data,
            lat='lat',
            lon='lon', 
            hover_name='geolocation_city',
            zoom=3,
            height=500
        )
    # Menggunakan style open-street-map untuk tampilan peta
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Drill-down Analysis: Detail Berdasarkan Negara Bagian
    # Menggunakan expander untuk memberikan opsi analisis lebih mendalam berdasarkan negara bagian.
    with st.expander("🔍 Analisis Detail Negara Bagian"):
        selected_state = st.selectbox(
            "Pilih Negara Bagian",
            sorted(filtered_data['customer_state'].unique())
        )
        # Filter data pelanggan berdasarkan negara bagian yang dipilih
        state_data = filtered_data[filtered_data['customer_state'] == selected_state]
        
        # Menampilkan dua tab: Distribusi Kota dan Trend Temporal
        tab1, tab2 = st.tabs(["Distribusi Kota", "Trend Temporal"])
        with tab1:
            # Membuat bar chart untuk 10 kota teratas di negara bagian yang dipilih
            city_dist = state_data['customer_city'].value_counts().nlargest(10)
            fig = px.bar(
                city_dist,
                orientation='h', 
                labels={'value': 'Jumlah Pelanggan', 'index': 'Kota'},
                title=f'Top 10 Kota di {selected_state}'
            )
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            # Trend Temporal: Jika terdapat kolom tanggal (misalnya order_purchase_timestamp), tampilkan tren bulanan order.
            if 'order_purchase_timestamp' in state_data.columns:
                # Ubah kolom tanggal menjadi datetime
                state_data['order_purchase_timestamp'] = pd.to_datetime(state_data['order_purchase_timestamp'])
                # Resample data per bulan dan hitung jumlah order
                ts_data = state_data.set_index('order_purchase_timestamp').resample('M').size()
                fig = px.line(ts_data, labels={'value': 'Jumlah Order'}, title='Trend Bulanan Order')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Data tanggal tidak tersedia")
    
    # 6. Menampilkan Data Mentah (jika opsi diaktifkan)
    if show_raw_data:
        st.subheader("Data Mentah")
        st.data_editor(
            filtered_data,
            column_config={
                "customer_id": "ID Pelanggan",
                "customer_city": st.column_config.TextColumn("Kota", help="Kota tempat pelanggan berada")
            },
            hide_index=True,
            use_container_width=True
        )
        
elif analysis_type == "Karakteristik Produk":
    # ---------------- ANALISIS KARAKTERISTIK PRODUK ----------------
    st.header("Analisis Karakteristik Produk")
    
    # Berdasarkan pilihan metrik (Berat, Dimensi, Korelasi) yang dipilih di sidebar, tampilkan analisis yang sesuai.
    if metric_choice == "Berat":
        # ANALISIS BERAT PRODUK
        st.subheader("Distribusi Berat Produk")
        # Slider untuk memilih jumlah bins pada histogram distribusi berat
        bin_size = st.slider("Jumlah Bins untuk Berat", 5, 100, 30)
        # Histogram distribusi berat produk menggunakan Plotly Express
        fig = px.histogram(
            products,
            x='product_weight_g',
            nbins=bin_size,
            title="Distribusi Berat Produk",
            color_discrete_sequence=['#3498db']
        )
        # Jika opsi outlier aktif, batasi sumbu x agar nilai ekstrem tidak mendominasi tampilan
        if show_outliers:
            fig.update_layout(xaxis_range=[0, products['product_weight_g'].quantile(0.95)])
        st.plotly_chart(fig, use_container_width=True)
    
    elif metric_choice == "Dimensi":
        # ANALISIS DIMENSI PRODUK
        st.subheader("Visualisasi 3D Dimensi Produk")
        # Membuat tiga kolom untuk memilih variabel yang ingin ditampilkan sebagai sumbu X, Y, dan Z
        col1, col2, col3 = st.columns(3)
        with col1:
            x_axis = st.selectbox("X Axis", options=['product_length_cm', 'product_height_cm', 'product_width_cm'], key="x_axis")
        with col2:
            y_axis = st.selectbox("Y Axis", options=['product_length_cm', 'product_height_cm', 'product_width_cm'], key="y_axis")
        with col3:
            z_axis = st.selectbox("Z Axis", options=['product_length_cm', 'product_height_cm', 'product_width_cm'], key="z_axis")
        # Scatter plot 3D untuk melihat distribusi dimensi produk dengan warna berdasarkan berat
        fig = px.scatter_3d(
            products,
            x=x_axis,
            y=y_axis,
            z=z_axis,
            color='product_weight_g',
            hover_name='product_category_name',
            height=800
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif metric_choice == "Korelasi":
        # ANALISIS KORELASI PRODUK
        st.subheader("Analisis Korelasi Interaktif")
        # Multi-select untuk memilih variabel apa saja yang ingin dibandingkan korelasinya
        corr_vars = st.multiselect(
            "Pilih Variabel untuk Korelasi",
            options=['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
            default=['product_weight_g', 'product_length_cm']
        )
        if len(corr_vars) > 1:
            # Scatter matrix untuk melihat hubungan antar variabel terpilih
            fig = px.scatter_matrix(
                products,
                dimensions=corr_vars,
                color_discrete_sequence=['#2ecc71']
            )
            st.plotly_chart(fig, use_container_width=True)
