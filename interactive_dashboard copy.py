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
> ℹ️ **Explore Singapore's employment trends (2000-2024)** across industries, education levels, and demographics  
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
            "Demographic Breakdown",
            "Industry Performance",
            "Occupation Performance",
            "Unemployment Trend",
            "Salary Trend"])

# Set new variable for data filtering
filtered_data = df.copy()

if "All" not in selected_gender:
    filtered_data = filtered_data[filtered_data["Sex"].isin(selected_gender)]

if "All Ages" not in selected_age:
    filtered_data = filtered_data[filtered_data["Age Group"].isin(selected_age)]

if "All Occupations" not in selected_jobs:
    filtered_data = filtered_data[filtered_data["Occupation"].isin(selected_jobs)]

# Convert selected year columns to numbers
selected_year_cols = []

for year in year_list:
    if year >= year_min and year <= year_max:
        selected_year_cols.append(str(year))
for year in selected_year_cols:
    if year in filtered_data.columns:
        filtered_data[year] = pd.to_numeric(filtered_data[year], errors="coerce").fillna(0)

# Get latest, previous, and two-years-ago columns
latest_col = str(year_max)
prev_col = str(year_max - 1)
prev2_col = str(year_max - 2)

# TAB 1: Overview
with tab1:
    # Find the previous years available in the data
    latest_col = str(year_max)
    prev_col = None
    prev2_col = None

    # Find the index of the latest selected year in the sorted list of all available years
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
            value=f"{period_growth:.2f}%"
        )
        st.caption("For the entire selected period")
        
    with col2:
        # Get the grand total for the metric value from the unfiltered dataframe
        grand_total_latest_year = df.loc[(df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations') & (df['Sex'] == 'All'), latest_col].item()
        numeric_total = float(grand_total_latest_year)
        
        st.metric(
            label=f"Total Employment ({latest_col}) - (in Thousands)",
            value=f"{numeric_total:.1f}",
            # Only show the delta if there is a previous year to compare 
            delta=f"{growth:.2f}%" if prev_col else None 
        )
        # Update the caption to show the actual year being compared
        st.caption(f"Year-over-year vs. {prev_col}" if prev_col else "No previous year for comparison")
        
    with col3:
        st.metric(
            # Show "N/A" if growth can't be calculated
            label=f"YoY Growth Rate ({latest_col})",
            value=f"{growth:.2f}%" if prev_col else "N/A",
            # Only show the delta if two previous years exist
            delta=f"{change:.2f} pp" if prev2_col else None
        )
        # Update the caption to reflect what's being compared
        st.caption(f"Growth momentum vs. {prev_col}" if prev2_col else "Insufficient data for momentum")

    with col4:
        st.metric(
            label=f"Female Employment ({latest_col})",
            value=f"{female_ratio:.1f}%"
        )
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

# TAB 2: Age Group Breakdown
with tab2:
    st.subheader(f"Employment by Age Group ({year_max})")
    
    age_filtered = filtered_data[filtered_data["Age Group"] != "All Ages"]
    
    # Group by Age Group
    age_snapshot = age_filtered.groupby("Age Group")[latest_col].sum().reset_index()
    age_snapshot.columns = ['Age Group', 'Employment Count']

    # Create a list to set the correct order from youngest to oldest age
    age_order = [
        "15-19 Years Old", "20-24 Years Old", "25-29 Years Old", 
        "30-34 Years Old", "35-39 Years Old", "40-44 Years Old",
        "45-49 Years Old", "50-54 Years Old", "55-59 Years Old",
        "60-64 Years Old", "65 Years & Over"]
    
    # Apply the custom order to the 'Age Group' column
    age_snapshot['Age Group'] = pd.Categorical(age_snapshot['Age Group'], categories=age_order, ordered=True)
    
    # Sort the data based on the new custom order
    age_snapshot = age_snapshot.sort_values('Age Group')

    # Create the bar chart with the sorted data
    fig_bar = px.bar(age_snapshot, x='Age Group', y='Employment Count', 
                     title=f"<b>Employment by Age Group in {year_max}</b>",
                     color='Age Group', text_auto='.2s')
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader(f"Employment Trends by Age Group ({year_min}–{year_max})")
    
    # Create line chart
    age_trend = age_filtered.groupby("Age Group")[selected_year_cols].sum().T
    age_trend.index = age_trend.index.astype(int)
    
    fig_line = px.line(age_trend, x=age_trend.index, y=age_trend.columns,
                       title="<b>Year-over-Year Employment Trends by Age Group</b>", markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Total Employment", legend_title_text='Age Group')
    st.plotly_chart(fig_line, use_container_width=True)
    
# Tab 3: Industry and Occupation
with tab3:
    st.subheader("Industry × Occupation Analysis")
    df_io = pd.read_csv("Industry and Occupation.csv")
    df_io.columns = [c.strip().lower().replace(" ", "_") for c in df_io.columns]

    value_col = "employment"  
    for c in ("year", value_col):
        df_io[c] = pd.to_numeric(df_io[c], errors="coerce")

    filtered = df_io.dropna(subset=["year", value_col]).copy()

    if "gender" in filtered.columns and "All" not in selected_gender:
        filtered = filtered[filtered["gender"].isin(selected_gender)]

    if "occupation" in filtered.columns and "All Occupations" not in selected_jobs:
        filtered = filtered[filtered["occupation"].isin(selected_jobs)]

    if "year" in filtered.columns:
        # Renamed variables to avoid conflict with main page filters
        y_min_io = int(filtered["year"].min())
        y_max_io = int(filtered["year"].max())
        selected_years = [y for y in year_list if y_min_io <= y <= y_max_io]
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

    latest_year = int(filtered["year"].max())

    # Chart1
    drop_inds = {
        "All Industries",
        "Services",
        "All Industries (Employed Residents)",
        "Services (Total)"
    }
    if "industry" in filtered.columns:
        filtered_no_aggs = filtered[~filtered["industry"].isin([d for d in drop_inds if d in filtered["industry"].unique()])]
    else:
        filtered_no_aggs = filtered.copy()

    by_industry = (filtered_no_aggs[filtered_no_aggs["year"] == latest_year]
               .groupby("industry", as_index=False)[value_col].sum()
               .sort_values(value_col, ascending=False))

    fig1 = px.bar(
        by_industry, x="industry", y=value_col,
        template="plotly_dark", text=value_col
    )
    fig1.update_traces(
        texttemplate="%{text:.0f}",   
        textposition="outside"
    )
    fig1.update_layout(
        title="Hiring Volume by Industry — {}".format(latest_year),
        xaxis_title="",
        yaxis_title="Employment (thousands)",
        xaxis=dict(tickangle=-65),   
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=80)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Chart2
    top_inds = by_industry["industry"].head(8).tolist()
    trends = (filtered[filtered["industry"].isin(top_inds)]
              .groupby(["industry", "year"], as_index=False)[value_col].sum())

    fig2 = px.line(
        trends, x="year", y=value_col, color="industry",
        markers=True, template="plotly_dark"
    )
    fig2.update_layout(
        title="Employment Trends by Industry (2000-2024)",
        xaxis_title="Year",
        yaxis_title="Total Employment",
        legend_title_text="Industry",
        legend=dict(orientation="v", y=0.5, x=1.02),
        margin=dict(l=40, r=160, t=60, b=40),
    )
    fig2.update_yaxes(tickformat=",")
    st.plotly_chart(fig2, use_container_width=True)

    # Chart3
    d_latest = filtered[filtered["year"] == latest_year].copy()
    io = d_latest.groupby(["industry", "occupation"], as_index=False)[value_col].sum()

    drop_occs = {
        "All Occupation Groups",
        "All Occupation Groups Nes",
        "All Occupation Groups, (Total Employed Residents)",
        "All Occupation Groups (Total Employed Residents)",
        "All Occupation Groups, Total Employed Residents"
    }
    io = io[~io["occupation"].isin([d for d in drop_occs if d in io["occupation"].unique()])]

    totals = io.groupby("industry", as_index=False)[value_col].sum().rename(columns={value_col: "total_ind"})
    io = io.merge(totals, on="industry", how="left")
    io["share"] = io[value_col] / io["total_ind"]

    io["industry"] = pd.Categorical(io["industry"], categories=by_industry["industry"].tolist(), ordered=True)
    io = io.sort_values(["industry", "occupation"])

    fig3 = px.bar(
        io, x="industry", y="share", color="occupation",
        template="plotly_dark", barmode="stack",
        category_orders={"industry": by_industry["industry"].tolist()},
        text="share"  
    )
    fig3.update_traces(
        texttemplate="%{text:.0%}",
        textposition="inside",
        textfont_size=12,
        cliponaxis=False
    )
    fig3.update_layout(
        height=900,
        margin=dict(l=70, r=260, t=80, b=200),
        legend=dict(orientation="v", y=1.0, x=1.02),
        xaxis_title="Industry",
        yaxis_title="Share of employment",
    )
    fig3.update_xaxes(tickangle=-45, tickfont=dict(size=11))
    fig3.update_yaxes(range=[0, 1], tickformat=".0%")

    st.plotly_chart(fig3, use_container_width=True)

# TAB 4: Occupation Performance (all charts obey filter logic)
with tab4:
    st.header("📈 Occupation Performance (Interactive)")

    # Helper: Define year columns based on the slider and what's available in the data
    selected_year_cols = [str(y) for y in year_list if year_min <= y <= year_max]
    end_year = str(year_max)
    start_year_for_growth = str(year_min)

    # --- 1) Employment Trend (Overall) ---
    st.subheader("1️⃣ Employment Trend (Overall)")
    overall_all = df[
        (df["Occupation"] == "All Occupations") &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ]
    # Melt using all available years, not just the selected range for a full overview
    trend_all = overall_all.melt(value_vars=[str(y) for y in year_list], var_name="Year", value_name="Employment")
    trend_all["Year"] = trend_all["Year"].astype(int)

    fig1 = px.line(trend_all, x="Year", y="Employment", markers=True,
                   title="Overall Employment Trend (2000–2024)")
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    # --- 2) Gender trend — responds ONLY to gender filter ---
    st.subheader("2️⃣ Employment Trend by Gender (All Occupations)")
    gsrc = df[
        (df["Occupation"] == "All Occupations") &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] != "All")
    ].copy()
    # CORRECTED: Used selected_gender instead of selected_sex
    if "All" not in selected_gender:
        gsrc = gsrc[gsrc["Sex"].isin(selected_gender)]

    g_melt = gsrc.melt(id_vars=["Sex"], value_vars=selected_year_cols, # Use selected years
                       var_name="Year", value_name="Employment")
    g_melt["Year"] = g_melt["Year"].astype(int)

    fig2 = px.line(g_melt, x="Year", y="Employment", color="Sex",
                   markers=True, title="Employment Trend by Gender")
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # --- 3) Share of Age Groups — responds to age group filter ---
    st.subheader("3️⃣ Share of Age Groups in Workforce by Year (Stacked)")
    age_src = df[
        (df["Occupation"] == "All Occupations") &
        (df["Sex"] == "All") &
        (df["Age Group"] != "All Ages")
    ].copy()
    if "All Ages" not in selected_age:
        age_src = age_src[age_src["Age Group"].isin(selected_age)]

    age_melt = age_src.melt(id_vars=["Age Group"], value_vars=selected_year_cols,
                            var_name="Year", value_name="Employment")
    age_melt["Year"] = age_melt["Year"].astype(int)
    # Ensure no division by zero
    age_melt['Employment'] = pd.to_numeric(age_melt['Employment'], errors='coerce').fillna(0)
    tot = age_melt.groupby("Year")["Employment"].transform("sum")
    age_melt["Share (%)"] = age_melt.apply(lambda row: (row["Employment"] / tot[row.name]) * 100 if tot[row.name] > 0 else 0, axis=1)


    fig3 = px.area(age_melt, x="Year", y="Share (%)", color="Age Group",
                   title="Share of Age Groups in Workforce (Stacked)",
                   color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    # --- 4) Trend by Occupation — responds to occupation filter ---
    st.subheader("4️⃣ Employment Trend by Occupation")
    occ_src = df[
        (~df["Occupation"].isin(["All Occupations"])) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()
    # CORRECTED: Used selected_jobs instead of selected_occ
    if "All Occupations" not in selected_jobs:
        occ_src = occ_src[occ_src["Occupation"].isin(selected_jobs)]

    occ_melt = occ_src.melt(id_vars=["Occupation"], value_vars=selected_year_cols,
                            var_name="Year", value_name="Employment")
    occ_melt["Year"] = occ_melt["Year"].astype(int)

    fig4 = px.line(occ_melt, x="Year", y="Employment", color="Occupation",
                   markers=True, title="Employment Trend by Occupation (Filtered)")
    st.plotly_chart(fig4, use_container_width=True)
    st.divider()

    # --- 5) Top Growing & Declining — uses selected year range for growth ---
    st.subheader(f"5️⃣ Top 4 Growing & Declining Occupations ({year_min}–{year_max})")

    growth_base = df[
        (~df["Occupation"].isin(["All Occupations"])) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()

    if start_year_for_growth in growth_base.columns and end_year in growth_base.columns and start_year_for_growth != end_year:
        growth_base[start_year_for_growth] = pd.to_numeric(growth_base[start_year_for_growth], errors="coerce")
        growth_base[end_year] = pd.to_numeric(growth_base[end_year], errors="coerce")
        
        # Avoid division by zero
        growth_base_filtered = growth_base.dropna(subset=[start_year_for_growth, end_year])
        growth_base_filtered = growth_base_filtered[growth_base_filtered[start_year_for_growth] > 0]

        growth_base_filtered["Growth %"] = (
            (growth_base_filtered[end_year] - growth_base_filtered[start_year_for_growth]) /
            growth_base_filtered[start_year_for_growth]
        ) * 100

        top_grow = growth_base_filtered.nlargest(4, "Growth %")
        top_decl = growth_base_filtered.nsmallest(4, "Growth %")
    else:
        top_grow = pd.DataFrame(columns=["Occupation", "Growth %"])
        top_decl = pd.DataFrame(columns=["Occupation", "Growth %"])

    c1, c2 = st.columns(2)
    with c1:
        fig5a = px.bar(
            top_grow, x="Growth %", y="Occupation", orientation="h",
            text_auto='.1f', title=f"Top 4 Growing Occupations"
        )
        fig5a.update_traces(texttemplate='%{x:.1f}%', textposition="outside")
        fig5a.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig5a, use_container_width=True)

    with c2:
        fig5b = px.bar(
            top_decl, x="Growth %", y="Occupation", orientation="h",
            text_auto='.1f', title=f"Top 4 Declining Occupations"
        )
        fig5b.update_traces(texttemplate='%{x:.1f}%', textposition="outside")
        fig5b.update_layout(showlegend=False, yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig5b, use_container_width=True)
    st.divider()

    # --- 6) Gender Distribution — responds to year, occupation, and gender filters ---
    st.subheader(f"6️⃣ Gender Distribution by Occupation ({end_year})")

    gender_occ = df[
        (df["Age Group"] == "All Ages") &
        (df["Sex"] != "All") &
        (~df["Occupation"].isin(["All Occupations"]))
    ].copy()

    # CORRECTED: Used selected_jobs and selected_gender
    if "All Occupations" not in selected_jobs:
        gender_occ = gender_occ[gender_occ["Occupation"].isin(selected_jobs)]
    if "All" not in selected_gender:
        gender_occ = gender_occ[gender_occ["Sex"].isin(selected_gender)]

    if end_year in gender_occ.columns:
        gender_occ[end_year] = pd.to_numeric(gender_occ[end_year], errors="coerce").fillna(0)
        
        pivot_gender = gender_occ.pivot_table(
            index="Occupation", columns="Sex", values=end_year, aggfunc="sum"
        ).fillna(0)

        pivot_share_gen = pivot_gender.div(pivot_gender.sum(axis=1), axis=0) * 100
        pivot_share_gen = pivot_share_gen.reset_index().melt(
            id_vars="Occupation", var_name="Gender", value_name="Share (%)"
        )

        fig6 = px.bar(
            pivot_share_gen, x="Share (%)", y="Occupation", color="Gender", orientation="h",
            text_auto='.1f', title=f"Gender Distribution by Occupation ({end_year})",
            color_discrete_map={"Male": "#004C99", "Female": "#FF9999"}
        )
        fig6.update_traces(texttemplate="%{x:.1f}%", textposition="inside")
        fig6.update_layout(
            barmode="stack", xaxis_title="Share (%)", yaxis_title="Occupation",
            showlegend=True, legend_title_text="Gender", yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning(f"No gender distribution data available for the year {end_year}.")
    st.divider()

    # --- Chart 7: The big chart with lots of small charts inside ---
    # This one shows jobs broken down by Age, Gender, and Occupation.
    st.subheader(f"7. Detailed Job Breakdown for {end_year}")

    # First, get all the data but remove the "All" categories.
    filtered_df = df[
        (df["Age Group"] != "All Ages") &
        (df["Sex"] != "All") &
        (df["Occupation"] != "All Occupations")
    ].copy()

    # Now, apply the filters from the sidebar that the user chose.
    # 1. Filter by Occupation
    if "All Occupations" not in selected_jobs:
        filtered_df = filtered_df[filtered_df["Occupation"].isin(selected_jobs)]

    # 2. Filter by Gender
    if "All" not in selected_gender:
        filtered_df = filtered_df[filtered_df["Sex"].isin(selected_gender)]

    # 3. Filter by Age Group
    if "All Ages" not in selected_age:
        filtered_df = filtered_df[filtered_df["Age Group"].isin(selected_age)]

    # We need to make sure the end_year column exists and has numbers.
    if end_year in filtered_df.columns and not filtered_df.empty:
        filtered_df[end_year] = pd.to_numeric(filtered_df[end_year], errors='coerce')
        filtered_df = filtered_df.fillna(0) # Replace any blanks with 0

        # We want the age groups to be in order, like "15-19", "20-24", etc.
        # Let's get all the unique age groups and sort them.
        age_groups_in_order = sorted(filtered_df["Age Group"].unique())
        
        # We also want the occupations to be in alphabetical order.
        occupations_in_order = sorted(filtered_df["Occupation"].unique())

        # Tell pandas the correct order for our columns.
        filtered_df["Age Group"] = pd.Categorical(filtered_df["Age Group"], categories=age_groups_in_order, ordered=True)
        filtered_df["Occupation"] = pd.Categorical(filtered_df["Occupation"], categories=occupations_in_order, ordered=True)
        
        # Sort the data so the charts appear in order.
        filtered_df = filtered_df.sort_values(by=["Occupation", "Age Group"])
        
        # Create the plot. `facet_col` makes the small charts. `facet_col_wrap` tells it to make a new row after 3 charts.
        fig8 = px.bar(
            filtered_df,
            x="Age Group",
            y=end_year,
            color="Sex",
            facet_col="Occupation",
            facet_col_wrap=3, # 3 charts per row
            barmode="group",
            height=300 * ((len(occupations_in_order) - 1) // 3 + 1), # Make the chart taller if there are more rows
            title=f"Job Breakdown by Age, Gender, and Occupation ({end_year})",
            color_discrete_map={"Male": "navy", "Female": "lightcoral"}
        )

        # This part is a bit tricky. We want each ROW of charts to have the same y-axis height.
        # We will loop through the occupations, 3 at a time (one for each row).
        
        # First row of charts (charts 1, 2, 3)
        row1_occupations = occupations_in_order[0:3]
        if row1_occupations: # Check if there are any occupations for this row
            # Find the biggest number in the first row's data.
            max_value_row1 = filtered_df[filtered_df['Occupation'].isin(row1_occupations)][end_year].max()
            # Set the y-axis for the first row to be a little bigger than the max value.
            fig8.update_yaxes(range=[0, max_value_row1 * 1.1], row=1)

        # Second row of charts (charts 4, 5, 6)
        row2_occupations = occupations_in_order[3:6]
        if row2_occupations:
            max_value_row2 = filtered_df[filtered_df['Occupation'].isin(row2_occupations)][end_year].max()
            fig8.update_yaxes(range=[0, max_value_row2 * 1.1], row=2)

        # Third row of charts (and so on, if they exist)
        row3_occupations = occupations_in_order[6:9]
        if row3_occupations:
            max_value_row3 = filtered_df[filtered_df['Occupation'].isin(row3_occupations)][end_year].max()
            fig8.update_yaxes(range=[0, max_value_row3 * 1.1], row=3)

        # We only want the y-axis title on the very first chart of each row.
        fig8.update_yaxes(title_text="Employed Persons (thousands)", col=1)
        fig8.update_yaxes(title_text="", col=2)
        fig8.update_yaxes(title_text="", col=3)
        
        # The titles for each small chart look like "Occupation=Professionals". Let's clean that up.
        # This loop goes through each title and removes the "Occupation=" part.
        for annotation in fig8.layout.annotations:
            text = annotation.text
            new_text = text.replace("Occupation=", "")
            annotation.text = new_text

        # Finally, show the chart in Streamlit.
        st.plotly_chart(fig8, use_container_width=True)

    else:
        # If there's no data for the filters the user picked, show a message.
        st.warning(f"Sorry, no data to show for {end_year} with these filters.")


# TAB 5: Unemployment Trend


# TAB 6: Salary Trend
with tab6:
    filtered_data2 = df2.copy()

    if "All" not in selected_gender:
        # Convert to lowercase to match 'salary.csv' column values
        lowercase_gender = [g.lower() for g in selected_gender]
        filtered_data2 = filtered_data2[filtered_data2["gender"].isin(lowercase_gender)]

    if "All Occupations" not in selected_jobs:
        filtered_data2 = filtered_data2[filtered_data2["occupation"].isin(selected_jobs)]
    
    # Filter by the main year slider
    filtered_data2 = filtered_data2[(filtered_data2['year'] >= year_min) & (filtered_data2['year'] <= year_max)]

    if not filtered_data2.empty:
        # Get year range from the filtered salary data
        selected_year_cols2 = sorted(filtered_data2["year"].unique())
        year_min_sal = min(selected_year_cols2)
        year_max_sal = max(selected_year_cols2)

        st.markdown(
            """
            📍 <u><b>Note:</b></u><br>
            &emsp;•&emsp;Age filter does not apply for this specific tab.<br>
            &emsp;•&emsp;Data of this tab is available up to 2023 only.
            """,
            unsafe_allow_html=True
        )
        st.subheader(f"Snapshot of Salary by Industry ({year_max_sal})")
        sal_snapshot = filtered_data2[filtered_data2["year"]==year_max_sal].groupby("occupation")["value"].mean().sort_values(ascending=False).reset_index()
        sal_snapshot.columns = ['occupation', 'value']
        sal_snapshot = sal_snapshot.rename(columns={
            "occupation": "Occupation",
            "value": "Gross Monthly Income"
        })

        fig_bar = px.bar(sal_snapshot, x='Occupation', y='Gross Monthly Income', 
                         title=f"<b>Gross Monthly Income by Occupation in {year_max_sal}</b>",
                         color='Occupation', text_auto='.2s')
        fig_bar.update_traces(textposition='outside', cliponaxis=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Salary by occupation in most recent year, broken down by gender
        rank_m = df2[df2["gender"] == "male"]
        rank_f = df2[df2["gender"] == "female"]

        # Merge & calculate gender salary gap
        salary_gap = rank_m.merge(rank_f, how='left', on=('occupation','year'), suffixes=('_m', '_f'))
        salary_gap["gap"] = salary_gap["value_m"] - salary_gap["value_f"]
        
        # Filter salary gap data based on main year slider
        salary_gap = salary_gap[(salary_gap['year'] >= year_min) & (salary_gap['year'] <= year_max)]
        
        if not salary_gap.empty:
            ### Current salary gap chart
            gap_snapshot = salary_gap[salary_gap["year"]==year_max_sal].groupby(["occupation","year"])["gap"].mean().sort_values(ascending=False).reset_index()
            gap_snapshot = gap_snapshot.rename(columns={
                "occupation": "Occupation",
                "gap": "Monthly Income Gap"
            })

            fig_bar_gap = px.bar(gap_snapshot, x='Occupation', y='Monthly Income Gap', 
                             title=f"<b>Gender Monthly Income Gap by Occupation in {year_max_sal} (Men − Women)</b>",
                             color='Occupation', text_auto='.2s')
            fig_bar_gap.update_traces(textposition='outside', cliponaxis=False)
            st.plotly_chart(fig_bar_gap, use_container_width=True)

        st.divider()

        ### Salary trend over the years chart
        st.subheader(f"Salary Trends by Occupation ({year_min_sal}–{year_max_sal})")
        sal_trend = filtered_data2[filtered_data2["year"].isin(selected_year_cols2)].groupby(["occupation","year"])["value"].mean().reset_index()
        
        fig_line_sal = px.line(sal_trend, x="year", y="value", color = "occupation",
                           title="<b>Year-over-Year Salary Trends by Occupation</b>", markers=True)
        fig_line_sal.update_layout(xaxis_title="Year", yaxis_title="Gross Monthly Income", legend_title_text='Occupation')
        st.plotly_chart(fig_line_sal, use_container_width=True)

        ### Salary gap over the years chart
        if not salary_gap.empty:
            gap_trend = salary_gap[salary_gap["year"].isin(selected_year_cols2)].groupby(["occupation","year"])["gap"].mean().reset_index()
            
            fig_line_gap = px.line(gap_trend, x="year", y="gap", color = "occupation",
                               title="<b>Year-over-Year Gender Salary Gap Trends by Occupation (Men − Women)</b>", markers=True)
            fig_line_gap.update_layout(xaxis_title="Year", yaxis_title="Monthly Income Gap", legend_title_text='Occupation')
            st.plotly_chart(fig_line_gap, use_container_width=True)
    else:
        st.info("No salary data available for the selected period. Please adjust the year range.")