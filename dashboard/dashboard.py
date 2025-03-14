import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # Tambahkan library visualisasi interaktif

# Set judul halaman
st.set_page_config(page_title="E-commerce Analysis Dashboard", layout="wide")
st.title("Analisis Data E-commerce")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    customers = pd.read_csv("data/customers_dataset.csv")
    geolocation = pd.read_csv("data/geolocation_dataset.csv")
    products = pd.read_csv("data/products_dataset.csv")
    return customers, geolocation, products

# Memuat data
customers, geolocation, products = load_data()

# ================= FITUR INTERAKTIF BARU =================
# Sidebar untuk kontrol utama
st.sidebar.header("Pengaturan Analisis")
analysis_type = st.sidebar.selectbox(
    "Pilih Jenis Analisis",
    ["Distribusi Pelanggan", "Karakteristik Produk"]
)

# Panel kontrol tambahan
with st.sidebar.expander("⚙️ Pengaturan Lanjutan"):
    # Inisialisasi variabel show_raw_data agar selalu terdefinisi
    show_raw_data = False  
    if analysis_type == "Distribusi Pelanggan":
        show_raw_data = st.checkbox("Tampilkan Data Mentah", value=True)
        cluster_size = st.slider("Ukuran Cluster Peta", 100, 1000, 500)
    elif analysis_type == "Karakteristik Produk":
        metric_choice = st.radio(
            "Metrik Analisis",
            ["Berat", "Dimensi", "Korelasi"]
        )
        show_outliers = st.checkbox("Tampilkan Outlier")

# Menambahkan Pertanyaan Bisnis di sidebar
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

# Konten utama berdasarkan jenis analisis
if analysis_type == "Distribusi Pelanggan":
    # 1. Interactive City Selector dengan Search
    selected_cities = st.multiselect(
        "Pilih Kota untuk Filter",
        options=customers['customer_city'].unique(),
        default=["sao paulo", "rio de janeiro"],
        format_func=lambda x: x.title()
    )
    
    # 2. Dynamic Filtering
    if selected_cities:
        filtered_data = customers[customers['customer_city'].isin(selected_cities)]
    else:
        filtered_data = customers.copy()
    
    # 3. Tampilkan Statistik Real-time
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pelanggan", filtered_data.shape[0])
    with col2:
        st.metric("Kota Unik", filtered_data['customer_city'].nunique())
    with col3:
        st.metric("Negara Bagian", filtered_data['customer_state'].nunique())
    
    # 4. Interactive Map dengan Layer Control
    st.subheader("Peta Interaktif Pelanggan")
    map_data = geolocation.sample(1000).rename(columns={
        'geolocation_lat': 'lat', 
        'geolocation_lng': 'lon'
    })
    
    # Layer kontrol interaktif
    layer_choice = st.radio(
        "Tipe Peta",
        ["Heatmap", "Point Map"],
        horizontal=True
    )
    
    if layer_choice == "Heatmap":
        fig = px.density_mapbox(map_data, lat='lat', lon='lon', radius=10,
                                zoom=3, height=500)
    else:
        fig = px.scatter_mapbox(map_data, lat='lat', lon='lon', 
                                hover_name='geolocation_city',
                                zoom=3, height=500)
    
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Drill-down Analysis
    with st.expander("🔍 Analisis Detail Negara Bagian"):
        selected_state = st.selectbox(
            "Pilih Negara Bagian",
            sorted(filtered_data['customer_state'].unique())
        )
        state_data = filtered_data[filtered_data['customer_state'] == selected_state]
        
        # Tampilkan data dalam tabs
        tab1, tab2 = st.tabs(["Distribusi Kota", "Trend Temporal"])
        
        with tab1:
            city_dist = state_data['customer_city'].value_counts().nlargest(10)
            fig = px.bar(city_dist, orientation='h', 
                         labels={'value':'Jumlah Pelanggan','index':'Kota'},
                         title=f'Top 10 Kota di {selected_state}')
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Asumsi ada kolom tanggal (contoh implementasi)
            try:
                fig = px.line(state_data.set_index('order_purchase_timestamp').resample('M').size(),
                              labels={'value':'Jumlah Order'},
                              title='Trend Bulanan Order')
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning("Data tanggal tidak tersedia")
                
elif analysis_type == "Karakteristik Produk":
    st.header("Analisis Karakteristik Produk")
    
    # 1. Interactive Correlation Explorer
    st.subheader("Analisis Korelasi Interaktif")
    corr_vars = st.multiselect(
        "Pilih Variabel untuk Korelasi",
        options=['product_weight_g', 'product_length_cm',
                 'product_height_cm', 'product_width_cm'],
        default=['product_weight_g', 'product_length_cm']
    )
    
    if len(corr_vars) > 1:
        fig = px.scatter_matrix(
            products,
            dimensions=corr_vars,
            color_discrete_sequence=['#2ecc71']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 2. Dynamic Histogram
    st.subheader("Distribusi Dinamis")
    dist_var = st.selectbox(
        "Pilih Variabel untuk Distribusi",
        options=['product_weight_g', 'product_length_cm',
                 'product_height_cm', 'product_width_cm']
    )
    
    bin_size = st.slider("Jumlah Bins", 5, 100, 30)
    fig = px.histogram(products, x=dist_var, nbins=bin_size,
                       title=f'Distribusi {dist_var}',
                       color_discrete_sequence=['#3498db'])
    if show_outliers:
        fig.update_layout(xaxis_range=[0, products[dist_var].quantile(0.95)])
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. 3D Scatter Plot Interaktif
    st.subheader("Visualisasi 3D Dimensi Produk")
    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("X Axis", options=['product_length_cm', 'product_height_cm', 'product_width_cm'])
    with col2:
        y_axis = st.selectbox("Y Axis", options=['product_height_cm', 'product_width_cm', 'product_length_cm'])
    with col3:
        z_axis = st.selectbox("Z Axis", options=['product_width_cm', 'product_length_cm', 'product_height_cm'])
    
    fig = px.scatter_3d(products, x=x_axis, y=y_axis, z=z_axis,
                          color='product_weight_g',
                          hover_name='product_category_name',
                          height=800)
    st.plotly_chart(fig, use_container_width=True)

# Tampilkan data mentah dengan filter (hanya untuk Distribusi Pelanggan)
if analysis_type == "Distribusi Pelanggan" and show_raw_data:
    st.subheader("Data Mentah")
    st.data_editor(
        filtered_data,
        column_config={
            "customer_id": "ID Pelanggan",
            "customer_city": st.column_config.TextColumn(
                "Kota",
                help="Kota tempat pelanggan berada"
            )
        },
        hide_index=True,
        use_container_width=True
    )
