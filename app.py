import streamlit as st
import plotly_express as px
import pandas as pd
import numpy as np
import mysql.connector
import statistics
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from sklearn.cluster import KMeans

# koneksi ke database	194.233.77.193
db_app = mysql.connector.connect(host="194.233.77.193", user="udi93xus_root", passwd="_xRy3+zG@X8=", database="udi93xus_fishmap_v1_db")

# css to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """

# inject css with markdown
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

# dataset
dbcursor = db_app.cursor()
dbcursor.execute("SELECT * FROM dokumen_file WHERE deleted_at IS NULL AND doc_active = '1' ")
post_list = dbcursor.fetchall()

# read data
data_klorofil = pd.read_csv('http://ahmadfaisalsiregar.skom.id/' + post_list[0][6])
data_spl = pd.read_csv('http://ahmadfaisalsiregar.skom.id/' + post_list[1][6])
data_tpl = pd.read_csv('http://ahmadfaisalsiregar.skom.id/' + post_list[2][6])
data_arus = pd.read_csv('http://ahmadfaisalsiregar.skom.id/' + post_list[3][6])

# gabungkan dataset
gabungan_klorofil_tpl = data_klorofil.append(data_tpl, ignore_index=True)
gabungan_klorofil_tpl_spl = gabungan_klorofil_tpl.append(data_spl, ignore_index=True)
gabungan_klorofil_tpl_spl_arus = gabungan_klorofil_tpl_spl.append(data_arus, ignore_index=True)

"""### Data Perairan Teluk Tapian Nauli"""

# rata-rata (mean) dari tiap kolom yang memiliki missing value
mean1 = gabungan_klorofil_tpl_spl_arus["thetao [degrees_C]"].mean()
mean2 = gabungan_klorofil_tpl_spl_arus["chl [mg m-3]"].mean()
mean3 = gabungan_klorofil_tpl_spl_arus["zos [m]"].mean()
mean4 = gabungan_klorofil_tpl_spl_arus["uo [m s-1]"].mean()
mean5 = gabungan_klorofil_tpl_spl_arus["vo [m s-1]"].mean()
mean6 = gabungan_klorofil_tpl_spl_arus["depth [m]"].mean()

# me-replace/menimpa missing value (NaN) dengan nilai rata-rata (mean)
gabungan_klorofil_tpl_spl_arus["thetao [degrees_C]"] = gabungan_klorofil_tpl_spl_arus["thetao [degrees_C]"].replace(np.nan, mean1)
gabungan_klorofil_tpl_spl_arus["chl [mg m-3]"] = gabungan_klorofil_tpl_spl_arus["chl [mg m-3]"].replace(np.nan, mean2)
gabungan_klorofil_tpl_spl_arus["zos [m]"] = gabungan_klorofil_tpl_spl_arus["zos [m]"].replace(np.nan, mean3)
gabungan_klorofil_tpl_spl_arus["uo [m s-1]"] = gabungan_klorofil_tpl_spl_arus["uo [m s-1]"].replace(np.nan, mean4)
gabungan_klorofil_tpl_spl_arus["vo [m s-1]"] = gabungan_klorofil_tpl_spl_arus["vo [m s-1]"].replace(np.nan, mean5)
gabungan_klorofil_tpl_spl_arus["depth [m]"] = gabungan_klorofil_tpl_spl_arus["depth [m]"].replace(np.nan, mean6)

# tampilkan dataset
df = gabungan_klorofil_tpl_spl_arus.drop(['Cruise', 'Type', 'yyyy-mm-ddThh:mm:ss.sss', 'Dummy', 'latitude [degrees_north]', 'longitude [degrees_east]', 'time [hours since 1950-01-01 00:00:00]', 'Station'], axis=1)
# mengganti nama
df.rename(columns = {'Longitude [degrees_east]':'longitude', 'Latitude [degrees_north]':'latitude', 'chl [mg m-3]':'klorofil', 'depth [m]':'kedalaman_laut', 'zos [m]':'tinggi_permukaan_laut', 'thetao [degrees_C]':'suhu_permukaan_laut', 'uo [m s-1]':'arus_laut_arah_X', 'vo [m s-1]':'arus_laut_arah_Y'}, inplace = True)
st.dataframe(df)

BBox = ((df.longitude.min(),   df.longitude.max(),      
         df.latitude.min(), df.latitude.max()))

# scaling data
ss = StandardScaler()
df_scale= ss.fit_transform(df)
df_scale = pd.DataFrame(df_scale,columns=df.columns)
df_scale.to_csv("http://ahmadfaisalsiregar.skom.id/resource/doc/data/df_scale.csv", index=False)

df_scaled = pd.read_csv("http://ahmadfaisalsiregar.skom.id/resource/doc/data/df_scale.csv")
df_6c = df_scaled
df_6c['lat'] = df['latitude']
df_6c['lon'] = df['longitude']
df_6c['klo'] = df['klorofil']

