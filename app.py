import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import leafmap.foliumap as leafmap
import geopandas as gpd
from shapely.geometry import Point
import branca.colormap as cm
import plotly.express as px
import numpy
import altair as alt
import networkx as nx
import re

from vega_datasets import data
st.set_page_config(layout="wide")

#Setting Title
st.title('World Atlas of Language Structures Interactive Dashboard ')

#writing to dashboard
st.markdown('This interactive dashboard lets you explore the [World Atlas of Language Structures](https://wals.info/) Choose a column to visualise via the sidebar on the right! You can use Control + F to search for values within the table!')


def load_data():


    #function load_data() loads data from the wals table excel file


    #initialising file name
    file = 'wals.csv'

    #reading the dataset using pandas and assigning it to a variable 
    df = pd.read_csv(file, encoding = 'latin1')

    #returning the variable
    return df



df = load_data() #assigning the CSV to a dataframe df

#loading the dataframe via streamlit
st.dataframe(df, use_container_width= True)

def mapcountries():

    #function mapcountries() lets user visualise WALS by country

    st.header('Languages by Countries')

    #creating two columns that will be used to display the data. Col1 is used to display visualisations and col2 is used to display associated tables
    col1, col2 = st.columns([6, 6])

    #extracting countries after splitting using commas
    splitcountries = df['Countries'].str.split(',\s+', expand = True).stack().value_counts().rename_axis('unique_values').reset_index(name='counts')

    #displaying the count languages by countries
    col2.write("Table of Countries")

    col2.dataframe(splitcountries, use_container_width= True)   

    #plotting a bar chart of languges by countries                          
    c = alt.Chart(splitcountries, title="Bar Chart of Languages by Country").mark_bar().encode(
    x='unique_values', #plotting the different types of macroareas on the x axis
    y= 'counts', #plotting the counts of each macroarea on the y axis
).properties(
    width=600,
    height=400).interactive() #setting the bar chart to interactive


    col1.altair_chart(c) #displaying the altair chart

    #converting the dataframe to a geodataframe for plotting
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    gdf = gdf.set_crs('epsg:4326')


    #calling the world shapefile    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    #getting unique values of countries to select from 
    countrylist = splitcountries['unique_values'].unique()

    #initialising a multiselect on the sidebar to choose the country to visualise
    selected_countries = st.sidebar.multiselect('Select Country to visualize', countrylist)

    #checking if something has been selected
    if len(selected_countries) == 0:
        st.sidebar.text('Choose at least 1 Country to get started')
    
    #if 
    else:
        #locating the chosen countries from the geodataframe
        gdf1 = gdf.loc[gdf['Countries'].str.contains(' '.join(x for x in selected_countries), case=False, na=False)]
        gdf2 = gdf1.drop(['geometry'], axis=1)

        col2.markdown("**Chosen Language by Country**")
        col2.dataframe(gdf2, use_container_width= True)

        #plotting a scatter chart for languages in the chosen countries
        c1 = alt.Chart(gdf2, title="Scatter Chart - Chosen Language by Country").mark_circle(
            ).encode(
            x='Name',
            y='Family',
            color ='Family'
            ).properties(
        width=600,
        height=400).interactive()
        col1.altair_chart(c1)

        #initialising a map and rendering it via streamlit
        m = leafmap.Map(
                layers_control=True,
                draw_control=False,
                measure_control=False,
                fullscreen_control=False,
            )
        m.add_basemap('CartoDB.Positron')
        m.add_gdf(
                gdf=gdf1,
                zoom_to_layer=True,
                layer_name='Points',
                info_mode='on_click',
                style={'color': '#90EE90', 'fillOpacity': 0.3, 'weight': 0.5},
                )


        st.markdown('**Locating Langauges on a map!**')

        m_streamlit = m.to_streamlit(1200, 1500)
    

