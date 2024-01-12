# Import necessary packages
import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import numpy as np
import plotly.express as px
from folium import plugins
from PIL import Image

# -------Load necessary fields-----------------------------------------

def LoadDataFromSource():
    result_df_from_csv = \
        pd.read_csv(r'D:\Chindhu\RoadMap for Career\Data Science\Guvi\Python Codes\Airbnb\Airbnb_EDA.csv')
    
    return result_df_from_csv
    
def LoadPriceAgg(result_df, country_option):
    country_price_min_max = result_df.groupby('country')['price'].agg(['min', 'max'])
    min_price = country_price_min_max.loc[country_option, 'min']
    max_price = country_price_min_max.loc[country_option, 'max']

    return min_price, max_price

def LoadNoOfGuests(result_df, country_option):
    no_of_guests = result_df.groupby('country')['accommodates'].unique()
    guest = no_of_guests.loc[country_option]
    guest.sort()

    return guest

def LoadPropertyType(result_df, country_option):
    prop_type = result_df.groupby('country')['property_type'].unique()
    property_types = prop_type.loc[country_option]
    property_types.sort()

    return property_types

def LoadPropertyTypeBasedOnArea(result_df, country_option, area, avail_option):
    filter_result_df = result_df.query(f'country == "{country_option}" \
                                       and government_area == "{area}"')
    filter_result_df = result_df.query(f'{avail_option}>0')
    prop_types = filter_result_df['property_type'].unique()
    prop_types.sort()

    return prop_types

def LoadOverallRating(result_df, country_option):
    ratings_by_country = result_df.groupby('country')['overall_rating'].unique()
    rating = ratings_by_country.loc[country_option]
    sorted_indices = np.argsort(rating)[::-1]
    sorted_rating = rating[sorted_indices]

    return sorted_rating

def LoadGovernmentArea(result_df, country_option):
    area_df = result_df.groupby('country')['government_area'].unique()
    areas = area_df.loc[country_option]
    areas.sort()

    return areas

# ------------Filtering fields based on user's choice------------------

def FilterCountryGuestPrice(result_df, 
                            country_option, 
                            total_guests, 
                            min_price, 
                            max_price):
    filter_result_df = result_df.query(f'country == "{country_option}" \
                                       and accommodates == {total_guests}')
    filter_result_df = filter_result_df[filter_result_df['price'].between\
                                        (min_price, max_price)]
    filter_result_df = filter_result_df.loc[:,['name',
                                               'latitude',
                                               'longitude',
                                               'accommodates',
                                               'price']]

    return filter_result_df

def FilterCountryRatings(result_df, country_option, ratings):
    filter_df = pd.DataFrame()
    for rating in ratings :
        filter_result_df = result_df.query(f'country == "{country_option}" \
                                           and overall_rating == {rating}')
        filter_result_df = filter_result_df.loc[:,['name', 
                                                   'latitude', 
                                                   'longitude',
                                                   'accommodates',
                                                   'price',
                                                   'overall_rating']]
        filter_df = pd.concat([filter_df, filter_result_df], 
                              ignore_index=True)

    return filter_df

def FilterCountryProperty(result_df, country_option, selected_prop_types):
    filter_df = pd.DataFrame()
    for prop_type in selected_prop_types :
        filter_result_df = result_df.query(f'country == "{country_option}" \
                                           and property_type == "{prop_type}"')
        filter_result_df = filter_result_df.loc[:,['name',
                                                   'latitude',
                                                   'longitude',
                                                   'accommodates',
                                                   'price',
                                                   'property_type']]
        filter_df = pd.concat([filter_df, filter_result_df], ignore_index=True)

    return filter_df

def FilterPriceProperty(result_df, country_option):
    filter_result_df = result_df.query(f'country == "{country_option}"')
    price_country_agg = filter_result_df.groupby('property_type')\
                            ['price'].mean().reset_index()

    return price_country_agg

def FilterGovernmentAreaAvail(result_df, 
                              country_option, 
                              gov_area_option, 
                              avail_option):
    filter_result_df = result_df.query(f'country == "{country_option}" \
                                       and government_area == "{gov_area_option}"')
    filter_result_df = filter_result_df.query(f'{avail_option}>0')
    filter_result_df = filter_result_df.loc[:,['name',
                                               'latitude',
                                               'longitude', 
                                               avail_option]]
    return filter_result_df

