import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("clean_data_combined.csv")
df2 = pd.read_csv("Industry and Occupation.csv")

# Set up the page
st.set_page_config(
    page_title="Singapore Employment Trends",
    layout="wide")

# Page title and information
st.title("📊 Singapore Employment Trends (2000-2024)")
st.info("Explore how employment in Singapore changed across different demographics and occupation between 2000 and 2024.")
st.caption("Data Source: SingStat")
st.divider()

# Get list of year column and sort it
year_list = []
for i in df.columns:
    if i.isdigit():
        year_list.append(int(i))
year_list = sorted(year_list)

# Get the unique values for filter values
gender_list = sorted(df["Sex"].unique().tolist())
age_list = sorted(df["Age Group"].unique().tolist())
job_list = sorted(df["Occupation"].unique().tolist())

# Set a default data for filter
default_years = (year_list[0], year_list[-1])
default_gender = ["All"]
default_age = ["All Ages"]
default_jobs = ["All Occupations"]

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

# Create page tabs
with right:
    with st.container(border=True):
        tab1, tab2, tab3, tab4 = st.tabs([
            "Executive Summary",
            "Demographic Breakdown",
            "Occupation Performance",
            "Industry × Occupation Analysis"
            ])

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

# TAB 1: Executive Summary
with tab1:
    st.subheader("Executive Summary")

    total_latest = filtered_data[latest_col].sum()
    total_prev = filtered_data[prev_col].sum()
    total_prev2 = filtered_data[prev2_col].sum()


    # Calculate YoY growth
    growth = ((total_latest - total_prev) / total_prev * 100) if total_prev else 0
    growth_prev = ((total_prev - total_prev2) / total_prev2 * 100) if total_prev2 else 0
    change = round(growth - growth_prev, 2)

    # Total Period Growth Metrics
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=f"Total Growth ({year_min} to {year_max})",
            value=f"{period_growth:.2f}%"
        )
        st.caption("For the entire selected period")
        
    with col2:
        grand_total_latest_year = df.loc[(df['Age Group'] == 'All Ages') & (df['Occupation'] == 'All Occupations') & (df['Sex'] == 'All'), latest_col].item()
        numeric_total = float(grand_total_latest_year)
        st.metric(
            label=f"Total Employment ({latest_col}) - (in Thousands)",
            value=f"{numeric_total:.1f}",
            delta=f"{growth:.2f}%"
        )
        st.caption(f"Year-over-year vs. {prev_col}")
      
    with col3:
        st.metric(
            label=f"YoY Growth Rate ({latest_col})", 
            value=f"{growth:.2f}%", 
            delta=f"{change:.2f} pp"
        )
        st.caption(f"Growth momentum vs. {prev_col}")

    with col4:
        st.metric(
            label=f"Female Employment ({latest_col})",
            value=f"{female_ratio:.1f}%"
        )
        st.caption(f"{female_sum:,.0f} Female / {male_sum:,.0f} Male")

    st.divider()
    st.subheader(f"Highlights for the Period ({year_min}–{year_max})")

    if year_min < year_max:
        start_col = str(year_min)
        end_col = str(year_max)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Occupation Highlights**")
            occ_filtered = filtered_data[filtered_data["Occupation"] != "All Occupations"]
            occ_analysis = occ_filtered.groupby("Occupation")[[start_col, end_col]].sum()
            occ_analysis = occ_analysis[occ_analysis[start_col] > 0]
            if not occ_analysis.empty:
                occ_analysis["growth"] = ((occ_analysis[end_col] - occ_analysis[start_col]) / occ_analysis[start_col]) * 100
                fastest_occ = occ_analysis['growth'].idxmax()
                fastest_occ_growth = occ_analysis['growth'].max()
                slowest_occ = occ_analysis['growth'].idxmin()
                slowest_occ_growth = occ_analysis['growth'].min()
                st.success(f"🚀 **Fastest Growing:** {fastest_occ} ({fastest_occ_growth:+.2f}%)")
                st.error(f"📉 **Slowest Growing:** {slowest_occ} ({slowest_occ_growth:+.2f}%)")
            else:
                st.info("No occupation data to compare for this period.")
        with col2:
            st.markdown("**Age Group Highlights**")
            age_filtered = filtered_data[filtered_data["Age Group"] != "All Ages"]
            age_analysis = age_filtered.groupby("Age Group")[[start_col, end_col]].sum()
            age_analysis = age_analysis[age_analysis[start_col] > 0]
            if not age_analysis.empty:
                age_analysis["growth"] = ((age_analysis[end_col] - age_analysis[start_col]) / age_analysis[start_col]) * 100
                fastest_age = age_analysis['growth'].idxmax()
                fastest_age_growth = age_analysis['growth'].max()
                slowest_age = age_analysis['growth'].idxmin()
                slowest_age_growth = age_analysis['growth'].min()
                st.success(f"🚀 **Fastest Growing:** {fastest_age} ({fastest_age_growth:+.2f}%)")
                st.error(f"📉 **Slowest Growing:** {slowest_age} ({slowest_age_growth:+.2f}%)")
            else:
                st.info("No age group data to compare for this period.")
    else:
        st.info("Select a period longer than one year to see growth highlights.")

    st.divider()
    
    # --- VISUALIZATION REVISED ---
    st.subheader("Employment Trends Overview")
    col1, col2 = st.columns([2, 1])

    with col1:
        # Create a tidy dataframe for plotting
        if "All Ages" in selected_age and "All Occupations" in selected_jobs and "All" in selected_age:
            trend_df = filtered_data[selected_year_cols].sum().reset_index()
            trend_df.columns = ["Year", "Total Employment"]
            trend_df['Year'] = pd.to_numeric(trend_df['Year'])
            fig = px.line(trend_df, x="Year", y="Total Employment", title="<b>Overall Employment Trend in Singapore</b>", markers=True)
        else:
            # More detailed breakdown if filters are applied
            trend_df = filtered_data.melt(id_vars=["Sex", "Age Group", "Occupation"], value_vars=selected_year_cols, var_name="Year", value_name="Employment")
            trend_df['Year'] = pd.to_numeric(trend_df['Year'])
            # Group by Year and the most relevant filter
            grouping_var = "Occupation" if len(selected_jobs) > 1 and "All Occupations" not in selected_jobs else "Age Group"
            grouped_trend = trend_df.groupby(["Year", grouping_var])["Employment"].sum().reset_index()
            fig = px.line(grouped_trend, x="Year", y="Employment", color=grouping_var, title=f"<b>Employment Trend by {grouping_var}</b>", markers=True)
        
        fig.update_layout(legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        gender_dist_df = pd.DataFrame({
            'Gender': ['Female', 'Male'],
            'Count': [female_sum, male_sum]
        })
        fig = px.pie(gender_dist_df, values='Count', names='Gender', 
                     title=f"<b>Gender Distribution in {year_max}</b>",
                     hole=0.4, color_discrete_map={'Female':'#FF69B4', 'Male':'#6495ED'})
        fig.update_traces(textinfo='percent+label', pull=[0.05, 0])
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: Demographic Breakdown
with tab2:
    st.subheader(f"Snapshot of Employment by Age Group ({year_max})")
    age_filtered = filtered_data[filtered_data["Age Group"] != "All Ages"]
    age_snapshot = age_filtered.groupby("Age Group")[latest_col].sum().sort_values(ascending=False).reset_index()
    age_snapshot.columns = ['Age Group', 'Employment Count']

    fig_bar = px.bar(age_snapshot, x='Age Group', y='Employment Count', 
                     title=f"<b>Employment Count by Age Group in {year_max}</b>",
                     color='Age Group', text_auto='.2s')
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader(f"Employment Trends by Age Group ({year_min}–{year_max})")
    age_trend = age_filtered.groupby("Age Group")[selected_year_cols].sum().T
    age_trend.index = age_trend.index.astype(int)
    
    fig_line = px.line(age_trend, x=age_trend.index, y=age_trend.columns,
                       title="<b>Year-over-Year Employment Trends by Age Group</b>", markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Total Employment", legend_title_text='Age Group')
    st.plotly_chart(fig_line, use_container_width=True)

# TAB 3: Occupation Performance
with tab3:
    st.subheader(f"Snapshot of Employment by Occupation ({year_max})")
    occ_filtered = filtered_data[filtered_data["Occupation"] != "All Occupations"]
    occ_snapshot = occ_filtered.groupby("Occupation")[latest_col].sum().sort_values(ascending=False).reset_index()
    occ_snapshot.columns = ['Occupation', 'Employment Count']

    fig_bar = px.bar(occ_snapshot, x='Occupation', y='Employment Count', 
                     title=f"<b>Employment Count by Occupation in {year_max}</b>",
                     color='Occupation', text_auto='.2s')
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    st.subheader(f"Employment Trends by Occupation ({year_min}–{year_max})")
    occ_trend = occ_filtered.groupby("Occupation")[selected_year_cols].sum().T
    occ_trend.index = occ_trend.index.astype(int)
    
    fig_line = px.line(occ_trend, x=occ_trend.index, y=occ_trend.columns,
                       title="<b>Year-over-Year Employment Trends by Occupation</b>", markers=True)
    fig_line.update_layout(xaxis_title="Year", yaxis_title="Total Employment", legend_title_text='Occupation')
    st.plotly_chart(fig_line, use_container_width=True)

# Tab 4: Industry and Occupation
import plotly.express as px
import plotly.graph_objects as go
with tab4:
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
        y_min = int(filtered["year"].min())
        y_max = int(filtered["year"].max())
        selected_years = [y for y in year_list if y_min <= y <= y_max]
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
        textfont_size=12,          # bigger % numbers
        cliponaxis=False
    )
    fig3.update_layout(
        height=900,                # <-- key: taller figure
        margin=dict(l=70, r=260, t=80, b=200),
        legend=dict(orientation="v", y=1.0, x=1.02),
        xaxis_title="Industry",
        yaxis_title="Share of employment",
    )
    fig3.update_xaxes(tickangle=-45, tickfont=dict(size=11))
    fig3.update_yaxes(range=[0, 1], tickformat=".0%")

    st.plotly_chart(fig3, use_container_width=True)