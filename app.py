import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from pyproj import Transformer
from pyproj import CRS 
import geopandas as gpd
import matplotlib.pyplot as plt
import openpyxl
import warnings
import tempfile
import zipfile
import os
from shapely.geometry import Point, Polygon
import shutil

st.title("Jurisdiction Data Cleaning")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

selected_dist = st.selectbox(
    'Select Jusriscition Type', 
    options=["State House", "State Senate"]
    )

if uploaded_file is not None and selected_dist=="State House":
    # Read the file into a Pandas DataFrame
    adrian = pd.read_csv(uploaded_file)
    
    # Display the data in a table
    st.subheader("Uploaded Data Preview")
    st.dataframe(adrian)

    existing_zip_path ='2026StateHouseDistricts.zip'
    
    with tempfile.TemporaryDirectory() as tmpdir:

        tmp_zip_path = os.path.join(tmpdir, "temp_copy.zip")
        shutil.copy(existing_zip_path, tmp_zip_path)
        
        # 2. Extract zip
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
            
        # 3. Find the .shp file
        shp_files = [file for file in os.listdir(tmpdir) if file.endswith('.shp')]
        
        if len(shp_files) == 0:
            st.error("No .shp file found in ZIP.")
            st.stop()
            
        shp_path = os.path.join(tmpdir, shp_files[0])
        
        # 4. Read shapefile
        gdf = gpd.read_file(shp_path)

    latlon=[]
    for i in range(len(adrian["Residence_Addresses_Latitude"])):
        latlon.append(Point([adrian["Residence_Addresses_Longitude"][i], adrian["Residence_Addresses_Latitude"][i]]))
    
    adrian["Points"]=latlon

    selected_dept = st.selectbox(
    'Select House District', 
    options=gdf['DISTRICTNO'].unique()
    )

    filtered = gdf.loc[gdf['DISTRICTNO'] == selected_dept]
    polygon_coords = filtered["geometry"]
    poly = filtered["geometry"].iloc[0]

    for i in range(len(adrian["Points"])):
        if poly.contains(adrian["Points"][i]):
            pass
        else:
            adrian.loc[i, "Points"] = None

    adrian = adrian.dropna(subset=['Points'])
    
    # =========================
    # CREATE MAP
    # =========================
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        hover_name='DISTRICTNO',
        hover_data=["DISTRICTNO"],
        mapbox_style="carto-positron",
        zoom=5,
        center={
            "lat": gdf.geometry.centroid.y.mean(),
            "lon": gdf.geometry.centroid.x.mean()
        },
        opacity=0.5
    )

    # =========================
    # ADD USER POINTS
    # =========================
    fig.add_trace(
        go.Scattermapbox(
            lat=adrian["Residence_Addresses_Latitude"],
            lon=adrian["Residence_Addresses_Longitude"],
            mode="markers",
            marker=dict(
                size=9,
                color="blue"
            ),
            text=adrian.index,
            name="Uploaded Points"
        )
    )

    # =========================
    # LAYOUT
    # =========================
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=700
    )

    # =========================
    # SHOW MAP IN STREAMLIT
    # =========================
    st.plotly_chart(fig, use_container_width=True)

    adrian=adrian.drop(columns=["Points"])

    adrian = adrian.to_csv(index=False).encode('utf-8')
    
    st.download_button(
    label="Download data as CSV",
    data=adrian,
    file_name='StateHouse34.csv',
    mime='text/csv')

elif uploaded_file is not None and selected_dist=="State Senate":
    # Read the file into a Pandas DataFrame
    adrian = pd.read_csv(uploaded_file)
    
    # Display the data in a table
    st.subheader("Uploaded Data Preview")
    st.dataframe(adrian)

    existing_zip_path ='2026StateSenateDistricts.zip'
    
    with tempfile.TemporaryDirectory() as tmpdir:

        tmp_zip_path = os.path.join(tmpdir, "temp_copy.zip")
        shutil.copy(existing_zip_path, tmp_zip_path)
        
        # 2. Extract zip
        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
            
        # 3. Find the .shp file
        shp_files = [file for file in os.listdir(tmpdir) if file.endswith('.shp')]
        
        if len(shp_files) == 0:
            st.error("No .shp file found in ZIP.")
            st.stop()
            
        shp_path = os.path.join(tmpdir, shp_files[0])
        
        # 4. Read shapefile
        gdf = gpd.read_file(shp_path)

    latlon=[]
    for i in range(len(adrian["Residence_Addresses_Latitude"])):
        latlon.append(Point([adrian["Residence_Addresses_Longitude"][i], adrian["Residence_Addresses_Latitude"][i]]))
    
    adrian["Points"]=latlon

    selected_dept = st.selectbox(
    'Select Senate District', 
    options=gdf['DISTRICTNO'].unique()
    )

    filtered = gdf.loc[gdf['DISTRICTNO'] == selected_dept]
    polygon_coords = filtered["geometry"]
    poly = filtered["geometry"].iloc[0]

    for i in range(len(adrian["Points"])):
        if poly.contains(adrian["Points"][i]):
            pass
        else:
            adrian.loc[i, "Points"] = None

    adrian = adrian.dropna(subset=['Points'])

    # =========================
    # CREATE MAP
    # =========================
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        hover_name='DISTRICTNO',
        hover_data=["DISTRICTNO"],
        mapbox_style="carto-positron",
        zoom=5,
        center={
            "lat": gdf.geometry.centroid.y.mean(),
            "lon": gdf.geometry.centroid.x.mean()
        },
        opacity=0.5
    )

    # =========================
    # ADD USER POINTS
    # =========================
    fig.add_trace(
        go.Scattermapbox(
            lat=adrian["Residence_Addresses_Latitude"],
            lon=adrian["Residence_Addresses_Longitude"],
            mode="markers",
            marker=dict(
                size=9,
                color="blue"
            ),
            text=adrian.index,
            name="Uploaded Points"
        )
    )

    # =========================
    # LAYOUT
    # =========================
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=700
    )

    # =========================
    # SHOW MAP IN STREAMLIT
    # =========================
    st.plotly_chart(fig, use_container_width=True)

    adrian=adrian.drop(columns=["Points"])

    adrian = adrian.to_csv(index=False).encode('utf-8')
    
    st.download_button(
    label="Download data as CSV",
    data=adrian,
    file_name='StateHouse34.csv',
    mime='text/csv')
    
else:
    st.info("Please upload a CSV file to get started.")