def FilterPropertyTypeAvail(result_df, 
                            country_option, 
                            gov_area_option, 
                            avail_option):
    filter_result_df = result_df.query(f'country == "{country_option}" \
                                     and government_area == "{gov_area_option}"')
    filter_result_df = filter_result_df.query(f'{avail_option}>0')
    filter_result_df = filter_result_df.groupby('property_type')\
                            [avail_option].agg('count').reset_index()
    return filter_result_df

# -----------------Visualize the filtered results----------------------

def VisualizeFilterCountryGuestPrice(filter_result_df):
    # Create a folium map
    m = folium.Map( location = [filter_result_df['latitude'].mean(), 
                                filter_result_df['longitude'].mean()], 
                    zoom_start=10)

    # Create a MarkerCluster layer for better performance with many markers
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each Airbnb location
    for index, row in filter_result_df.iterrows():
        popup_content = f"Name: {row['name']} \
                        <br>Price: ${row['price']} \
                        <br>Accommodates: {row['accommodates']}"
        folium.Marker([row['latitude'], 
                       row['longitude']], 
                       popup=popup_content).add_to(marker_cluster)

    try :
        st.pydeck_chart(folium_static(m))

    except Exception as e:
        print('Error message' + str(e))

def VisualizeFilterCountryRatings(filter_result_df):
    # Create a folium map
    m = folium.Map(location = [filter_result_df['latitude'].mean(), 
                             filter_result_df['longitude'].mean()], 
                    zoom_start=10)

    # Create marker cluster layer
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each Airbnb location
    for index, row in filter_result_df.iterrows():
        popup_content = f"Name: {row['name']} \
                        <br>Price: ${row['price']} \
                        <br>Accommodates: {row['accommodates']} \
                        <br>Rating: {row['overall_rating']}"
        folium.Marker([row['latitude'], 
                       row['longitude']], 
                       popup=popup_content).add_to(marker_cluster)

    try :
        st.pydeck_chart(folium_static(m))

    except Exception as e:
        print('Error message' + str(e))

def VisualizeFilterCountryProperty(filter_result_df):
    # Create a folium map
    m = folium.Map(location = [filter_result_df['latitude'].mean(), 
                               filter_result_df['longitude'].mean()], 
                    zoom_start=10)

    # Create a MarkerCluster layer
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers for each Airbnb location
    for index, row in filter_result_df.iterrows():
        popup_content = f"Name: {row['name']} \
                        <br>Price: ${row['price']} \
                        <br>Accommodates: {row['accommodates']} \
                        <br>Property Type: {row['property_type']}"
        folium.Marker([row['latitude'], 
                       row['longitude']], 
                       popup=popup_content).add_to(marker_cluster)

    try :
        st.pydeck_chart(folium_static(m))

    except Exception as e:
        print('Error message' + str(e))

def VisualizePriceBasedOnCountry(price_country_agg):
    fig = px.bar(price_country_agg, 
                 x = 'country', 
                 y = 'price',
                 title = 'Average Price based on Country')
    fig.update_layout(
        xaxis_title = 'Countries',
        yaxis_title = 'Average Price (in $)'
    )
    return fig

def VisualizePriceBasedOnProperty(price_property_country_agg):
    fig = px.bar(price_property_country_agg, 
                 x = 'property_type', 
                 y = 'price',
                 title = 'Average Price based on Property')
    fig.update_layout(
        xaxis_title = 'Property Type',
        yaxis_title = 'Average Price (in $)'
    )
    return fig

def VisualizeAvailabilityBasedOnProperty(avail_prop_type_agg, avail_option, season):
    fig = px.pie(avail_prop_type_agg, 
                 values = avail_option, 
                 names = 'property_type',
                 title = 'No. of properties which are available for the next '\
                            + season)
    
    return fig