def mapMacro():

    #function MapMacro explores the dataset using the column Macroarea
    st.header('Languages by Macroarea')

    #creating two columns that will be used to display the data. Col1 is used to display visualisations and col2 is used to display associated tables
    col1, col2 = st.columns([6, 6])

    #grouping the df by macroarea
    grouped = df.groupby(['Macroarea','Family'], as_index = False).count()

    grouped = grouped[grouped.columns[0:3]].rename(columns={"Name":"Count"})


    #displaying the dataframe using streamlit
    col2.markdown("**Count of languages by Macroareas**")
    col2.dataframe(grouped, use_container_width= True)

    #using streamlit altair to plot the value counts using a bar chart
    c = alt.Chart(grouped, title="Bar Chart of Languages by Macroarea").mark_bar().encode(
    x='Macroarea', #plotting the different types of macroareas on the x axis
    y= 'Count', #plotting the counts of each macroarea on the y axis
    color = 'Family'
).properties(
    width=600,
    height=400).interactive() #setting the bar chart to interactive


    col1.altair_chart(c) #displaying the altair chart

    #converting the dataframe to a geodataframe using the points_from_xy method 
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    gdf = gdf.set_crs('epsg:4326')


    #calling the world shapefile    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    #getting all unique Macroarea values and adding it to a list
    macrolist = gdf['Macroarea'].unique()

    #initialising a 
    selected_drugs = st.sidebar.multiselect('Select Macroarea to visualize', macrolist)

    if len(selected_drugs) == 0:
        st.sidebar.text('Choose at least 1 Macroarea to get started')

    else:

        #locating the chosen countries using macroarea
        gdf1 = gdf.loc[gdf['Macroarea'].isin(selected_drugs)]
        gdf2 = gdf1.drop(['geometry'], axis=1)

        #plotting languages by chosen macroarea
        c1 = alt.Chart(gdf2, title="Scatter Chart - Chosen Language by Macroarea").mark_circle(
        ).encode(
        x='Genus',
        y='Family',
        color ='Genus'
        ).properties(
    width=600,
    height=400).interactive()

        col2.markdown("**Table of Chosen Language by Macroarea**")
        col2.dataframe(gdf2, use_container_width= True)

        col1.altair_chart(c1)

        #plotting it on a map 
        m = leafmap.Map(
            layers_control=True,
            draw_control=False,
            measure_control=False,
            fullscreen_control=False,
        )
        m.add_basemap('CartoDB.Positron')
        m.add_gdf(
            gdf=gdf1,
            zoom_to_layer=True,
            layer_name='Points',
            info_mode='on_click',
            style={'color': '#90EE90', 'fillOpacity': 0.3, 'weight': 0.5},
            )


        st.markdown('**Locating Langauges on a map!**')

        m_streamlit = m.to_streamlit(1200, 1500)
    




def mapgenus():

        #function mapgenus explores the dataset using the column Genus

    st.header('Languages by Genus')

    col1, col2 = st.columns([6, 6])

    #grouping the df by genus

    grouped = df.groupby(['Genus','Family'], as_index = False).count()

    grouped = grouped[grouped.columns[0:3]].rename(columns={"Name":"Count"})

    col2.markdown("**Counts of Genus**")
    col2.dataframe(grouped,use_container_width=True)

    #plotting genus counts
    c = alt.Chart(grouped,title = "Bar Chart of Genus Counts").mark_bar().encode(
    x='Genus',
    y='Count',
    color='Family'
    ).properties(
    width=600,
    height=400).interactive()
    col1.altair_chart(c)

    #converting the dataframe to a geodataframe
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    
    gdf = gdf.set_crs('epsg:4326')

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    #geting unique values and assigning it a list
    Genuslist = gdf['Genus'].unique()

    selected_drugs = st.sidebar.multiselect('Select Genus to visualize', Genuslist)

    #checking if a genus has been selected using the sidebar
    if len(selected_drugs) == 0:
        st.sidebar.text('Choose at least 1 Genus to get started')

    else:

        #locating and checking if the genus is in the selected list 
        gdf1 = gdf.loc[gdf['Genus'].isin(selected_drugs)]
        gdf2 = gdf1.drop(['geometry'], axis=1)

        #plotting a scatterplot of the languages by the chosen Genus 
        c1 = alt.Chart(gdf2, title ="Scatter Chart of Chosen Language by Genus").mark_circle(
        ).encode(
        x='Name',
        y='Family',
        color ='Family'
        ).properties(
    width=600,
    height=400).interactive()

        col2.markdown("**Chosen Language by Genus**")


        #showing the geodataframe of chosen Genus
        col2.dataframe(gdf2, use_container_width= True)



        col1.altair_chart(c1)

        #plotting a map of the chosen genus 
        m = leafmap.Map(
            layers_control=True,
            draw_control=False,
            measure_control=False,
            fullscreen_control=False,
        )
        m.add_basemap('CartoDB.Positron')
        m.add_gdf(
            gdf=gdf1,
            zoom_to_layer=True,
            layer_name='Points',
            info_mode='on_click',
            style={'color': '#90EE90', 'fillOpacity': 0.3, 'weight': 0.5},
            )


        st.markdown('**Locating Langauges on a map!**')

        m_streamlit = m.to_streamlit(1200, 1500)

