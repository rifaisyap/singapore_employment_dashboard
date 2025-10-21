# Import library
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Load dataset
df = pd.read_csv("clean_data_combined.csv")
df2 = pd.read_csv("salary.csv")
df_age = pd.read_csv("unemployment_by_age.csv")
df_sex = pd.read_csv("unemployment_by_sex.csv")
df_qual = pd.read_csv("unemployment_by_qualification.csv")
df_io = pd.read_csv("Industry and Occupation.csv")

# Set up the page
st.set_page_config(
    page_title="Singapore Employment Trends",
    layout="wide")

# Page title and information
st.title("📊 Singapore Employment Dashboard (2000-2024)")
st.markdown("""
> **Explore Singapore's employment trends (2000-2024)** across industries, education levels, and demographics  
> to uncover which career paths offer the most promising and resilient prospects for students.
""")
st.caption("Data Source: SingStat")
st.divider()

# Get list of year column and sort it
year_list = []
for i in df.columns:
    if i.isdigit():
        year_list.append(int(i))
year_list = sorted(year_list)

year_cols = [c for c in df.columns if c.isdigit()]
for c in year_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Get the unique values for filter values
gender_list = sorted(df["Sex"].unique().tolist())
age_list = sorted(df["Age Group"].unique().tolist())
job_list = sorted(df["Occupation"].unique().tolist())
qual_list = sorted(df_qual["Highest Qualification"].unique().tolist())


# Set a default data for filter
default_years = (year_list[0], year_list[-1])
default_gender = ["All"]
default_age = ["All Ages"]
default_jobs = ["All Occupations"]
default_qual = qual_list # Select all by default


# Set the page layout
left, mid, right = st.columns([1, 0.5, 5])

with left:
    st.subheader("🔎 Filters")
    # Set filter setting for year with slider
    year_min, year_max = st.select_slider("Pick Year Range", options=year_list, value=default_years)
    # Set filter setting for gender, age, and occupation with dropdown
    selected_gender = st.multiselect("Gender", options=gender_list, default=default_gender)
    selected_age = st.multiselect("Age Group", options=age_list, default=default_age)
    selected_jobs = st.multiselect("Occupation", options=job_list, default=default_jobs)
    st.caption("⚠️ If you select **All**, the other filters for that category won't apply. To choose specific gender, age group, or occupation, uncheck **All** first.")

# Create page tabs with border line
with right:
    with st.container(border=True):
        # Corrected tab name list to be valid
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Overview",
            "Demographic Analysis",
            "Industry Performance",
            "Occupation Performance",
            "Salary Trend",
            "Unemployment Trend"])

# Set new variable for data filtering
filtered_data = df.copy()

if "All" not in selected_gender:
    filtered_data = filtered_data[filtered_data["Sex"].isin(selected_gender)]

if "All Ages" not in selected_age:
    filtered_data = filtered_data[filtered_data["Age Group"].isin(selected_age)]

if "All Occupations" not in selected_jobs:
    filtered_data = filtered_data[filtered_data["Occupation"].isin(selected_jobs)]

# Give error message, because we spot there's an error if we didn't set any filter in the dashboard
if filtered_data.empty: st.info("Please choose your filters."); st.stop()

# Convert selected year columns to numbers
selected_year_cols = []

for year in year_list:
    if year >= year_min and year <= year_max:
        selected_year_cols.append(str(year))
for year in selected_year_cols:
    if year in filtered_data.columns:
        filtered_data[year] = pd.to_numeric(filtered_data[year], errors="coerce").fillna(0)

# Give error message, because we spot there's an error if we didn't set any filter in the dashboard
if not selected_year_cols: st.info("Please set your filters."); st.stop()

# Get latest, previous, and two-years-ago columns
latest_col = str(year_max)
prev_col = str(year_max - 1)
prev2_col = str(year_max - 2)

