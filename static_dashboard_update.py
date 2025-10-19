# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Setup
st.set_page_config(page_title="Singapore Employment Trends", layout="wide")


# Content Setup
def slide_intro():
    st.title("📊 Singapore Employment Trends (2000-2024)")
    st.markdown("""
> **Explore Singapore's employment trends (2000-2024)** across industries, education levels, and demographics  
> to uncover which career paths offer the most promising and resilient prospects for students.
""")
    st.caption("Data Source: SingStat")
    st.divider()
    st.subheader("Prepared and presented by: Team B08")

    # Make two columns to show the team members' names
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

def slide_overview():
    st.header("Overview")
    # Load the data from the CSV files
    df = pd.read_csv("occupation_age.csv")
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
            st.markdown(f"This Occupation offers one of the best salary, with an average salary of **S${top_paying_val:,.0f}/month** in {latest_sal_year}.")


# Create second slide for demographic analysis
def slide_demographics():
    st.header("Demographic Analysis")
    
    # Load data
    df = pd.read_csv("occupation_age.csv")

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
def slide_A():
    st.header("Industry Performance")
    df = pd.read_csv("employment_by occupation & industry.csv")
# Page Setup
    st.set_page_config(page_title="Industry Dashboard Slides", layout="wide")


    tab1, tab2, tab3 = st.tabs([
        "Hiring volume by Industry", 
        "Trend by industry", 
        "Occupation percentage by industry"])
    with tab1:
       df["year"] = pd.to_numeric(df["year"], errors="coerce")
       df["employment"] = pd.to_numeric(df["employment"], errors="coerce")
       df = df.dropna(subset=["year", "employment"])
       latest_year = int(df["year"].max())
    # Set the page layout
       left, mid, right = st.columns([1, 0.5, 5])
       drop_inds = ["All Industries", "Services"]
       d = df[(df["year"] == latest_year) & (~df["industry"].isin(drop_inds))]
       by_industry = (d.groupby("industry", as_index=False)["employment"]
                     .sum()
                     .sort_values("employment", ascending=False))

       fig = px.bar(by_industry, x="industry", y="employment",
                 template="plotly_dark", text="employment",
                 title=f"Hiring Volume by Industry — {latest_year}")
       fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
       fig.update_layout(xaxis_title="", yaxis_title="Employment (thousands)",
                      xaxis=dict(tickangle=-65), showlegend=False,
                      margin=dict(l=40, r=40, t=60, b=80))
       st.plotly_chart(fig, use_container_width=True)
       
       with tab2:
         drop_inds = ["All Industries", "Services"]
         d1 = df[(df["year"] == latest_year) & (~df["industry"].isin(drop_inds))]
         by_industry = (d1.groupby("industry", as_index=False)["employment"]
                     .sum()
                     .sort_values("employment", ascending=False))
         top_inds = by_industry["industry"].head(8).tolist()

         d2 = df[df["industry"].isin(top_inds)]
         trends = d2.groupby(["industry", "year"], as_index=False)["employment"].sum()

         fig = px.line(trends, x="year", y="employment", color="industry",
                  markers=True, template="plotly_dark",
                  title=f"Employment Trends by Industry (2000–{latest_year})")
         fig.update_layout(xaxis_title="Year", yaxis_title="Total Employment",
                      legend_title_text="Industry",
                      legend=dict(orientation="v", y=0.5, x=1.02),
                      margin=dict(l=40, r=160, t=60, b=40))
         fig.update_yaxes(tickformat=",")
         st.plotly_chart(fig, use_container_width=True)

       with tab3:
            d = df[df["year"] == latest_year].copy()
            drop_occs = [
        "All Occupation Groups",
        "All Occupation Groups Nes",
        "All Occupation Groups, (Total Employed Residents)",
        "All Occupation Groups (Total Employed Residents)",
        "All Occupation Groups, Total Employed Residents"
    ]
            d = d[~d["occupation"].isin(drop_occs)]

            io = d.groupby(["industry", "occupation"], as_index=False)["employment"].sum()
            io["total"] = io.groupby("industry")["employment"].transform("sum")
            io["share"] = io["employment"] / io["total"]

            d1 = df[(df["year"] == latest_year) & (~df["industry"].isin(["All Industries", "Services"]))]
            order_inds = (d1.groupby("industry")["employment"].sum()
                    .sort_values(ascending=False).index.tolist())

            fig = px.bar(io, x="industry", y="share", color="occupation",
                 barmode="stack", template="plotly_dark",
                 category_orders={"industry": order_inds},
                 text="share",
                 title=f"Occupation Percentage by Industry — {latest_year}")
            fig.update_traces(texttemplate="%{text:.0%}", textposition="inside", textfont_size=12)
            fig.update_layout(height=900, margin=dict(l=70, r=260, t=80, b=200),
                      xaxis_title="Industry", yaxis_title="Share of employment",
                      legend=dict(orientation="v", y=1.0, x=1.02))
            fig.update_xaxes(tickangle=-45, tickfont=dict(size=11))
            fig.update_yaxes(range=[0, 1], tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
    

def slide_B():
    st.header("Occupation Performance")
    st.set_page_config(page_title="Singapore Hiring Insights", layout="wide")
    st.title("Singapore Occupations Trends Dashboard (2000–2024)")
    st.caption("Employed Residents Aged 15 Years And Over By Occupation And Age Group, (June)")
    st.divider()

    # Read data
    df = pd.read_csv("occupation_age.csv")

    # Detect year columns and FORCE numeric
    year_cols = [c for c in df.columns if c.isdigit()]
    for c in year_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")  

    latest_year = max(year_cols)
    start_year, end_year = "2020", "2024"

    # Employment Trend (Overall + By Gender)
    st.markdown("### Employment Trends Overview")
    st.caption("Overall employment and gender-specific employment trends from 2000 to 2024.")

    # Filter 'All Occupations'
    trend_df = df[
        (df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages")
    ].copy()

    # Keep only All, Male, Female
    trend_df = trend_df[trend_df["Sex"].isin(["All", "Male", "Female"])]

    # Melt data
    trend_melt = trend_df.melt(
        id_vars=["Sex"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Employment"
    )
    trend_melt["Year"] = trend_melt["Year"].astype(int)
    trend_melt["Employment"] = pd.to_numeric(trend_melt["Employment"], errors="coerce")

    # Calculate Growth % (2000 → 2024)
    growth_summary = []
    for sex in ["All", "Female", "Male"]:
        subset = trend_melt[trend_melt["Sex"] == sex]
        val_2000 = subset.loc[subset["Year"] == 2000, "Employment"].values[0]
        val_2024 = subset.loc[subset["Year"] == 2024, "Employment"].values[0]
        growth = ((val_2024 - val_2000) / val_2000) * 100
        growth_summary.append({"Sex": sex, "Growth %": growth})

    growth_df = pd.DataFrame(growth_summary)
    
    tab1, tab2, tab3,tab4 = st.tabs([
        "Trend by Occupation", 
        "Top 5 growing and declining occupations",
        "Gender Distribution by Occupation", 
        "Age × Gender × Occupation Distribution"])
    

    with tab1:
       # Employment Trend by Occupation
       st.header(" Employment Trend by Occupation")
       occ_df = df[
        (~df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()

       occ_melt = occ_df.melt(id_vars=["Occupation"], value_vars=year_cols,
                           var_name="Year", value_name="Employment")
       occ_melt["Year"] = occ_melt["Year"].astype(int)
       occ_melt["Employment"] = pd.to_numeric(occ_melt["Employment"], errors="coerce")

       fig = px.line(occ_melt, x="Year", y="Employment", color="Occupation",
                  title="Employment Trend by Occupation", markers=True,
                  labels={"Employment": "Employed Persons (thousands)", "Year": "Year"})
       st.plotly_chart(fig, use_container_width=True)

    with tab2:
       # Top 4 Growing / Declining Occupations (2020–2024)
       st.markdown("### Top 5 Growing & Declining Occupations (2020–2024)")
       st.caption("Occupational groups with the highest and lowest employment growth between 2020 and 2024.")

    # Prepare growth data
       growth_df = occ_df.copy()
       growth_df[start_year] = pd.to_numeric(growth_df[start_year], errors="coerce")
       growth_df[end_year] = pd.to_numeric(growth_df[end_year], errors="coerce")
       growth_df["Growth %"] = ((growth_df[end_year] - growth_df[start_year]) / growth_df[start_year]) * 100
       growth_df["Growth_label"] = growth_df["Growth %"].round(1).astype(str) + "%"

    # Select top 4 groups
       top_grow = growth_df.sort_values("Growth %", ascending=False).head(5)
       top_decl = growth_df.sort_values("Growth %", ascending=True).head(5)

    # Color scheme (consistent with dashboard)
       grow_colors = ["#004C99", "#4DB8FF", "#FF4D4D", "#FF9999"]
       decl_colors = ["#004C99", "#4DB8FF", "#FF4D4D", "#FF9999"]

       col1, col2 = st.columns(2)

       with col1:
         fig1 = px.bar(
            top_grow,
            x="Growth %",
            y="Occupation",
            orientation="h",
            color="Occupation",
            text="Growth_label",
            color_discrete_sequence=grow_colors,
            title="Top 5 Growing Occupations (2020–2024)"
        )

         fig1.update_traces(
            textposition="outside",
            marker_line_color="white",
            marker_line_width=1.2,
            width=0.65
        )

         fig1.update_layout(
            showlegend=False,
            template="simple_white",
            font=dict(family="Segoe UI", size=11),
            title_font=dict(size=14, color="#1a4e8a"),
            margin=dict(t=60, b=30, l=80, r=40),
            height=320,
            bargap=0.15,  
            xaxis_title="Growth %",
            yaxis_title="Occupation",
        )

        # Remove dark axis lines, add margin for text visibility
         fig1.update_xaxes(showline=False, showgrid=True, zeroline=False, range=[-10, 30])
         fig1.update_yaxes(showline=False, showgrid=False, zeroline=False)
         st.plotly_chart(fig1, use_container_width=True)

       with col2:
         fig2 = px.bar(
            top_decl,
            x="Growth %",
            y="Occupation",
            orientation="h",
            color="Occupation",
            text="Growth_label",
            color_discrete_sequence=decl_colors,
            title="Top 5 Declining Occupations (2020–2024)"
        )

         fig2.update_traces(
            textposition="outside",
            marker_line_color="white",
            marker_line_width=1.2,
            width=0.65
        )

         fig2.update_layout(
            showlegend=False,
            template="simple_white",
            font=dict(family="Segoe UI", size=11),
            title_font=dict(size=14, color="#1a4e8a"),
            margin=dict(t=60, b=30, l=80, r=40),
            height=320,
            bargap=0.15
        )

        # Hide axis lines and add right padding for long labels
         fig2.update_xaxes(showline=False, showgrid=True, zeroline=False, range=[top_decl["Growth %"].min() * 1.15, 0])
         fig2.update_yaxes(showline=False, showgrid=False, zeroline=False)
         st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    with tab3:
       latest_year = "2024"

       df_gender_occ = df[(df["Occupation"]!="All Occupations") & 
                   (df["Age Group"]=="All Ages") & 
                   (df["Occupation"]!="Others") & 
                   (df["Sex"]!="All")]

       df_gender_occ_latest = df_gender_occ[["Occupation","Sex",latest_year]].copy()
       df_gender_occ_latest[latest_year] = pd.to_numeric(df_gender_occ_latest[latest_year], errors="coerce")

       pivot_gender_occ = df_gender_occ_latest.pivot_table(index="Occupation", 
                                                    columns="Sex", 
                                                    values=latest_year, 
                                                    aggfunc="sum").fillna(0)

# Calculate the ratio
       pivot_gender_occ_pct = pivot_gender_occ.div(pivot_gender_occ.sum(axis=1), axis=0) * 100
       df_wide = pivot_gender_occ_pct.reset_index() 
       fig = px.bar(
       df_wide,
       x=["Male", "Female"],          
       y="Occupation",
       orientation="h",
       barmode="stack",
       color_discrete_map={"Male": "#004C99", "Female": "#FF9999"}
)
       fig.update_traces(texttemplate="%{x:.1f}%", textposition="inside")
       fig.update_layout(
    title=f"Gender Distribution by Occupation ({latest_year})",
    xaxis_title="Share (%)",
    yaxis_title="Occupation",
    legend_title="Gender",
    template="simple_white",
    bargap=0.15,
    margin=dict(l=120, r=40, t=60, b=40)
)
       fig.update_xaxes(range=[0, 100], ticksuffix="%")
       st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
       
    # Age × Gender × Occupation Distribution (Latest Year)
      st.header("Age × Gender × Occupation Distribution")

      selected_occupations = [
        "Professionals",
        "Associate Professionals & Technicians",
        "Clerical Support Workers",
        "Service & Sales Workers",
        "Craftsmen & Related Trade Workers",
        "Plant & Machine Operators & Assemblers"
    ]

    # Filter & preprocess
      dist_df = df[
        (df["Occupation"].isin(selected_occupations)) &
        (df["Age Group"] != "All Ages") &
        (df["Sex"] != "All")
    ].copy()
      dist_df[latest_year] = pd.to_numeric(dist_df[latest_year], errors="coerce")

    # Age sorting function
    

      age_order = sorted(dist_df["Age Group"].unique())

    # Custom colors
      colors = {"Male": "#004C99", "Female": "#FF9999"}  # Blue + Soft Pink

    # Create 2 × 3 grid layout
    # Subplot Layout 2 rows × 3 columns
      fig = make_subplots(
      rows=2, cols=3,
      subplot_titles=[
        "Professionals",
        "Clerical Support Workers",
        "Craftsmen & Related Trade Workers",
        "Associate Professionals & Technicians",
        "Service & Sales Workers",
        "Plant & Machine Operators & Assemblers"
    ],
      horizontal_spacing=0.10,
      vertical_spacing=0.20
)

# Manual mapping: each occupation → (row, col)
      layout_positions = {
    "Professionals": (1, 1),
    "Clerical Support Workers": (1, 2),
    "Craftsmen & Related Trade Workers": (1, 3),
    "Associate Professionals & Technicians": (2, 1),
    "Service & Sales Workers": (2, 2),
    "Plant & Machine Operators & Assemblers": (2, 3)
}
      colors = {"Male": "#004C99", "Female": "#FF9999"} 
# Add bar charts for each occupation
      for occ in selected_occupations:
        r, c = layout_positions[occ]
        subset = dist_df[dist_df["Occupation"] == occ].copy()
        subset = subset.groupby(["Age Group", "Sex"])[latest_year].sum().reset_index()

        subset["Age Group"] = pd.Categorical(subset["Age Group"], categories=age_order, ordered=True)
        subset = subset.sort_values("Age Group")

        for gender in ["Male", "Female"]:
          gender_data = subset[subset["Sex"] == gender]
          fig.add_trace(
            go.Bar(
                x=gender_data["Age Group"],
                y=gender_data[latest_year],
                name=gender,
                marker_color=colors[gender],
                showlegend=True if occ == "Professionals" else False  # Legend only once
            ),
            row=r, col=c
        )

# Layout Customization
      fig.update_layout(
    height=800,
    width=1200,
    barmode="group",
    title_text=f"Age × Gender × Occupation Distribution ({latest_year})",
    title_font=dict(size=16, color="#333", family="Arial", weight="bold"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text="Gender",
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05
    ),
    margin=dict(l=50, r=220, t=90, b=80)
)

# Consistent axis style
      fig.update_xaxes(title_text="Age Group", showgrid=True, gridcolor="lightgrey", tickangle=35)
      fig.update_yaxes(title_text="Employed Persons (thousands)", showgrid=True, gridcolor="lightgrey")

      st.plotly_chart(fig, use_container_width=True)

def slide_C():
    st.header("Salary Trend")
    
    df2 = pd.read_csv("salary.csv")

# Set up the page
    st.set_page_config(
    page_title="Singapore Employment Trends",
    layout="wide")

# Page title and information
    st.title("📊 Singapore Employment Trends (2000-2024)")
    st.info("Explore how employment in Singapore changed across different demographics and occupation between 2000 and 2024.")
    st.caption("Data Source: SingStat")
    st.divider()

# Create page tabs
    with st.container(border=True):
      tab1, = st.tabs([
        "Salary Trend"])

# TAB 1: Executive Summary
    with tab1:
    # Update variables
      year_min_sal = df2["year"].min()
      year_max_sal = df2["year"].max()
      latest_col_sal = str(year_max_sal)

    st.markdown(
        "📍  Data of this tab is available up to 2023 only."
    )

    dist_tab, gap_tab, trend_tab, gap_trend_tab = st.tabs([
            "Distribution by Occupation",
            "Gap (Snapshot)",
            "Trend by Occupation",
            "Trend of Gap"
        ])
        # -----------------------------------------------------------

        # TAB: distribution by Occupation 
    with dist_tab:
            male_tab, female_tab = st.tabs(["Male", "Female"])

            # Male Snapshot
            with male_tab:
                st.subheader(f"Snapshot of Salary by Industry ({year_max_sal})")
                sal_snapshot = df2[(df2["year"]==df2["year"].max()) & (df2["gender"]=="Male")]\
                    .groupby("occupation")["value"].mean().sort_values(ascending=False).reset_index()
                sal_snapshot.columns = ['occupation', 'value']
                sal_snapshot = sal_snapshot.rename(columns={
                    "occupation": "Occupation",
                    "value": "Gross Monthly Income"
                })

                fig_bar = px.bar(
                    sal_snapshot, x='Occupation', y='Gross Monthly Income',
                    title=f"<b>Gross Monthly Income by Occupation in {year_max_sal} - Male</b>",
                    color='Occupation', text_auto='.2s'
                )
                fig_bar.update_traces(textposition='outside', cliponaxis=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            

            # Female Snapshot
            with female_tab:
                sal_snapshot = df2[(df2["year"]==df2["year"].max()) & (df2["gender"]=="Female")]\
                    .groupby("occupation")["value"].mean().sort_values(ascending=False).reset_index()
                sal_snapshot.columns = ['occupation', 'value']
                sal_snapshot = sal_snapshot.rename(columns={
                    "occupation": "Occupation",
                    "value": "Gross Monthly Income"
                })

                fig_bar = px.bar(
                    sal_snapshot, x='Occupation', y='Gross Monthly Income',
                    title=f"<b>Gross Monthly Income by Occupation in {year_max_sal} - Female</b>",
                    color='Occupation', text_auto='.2s'
                )
                fig_bar.update_traces(textposition='outside', cliponaxis=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            # 

        #  TAB: Gap Snapshot =
    with gap_tab:
            #  Gap Snapshot)
            # Salary by occupation in most recent year, broken down by gender
            rank_m = df2[df2["gender"] == "Male"]
            rank_f = df2[df2["gender"] == "Female"]

            # Merge & calculate gender salary gap
            salary_gap = rank_m.merge(rank_f, how='left', on=('occupation','year'), suffixes=('_m', '_f'))
            salary_gap["gap"] = salary_gap["value_m"] - salary_gap["value_f"]

            # Current salary gap chart
            gap_snapshot = salary_gap[salary_gap["year"]==year_max_sal]\
                .groupby(["occupation","year"])["gap"].mean().sort_values(ascending=False).reset_index()
            gap_snapshot = gap_snapshot.rename(columns={
                "occupation": "Occupation",
                "gap": "Monthly Income Gap"
            })

            fig_bar = px.bar(
                gap_snapshot, x='Occupation', y='Monthly Income Gap',
                title=f"<b>Gender Monthly Income Gap by Occupation in {year_max_sal} (Men − Women)</b>",
                color='Occupation', text_auto='.2s'
            )
            fig_bar.update_traces(textposition='outside', cliponaxis=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            

        #  TAB: Trend by Occupation 
    with trend_tab:
            trend_m_tab, trend_f_tab = st.tabs(["Male", "Female"])

            #  Male Trend
            with trend_m_tab:
                st.subheader(f"Salary Trends by Occupation ({year_min_sal}–{year_max_sal})")
                sal_trend = df2[df2["gender"]=="Male"].groupby(["occupation","year"])["value"].mean().reset_index()

                fig_line = px.line(
                    sal_trend, x="year", y="value", color="occupation",
                    title="<b>Year-over-Year Salary Trends by Occupation - Male</b>", markers=True
                )
                fig_line.update_layout(
                    xaxis_title="Year", yaxis_title="Gross Monthly Income", legend_title_text='Occupation'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            

            # Female Trend
            with trend_f_tab:
                sal_trend = df2[df2["gender"]=="Female"].groupby(["occupation","year"])["value"].mean().reset_index()

                fig_line = px.line(
                    sal_trend, x="year", y="value", color="occupation",
                    title="<b>Year-over-Year Salary Trends by Occupation - Female</b>", markers=True
                )
                fig_line.update_layout(
                    xaxis_title="Year", yaxis_title="Gross Monthly Income", legend_title_text='Occupation'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            # ---------------------------------------------------

        # Trend of Gap 
    with gap_trend_tab:
            
            gap_trend = salary_gap.groupby(["occupation","year"])["gap"].mean().reset_index()

            fig_line = px.line(
                gap_trend, x="year", y="gap", color="occupation",
                title="<b>Year-over-Year Gender Salary Gap Trends by Occupation (Men − Women)</b>", markers=True
            )
            fig_line.update_layout(
                xaxis_title="Year", yaxis_title="Monthly Income Gap", legend_title_text='Occupation'
            )
            st.plotly_chart(fig_line, use_container_width=True, cliponaxis=False)

def slide_D():
    
# 0. Basic Configuration
    st.set_page_config(page_title="Singapore Unemployment Insights", layout="wide")
    st.title("🔍 Singapore Unemployment Rate Analysis Dashboard (2000–2024)")
    st.info("Explore how unemployment rate in Singapore changed across different age groups and qualification between 2000 and 2024.")
    st.caption("Data Source: SingStat")
    st.divider()


# Part 1. Overall Unemployment Trend (2000-2024)

    tab1, tab2 = st.tabs([
        "Unemployment Trend", 
        "Detailed unemployment breakdown",
        ])
    
    with tab1:
       st.header("Overall Unemployment Rate Trend (2000–2024)")
       st.markdown("This section shows the overall unemployment rate trajectory in Singapore over the past 25 years.")

# Read data - using age group data to calculate overall rate
       df_age_all = pd.read_csv("unemployment_by_age.csv")

# Filter for "Total" or calculate weighted average if Total exists
       df_overall = df_age_all[df_age_all["Age Group"] == "Total"].copy() if "Total" in df_age_all["Age Group"].values else df_age_all.groupby("Year")["Unemployment"].mean().reset_frame()

       df_overall = df_overall[(df_overall["Year"] >= 2000) & (df_overall["Year"] <= 2024)].copy()
       df_overall["Unemployment"] = pd.to_numeric(df_overall["Unemployment"], errors="coerce")
       df_overall = df_overall.sort_values("Year")

# Create line chart with area fill
       fig = go.Figure()

       fig.add_trace(go.Scatter(
       x=df_overall["Year"],
       y=df_overall["Unemployment"],
       mode='lines+markers',
       name='Unemployment Rate',
       line=dict(color='#e74c3c', width=3),
       marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='white')),
       fill='tozeroy',
       fillcolor='rgba(231, 76, 60, 0.2)'
))

# Highlight key events
       fig.add_annotation(x=2003, y=df_overall[df_overall["Year"]==2003]["Unemployment"].values[0] if 2003 in df_overall["Year"].values else 3,
                  text="SARS Pandemic", showarrow=True, arrowhead=2, ax=0, ay=-40)
       fig.add_annotation(x=2008, y=df_overall[df_overall["Year"]==2008]["Unemployment"].values[0] if 2008 in df_overall["Year"].values else 3,
                  text="Global Financial Crisis", showarrow=True, arrowhead=2, ax=0, ay=-40)
       fig.add_annotation(x=2020, y=df_overall[df_overall["Year"]==2020]["Unemployment"].values[0] if 2020 in df_overall["Year"].values else 3,
                  text="COVID-19 Pandemic", showarrow=True, arrowhead=2, ax=0, ay=-40)

       fig.update_layout(
       title="Overall Unemployment Rate Trend",
       xaxis_title="Year",
       yaxis_title="Unemployment Rate (%)",
       height=500,
       hovermode="x unified"
)

       st.plotly_chart(fig, use_container_width=True)


 
# Part 2. Age Group Distribution (2024)

    with tab2:
       st.header("Detailed Unemployment Breakdown for 2024")
       col1, col2= st.columns(2)
       with col1:
          
          

# Read age group data
          df_age = pd.read_csv("unemployment_by_age.csv")

# Filter 2024 data
          df_2024 = df_age[df_age["Year"] == 2024].copy()
          df_2024["Unemployment"] = pd.to_numeric(df_2024["Unemployment"], errors="coerce")

# Define target age groups
          target_age_groups = [
          "15 - 24",
          "25 - 29", 
          "30 - 39",
          "40 - 49",
          "50 - 59",
          "60 & Over"
]

# Filter and sort
          df_filtered = df_2024[df_2024["Age Group"].isin(target_age_groups)].copy()
          df_filtered["Age Group"] = pd.Categorical(
          df_filtered["Age Group"], 
          categories=target_age_groups, 
          ordered=True
)
          df_filtered = df_filtered.sort_values("Age Group").reset_index(drop=True)

# Create multi-color area chart using Plotly
          x = np.arange(len(df_filtered))
          y = df_filtered["Unemployment"].values
          labels = df_filtered["Age Group"].values

# Create figure
          fig = go.Figure()

# Use rainbow colors
          colors_list = px.colors.sequential.Turbo
          colors_mapped = [colors_list[int(i * len(colors_list) / len(df_filtered))] for i in range(len(df_filtered))]

# Add individual bars with different colors to simulate multi-color area
          for i in range(len(df_filtered)):
             fig.add_trace(go.Bar(
             x=[labels[i]],
             y=[y[i]],
             marker_color=colors_mapped[i],
             name=labels[i],
             showlegend=False,
             width=0.8
    ))

# Add connecting line
          fig.add_trace(go.Scatter(
          x=labels,
          y=y,
          mode='lines+markers',
          line=dict(color='navy', width=3),
          marker=dict(size=12, color='white', line=dict(width=2.5, color='navy')),
          showlegend=False
))

          fig.update_layout(
          title="By Age  (2024)",
          xaxis_title="Age Group",
          yaxis_title="Unemployment Rate (%)",
          height=500,
          hovermode="x"
)

          st.plotly_chart(fig, use_container_width=True)
    
       with col2:
          # Part 4. Unemployment by Qualification - Combined Chart (2000-2024)
         # Read qualification data
         df_qual = pd.read_csv("unemployment_by_qualification.csv")

# Filter 2000-2024
         df_qual_filtered = df_qual[(df_qual["Year"] >= 2000) & (df_qual["Year"] <= 2024)].copy()
         df_qual_filtered["Unemployment"] = pd.to_numeric(df_qual_filtered["Unemployment"], errors="coerce")
         df_qual_filtered = df_qual_filtered.dropna(subset=["Unemployment"])

# Get unique qualifications
         qualifications = sorted(df_qual_filtered["Highest Qualification"].unique())
         df_2024_qual = df_qual_filtered[df_qual_filtered["Year"] == 2024].sort_values("Unemployment", ascending=False)
    
         fig_bar = px.bar(
         df_2024_qual,
         x="Unemployment",
         y="Highest Qualification",
         orientation='h',
         color="Unemployment",
         color_continuous_scale="RdYlGn_r",
         title="By Qualification (2024)"
    )
         fig_bar.update_layout(height=400, showlegend=False)
         st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()


def slide_summary():
    st.header("Summary")
    # (Empty content)

# Slide Setup
SLIDES = [("Introduction", slide_intro),
          ("Data Overview", slide_overview),
          ("Age Group Analysis", slide_demographics), 
          ("Industry Performance", slide_A),
          ("Occupation Performance", slide_B),
          ("Salary Trend", slide_C),
          ("Unemployment Trend", slide_D),
          ("Summary", slide_summary)]

# Keep track of which slide we are on
if "idx" not in st.session_state:
    st.session_state.idx = 0

# Make the sidebar for navigation
with st.sidebar:
    st.header("Presentation Slides")
    
    # Get the names of the slides for the radio buttons
    labels = []
    for name, func in SLIDES:
        labels.append(name)
    
    # Function to update the slide when a radio button is clicked
    def update_index_from_radio():
        st.session_state.idx = labels.index(st.session_state.idx_radio)

    # Create the radio buttons
    st.radio(
        "Go to slide",
        labels,
        index=st.session_state.idx,
        key="idx_radio",
        on_change=update_index_from_radio,)

    st.markdown("---")
    
    # Functions for the next and previous buttons
    def go_prev():
        current_index = st.session_state.idx
        if current_index > 0:
            st.session_state.idx = current_index - 1

    def go_next():
        current_index = st.session_state.idx
        if current_index < len(SLIDES) - 1:
            st.session_state.idx = current_index + 1
    
    # Create the next and previous buttons
    prev_col, next_col = st.columns(2)
    prev_col.button("◀ Prev", use_container_width=True, on_click=go_prev, disabled=(st.session_state.idx == 0))
    next_col.button("Next ▶", use_container_width=True, on_click=go_next, disabled=(st.session_state.idx == len(SLIDES) - 1))


# Get the function for the current slide and run it to show the content
slide_name, render_fn = SLIDES[st.session_state.idx]
render_fn()  