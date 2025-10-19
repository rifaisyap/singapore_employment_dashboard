import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Singapore Employment Trends", layout="wide")


# Set a function for the first slide
def slide_intro():
    st.title("📊 Singapore Employment Trends (2000-2024)")
    st.divider()
    st.subheader("Prepared and presented by: Team B08")

    # Create two columns to show the team members' names
    column_1, column_2 = st.columns(2)
    with column_1:
        st.markdown("""
        - Du Yixuan
        - Lan Xiaolu
        - Nguyen Ngoc Thien Huong
        """)
    with column_2:
        st.markdown("""
        - Rifa Aisya Putri
        - Shen Wenquan
        - Zhao Hengjie
        """)
    
    st.info("Use the sidebar to navigate through the presentation slides.")

# Create function for overview slide
def slide_overview():
    st.header("Overview")

    # Load the data from the CSV files
    df = pd.read_csv("clean_data_combined.csv")
    df_io = pd.read_csv("Industry and Occupation.csv")
    df2 = pd.read_csv("salary.csv")
    
    # Get a list of all the year columns
    year_list_full = []
    for column_name in df.columns:
        if column_name.isdigit():
            year_list_full.append(int(column_name))
    year_list_full.sort() # sort the years from oldest to newest

    # Go through each year column 
    for year in year_list_full:
        column_name = str(year)
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        df[column_name] = df[column_name].fillna(0) 

    # Calculate the numbers for the summary cards
    st.divider()
    st.subheader(f"Key Highlights: {year_list_full[0]}-{year_list_full[-1]} Overview")
    
    # Set minimum and maximum year to get year range
    year_min = year_list_full[0]
    year_max = year_list_full[-1]
    
    # Define the latest year, the year before, and two years before
    latest_col = str(year_max)
    prev_col = str(year_list_full[-2])
    prev2_col = str(year_list_full[-3])

    # Get only the rows with "All" to get the grand totals calculation
    filtered_data = df[(df['Sex'] == 'All') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations')]

    # Get the total employment for each important year
    total_latest = filtered_data[latest_col].sum()
    total_prev = filtered_data[prev_col].sum()
    total_prev2 = filtered_data[prev2_col].sum()
    start_col = str(year_min)
    total_start = filtered_data[start_col].sum()
    
    # Calculate the growth percentage
    growth = 0
    if total_prev > 0:
        growth = ((total_latest - total_prev) / total_prev) * 100
        
    growth_prev = 0
    if total_prev2 > 0:
        growth_prev = ((total_prev - total_prev2) / total_prev2) * 100
        
    change = round(growth - growth_prev, 2)
    
    period_growth = 0
    if total_start > 0:
        period_growth = ((total_latest - total_start) / total_start) * 100

    # Calculate the numbers for male and female employment
    female_sum = df[(df["Sex"] == "Female") & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations')][latest_col].sum()
    male_sum = df[(df["Sex"] == "Male") & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations')][latest_col].sum()
    
    female_ratio = 0
    if (female_sum + male_sum) > 0:
        female_ratio = (female_sum / (female_sum + male_sum)) * 100

    # Create the 4 cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label=f"Total Growth ({year_min} to {year_max})", value=f"{period_growth:.2f}%")
    col1.caption(f"For the entire period")
        
    col2.metric(
        label=f"Total Employment ({latest_col}, in Thousands)",
        value=f"{float(total_latest):.1f}",
        delta=f"{growth:.2f}%")
    col2.caption(f"Year-over-year vs. {prev_col}")
        
    col3.metric(
        label=f"YoY Growth Rate ({latest_col})",
        value=f"{growth:.2f}%",
        delta=f"{change:.2f} pp")
    col3.caption(f"Growth momentum vs. {prev_col}")

    col4.metric(label=f"Female Employment ({latest_col})", value=f"{female_ratio:.1f}%")
    col4.caption(f"{female_sum:,.0f} Female / {male_sum:,.0f} Male")
    
    st.divider()

    # Crate the chart and the key insights
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Employment Trend by Gender")
        
        # Prepare the data ready for the line chart
        selected_year_cols = []
        for y in year_list_full:
            selected_year_cols.append(str(y))

        total_trend = df.loc[(df['Sex'] == 'All') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()
        male_trend = df.loc[(df['Sex'] == 'Male') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()
        female_trend = df.loc[(df['Sex'] == 'Female') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()

        # Create the chart figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=total_trend.index, y=total_trend.values, fill='tozeroy', mode='lines', line_color='rgba(100, 149, 237, 0.5)', name='Total'))
        # Add blue line for male employment
        fig.add_trace(go.Scatter(x=male_trend.index, y=male_trend.values, mode='lines', line_color='#6495ED', name='Male'))
        # Add pink line for female employment
        fig.add_trace(go.Scatter(x=female_trend.index, y=female_trend.values, mode='lines', line_color='#FF69B4', name='Female'))
        
        # Create the chart layout to add a title, etc.
        fig.update_layout(
            title="<b>Overall Employment Trend by Gender</b>",
            height=350, 
            margin=dict(l=20, r=20, t=60, b=20), 
            legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(f"Key Insights")
        
        # Create Insight 1: Find the top hiring industry
        st.markdown("🚀 **Top Hiring Industry**")
        io_filtered = df_io[(df_io['year'].isin([year_min, year_max])) & (~df_io['industry'].isin(["All Industries", "Services"]))]
        io_pivot = io_filtered.pivot_table(index='industry', columns='year', values='employment', aggfunc='sum')
        
        if year_min in io_pivot.columns and year_max in io_pivot.columns:
            io_pivot['growth'] = io_pivot[year_max] - io_pivot[year_min]
            top_hiring_industry = io_pivot['growth'].idxmax()
            top_hiring_value = io_pivot['growth'].max()
            st.markdown(f"##### {top_hiring_industry}") 
            # Write an insight for the shown chart
            st.markdown(f"""
            This industry has been a major driver of employment, creating around **{top_hiring_value:,.0f}k** new jobs between {year_min} and {year_max}. 
            It shows a great place to find career opportunities.
            """)

        st.markdown("---")

        # Create Insight 2: Find the highest paying occupation
        st.markdown("💰 **Highest Paying Occupation**")
        latest_sal_year = int(df2['year'].max())
        sal_latest = df2[(df2['year'] == latest_sal_year) & (df2['occupation'] != 'All Occupations')]
        
        if not sal_latest.empty:
            top_paying_occ = sal_latest.groupby('occupation')['value'].mean().idxmax()
            top_paying_val = sal_latest.groupby('occupation')['value'].mean().max()
            st.markdown(f"##### {top_paying_occ}")
            st.markdown(f"This industry offers one of the best salary, with an average salary of **S${top_paying_val:,.0f}/month** in {latest_sal_year}.")


# Create second slide for demographic analysis
def slide_demographics():
    st.header("Demographic Analysis")
    
    # Load data
    df = pd.read_csv("clean_data_combined.csv")

    # Get the full list of available years from the data
    year_list = [int(c) for c in df.columns if c.isdigit()]
    year_list.sort()
    year_min, year_max = year_list[0], year_list[-1]
    year_cols = [str(y) for y in year_list]
    latest_col = str(year_max)

    # Ensure all year columns are numeric
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Create tabs for each chart
    tab1, tab2, tab3 = st.tabs([
        "Trend by Gender", 
        "Distribution by Age (2024)", 
        "Trend by Age"])

    with tab1:
        # Create visualizatin fro Employment Trend by Gender
        st.subheader(f"Employment Trend by Gender ({year_min}–{year_max})")
        # Write the chart interpretation
        st.markdown("""
        * Employment in Singapore has been rising steadily for both male and female over the years.
        * The gap between male and female employment has become much smaller, showing that more female are taking part in the workforce.
        """)

        # Filter data for the chart
        gender_df = df[
            (df["Sex"].isin(["All", "Male", "Female"])) &
            (df["Occupation"] == "All Occupations") &
            (df["Age Group"] == "All Ages")
        ]
        
        # Prepare data for plotting
        gender_melt = gender_df.melt(id_vars=["Sex"], value_vars=year_cols, var_name="Year", value_name="Employment")
        gender_melt["Year"] = gender_melt["Year"].astype(int)
        gender_melt['Sex'] = gender_melt['Sex'].replace({'All': 'Total'})

        # Create the line/area chart
        fig_area = px.line(
            gender_melt, x="Year", y="Employment", color="Sex", markers=False,
            category_orders={"Sex": ["Total", "Male", "Female"]},
            color_discrete_map={'Total': 'lightskyblue', 'Male': 'blue', 'Female': 'hotpink'})
        
        # Make the 'Total' with filled area
        fig_area.update_traces(selector={'name': 'Total'}, fill='tozeroy')
        st.plotly_chart(fig_area, use_container_width=True)

    with tab2:
        # Create Employment by Age Group chart
        st.subheader(f"Employment by Age Group ({year_max})")
        # Write chart interpretation
        st.markdown(f"""
        * The chart shows that most jobs in Singapore are in aged 30 to 54, reflecting the stage where employees are skilled and experienced. This indicates that investing in education and skill development early can help students build a strong foundation for long-term career growth.
        * Employment starts to rise sharply after age 25, indicating that the early 20s are a critical transition phase from education to full-time work.
        """)

        # Create Age Filter to get the total employment for each age group
        age_filtered = df[
            (df["Age Group"] != "All Ages") &
            (df["Sex"] == "All") &
            (df["Occupation"] == "All Occupations")
        ]
        # Use the filtered data without summing
        age_snapshot = age_filtered[['Age Group', latest_col]].copy()
        age_snapshot.columns = ['Age Group', 'Employment Count']

        # Set an order for the age groups
        age_order = [
            "15-19 Years Old", "20-24 Years Old", "25-29 Years Old", 
            "30-34 Years Old", "35-39 Years Old", "40-44 Years Old",
            "45-49 Years Old", "50-54 Years Old", "55-59 Years Old",
            "60-64 Years Old", "65 Years & Over"]
        age_snapshot['Age Group'] = pd.Categorical(age_snapshot['Age Group'], categories=age_order, ordered=True)
        age_snapshot = age_snapshot.sort_values('Age Group')

        # Create the bar chart
        fig_bar = px.bar(age_snapshot, x='Age Group', y='Employment Count', 
                         color='Age Group', text_auto='.2s')
        fig_bar.update_traces(textposition='outside', cliponaxis=False)
        fig_bar.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        # Create Employment Trends by Age Group with Line Chart
        st.subheader(f"Employment Trends by Age Group ({year_min}–{year_max})")
        # Write chart interpretation
        st.markdown("""
        * Employment among those aged 15-24 has grown slowly and remains low over the years, highlighting the importance of continuous learning and skill-building to stay competitive when entering the workforce.
        * Stable employment in the 30-54 age range shows that most careers peak in these years. Students should build strong skills and experience early to achieve long-term career growth.
        """)
        
        # Create Age Filter to get the total employment trend for each age group
        age_filtered_line = df[
            (df["Age Group"] != "All Ages") &
            (df["Sex"] == "All") &
            (df["Occupation"] == "All Occupations")
        ]
        # Create the new data without summing
        age_trend_data = age_filtered_line.set_index("Age Group")[year_cols].T
        age_trend_data.index = age_trend_data.index.astype(int)
        
        # Create the line chart
        fig_line = px.line(age_trend_data, x=age_trend_data.index, y=age_trend_data.columns, markers=True)
        fig_line.update_layout(
            xaxis_title="Year", 
            yaxis_title="Total Employment (in Thousands)", 
            legend_title_text='Age Group',
            height=500
        )
        st.plotly_chart(fig_line, use_container_width=True)

# Empty slide
def slide_B():
    st.header("Occupation Performance")
    st.info("Content for this slide can be added here.")

def slide_C():
    st.header("Salary Analysis")
    st.info("Content for this slide can be added here.")

def slide_D():
    st.header("Further Insights")
    st.info("Content for this slide can be added here.")

def slide_summary():
    st.header("Summary & Conclusion")
    st.info("Content for this slide can be added here.")


# Set list of all our slides
SLIDES = [
    ("Introduction", slide_intro),
    ("Data Overview", slide_overview),
    ("Demographic Analysis", slide_demographics), # <-- UPDATED SLIDE
    ("Occupation Performance", slide_B),
    ("Salary Analysis", slide_C),
    ("Further Insights", slide_D),
    ("Summary", slide_summary),
]

# Keep track of which slide we are on to present
if "idx" not in st.session_state:
    st.session_state.idx = 0

# Make the sidebar for navigation
with st.sidebar:
    st.header("Presentation Slides")
    
    # Get the names of the slides for the radio buttons
    labels = [name for name, func in SLIDES]
    
    # Function to update the slide when a radio button is clicked
    def update_index_from_radio():
        st.session_state.idx = labels.index(st.session_state.idx_radio)

    # Create the radio buttons
    st.radio(
        "Go to slide",
        labels,
        index=st.session_state.idx,
        key="idx_radio",
        on_change=update_index_from_radio,
    )

    st.markdown("---")
    
    # Functions for the next and previous buttons
    def go_prev():
        if st.session_state.idx > 0:
            st.session_state.idx -= 1

    def go_next():
        if st.session_state.idx < len(SLIDES) - 1:
            st.session_state.idx += 1
    
    # Create the next and previous buttons
    prev_col, next_col = st.columns(2)
    prev_col.button("◀ Prev", use_container_width=True, on_click=go_prev, disabled=(st.session_state.idx == 0))
    next_col.button("Next ▶", use_container_width=True, on_click=go_next, disabled=(st.session_state.idx == len(SLIDES) - 1))


# Get the function for the current slide and run it to show the content
slide_name, render_fn = SLIDES[st.session_state.idx]
render_fn()