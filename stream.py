import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Redbus Availability Checker", layout="wide")

st.markdown(
    """
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Arial', sans-serif;
            color: #212529;
        }
        .main {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #007bff;
            font-size: 3rem;
            text-align: center;
            font-family: 'Georgia', serif;
        }
        h3 {
            color: #6c757d;
            text-align: center;
            font-size: 1.5rem;
        }
        .stButton button {
            background-color: #007bff !important;
            color: white !important;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1rem;
        }
        .sidebar .stRadio > label {
            font-size: 1rem;
            font-weight: bold;
            color: #495057;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Page Header
st.markdown("<h1>Redbus - Bus Availability Checker</h1>", unsafe_allow_html=True)
st.markdown("<h3>Find your ideal bus with ease and comfort!</h3>", unsafe_allow_html=True)

conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Update with your database password
            database= 'redbus_data'  # Update with your database name
        )
cursor = conn.cursor()

cursor.execute("SELECT * FROM busdetail")
data = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
table = pd.DataFrame(data, columns=columns)
#st.table(table.head())
table['seats_available'] = pd.to_numeric(table['seats_available'], errors='coerce', downcast='integer')
table['star_rating'] = table['star_rating'].astype(float).round(0).astype('Int64')
table['price'] = table['price'].astype(float).round(0).astype('Int64')  # Remove decimal in price
table['duration'] = table['duration'].str.replace(r'(\d)(?=\D)', r'\1 ', regex=True)  # Format duration

        # State selection
statelist = table["state"].unique().tolist()
statelist = ["Choose your state"] + statelist
selected_state = st.selectbox("Select Your State", statelist)

if selected_state != "Choose your state":
            # Route selection
            routes = table[table["state"] == selected_state]["route_name"].unique().tolist()
            route_selected = st.selectbox("Select Your Route", ["Choose your desired route"] + routes)
            
            if route_selected != "Choose your desired route":
                st.sidebar.markdown("<h3 style='color: maroon;'>Filter Options</h3>", unsafe_allow_html=True)
                
                rating = st.sidebar.radio(
                    "Star Rating",
                    options=[5, 4, 3, 2, 1],
                    format_func=lambda x: "⭐" * x,
                    horizontal=True
                )
                
                max_price = st.sidebar.slider("Max Ticket Price (INR)", 100, 10000, step=100, value=5000)
                
                seats = st.sidebar.number_input("Seats Required", min_value=1, max_value=57, value=1)
               

                # Filter buses based on user input
                filtered_buses = table[
                    (table["route_name"] == route_selected) &
                    (table["star_rating"] >= rating) &
                    (table["price"] <= max_price) &
                    (table["seats_available"] >= seats)
                ]
                
                if not filtered_buses.empty:
                    # Show available buses
                    bus_names = filtered_buses["busname"].unique().tolist()
                    bus_selected = st.radio("Available Buses", bus_names)

                    if bus_selected:
                        # Show details of the selected bus
                        if st.button(f"Show {bus_selected} Bus Details"):
                            bus_details = filtered_buses[filtered_buses["busname"] == bus_selected][
                                ["bustype", "departing_time", "duration", "star_rating", "price","reaching_time", "seats_available"]
                            ]
                            st.markdown("<h3>Bus Details:</h3>", unsafe_allow_html=True)
                            st.table(bus_details)
                else:
                    st.warning("No buses found for the selected filters. Please try adjusting the filters.")