import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Flight Delay Intelligence Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1D9E75;
    }
    .subtitle {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def get_engine():
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=300)
def load_flight_data():
    """Load data from warehouse"""
    engine = get_engine()
    query = """
        SELECT 
            flight_date,
            airline_code,
            airline_name,
            origin_airport,
            destination_airport,
            flight_type,
            route,
            departure_delay,
            arrival_delay,
            delay_category,
            is_delayed,
            time_of_day,
            day_of_week,
            is_weekend,
            flight_status,
            is_monsoon_season
        FROM warehouse_warehouse.fact_flights
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_summary_stats():
    """Load summary statistics"""
    engine = get_engine()
    query = """
        SELECT 
            COUNT(*) as total_flights,
            SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) as delayed_flights,
            SUM(CASE WHEN flight_status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_flights,
            ROUND(AVG(arrival_delay)::numeric, 2) as avg_delay_mins,
            ROUND(100.0 * SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) / COUNT(*), 2) as delay_rate,
            SUM(CASE WHEN flight_type = 'domestic' THEN 1 ELSE 0 END) as domestic_flights,
            SUM(CASE WHEN flight_type = 'international' THEN 1 ELSE 0 END) as international_flights
        FROM warehouse_warehouse.fact_flights
    """
    return pd.read_sql(query, engine).iloc[0]

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Overview",
    "Airline Analysis",
    "Route Analysis",
    "Trends & Insights",
    "Delay Predictor"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Data refreshes every 5 mins**")
st.sidebar.markdown("Rolling 60-day window")

# ══════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════
if page == "Overview":
    st.markdown('<p class="main-title">✈️ Flight Delay Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Real-time insights from live flight data — Indian domestic & international routes</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Load data
    stats = load_summary_stats()
    df = load_flight_data()

    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Flights", f"{int(stats['total_flights']):,}")
    with col2:
        st.metric("Delayed Flights", f"{int(stats['delayed_flights']):,}")
    with col3:
        st.metric("Cancelled Flights", f"{int(stats['cancelled_flights']):,}")
    with col4:
        st.metric("Avg Delay", f"{float(stats['avg_delay_mins'])} mins")
    with col5:
        st.metric("Delay Rate", f"{float(stats['delay_rate'])}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Domestic vs International")
        fig = px.pie(
            values=[stats['domestic_flights'], stats['international_flights']],
            names=['Domestic', 'International'],
            color_discrete_sequence=['#1D9E75', '#085041']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Delay Categories")
        delay_counts = df['delay_category'].value_counts().reset_index()
        delay_counts.columns = ['category', 'count']
        fig = px.bar(
            delay_counts,
            x='category',
            y='count',
            color='category',
            color_discrete_sequence=['#1D9E75', '#FAC775', '#F0997B', '#E24B4A']
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Flight Status Breakdown")
    status_counts = df['flight_status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    fig = px.bar(
        status_counts,
        x='status',
        y='count',
        color='status',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════
# PAGE 2: AIRLINE ANALYSIS
# ══════════════════════════════════
elif page == "Airline Analysis":
    st.title("Airline Performance Analysis")
    st.markdown("---")

    df = load_flight_data()

    airline_stats = df.groupby(['airline_name', 'flight_type']).agg(
        total_flights=('flight_status', 'count'),
        delayed_flights=('is_delayed', 'sum'),
        avg_delay=('arrival_delay', 'mean')
    ).reset_index()
    airline_stats['delay_rate'] = round(
        100 * airline_stats['delayed_flights'] / airline_stats['total_flights'], 2
    )
    airline_stats['avg_delay'] = round(airline_stats['avg_delay'], 2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Airlines by Delay Rate")
        top_delayed = airline_stats.sort_values('delay_rate', ascending=False).head(10)
        fig = px.bar(
            top_delayed,
            x='delay_rate',
            y='airline_name',
            orientation='h',
            color='flight_type',
            color_discrete_map={'domestic': '#1D9E75', 'international': '#085041'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Delay by Airline (mins)")
        top_avg = airline_stats.sort_values('avg_delay', ascending=False).head(10)
        fig = px.bar(
            top_avg,
            x='avg_delay',
            y='airline_name',
            orientation='h',
            color='flight_type',
            color_discrete_map={'domestic': '#1D9E75', 'international': '#085041'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Airline Performance Table")
    st.dataframe(
        airline_stats[['airline_name', 'flight_type', 'total_flights',
                       'delayed_flights', 'delay_rate', 'avg_delay']]
        .sort_values('delay_rate', ascending=False),
        use_container_width=True
    )

# ══════════════════════════════════
# PAGE 3: ROUTE ANALYSIS
# ══════════════════════════════════
elif page == "Route Analysis":
    st.title("Route Performance Analysis")
    st.markdown("---")

    df = load_flight_data()

    route_stats = df.groupby(['route', 'flight_type']).agg(
        total_flights=('flight_status', 'count'),
        delayed_flights=('is_delayed', 'sum'),
        avg_delay=('arrival_delay', 'mean')
    ).reset_index()
    route_stats['delay_rate'] = round(
        100 * route_stats['delayed_flights'] / route_stats['total_flights'], 2
    )
    route_stats['avg_delay'] = round(route_stats['avg_delay'], 2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Delayed Routes")
        top_routes = route_stats.sort_values('avg_delay', ascending=False).head(10)
        fig = px.bar(
            top_routes,
            x='avg_delay',
            y='route',
            orientation='h',
            color='flight_type',
            color_discrete_map={'domestic': '#1D9E75', 'international': '#085041'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Routes by Delay Rate %")
        route_stats['avg_delay_size'] = route_stats['avg_delay'].clip(lower=1)
        fig = px.scatter(
            route_stats,
            x='total_flights',
            y='delay_rate',
            size='avg_delay_size',
            color='flight_type',
            hover_name='route',
            color_discrete_map={'domestic': '#1D9E75', 'international': '#085041'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Route Performance Table")
    st.dataframe(
        route_stats.sort_values('avg_delay', ascending=False),
        use_container_width=True
    )

# ══════════════════════════════════
# PAGE 4: DELAY PREDICTOR
# ══════════════════════════════════
elif page == "Delay Predictor":
    st.title("Flight Delay Predictor")
    st.markdown("Will your flight be delayed? Find out below.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        airline_code = st.selectbox("Airline", [
            "AI", "6E", "SG", "G8", "UK",
            "EK", "QR", "SQ", "BA", "LH", "AF"
        ])
        origin = st.selectbox("Origin Airport", [
            "BOM", "DEL", "BLR", "HYD", "MAA",
            "CCU", "GOI", "AMD"
        ])
        destination = st.selectbox("Destination Airport", [
            "DEL", "BOM", "BLR", "HYD", "MAA",
            "CCU", "DXB", "SIN", "LHR", "JFK", "BKK"
        ])
        flight_type = st.selectbox("Flight Type", ["domestic", "international"])

    with col2:
        departure_hour = st.slider("Departure Hour", 0, 23, 8)
        day_of_week = st.selectbox("Day of Week", [
            0, 1, 2, 3, 4, 5, 6
        ], format_func=lambda x: [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ][x])
        is_weekend = st.checkbox("Weekend Flight")
        is_monsoon = st.checkbox("Monsoon Season (Jun-Sep)")
        avg_route_delay = st.number_input("Avg Route Delay (mins)", 0.0, 200.0, 6.0)
        avg_carrier_delay = st.number_input("Avg Carrier Delay (mins)", 0.0, 200.0, 7.6)

    st.markdown("---")

    if st.button("Predict Delay", type="primary"):
        payload = {
            "airline_code": airline_code,
            "origin_airport": origin,
            "destination_airport": destination,
            "flight_type": flight_type,
            "departure_hour": departure_hour,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "is_monsoon_season": is_monsoon,
            "avg_route_delay": avg_route_delay,
            "avg_carrier_delay": avg_carrier_delay
        }

        try:
            response = requests.post(f"{API_URL}/predict", json=payload)
            result = response.json()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Flight", result['flight'])
            with col2:
                st.metric("Delay Probability", f"{result['delay_probability']*100:.1f}%")
            with col3:
                st.metric("Risk Level", result['risk_level'].upper())

            if result['is_delayed']:
                st.error(f"⚠️ {result['message']}")
            else:
                st.success(f"✅ {result['message']}")

        except Exception as e:
            st.error(f"API Error: Make sure the FastAPI server is running. {e}")

# ══════════════════════════════════
# PAGE 5: TRENDS & INSIGHTS
# ══════════════════════════════════
elif page == "Trends & Insights":
    st.title("Trends & Insights")
    st.markdown("---")

    df = load_flight_data()

    # ── Delay Rate Over Time ──
    st.subheader("📈 Delay Rate Over Time")
    daily_stats = df.groupby('flight_date').agg(
        total_flights=('flight_status', 'count'),
        delayed_flights=('is_delayed', 'sum')
    ).reset_index()
    daily_stats['delay_rate'] = round(
        100 * daily_stats['delayed_flights'] / daily_stats['total_flights'], 2
    )
    fig = px.line(
        daily_stats,
        x='flight_date',
        y='delay_rate',
        title='Daily Delay Rate (%)',
        color_discrete_sequence=['#1D9E75']
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    # ── Time of Day Analysis ──
    with col1:
        st.subheader("🕐 Delays by Time of Day")
        tod_stats = df.groupby('time_of_day').agg(
            total_flights=('flight_status', 'count'),
            delayed_flights=('is_delayed', 'sum')
        ).reset_index()
        tod_stats['delay_rate'] = round(
            100 * tod_stats['delayed_flights'] / tod_stats['total_flights'], 2
        )
        tod_order = ['morning', 'afternoon', 'evening', 'night']
        tod_stats['time_of_day'] = pd.Categorical(
            tod_stats['time_of_day'], categories=tod_order, ordered=True
        )
        tod_stats = tod_stats.sort_values('time_of_day')
        fig = px.bar(
            tod_stats,
            x='time_of_day',
            y='delay_rate',
            color='time_of_day',
            color_discrete_sequence=['#FAC775', '#F0997B', '#E24B4A', '#085041']
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Day of Week Analysis ──
    with col2:
        st.subheader("📅 Delays by Day of Week")
        dow_stats = df.groupby('day_of_week').agg(
            total_flights=('flight_status', 'count'),
            delayed_flights=('is_delayed', 'sum')
        ).reset_index()
        dow_stats['delay_rate'] = round(
            100 * dow_stats['delayed_flights'] / dow_stats['total_flights'], 2
        )
        dow_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        dow_stats['day_name'] = dow_stats['day_of_week'].map(dow_map)
        fig = px.bar(
            dow_stats,
            x='day_name',
            y='delay_rate',
            color='day_name',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Monsoon vs Non-Monsoon ──
    st.subheader("🌧️ Monsoon vs Non-Monsoon Delay Rate")
    monsoon_stats = df.groupby('is_monsoon_season').agg(
        total_flights=('flight_status', 'count'),
        delayed_flights=('is_delayed', 'sum'),
        avg_delay=('arrival_delay', 'mean')
    ).reset_index()
    monsoon_stats['delay_rate'] = round(
        100 * monsoon_stats['delayed_flights'] / monsoon_stats['total_flights'], 2
    )
    monsoon_stats['season'] = monsoon_stats['is_monsoon_season'].map(
        {True: 'Monsoon', False: 'Non-Monsoon'}
    )
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            monsoon_stats,
            x='season',
            y='delay_rate',
            color='season',
            color_discrete_sequence=['#1D9E75', '#085041']
        )
        fig.update_layout(height=300, showlegend=False, title='Delay Rate %')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(
            monsoon_stats,
            x='season',
            y='avg_delay',
            color='season',
            color_discrete_sequence=['#FAC775', '#F0997B']
        )
        fig.update_layout(height=300, showlegend=False, title='Avg Delay (mins)')
        st.plotly_chart(fig, use_container_width=True)