def VisualizeAvailabilityBasedOnArea(avail_location_season_agg):

    lat = avail_location_season_agg['latitude'].tolist()
    lon = avail_location_season_agg['longitude'].tolist()
    
    initial_lat = avail_location_season_agg['latitude'].mean()
    initial_lon = avail_location_season_agg['longitude'].mean()

    map = folium.Map(location = [initial_lat, initial_lon], 
                     tiles = "Cartodb dark_matter", 
                     zoom_start = 10)

    plugins.HeatMap(list(zip(lat, lon))).add_to(map)

    marker_cluster = MarkerCluster().add_to(map)

    column_headers = list(avail_location_season_agg.columns.values)

    for index, row in avail_location_season_agg.iterrows():
        popup_content = f"Name: {row['name']} \
                        <br>Latitude: ${row['latitude']} \
                        <br>Longitude: {row['longitude']} \
                        <br>{column_headers[3]}: {row[column_headers[3]]}"
        folium.Marker([row['latitude'], 
                       row['longitude']], 
                       popup=popup_content).add_to(marker_cluster)

    try :
        st.pydeck_chart(folium_static(map))

    except Exception as e:
        print('Error message' + str(e))

    
# --------------------Main Method--------------------------------------
def main():

    #Streamlit page setup
    st.set_page_config(
        page_title = "Airbnb Data Visualization",
        page_icon =  ":hotel:",
        initial_sidebar_state = "auto"
        )
    
    with st.sidebar:
        selected_menu =  option_menu (
            menu_title = "Airbnb",
            menu_icon = "buildings",
            options = ['Home', 
                       'Explore location', 
                       'Price Analysis',
                       'Availaibility Analysis'
                      ],
            icons = ['house', 
                     'search',
                     'currency-dollar',
                     'calendar-week'
                    ],
        )

    # Initially Load Data From MongoDB
    result_df=LoadDataFromSource()

    # Populating the sidebars
    if selected_menu == 'Home':
        st.title("Airbnb Analysis\n\n")
        image_path=r'D:\Chindhu\RoadMap for Career\Data Science\Guvi\Python Codes\Airbnb\airbnb_banner.jpg'
        pil_image = Image.open(image_path)
        st.image(pil_image, caption = 'airbnb logo', use_column_width=False)
        st.write("\n\nAirbnb, is an American San Francisco-based company \
                 operating an online marketplace for short- and long-term \
                 homestays and experiences. The company acts as a broker \
                 and charges a commission from each booking.\n")
        st.write("Developed by Chindhu as an open source project which \
                 deals with extracting data from airbnb dataset available \
                 in mongoDB as a sample dataset, cleaning and transforming \
                 it to a CSV file. Exploratory Data Visualization (EDA) is \
                 done using Streamlit along with Plotly charts and Folium \
                 Geospatial Visualization. Also, an interactive dashboard \
                 is build using Power BI to acquire insights from the data.\n")
        st.write("Do leave your suggestions or bottle necks while using the \
                 portal, so that it can be revised and improved.\n")
        st.write('Email - chindhual@gmail.com')

    elif selected_menu == 'Explore location':
        st.write('## Location Details')
        country = result_df['country'].unique()
        st.write('### Country')
        country_option = st.selectbox(
            "Select the country to view properties...",
            country,
            index = None,
            placeholder = "Select one country",
            )
        if country_option is not None:
            tab1, tab2, tab3 = st.tabs(['Price', 
                                        'Ratings', 
                                        'Property Type'])
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    guest = LoadNoOfGuests(result_df,
                                           country_option)
                    st.markdown('**Total Guest**')
                    total_guests = st.radio('Select the number of guests',guest)

                with col2:
                    min_price, max_price = LoadPriceAgg(result_df, country_option)
                    st.markdown('**Price**')
                    slider_range = st.slider("Select the price range(per night) in dollars", 
                                             value = [min_price, max_price])

                if(st.button('Apply', key = 'filter_country_guest_price')):
                    filter_result_df = FilterCountryGuestPrice(result_df,
                                                               country_option,
                                                               total_guests,
                                                               slider_range[0],
                                                               slider_range[1])
                    VisualizeFilterCountryGuestPrice(filter_result_df)
                    st.write('**Filtered Results :**')
                    st.dataframe(filter_result_df)

            with tab2:
                overall_ratings = LoadOverallRating(result_df, country_option)
                st.markdown('**Overall Rating**')
                selected_ratings = st.multiselect('Choose any rating(s)', 
                                                  overall_ratings)
                if selected_ratings:
                    if(st.button('Apply', key = 'filter_country_rating')):
                        filter_result_df = FilterCountryRatings(result_df,
                                                                country_option,
                                                                selected_ratings)
                        VisualizeFilterCountryRatings(filter_result_df)
                        st.write('**Filtered Results :**')
                        st.dataframe(filter_result_df)
            with tab3:
                prop_type = LoadPropertyType(result_df, country_option)
                st.markdown('**Property Types**')
                property_types_check_box = [st.checkbox(prop, key=prop) for prop in prop_type]
                selected_prop_types = [prop for prop, selected in zip(prop_type, property_types_check_box) if selected]
                if selected_prop_types is not None:
                    if (st.button('Apply', key = 'filter_country_property')):
                        filter_result_df = FilterCountryProperty(result_df,
                                                                 country_option,
                                                                 selected_prop_types)
                        VisualizeFilterCountryProperty(filter_result_df)
                        st.write('**Filtered Results :**')
                        st.dataframe(filter_result_df)

    elif selected_menu == 'Price Analysis':  
        st.write('## Price Details')
        tab1, tab2  = st.tabs(['Locations', 'Property Types'])
        with tab1:
            price_country_agg = result_df.groupby('country')['price'].mean().reset_index()
            st.plotly_chart(VisualizePriceBasedOnCountry(price_country_agg),
                            use_container_width = True, 
                            config = {'responsive': True})

        with tab2:
            country = result_df['country'].unique()
            st.write('### Country')
            country_option = st.selectbox(
                "Select the country to view properties...",
                country,
                index = None,
                placeholder = "Select one country",
            )
            if country_option is not None:
                price_property_country_agg = FilterPriceProperty(result_df,
                                                                 country_option)
                st.plotly_chart(VisualizePriceBasedOnProperty(price_property_country_agg),
                                use_container_width = True, 
                                config = {'responsive': True})

    elif selected_menu == 'Availaibility Analysis':
        st.write('## Availability Details')
        tab1, tab2 = st.tabs(['Locations', 'Property Types'])
        with tab1:
            country = result_df['country'].unique()
            st.write('### Location')
            country_option = st.selectbox(
                "Select the country to view the availability...",
                country,
                index = None,
                placeholder = "Select one country",
                )
            if country_option is not None:
                gov_area = LoadGovernmentArea(result_df, country_option)
                gov_area_option = st.selectbox(
                    "Select the area to view the availability...",
                    gov_area,
                    index = None,
                    placeholder = "Select one area",
                    )
                if gov_area_option is not None:
                    season = {
                            '30 Days' : 'availability_30',
                            '60 Days' : 'availability_60',
                            '90 Days' : 'availability_90',
                            '1 Year' : 'availability_365'
                            }
                    avail_option = st.selectbox(
                        "Select the time period to view availability details",
                        season.keys(),
                        index = None,
                        placeholder = "Select any one",
                        )
                    if avail_option is not None and st.button('Apply', key = 'avail_loc'):
                        avail_location_season_agg = FilterGovernmentAreaAvail(result_df,
                                                                              country_option,
                                                                              gov_area_option,
                                                                              season[avail_option])
                        VisualizeAvailabilityBasedOnArea(avail_location_season_agg)
                        st.write('**Filtered Results**')
                        st.dataframe(avail_location_season_agg)

        with tab2:
            country = result_df['country'].unique()
            st.write('### Property Types')
            country_option = st.selectbox(
                "Select the country to view the availability...",
                country,
                index = None,
                placeholder = "Select one country",
                key = 'avail_prop1'
                )
            if country_option is not None:
                gov_area = LoadGovernmentArea(result_df, country_option)
                gov_area_option = st.selectbox(
                    "Select the area to view the availability...",
                    gov_area,
                    index = None,
                    placeholder = "Select one area",
                    key = 'avail_prop2'
                    )
                if gov_area_option is not None:
                    season = {
                            '30 Days' : 'availability_30',
                            '60 Days' : 'availability_60',
                            '90 Days' : 'availability_90',
                            '1 Year' : 'availability_365'
                            }
                    avail_option = st.selectbox(
                        "Select the time period to view availability details",
                        season.keys(),
                        index = None,
                        placeholder = "Select any one",
                        key = 'avail_prop3'
                        )
                    if avail_option is not None and st.button('Apply', key = 'avail_prop'):
                        avail_prop_type_agg = FilterPropertyTypeAvail(result_df,
                                                                      country_option,
                                                                      gov_area_option,
                                                                      season[avail_option])
                        st.plotly_chart(VisualizeAvailabilityBasedOnProperty\
                                        (avail_prop_type_agg,
                                        season[avail_option],
                                        avail_option),
                                        use_container_width = True, 
                                        config = {'responsive': True})
                    
if __name__ == "__main__":
    main()