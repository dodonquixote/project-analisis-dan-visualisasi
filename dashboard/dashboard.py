import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Sidebar untuk kontrol
st.sidebar.header("Pengaturan Analisis")
analysis_type = st.sidebar.selectbox(
    "Pilih Jenis Analisis",
    ["Distribusi Pelanggan", "Karakteristik Produk"]
)

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

# Menambahkan fitur interaktif untuk masing-masing analisis
if analysis_type == "Distribusi Pelanggan":
    # Filter interaktif: Pilih kota yang ingin ditampilkan
    city_options = customers['customer_city'].unique()
    selected_cities = st.sidebar.multiselect("Pilih Kota", options=city_options, default=city_options[:5])
    filtered_customers = customers[customers['customer_city'].isin(selected_cities)]
elif analysis_type == "Karakteristik Produk":
    # Filter interaktif: Slider untuk rentang berat produk
    min_weight = int(products['product_weight_g'].min())
    max_weight = int(products['product_weight_g'].max())
    weight_range = st.sidebar.slider("Filter Berat Produk (gram)", min_value=min_weight, max_value=max_weight, value=(min_weight, max_weight))
    filtered_products = products[(products['product_weight_g'] >= weight_range[0]) & (products['product_weight_g'] <= weight_range[1])]

# Tab untuk analisis
tab1, tab2 = st.tabs(["📊 Visualisasi", "📈 Data Mentah"])

with tab1:
    if analysis_type == "Distribusi Pelanggan":
        st.header("Analisis Distribusi Pelanggan")
        # Top 10 Kota dari data yang sudah difilter
        plt.figure(figsize=(10, 6))
        top_cities = filtered_customers['customer_city'].value_counts().head(10)
        sns.barplot(x=top_cities.values, y=top_cities.index, palette="viridis")
        plt.title('Top 10 Kota dengan Jumlah Pelanggan Terbanyak')
        plt.xlabel('Jumlah Pelanggan')
        plt.ylabel('Kota')
        st.pyplot(plt)
        
        # Peta Geolokasi (menggunakan sampel data untuk performa)
        st.subheader("Distribusi Geografis Pelanggan")
        # Pastikan kolom geolocation memiliki nama latitude dan longitude yang sesuai
        st.map(geolocation.sample(1000).rename(columns={
            'geolocation_lat': 'latitude', 
            'geolocation_lng': 'longitude'
        }))

    elif analysis_type == "Karakteristik Produk":
        st.header("Analisis Karakteristik Produk")
        
        # Distribusi Berat Produk dari data yang sudah difilter
        plt.figure(figsize=(10, 6))
        sns.histplot(filtered_products['product_weight_g'].dropna(), bins=30, kde=True)
        plt.title('Distribusi Berat Produk (gram)')
        plt.xlabel('Berat (gram)')
        plt.ylabel('Frekuensi')
        st.pyplot(plt)

        # Distribusi Dimensi Produk
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        sns.histplot(filtered_products['product_length_cm'].dropna(), bins=30, ax=axes[0, 0], kde=True)
        sns.histplot(filtered_products['product_height_cm'].dropna(), bins=30, ax=axes[0, 1], kde=True)
        sns.histplot(filtered_products['product_width_cm'].dropna(), bins=30, ax=axes[1, 0], kde=True)
        
        axes[0, 0].set_title('Panjang Produk (cm)')
        axes[0, 1].set_title('Tinggi Produk (cm)')
        axes[1, 0].set_title('Lebar Produk (cm)')
        plt.tight_layout()
        st.pyplot(fig)

with tab2:
    if analysis_type == "Distribusi Pelanggan":
        st.subheader("Data Pelanggan (Tampilan Terfilter)")
        st.write(filtered_customers.head())
        
        st.subheader("Data Geolokasi")
        st.write(geolocation.head())
    
    elif analysis_type == "Karakteristik Produk":
        st.subheader("Data Produk (Tampilan Terfilter)")
        st.write(filtered_products.head())