def mapfamily():

    #function mapfamily explores WALS using the family column
    st.header('Languages by Families')

    col1, col2 = st.columns([6, 6])

    #grouping the df by family
    grouped = df.groupby(['Family','Genus'], as_index = False).count()

    grouped = grouped[grouped.columns[0:3]].rename(columns={"Name":"Count"})

    col2.markdown('**Count of Language Families**')

    #showing the df grouped by family 
    col2.dataframe(grouped,use_container_width=True)

    #plotting value counts of different families
    c = alt.Chart(grouped, title = " Bar Chart of Languages by Family").mark_bar().encode(
    x='Family',
    y='Count',
    color='Genus'
    ).properties(
    width=600,
    height=400).interactive()
    col1.altair_chart(c)
    
    #converting the df to a gdf
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    
    gdf = gdf.set_crs('epsg:4326')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    #getting list of unique values to filter by 
    Familylist = gdf['Family'].unique()

    #select bar to choose family to visualise 
    selected_family = st.sidebar.multiselect('Select Family to visualize', Familylist)

    #checking if family has been selected
    if len(selected_family) == 0:
        st.sidebar.text('Choose at least 1 Family to get started')

    else:
        #filtering the gdf by chosen family
        gdf1 = gdf.loc[gdf['Family'].isin(selected_family)]
        gdf2 = gdf1.drop(['geometry'], axis=1)

        #scatter plot of chosen family
        c1 = alt.Chart(gdf2, title = "Scatter Chart of Chosen Language Family").mark_circle(
        ).encode(
        x='Name',
        y='Genus',
        color ='Genus'
        ).properties(
    width=600,
    height=400).interactive()
        col2.markdown('**Languages in chosen Families**')
        col2.dataframe(gdf2, use_container_width= True)

        col1.altair_chart(c1)

        #plotting it on a map
  
        m = leafmap.Map(
            layers_control=True,
            draw_control=False,
            measure_control=False,
            fullscreen_control=False,
        )
        m.add_basemap('CartoDB.Positron')

        m.add_gdf(
            gdf=gdf1,
            zoom_to_layer=True,
            layer_name='Points',
            style={'color': '#90EE90', 'fillOpacity': 0.3, 'weight': 0.5},

            info_mode='on_click',
            )


        st.markdown('**Locating Langauges on a map!**')
        m_streamlit = m.to_streamlit(1200, 1500)


#giving the user the column to visualise the dataset by
option=st.sidebar.selectbox('Select a Column to Visualise ',('Select an Option', 'Genus','Family', 'Macroarea', 'Country'))
if option == 'Genus':
    mapgenus()

if option == 'Family':

    mapfamily()

if option == 'Macroarea':
    mapMacro()

if option == 'Country':
    mapcountries() 