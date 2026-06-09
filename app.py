import streamlit as st
import pandas as pd
import plotly.express as px

# title and styling
st.set_page_config(
    page_title="Global COVID-19 Analytics",
    page_icon="🌍",
    layout="wide"
)

#dark-mode dashboard
st.markdown("""
<style>

/* Main App Background */
.stApp { 
    background: linear-gradient(135deg, #0f172a, #1e293b, #334155); 
}

/* Text Colors */
h1, h2, h3, p, label, div, span {
    color: white !important;
}
            
/* Sidebar Background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a) !important;
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #of172a !important;
    color: white !important;
    border-radius: 8px;
}

/* Dropdown menu */
div[role="listbox"] {
    background_color: #of172a !important;
    color: white !important;
}

div[role="option"]:hover {
    background-color: #1e293b !important;
    color: white !important;
}

/* Radio Buttons */
div[role="radiogroup"] label {
    color: black !important;
}

/* Download Button */
.stDownloadButton button {
    background-color: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

/* Normal Buttons */
.stButton button {
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* DataFrame */
[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.03);
    border-radius: 10px;
}

/* Expander */
.streamlit-expanderHeader {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

st.title("🌍 Global COVID-19 Analytical Dashboard")
st.markdown("A simple dashboard to explore COVID-19 data, compare countries, and see global trends.")

# 2. LOAD AND PREPARE DATA
# We use @st.cache_data so the app doesn't download the file every single time you click a button
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/latest/owid-covid-latest.csv"
    data = pd.read_csv(url)
    clean_data = data.dropna(subset=['continent'])
    
    # Calculate some extra helpful percentages manually
    clean_data['vaccination_rate'] = (clean_data['people_vaccinated'] / clean_data['population']) * 100
    clean_data['death_rate'] = (clean_data['total_deaths'] / clean_data['total_cases']) * 100
    
    return clean_data

df = load_data()

# Get a sorted list of all country names to use in our dropdown menus
country_list = df["location"].dropna().unique()
countries = sorted(country_list)

# 3. SIDEBAR (USER INPUTS)
st.sidebar.header("Control Panel")

# Create dropdown menus for the user to select countries
selected_country = st.sidebar.selectbox("Analyze Primary Country", countries, index=countries.index("India"))
country2 = st.sidebar.selectbox("Compare Against", countries, index=countries.index("United States"))

# Create a radio button to let the user choose what the map should show
metric_choice = st.sidebar.radio(
    "Choose Map Metric", 
    ["total_cases_per_million", "total_deaths_per_million", "vaccination_rate"]
)

# Extract just the data for the two countries the user selected
data_country_1 = df[df["location"] == selected_country].iloc[0] # iloc[0] gets the first (and only) row
data_country_2 = df[df["location"] == country2].iloc[0]

# 4. GLOBAL SUMMARY (TOP SECTION)
st.subheader("🌎 Global Executive Summary")

# Calculate global totals from the entire dataframe
total_countries = len(df)
total_global_cases = df['total_cases'].sum()
total_global_deaths = df['total_deaths'].sum()

# Calculate global vaccination rate
total_vaccinated_people = df['people_vaccinated'].sum()
total_global_population = df['population'].sum()
global_vax_rate = (total_vaccinated_people / total_global_population) * 100

# Display the totals in 4 columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Countries Tracked", total_countries)
col2.metric("Total Global Cases", f"{int(total_global_cases):,}")
col3.metric("Total Global Deaths", f"{int(total_global_deaths):,}")
col4.metric("Global Vax Rate", f"{global_vax_rate:.1f}%")

st.divider() # Adds a nice horizontal line

# 5. DASHBOARD TABS
# Create three tabs to organize our charts and data
tab1, tab2, tab3 = st.tabs(["🗺️ Global Map & Trends", "📊 Country Details", "⚖️ Compare Countries"])

#TAB 1: MAPS AND SCATTER PLOTS
with tab1:
    st.subheader("Global Heatmap")
    
    # Create a Choropleth (color-coded) map
    fig_map = px.choropleth(
        df, 
        locations="iso_code", # This code tells the map where the country is
        color=metric_choice,  # Colors based on what the user picked in the sidebar
        hover_name="location", # Shows country name when you hover
        title=f"Global Map: {metric_choice}"
    )
    # Make the map background transparent so it looks good on dark mode
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Does Wealth Affect Vaccination?")
    # Create a scatter plot comparing Money (GDP) vs Vaccinations
    # Drop rows that are missing GDP or Vaccination data so the chart doesn't break
    scatter_data = df.dropna(subset=['gdp_per_capita', 'vaccination_rate'])
    
    fig_scatter = px.scatter(
        scatter_data,
        x="gdp_per_capita", 
        y="vaccination_rate",
        size="population",     # Make bubbles bigger for countries with more people
        color="continent",     # Color the bubbles by continent
        hover_name="location",
        log_x=True,            # Squish the money axis so rich and poor countries both fit nicely
        title="GDP per Capita vs. Vaccination Rate"
    )
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 2: SPECIFIC COUNTRY DETAILS
with tab2:
    st.subheader(f"Details for {selected_country}")
    
    # Show basic stats in 3 columns
    c1, c2, c3 = st.columns(3)
    c1.metric("Population", f"{int(data_country_1['population']):,}")
    c2.metric("Total Cases", f"{int(data_country_1['total_cases']):,}")
    c3.metric("Total Deaths", f"{int(data_country_1['total_deaths']):,}")
    
    # Show rates in another 3 columns
    c4, c5, c6 = st.columns(3)
    c4.metric("Cases per Million People", f"{data_country_1['total_cases_per_million']:,.0f}")
    
    # Use simple if/else to handle missing data for death rate
    if pd.notna(data_country_1['death_rate']):
        c5.metric("Case Fatality Rate", f"{data_country_1['death_rate']:.2f}%")
    else:
        c5.metric("Case Fatality Rate", "No Data")
        
    # Use simple if/else to handle missing data for vaccination rate
    if pd.notna(data_country_1['vaccination_rate']):
        c6.metric("Vaccination Rate", f"{data_country_1['vaccination_rate']:.1f}%")
    else:
        c6.metric("Vaccination Rate", "No Data")

    st.markdown("### Top 10 Most Impacted Countries")
    # Get the top 10 countries with the most cases per million
    top_10 = df.nlargest(10, 'total_cases_per_million')
    
    #bar chart
    fig_bar = px.bar(
        top_10, 
        x="location", 
        y="total_cases_per_million", 
        color="total_cases_per_million",
        title="Highest Cases Per Million People"
    )
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

# TAB 3: COUNTRY COMPARISON 
with tab3:
    st.subheader(f"Comparing {selected_country} vs {country2}")
    st.markdown("Comparing raw totals is unfair because populations are different sizes. Here is the impact **per one million people**.")
    
    # Filter the dataset to ONLY include the two selected countries
    comparison_dataset = df[df['location'].isin([selected_country, country2])]
    
    # Plotly makes it easy to compare two columns side-by-side using barmode="group"
    fig_comp = px.bar(
        comparison_dataset, 
        x="location", 
        y=["total_cases_per_million", "total_deaths_per_million"], # The two things we want to compare
        barmode="group",
        title="Cases and Deaths per Million People"
    )
    fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

# 6. RAW DATA & DOWNLOAD
st.divider()

# Put the raw data table inside a dropdown expander so it doesn't clutter the screen
with st.expander("Click here to view the raw data table"):
    st.dataframe(df, use_container_width=True)
# file download
csv_data = df.to_csv(index=False)
st.download_button(
    label="Download Data (CSV)",
    data=csv_data,
    file_name="covid_data.csv",
    mime="text/csv"
)