clustering_kmeans = KMeans(n_clusters=6)
df_6c['cluster'] = clustering_kmeans.fit_predict(df_6c)

df_6c.loc[df_6c['cluster'] == 0, 'color'] = 'r'
df_6c.loc[df_6c['cluster'] == 1, 'color'] = 'g'
df_6c.loc[df_6c['cluster'] == 2, 'color'] = 'b'
df_6c.loc[df_6c['cluster'] == 3, 'color'] = 'c'
df_6c.loc[df_6c['cluster'] == 4, 'color'] = 'm'
df_6c.loc[df_6c['cluster'] == 5, 'color'] = 'y'

BBox = ((df_6c.longitude.min(),   df_6c.longitude.max(),      
         df_6c.latitude.min(), df_6c.latitude.max()))

df_6c['cluster'] = clustering_kmeans.labels_

# Menentukan cluster dengan konsentrasi dari yang terkecil hingga terbesar
total1 = 0
total2 = 0
total3 = 0
total4 = 0
total5 = 0
total6 = 0
y1 = []
y2 = []
y3 = []
y4 = []
y5 = []
y6 = []

for i in range(len(df_6c['cluster'])):
  if (df_6c['cluster'][i] == 0):              
    avg1 = df['klorofil'][i]
    total1 = avg1 + total1
    y1.append(total1)
  elif (df_6c['cluster'][i] == 1):          
    avg2 = df['klorofil'][i]
    total2 = avg2 + total2
    y2.append(total2)
  elif (df_6c['cluster'][i] == 2):        
    avg3 = df['klorofil'][i]
    total3 = avg3 + total3
    y3.append(total3)
  elif (df_6c['cluster'][i] == 3):        
    avg4 = df['klorofil'][i]
    total4 = avg4 + total4
    y4.append(total4)
  elif (df_6c['cluster'][i] == 4):          
    avg5 = df['klorofil'][i]
    total5 = avg5 + total5
    y5.append(total5)
  elif (df_6c['cluster'][i] == 5):        
    avg6 = df['klorofil'][i]
    total6 = avg6 + total6
    y6.append(total6)
          
x1 = statistics.mean(y1)
x2 = statistics.mean(y2)
x3 = statistics.mean(y3)
x4 = statistics.mean(y4)    
x5 = statistics.mean(y5)
x6 = statistics.mean(y6)

df_6c['mean_klorofil'] = ""

for i in range(len(df_6c['cluster'])):
  if (df_6c['cluster'][i] == 0):              
    df_6c['mean_klorofil'][i] = x1
  elif (df_6c['cluster'][i] == 1):          
    df_6c['mean_klorofil'][i] = x2      
  elif (df_6c['cluster'][i] == 2):        
    df_6c['mean_klorofil'][i] = x3      
  elif (df_6c['cluster'][i] == 3):        
    df_6c['mean_klorofil'][i] = x4      
  elif (df_6c['cluster'][i] == 4):          
    df_6c['mean_klorofil'][i] = x5      
  elif (df_6c['cluster'][i] == 5):        
    df_6c['mean_klorofil'][i] = x6      

print(x1)
print(x2)
print(x3)
print(x4)
print(x5)
print(x6)

# urutan cluster dengan klorofil tertinngi sampai yang terendah
data_cluster = df_6c.sort_values('mean_klorofil', ascending=False)
urutan_cluster = data_cluster.drop_duplicates(subset=['mean_klorofil'], keep='first')

"""#### Daftar Cluster"""
urutan_cluster[['cluster','mean_klorofil']]
"""###### Catatan: Cluster dengan rata-rata klorofil tertinggi merupakan daerah dengan potensi ikan terbesar"""

data = df_6c.drop_duplicates(
                  subset = ['longitude', 'latitude'],
                  keep = 'last').reset_index(drop = True)

# visualisasi data 
"""### Visualisasi Data (Chart)"""
plot = px.scatter(data_frame=df_6c, 
                  x = df_6c['longitude'], 
                  y = df_6c['latitude'],                   
                  hover_name = df_6c['mean_klorofil'],
                  color = 'cluster')
st.plotly_chart(plot)

"""### Peta Prediksi Daerah Penangkapan Ikan"""
fig = px.scatter_mapbox(df_6c, 
                  lat = df_6c['lat'], 
                  lon = df_6c['lon'], 
                  color = df_6c['cluster'], 
                  size = df_6c['klo'],
                  color_continuous_scale = px.colors.sequential.Viridis, 
                  size_max = 10, 
                  zoom = 7,                  
                  mapbox_style = 'carto-positron')
fig

df_6c.drop(df_6c.columns[df_6c.columns.str.contains('color',case = False)],axis = 1, inplace = True)
silhouette_avg = metrics.silhouette_score(df_6c, df_6c['cluster'])
"""##### Silhouette Coefficient for the above clustering:"""
silhouette_avg
