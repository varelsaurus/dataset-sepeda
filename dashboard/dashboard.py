import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# Load data
df = pd.read_csv("day.csv")
df['dteday'] = pd.to_datetime(df['dteday'])
df['season_label'] = df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
min_date = df["dteday"].min()
max_date = df["dteday"].max()

with st.sidebar:
    st.header("Filter Rentang Waktu")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    selected_seasons = st.multiselect(
        "Pilih Musim",
        options=df['season_label'].unique(),
        default=df['season_label'].unique()
    )
    
    temp_min, temp_max = st.slider(
        "Rentang Suhu (Normalized)",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0)
    )

filtered_df = df[
    (df['dteday'] >= pd.to_datetime(start_date)) &
    (df['dteday'] <= pd.to_datetime(end_date)) &
    (df['season_label'].isin(selected_seasons)) &
    (df['temp'] >= temp_min) &
    (df['temp'] <= temp_max)
]

filtered_df['month'] = filtered_df['dteday'].dt.month

# Kelompokkan berdasarkan bulan
month_counts = filtered_df.groupby('month')['cnt'].sum()

# Mapping warna berdasarkan season_label yang difilter
season_colors = {
    'Spring': '#FF9999',
    'Summer': '#99FF99',
    'Fall': '#FFFF99',
    'Winter': '#99CCFF'
}

if len(selected_seasons) == 1:
    dominant_season = selected_seasons[0]
    month_colors = {month: season_colors[dominant_season] for month in range(1, 13)}
else:
    month_colors = {month: season_colors.get(filtered_df[filtered_df['month'] == month]['season_label'].iloc[0] 
                                           if not filtered_df[filtered_df['month'] == month].empty 
                                           else 'Spring', 'Spring') 
                    for month in range(1, 13)}

st.title("Dashboard Analisis Penyewaan Sepeda")
st.subheader("✏️ Ringkasan Pengguna Sepeda")
col1, col2 = st.columns([1, 0.5])

with col1:
    st.metric("Jumlah Penyewa Sepeda", f"{df['cnt'].sum():,}")
    st.metric("Rata - rata Penyewa Perhari", f"{df['cnt'].mean():,.2f}")

with col2:
    st.metric("Penyewa Terbanyak Perhari", f"{df['cnt'].max():,}")
    st.metric("Penyewa Terdikit Perhari", f"{df['cnt'].min():,}")

st.subheader("🍁 Pola Penyewaan Berdasarkan Musim")
season_group = filtered_df.groupby('season_label')['cnt'].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x='season_label', y='cnt', data=season_group, palette='Blues_d', ax=ax1)
ax1.set_xlabel('Musim')
ax1.set_ylabel('Total Penyewaan')
ax1.set_title('Total Penyewaan Sepeda per Musim')

for i, v in enumerate(season_group['cnt']):
    ax1.text(i, v + 100, f'{v:,.0f}', ha='center', va='bottom')  

st.pyplot(fig1)

# Visualisasi 2: Korelasi antara Suhu dan Jumlah Penyewaan
st.subheader("🌡️ Korelasi antara Suhu dan Jumlah Penyewaan")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.scatterplot(x='temp', y='cnt', data=filtered_df, color='#72BCD4', ax=ax2)
ax2.set_xlabel('Normalized Temperature (temp)')
ax2.set_ylabel('Total Penyewaan (cnt)')
ax2.set_title('Scatter Plot: Suhu vs Penyewaan Sepeda')
ax2.grid(True)
st.pyplot(fig2)

correlation = filtered_df['temp'].corr(filtered_df['cnt'])
st.markdown(f"**Korelasi Pearson**: {correlation:.2f} (Positif, penyewaan meningkat seiring suhu naik).")