# TAB 1: Overview
with tab1:
    # Get the previous years available in the data
    latest_col = str(year_max)
    prev_col = None
    prev2_col = None

    # Get the index of the latest selected year in the sorted list of all available years
    if year_max in year_list:
        latest_year_index = year_list.index(year_max)
        
        # Get the previous available year
        if latest_year_index > 0:
            prev_col = str(year_list[latest_year_index - 1])
        
        # Get the year before that
        if latest_year_index > 1:
            prev2_col = str(year_list[latest_year_index - 2])

    # Calculate totals only if the year columns exist
    total_latest = filtered_data[latest_col].sum() if latest_col in filtered_data.columns else 0
    total_prev = filtered_data[prev_col].sum() if prev_col and prev_col in filtered_data.columns else 0
    total_prev2 = filtered_data[prev2_col].sum() if prev2_col and prev2_col in filtered_data.columns else 0

    # Calculate YoY or Yeor over Year growth if previous year's data is available
    growth = ((total_latest - total_prev) / total_prev * 100) if total_prev else 0
    growth_prev = ((total_prev - total_prev2) / total_prev2 * 100) if total_prev2 else 0
    change = round(growth - growth_prev, 2)

    # Total period growth metrics
    start_col = str(year_min)
    total_start = filtered_data[start_col].sum() if start_col in filtered_data.columns else 0
    period_growth = ((total_latest - total_start) / total_start * 100) if total_start else 0

    # Gender breakdown
    gender_data = df.copy()
    if "All Ages" not in selected_age:
        gender_data = gender_data[gender_data["Age Group"].isin(selected_age)]
    if "All Occupations" not in selected_jobs:
        gender_data = gender_data[gender_data["Occupation"].isin(selected_jobs)]
    gender_data[latest_col] = pd.to_numeric(gender_data[latest_col], errors="coerce")
    female_sum = gender_data[gender_data["Sex"] == "Female"][latest_col].sum()
    male_sum = gender_data[gender_data["Sex"] == "Male"][latest_col].sum()
    female_ratio = (female_sum / (female_sum + male_sum) * 100) if (female_sum + male_sum) else 0

    # Show metric card
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=f"Total Growth ({year_min} to {year_max})",
            value=f"{period_growth:.2f}%")
        st.caption("For the entire selected period")
        
    with col2:
        # Get the grand total for the metric value from the unfiltered dataframe
        grand_total_latest_year = df.loc[(df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations') & (df['Sex'] == 'All'), latest_col].item()
        numeric_total = float(grand_total_latest_year)
        
        st.metric(
            label=f"Total Employment ({latest_col}) - (in Thousands)",
            value=f"{numeric_total:.1f}",
            # Only show the delta if there is a previous year to compare 
            delta=f"{growth:.2f}%" if prev_col else None)
        # Update the caption to show the actual year being compared
        st.caption(f"Year-over-year vs. {prev_col}" if prev_col else "No previous year for comparison")
        
    with col3:
        st.metric(
            label=f"YoY Growth Rate ({latest_col})",
            value=f"{growth:.2f}%" if prev_col else "N/A", 
            # Only show the delta if two previous years exist
            delta=f"{change:.2f} pp" if prev2_col else None)
        # Update the streamlit caption to reflect what's being compared
        st.caption(f"Growth momentum vs. {prev_col}" if prev2_col else "Insufficient data for momentum")

    with col4:
        st.metric(
            label=f"Female Employment ({latest_col})",
            value=f"{female_ratio:.1f}%")
        st.caption(f"{female_sum:,.0f} Female / {male_sum:,.0f} Male")

    st.divider()
    # Add key visualization
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Employment Trend")
        # Create "Overall Employment Trend" chart
        if "All Ages" in selected_age and "All Occupations" in selected_jobs and "All" in selected_gender:
            # Prepare data for each trace
            total_trend = df.loc[(df['Sex'] == 'All') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()
            male_trend = df.loc[(df['Sex'] == 'Male') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()
            female_trend = df.loc[(df['Sex'] == 'Female') & (df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations'), selected_year_cols].sum()

            # Create a figure with graph_objects for layering
            fig = go.Figure()

            # Add the color to fill area for Total Employment chart
            fig.add_trace(go.Scatter(
                x=total_trend.index, y=total_trend.values,
                fill='tozeroy',
                mode='lines',
                line_color='rgba(100, 149, 237, 0.5)', 
                name='Total'))

            # Add the line for Male Employment
            fig.add_trace(go.Scatter(
                x=male_trend.index, y=male_trend.values,
                mode='lines',
                line_color='#6495ED', 
                name='Male'))

            # Add the line for Female Employment
            fig.add_trace(go.Scatter(
                x=female_trend.index, y=female_trend.values,
                mode='lines',
                line_color='#FF69B4', 
                name='Female'))
            
            title = "<b>Overall Employment Trend by Gender</b>"
        
        # Setting the chart when user uses filters
        else:
            trend_df = filtered_data.melt(id_vars=["Sex", "Age Group", "Occupation"], value_vars=selected_year_cols, var_name="Year", value_name="Employment")
            trend_df['Year'] = pd.to_numeric(trend_df['Year'])

            if "All" not in selected_gender:
                grouping_var = "Sex"
            elif "All Occupations" not in selected_jobs and len(selected_jobs) > 1:
                grouping_var = "Occupation"
            else:
                grouping_var = "Age Group"

            grouped_trend = trend_df.groupby(["Year", grouping_var])["Employment"].sum().reset_index()
            color_map = {'Male': '#6495ED', 'Female': '#FF69B4'} if grouping_var == "Sex" else {}
            
            fig = px.line(grouped_trend, x="Year", y="Employment", color=grouping_var, 
                          markers=True, color_discrete_map=color_map)
            
            title = f"<b>Employment Trend by {grouping_var}</b>"
        
        # Set final layout updates to the figure
        fig.update_layout(
            title=title,
            height=350, 
            margin=dict(l=20, r=20, t=60, b=20), 
            legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Key Insights")
        
        # Create key insight for Top Hiring Industry
        st.markdown("🚀 **Top Hiring Industry**")
        if year_min < year_max:
            # Use the industry and occupation dataframe for this insight
            io_filtered = df_io[(df_io['year'].isin([year_min, year_max])) & (~df_io['industry'].isin(["All Industries", "Services"]))]
            
            # Need to set pivot to get years as columns
            io_pivot = io_filtered.pivot_table(index='industry', columns='year', values='employment', aggfunc='sum')
            
            # Calculate absolute growth and find the max
            if year_min in io_pivot.columns and year_max in io_pivot.columns:
                io_pivot['growth'] = io_pivot[year_max] - io_pivot[year_min]
                top_hiring_industry = io_pivot['growth'].idxmax()
                top_hiring_value = io_pivot['growth'].max()
                st.markdown(f"##### {top_hiring_industry}") 
                st.caption(f"This industry added the most jobs (**{top_hiring_value:,.0f}k**) from {year_min} to {year_max}, signaling strong hiring growth.")
            else:
                st.info("Insufficient data for industry growth analysis.")
        else:
            st.info("Select a period longer than one year to see hiring trends.")

        st.markdown("---")

        # Create key insight for Highest Paying Occupation
        st.markdown("💰 **Highest Paying Occupation**")
        
        # If 2024 is selected, use 2023 data for this insight instead, because there's no 2024 data in salary dataset
        year_for_salary = 2023 if year_max == 2024 else year_max
        
        # Filter the salary data using the adjusted year
        sal_latest = df2[(df2['year'] == year_for_salary) & (df2['occupation'] != 'All Occupations')]
        
        if not sal_latest.empty:
            top_paying_occ = sal_latest.groupby('occupation')['value'].mean().idxmax()
            top_paying_val = sal_latest.groupby('occupation')['value'].mean().max()
            st.markdown(f"##### {top_paying_occ}")
            st.caption(f"Offered the highest average salary of **S${top_paying_val:,.0f}/month** in {year_for_salary}.")
        else:
            st.info(f"Salary data for the year {year_for_salary} is not available.")

# TAB 2: Demographic Breakdown
with tab2:
    # Create Employment Trend chart (Overall & By Gender)
    st.subheader(f"Employment Trend (Overall & By Gender) ({year_min} - {year_max})")

    genders_to_plot = ["All"]
    if "All" in selected_gender:
        genders_to_plot.extend(["Male", "Female"])
    else:
        genders_to_plot.extend(selected_gender)

    gender_filter = df["Sex"].isin(genders_to_plot)
    combined_src = df[
        (df["Occupation"] == "All Occupations") &
        (df["Age Group"] == "All Ages") &
        gender_filter]

    combined_melt = combined_src.melt(
        id_vars=["Sex"],
        value_vars=selected_year_cols,
        var_name="Year",
        value_name="Employment")
    combined_melt["Year"] = combined_melt["Year"].astype(int)
    combined_melt['Sex'] = combined_melt['Sex'].replace({'All': 'Total'})

    fig_area = px.line(
        combined_melt, x="Year", y="Employment", color="Sex",
        markers=False, category_orders={"Sex": ["Total", "Male", "Female"]},
        color_discrete_map={'Total': 'lightskyblue', 'Male': 'blue', 'Female': 'hotpink'})

    fig_area.update_traces(selector={'name': 'Total'}, fill='tozeroy')
    st.plotly_chart(fig_area, use_container_width=True)
    st.divider()
    
    # Use the main 'filtered_data' which already connect to the year, gender, and age filters from the sidebar.
    age_chart_df = filtered_data.copy()

    # If the user select "All Occupations", we must  use only those pre-aggregated rows.
    if "All Occupations" in selected_jobs:
        age_chart_df = age_chart_df[age_chart_df['Occupation'] == 'All Occupations']
    
    # If the user selected specific occupations, 'filtered_data' is already correct,
    # so we don't need to do anything else. The sum will be calculated correctly.
    age_filtered = age_chart_df[age_chart_df["Age Group"] != "All Ages"]

    # Create Employment by Age Group bar chart
    st.subheader(f"Employment by Age Group ({year_max})")
    
    # Group by Age Group and sum
    age_snapshot = age_filtered.groupby("Age Group")[latest_col].sum().reset_index()
    age_snapshot.columns = ['Age Group', 'Employment Count']

    # Set age group order from youngest to older year
    age_order = [
        "15-19 Years Old", "20-24 Years Old", "25-29 Years Old", "30-34 Years Old", 
        "35-39 Years Old", "40-44 Years Old", "45-49 Years Old", "50-54 Years Old", 
        "55-59 Years Old", "60-64 Years Old", "65 Years & Over" ]
    age_snapshot['Age Group'] = pd.Categorical(age_snapshot['Age Group'], categories=age_order, ordered=True)
    age_snapshot = age_snapshot.sort_values('Age Group')

    fig_bar = px.bar(age_snapshot, x='Age Group', y='Employment Count', 
                     color='Age Group', text_auto='.2s')
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Create Employment Trends by Age Group using line chart
    st.subheader(f"Employment Trends by Age Group ({year_min}–{year_max})")
    
    age_trend = age_filtered.groupby("Age Group")[selected_year_cols].sum().T
    age_trend.index = age_trend.index.astype(int)
    
    fig_line = px.line(age_trend, x=age_trend.index, y=age_trend.columns, markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Total Employment", legend_title_text='Age Group')
    st.plotly_chart(fig_line, use_container_width=True)

    
# Tab 3: Industry Performance
# --- Tab 3: Employment by Industry ---
with tab3:
    # Use the title from your image, linked to the global year filter
    st.subheader(f"Employment Volume by Industry ({year_max})")
    st.caption("This chart shows the total number of employed residents for each industry in the latest selected year.")

    # Define the rows to drop: "All Industries" and the "Services" sub-total
    # This is the key step to matching your screenshot
    industries_to_drop = ["All Industries", "Services"]
    
    # Filter data based on:
    # 1. The GLOBAL year filter (year_max)
    # 2. Hardcode the occupation to "All" (as requested)
    # 3. Exclude the "All Industries" and "Services" total rows
    df_chart_data = df_io[
        (df_io['year'] == year_max) &
        (df_io['occupation'] == "All Occupation Groups, (Total Employed Residents)") &
        (~df_io['industry'].isin(industries_to_drop)) # Use ~isin to drop the list
    ]

    if not df_chart_data.empty:
        # Sort ascending=True so the horizontal bar chart shows the highest value at the top
        df_chart_data = df_chart_data.sort_values("employment", ascending=True)
        
        # Create the HORIZONTAL bar chart
        fig_io_bar = px.bar(
            df_chart_data,
            x="employment",  # Set x to the numeric value
            y="industry",    # Set y to the category
            orientation='h', # Set orientation to 'h'
            title=f"Employment Volume by Industry ({year_max})",
            color="employment",
            color_continuous_scale=px.colors.sequential.Viridis,
            text_auto='.1f' # Add data labels (e.g., 336.0)
        )
        
        fig_io_bar.update_layout(
            xaxis_title="Employment (in '000s)", # Matches your image
            yaxis_title=None, # Cleaner look
            height=500,
            showlegend=False,
            coloraxis_showscale=True
        )
        
        # Position the text outside the bars for clarity
        fig_io_bar.update_traces(textposition='outside')
        
        st.plotly_chart(fig_io_bar, use_container_width=True)
    else:
        # Show a warning if no data exists for that year
        st.warning(f"No industry data available for {year_max}.")

    # Create Line Chart of Employment Trends
    st.subheader(f"Employment Trends Across Top 10 Industries ({year_min} - {year_max})")
    st.caption("This trend line shows the employment trend over the period for the top 10 industries.")
    fig2 = px.line(
        trends_data, 
        x="year", 
        y="employment", 
        color="industry",
        markers=True
    )
    fig2.update_layout(
        xaxis_title="Year",
        yaxis_title="Employment (in Thousands)",
        legend_title_text="Industry"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()
    
    # Create Stacked Bar Chart for Occupation distribution
    st.subheader(f"Occupation Distribution in Each Industry in {year_max}")

    # Filter for the latest year and exclude aggregate occupation categories
    latest_year_data = tab3_filtered[
        (tab3_filtered["year"] == year_max) &
        (~tab3_filtered["industry"].isin(industries_to_drop))
    ]
    occupations_to_drop = ["All Occupation Groups, (Total Employed Residents)", "Other Occupation Groups Nes"]
    composition_data = latest_year_data[~latest_year_data["occupation"].isin(occupations_to_drop)]

    if composition_data.empty:
        st.info("No detailed occupation data to display for the current selection.")
    else:
        # Calculate the percentage share of each occupation within its industry
        totals = composition_data.groupby("industry")["employment"].sum().rename("total_employment")
        composition_data = composition_data.merge(totals, on="industry")
        composition_data["share"] = composition_data["employment"] / composition_data["total_employment"]

        # Create the stacked bar chart
        st.caption("This chart breaks down each industry's workforce by occupation, showing the percentage of employees in different roles.")
        fig3 = px.bar(
            composition_data,
            x="industry",
            y="share",
            color="occupation",
            labels={"share": "Share of Workforce", "industry": "Industry", "occupation": "Occupation"},
            text_auto='.0%'
        )
        fig3.update_traces(textposition='inside', insidetextanchor='middle')
        fig3.update_layout(
            height=700,
            barmode="stack",
            xaxis_title=None,
            yaxis_title="Share of Employment",
            yaxis_tickformat=".0%",
            legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig3, use_container_width=True)


# TAB 4: Occupation Performance
with tab4:
    st.header("Occupation Performance")
    
    # Get the latest year selected by the user from the slider
    end_year = str(year_max)

    # Chart 1: Employment Trend by Occupation
    st.subheader("Employment Trend by Occupation")
    
    # Use the data already filtered by the sidebar, but remove the "All Occupations" total
    occupation_trend_data = filtered_data[filtered_data["Occupation"] != "All Occupations"].copy()

    occupation_melted = occupation_trend_data.melt(
        id_vars=["Occupation"], 
        value_vars=selected_year_cols,
        var_name="Year", 
        value_name="Employment")
    occupation_melted["Year"] = occupation_melted["Year"].astype(int)

    # Calculate the sum of employment values to get the trend data
    final_trend = occupation_melted.groupby(["Year", "Occupation"])["Employment"].sum().reset_index()
    
    # Create the line chart
    fig_trend = px.line(final_trend, x="Year", y="Employment", color="Occupation", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.divider()

    # Chart 2: Top 4 Growing & Declining Occupations
    st.subheader(f"Top 4 Growing & Declining Occupations ({year_min}–{year_max})")

    # Define the start and end years for the growth calculation
    start_year_for_growth = str(year_min)
    
    # Check if the selected time range is valid for calculating growth (more than 1 year)
    if start_year_for_growth in filtered_data.columns and end_year in filtered_data.columns and start_year_for_growth != end_year:
        
        # Excluding the total ("All"( in occupation data
        growth_base = filtered_data[filtered_data["Occupation"] != "All Occupations"]
        
        # Group by occupation and sum the employment for start and end years
        growth_summary = growth_base.groupby("Occupation")[[start_year_for_growth, end_year]].sum()
        
        # Remove any occupations that had 0 employment at the start to avoid division-by-zero errors
        growth_summary = growth_summary[growth_summary[start_year_for_growth] > 0]
        
        # Calculate the growth percentage
        growth_summary["Growth %"] = (
            (growth_summary[end_year] - growth_summary[start_year_for_growth]) /
             growth_summary[start_year_for_growth]) * 100
        
        # Get the top 4 and least 4
        top_grow = growth_summary.nlargest(4, "Growth %").reset_index()
        top_decl = growth_summary.nsmallest(4, "Growth %").reset_index()
    else:
        # If the date range is not valid, create empty dataframes to avoid errors in dashboard
        top_grow = pd.DataFrame(columns=["Occupation", "Growth %"])
        top_decl = pd.DataFrame(columns=["Occupation", "Growth %"])

    # Create two columns to display the charts side-by-side
    c1, c2 = st.columns(2)
    with c1:
        fig_growing = px.bar(top_grow, x="Growth %", y="Occupation", orientation="h", color="Occupation", 
                          text_auto='.1f', title="Top 4 Growing Occupations")
        fig_growing.update_traces(texttemplate='%{x:.1f}%', textposition="outside")
        fig_growing.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_growing, use_container_width=True)
    with c2:
        fig_declining = px.bar(top_decl, x="Growth %", y="Occupation", orientation="h", color="Occupation",
                          text_auto='.1f', title="Top 4 Declining Occupations")
        fig_declining.update_traces(texttemplate='%{x:.1f}%', textposition="outside")
        fig_declining.update_layout(showlegend=False, yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_declining, use_container_width=True)
    st.divider()

    # Chart 3: Gender Distribution by Occupation
    st.subheader(f"Gender Distribution by Occupation ({end_year})")

    # Use the filtered data in mainpage, but ensure we only have Male/Female for comparison
    gender_dist_data = filtered_data[filtered_data["Sex"].isin(["Male", "Female"])]

    if end_year in gender_dist_data.columns and not gender_dist_data.empty:
        # Group data by Occupation and Sex, then sum the employment for the selected end year
        gender_summary = gender_dist_data.groupby(["Occupation", "Sex"])[end_year].sum().reset_index()
        
        # Calculate the total employment for each occupation to find the percentage
        occupation_totals = gender_summary.groupby("Occupation")[end_year].sum().rename("Total")
        gender_summary = gender_summary.merge(occupation_totals, on="Occupation")
        
        # Calculate the share for each gender
        gender_summary["Share (%)"] = (gender_summary[end_year] / gender_summary["Total"]) * 100
        
        # Create the 100% stacked bar chart
        fig_gender = px.bar(
            gender_summary, x="Share (%)", y="Occupation", color="Sex", orientation="h",
            text="Share (%)",
            color_discrete_map={"Male": "#004C99", "Female": "#FF9999"})
        fig_gender.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
        fig_gender.update_layout(
            barmode="stack", xaxis_title="Share of Workforce", yaxis_title=None,
            legend_title_text="Gender", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.warning(f"No gender distribution data available for {end_year} with these filters.")
    st.divider()

    # Chart 4: Job Breakdown by Age, Gender, and Occupation
    st.subheader(f"Job Breakdown by Age, Gender, and Occupation ({end_year})")

    # Use the non-aggregated data from the main dataframe
    breakdown_data = df[
        (df["Age Group"] != "All Ages") &
        (df["Sex"] != "All") &
        (df["Occupation"] != "All Occupations")
    ].copy()

    # Apply all sidebar filters to this detailed data
    if "All Occupations" not in selected_jobs:
        breakdown_data = breakdown_data[breakdown_data["Occupation"].isin(selected_jobs)]
    if "All" not in selected_gender:
        breakdown_data = breakdown_data[breakdown_data["Sex"].isin(selected_gender)]
    if "All Ages" not in selected_age:
        breakdown_data = breakdown_data[breakdown_data["Age Group"].isin(selected_age)]

    # Continue only if there is data left after filtering
    if end_year in breakdown_data.columns and not breakdown_data.empty:
        # Get a sorted list of unique occupations for the chart titles
        occupations_in_order = sorted(breakdown_data["Occupation"].unique())
        
        # Create a "facet" plot: a grid of smaller charts, one for each occupation
        fig_breakdown = px.bar(
            breakdown_data,
            x="Age Group", y=end_year, color="Sex",
            facet_col="Occupation",     # Create a new chart for each occupation
            facet_col_wrap=3,           # Show 3 charts per row
            barmode="group",
            height=300 * ((len(occupations_in_order) - 1) // 3 + 1), 
            color_discrete_map={"Male": "navy", "Female": "lightcoral"})
        
        # Set y-axis ranges for each chart for better visibility
        fig_breakdown.update_yaxes(matches=None, showticklabels=True)
        
        # tidy up the titles for each small chart 
        for annotation in fig_breakdown.layout.annotations:
            annotation.text = annotation.text.replace("Occupation=", "")

        # Add a y-axis title only to the first chart in each row to have a more clear chart
        fig_breakdown.update_yaxes(title_text="Employed (in Thousands)", col=1)
        fig_breakdown.update_yaxes(title_text="", col=2)
        fig_breakdown.update_yaxes(title_text="", col=3)

        st.plotly_chart(fig_breakdown, use_container_width=True)
    else:
        st.warning(f"Sorry, no detailed breakdown data to show for {end_year} with these filters.")


# TAB 5: Salary Trend
with tab5:
    # Create new dataframe
    filtered_data2 = df2.copy()

    if "All" not in selected_gender:
        filtered_data2 = filtered_data2[filtered_data2["gender"].isin(selected_gender)]

    if "All Occupations" not in selected_jobs:
        filtered_data2 = filtered_data2[filtered_data2["occupation"].isin(selected_jobs)]

    # Convert selected year columns to numbers
    selected_year_cols2 = []

    for year in filtered_data2["year"]:
        if year >= year_min and year <= year_max:
            selected_year_cols2.append(int(year))


    if not selected_year_cols2: st.info("Please set your filters."); st.stop()
    year_min_sal = min(selected_year_cols2)
    year_max_sal = max(selected_year_cols2)

    ### Current salary chart
    st.subheader(f"Salary Trend")

    st.warning(
            """
            **Note:** 
            - The **Age Group** filter is not applicable for this section.
            - Salary data is only available up to **2023**.
            """
        )
    st.subheader(f"Snapshot of Salary by Industry ({year_max_sal})")
    sal_snapshot = filtered_data2[filtered_data2["year"]==year_max_sal].groupby("occupation")["value"].mean().sort_values(ascending=False).reset_index()
    sal_snapshot.columns = ['occupation', 'value']
    sal_snapshot = sal_snapshot.rename(columns={
        "occupation": "Occupation",
        "value": "Gross Monthly Income"})

    fig_bar = px.bar(sal_snapshot, x='Occupation', y='Gross Monthly Income', 
                     title=f"<b>Gross Monthly Income by Occupation in {year_max_sal}</b>",
                     color='Occupation', text_auto='.2s')
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Salary by occupation in most recent year, broken down by gender
    rank_m = filtered_data2[filtered_data2["gender"] == "Male"]
    rank_f = filtered_data2[filtered_data2["gender"] == "Female"]

    # Merge & calculate gender salary gap
    salary_gap = rank_m.merge(rank_f, how='left', on=('occupation','year'), suffixes=('_m', '_f'))
    salary_gap["gap"] = salary_gap["value_m"] - salary_gap["value_f"]

    ### Current salary gap chart
    gap_snapshot = salary_gap[salary_gap["year"]==year_max_sal].groupby(["occupation","year"])["gap"].mean().sort_values(ascending=False).reset_index()
    gap_snapshot = gap_snapshot.rename(columns={
        "occupation": "Occupation",
        "gap": "Monthly Income Gap"})

    fig_bar = px.bar(gap_snapshot, x='Occupation', y='Monthly Income Gap', 
                     title=f"<b>Gender Monthly Income Gap by Occupation in {year_max_sal} (Men − Women)</b>",
                     color='Occupation', text_auto='.2s')
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    ### Salary trend over the years chart
    st.subheader(f"Salary Trends by Occupation ({year_min_sal}–{year_max_sal})")
    sal_trend = filtered_data2[filtered_data2["year"].isin(selected_year_cols2)].groupby(["occupation","year"])["value"].mean().reset_index()
    
    fig_line = px.line(sal_trend, x="year", y="value", color = "occupation",
                       title="<b>Year-over-Year Salary Trends by Occupation</b>", markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Gross Monthly Income", legend_title_text='Occupation')
    fig_line.update_traces(cliponaxis=False) 
    st.plotly_chart(fig_line, use_container_width=True)

    ### Salary gap over the years chart
    gap_trend = salary_gap[salary_gap["year"].isin(selected_year_cols2)].groupby(["occupation","year"])["gap"].mean().reset_index()
    
    fig_line = px.line(gap_trend, x="year", y="gap", color = "occupation",
                       title="<b>Year-over-Year Gender Salary Gap Trends by Occupation (Men − Women)</b>", markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Monthly Income Gap", legend_title_text='Occupation')
    fig_line.update_traces(cliponaxis=False) 
    st.plotly_chart(fig_line, use_container_width=True)

# TAB 6: Unemployment Trend
with tab6:
    st.header("Unemployment Trend Analysis")
    st.warning("Note: This section is only affected by the **year filter**. Selections for Gender, Age Group, and Occupation don't apply here.")
    st.divider()

    # Chart 1: Overall Unemployment Trend
    st.subheader(f"Overall Unemployment Trend ({year_min}–{year_max})")

    df_total_trend = df_age[
        (df_age["Age Group"] == "Total") &
        (df_age["Year"] >= year_min) &
        (df_age["Year"] <= year_max)
    ].sort_values("Year")

    if not df_total_trend.empty:
        fig_overall = go.Figure()
        fig_overall.add_trace(go.Scatter(
            x=df_total_trend["Year"], y=df_total_trend["Unemployment"],
            mode='lines+markers', name='Unemployment Rate',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8, color='#e74c3c', line=dict(width=1, color='white')),
            fill='tozeroy', fillcolor='rgba(231, 76, 60, 0.2)'
        ))
        events = {2003: "SARS Pandemic", 2008: "Global Financial Crisis", 2020: "COVID-19 Pandemic"}
        for year, text in events.items():
            if year in df_total_trend["Year"].values:
                unemployment_value = df_total_trend[df_total_trend["Year"] == year]["Unemployment"].iloc[0]
                fig_overall.add_annotation(
                    x=year, y=unemployment_value, text=text,
                    showarrow=True, arrowhead=2, ax=0, ay=-40
                )
        fig_overall.update_layout(
            xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=500,
            hovermode="x unified", showlegend=False
        )
        st.plotly_chart(fig_overall, use_container_width=True)
    else:
        st.warning("No overall unemployment data is available for the selected year range.")
    st.divider()

    # Combined Row for Second and Third Charts
    st.subheader(f"Detailed Unemployment Breakdown for {year_max}")
    
    col1, col2 = st.columns(2)

    # Chart 2: Unemployment by Age Group (with labels)
    with col1:
        df_age_latest = df_age[df_age["Year"] == year_max].copy()
        target_age_groups = ["15 - 24", "25 - 29", "30 - 39", "40 - 49", "50 - 59", "60 & Over"]
        df_age_latest = df_age_latest[df_age_latest["Age Group"].isin(target_age_groups)]

        if not df_age_latest.empty:
            df_age_latest["Age Group"] = pd.Categorical(df_age_latest["Age Group"], categories=target_age_groups, ordered=True)
            df_age_latest = df_age_latest.sort_values("Age Group")

            fig_age_dist = go.Figure()
            # Add bar trace with text labels
            fig_age_dist.add_trace(go.Bar(
                x=df_age_latest["Age Group"], y=df_age_latest["Unemployment"],
                marker_color=px.colors.sequential.Viridis, name="Unemployment Rate",
                text=df_age_latest["Unemployment"], texttemplate='%{text:.1f}%', textposition='outside'))
            # Add line trace
            fig_age_dist.add_trace(go.Scatter(
                x=df_age_latest["Age Group"], y=df_age_latest["Unemployment"],
                mode='lines+markers', line=dict(color='navy', width=3),
                marker=dict(size=12, color='white', line=dict(width=2.5, color='navy')),
                name="Trend Line"))
            fig_age_dist.update_layout(
                title="By Age Group", xaxis_title=None,
                yaxis_title="Unemployment Rate (%)", height=450, showlegend=False,
                uniformtext_minsize=8, uniformtext_mode='hide')
            st.plotly_chart(fig_age_dist, use_container_width=True)
        else:
            st.info(f"No age group breakdown is available for {year_max}.")

    # Chart 3: Unemployment by Qualification (with labels)
    with col2:
        df_qual_latest = df_qual[df_qual["Year"] == year_max]

        if not df_qual_latest.empty:
            df_chart_data = df_qual_latest.sort_values("Unemployment", ascending=True)
            # Add text_auto to create labels
            fig_qual_bar = px.bar(
                df_chart_data, x="Unemployment", y="Highest Qualification",
                orientation='h', color="Unemployment",
                color_continuous_scale="RdYlGn_r", title="By Qualification",
                text_auto='.1f')
            # Position the text outside the bars
            fig_qual_bar.update_traces(textposition='outside')
            fig_qual_bar.update_layout(
                height=450, showlegend=False,
                xaxis_title="Unemployment Rate (%)", yaxis_title=None)
            st.plotly_chart(fig_qual_bar, use_container_width=True)
        else:
            st.info(f"No qualification breakdown is available for {year_max}.")
    
    st.divider()