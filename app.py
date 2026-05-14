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


st.title("CSV Data Viewer")

# Create a file uploader widget for CSV files
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
uploaded_file2 = st.file_uploader("Choose a zipped shapefile", type="zip")

if uploaded_file is not None and uploaded_file2 is not None:
    # Read the file into a Pandas DataFrame
    adrian = pd.read_csv(uploaded_file)
    
    # Display the data in a table
    st.subheader("Uploaded Data Preview")
    st.dataframe(adrian)

    with tempfile.TemporaryDirectory() as tmpdir:

        # Save uploaded zip
        zip_path = os.path.join(tmpdir, "shapefile.zip")

        with open(zip_path, "wb") as f:
            f.write(uploaded_file2.getbuffer())

        # Extract zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Find the .shp file
        shp_files = [
            file for file in os.listdir(tmpdir)
            if file.endswith(".shp")
        ]

        if len(shp_files) == 0:
            st.error("No .shp file found in ZIP.")
            st.stop()

        shp_path = os.path.join(tmpdir, shp_files[0])

        # Read shapefile
        gdf = gpd.read_file(shp_path)

    latlon=[]
    for i in range(len(adrian["Residence_Addresses_Latitude"])):
        latlon.append(Point([adrian["Residence_Addresses_Longitude"][i], adrian["Residence_Addresses_Latitude"][i]]))
    
    adrian["Points"]=latlon
    polygon_coords = gdf["geometry"][33]
    poly = Polygon(polygon_coords)

    for i in range(len(adrian["Points"])):
        if poly.contains(adrian["Points"][i]):
            pass
        else:
            adrian["Points"][i]=None

    adrian = adrian.dropna(subset=['Points'])

    # Make sure gdf is EPSG:4326
    gdf = gdf.to_crs(epsg=4326)

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