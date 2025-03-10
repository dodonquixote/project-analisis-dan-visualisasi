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
    orders = pd.read_csv("data/orders_dataset.csv")
    order_items = pd.read_csv("data/order_items_dataset.csv")
    return customers, geolocation, products, orders, order_items

# Memuat data dan merge dataset
customers, geolocation, products, orders, order_items = load_data()
merged_data = order_items.merge(orders, on='order_id').merge(customers, on='customer_id').merge(products, on='product_id')

# Sidebar untuk kontrol
st.sidebar.header("Pengaturan Analisis")
analysis_type = st.sidebar.selectbox(
    "Pilih Jenis Analisis",
    [
        "Distribusi Pelanggan", 
        "Karakteristik Produk",
        "Pengaruh Lokasi pada Preferensi",
        "Pengaruh Berat & Dimensi"
    ]
)

# Tab untuk analisis
tab1, tab2 = st.tabs(["📊 Visualisasi", "📈 Data Mentah"])

with tab1:
    if analysis_type == "Distribusi Pelanggan":
        # Kode sebelumnya tetap sama...
        
    elif analysis_type == "Karakteristik Produk":
        # Kode sebelumnya tetap sama...

    elif analysis_type == "Pengaruh Lokasi pada Preferensi":
        st.header("Analisis Pengaruh Lokasi pada Preferensi Belanja")
        
        # Analisis preferensi kategori produk berdasarkan kota
        st.subheader("Preferensi Kategori Produk per Kota")
        city_preference = merged_data.groupby(['customer_city','product_category_name']).size().nlargest(10).reset_index(name='count')
        
        plt.figure(figsize=(12,6))
        sns.barplot(x='count', y='customer_city', hue='product_category_name', data=city_preference, dodge=False)
        plt.title('10 Kategori Produk Paling Populer per Kota')
        st.pyplot(plt)
        
        # Analisis pola pembelian berdasarkan wilayah geografis
        st.subheader("Pola Pembelian Berdasarkan Koordinat Geografis")
        geo_data = merged_data[['geolocation_lat','geolocation_lng','payment_value']].dropna()
        plt.figure(figsize=(10,6))
        sns.scatterplot(x='geolocation_lng', y='geolocation_lat', size='payment_value', 
                        data=geo_data.sample(1000), alpha=0.5)
        plt.title('Distribusi Nilai Pembelian Berdasarkan Lokasi')
        st.pyplot(plt)

    elif analysis_type == "Pengaruh Berat & Dimensi":
        st.header("Analisis Pengaruh Berat & Dimensi Produk")
        
        # Hubungan antara berat produk dengan frekuensi pembelian
        st.subheader("Korelasi Berat Produk vs Frekuensi Pembelian")
        weight_freq = merged_data.groupby('product_weight_g').size().reset_index(name='purchase_count')
        
        plt.figure(figsize=(10,6))
        sns.regplot(x='product_weight_g', y='purchase_count', data=weight_freq)
        plt.title('Hubungan Berat Produk dan Frekuensi Pembelian')
        st.pyplot(plt)
        
        # Analisis 3D dimensi produk
        st.subheader("Distribusi 3D Dimensi Produk Terpopuler")
        dimensions = merged_data[['product_length_cm','product_height_cm','product_width_cm']]
        dimensions = dimensions[(dimensions < dimensions.quantile(0.95)).all(axis=1)]
        
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(dimensions['product_length_cm'], 
                   dimensions['product_height_cm'], 
                   dimensions['product_width_cm'])
        ax.set_xlabel('Panjang (cm)')
        ax.set_ylabel('Tinggi (cm)')
        ax.set_zlabel('Lebar (cm)')
        st.pyplot(fig)

with tab2:
    # Kode sebelumnya tetap sama...
    if analysis_type == "Pengaruh Lokasi pada Preferensi":
        st.subheader("Data Transaksi Terkait Lokasi")
        st.write(merged_data[['customer_city','product_category_name','payment_value']].head())
    
    elif analysis_type == "Pengaruh Berat & Dimensi":
        st.subheader("Data Produk dengan Dimensi")
        st.write(products[['product_weight_g','product_length_cm',
                          'product_height_cm','product_width_cm']].head())

# Update penjelasan sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "Pertanyaan Bisnis yang Dijawab:\n"
    "1. Pengaruh lokasi geografis terhadap preferensi produk\n"
    "2. Hubungan karakteristik fisik produk dengan pola pembelian\n"
    "\nDataset yang digunakan termasuk data transaksi, produk, dan lokasi pelanggan"
)
