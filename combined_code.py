import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re # Added missing import
import matplotlib.pyplot as plt # Added missing import

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

# Create page tabs
with right:
    with st.container(border=True):
        # Corrected tab name list to be valid
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Executive Summary",
            "Demographic Breakdown",
            "Industry Performance",
            "Occupation Performance",
            "Unemployment Trend",
            "Salary Trend"
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
        if "All Ages" in selected_age and "All Occupations" in selected_jobs and "All" in selected_gender:
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
    fig_bar.update_traces(textposition='outside', cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader(f"Employment Trends by Age Group ({year_min}–{year_max})")
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

    # Helper: year columns within the current selection
    selected_year_cols = [str(y) for y in year_list if year_min <= y <= year_max]
    end_year = str(year_max)
    start_year_for_growth = str(year_min)

    # 1) Employment Trend (Overall) — ignores filters
    st.subheader("1️⃣ Employment Trend (Overall)")
    overall_all = df[
        (df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ]
    trend_all = overall_all.melt(value_vars=year_cols, var_name="Year", value_name="Employment")
    trend_all["Year"] = trend_all["Year"].astype(int)

    fig1 = px.line(trend_all, x="Year", y="Employment", markers=True,
                   title="Overall Employment Trend (2000–2024)")
    st.plotly_chart(fig1, use_container_width=True)

    # 2) Gender trend — responds ONLY to gender filter
    st.subheader("2️⃣ Employment Trend by Gender (All Occupations)")
    gsrc = df[
        (df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] != "All")
    ].copy()
    # CORRECTED: Used selected_gender instead of selected_sex
    if "All" not in selected_gender:
        gsrc = gsrc[gsrc["Sex"].isin(selected_gender)]

    g_melt = gsrc.melt(id_vars=["Sex"], value_vars=year_cols,
                       var_name="Year", value_name="Employment")
    g_melt["Year"] = g_melt["Year"].astype(int)

    fig2 = px.line(g_melt, x="Year", y="Employment", color="Sex",
                   markers=True, title="Employment Trend by Gender")
    st.plotly_chart(fig2, use_container_width=True)

    # 3) Share of Age Groups — shows only the selected age groups 
    st.subheader("3️⃣ Share of Age Groups in Workforce by Year (Stacked)")
    age_src = df[
        (df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Sex"] == "All") &
        (df["Age Group"] != "All Ages")
    ].copy()
    if "All Ages" not in selected_age:
        age_src = age_src[age_src["Age Group"].isin(selected_age)]

    age_melt = age_src.melt(id_vars=["Age Group"], value_vars=year_cols,
                            var_name="Year", value_name="Employment")
    age_melt["Year"] = age_melt["Year"].astype(int)
    tot = age_melt.groupby("Year")["Employment"].transform("sum")
    age_melt["Share (%)"] = (age_melt["Employment"] / tot) * 100

    fig3 = px.area(age_melt, x="Year", y="Share (%)", color="Age Group",
                   title="Share of Age Groups in Workforce (Stacked)",
                   color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig3, use_container_width=True)

    # 4) Trend by Occupation — shows only selected occupations 
    st.subheader("4️⃣ Employment Trend by Occupation")
    occ_src = df[
        (~df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()
    # CORRECTED: Used selected_jobs instead of selected_occ
    if "All Occupations" not in selected_jobs:
        occ_src = occ_src[occ_src["Occupation"].isin(selected_jobs)]

    occ_melt = occ_src.melt(id_vars=["Occupation"], value_vars=year_cols,
                            var_name="Year", value_name="Employment")
    occ_melt["Year"] = occ_melt["Year"].astype(int)

    fig4 = px.line(occ_melt, x="Year", y="Employment", color="Occupation",
                   markers=True, title="Employment Trend by Occupation (Filtered)")
    st.plotly_chart(fig4, use_container_width=True)

    # 5) Top Growing & Declining — uses selected year range for growth 
    st.subheader(f"5️⃣ Top 4 Growing & Declining Occupations ({year_min}–{year_max})")

    growth_base = df[
        (~df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()

    if start_year_for_growth in growth_base.columns and end_year in growth_base.columns:
        growth_base[start_year_for_growth] = pd.to_numeric(growth_base[start_year_for_growth], errors="coerce")
        growth_base[end_year] = pd.to_numeric(growth_base[end_year], errors="coerce")
        growth_base = growth_base.dropna(subset=[start_year_for_growth, end_year])

        growth_base["Growth %"] = (
            (growth_base[end_year] - growth_base[start_year_for_growth]) /
            growth_base[start_year_for_growth] * 100
        )

        top_grow = growth_base.sort_values("Growth %", ascending=False).head(4)
        top_decl = growth_base.sort_values("Growth %", ascending=True).head(4)
    else:
        top_grow = growth_base.head(0)
        top_decl = growth_base.head(0)

    c1, c2 = st.columns(2)
    with c1:
        fig5a = px.bar(top_grow, x="Growth %", y="Occupation", orientation="h",
                       color="Occupation",
                       text=top_grow["Growth %"].apply(lambda x: f"{x:.1f}%"),
                       title=f"Top 4 Growing Occupations ({year_min}–{year_max})")
        fig5a.update_traces(textposition="outside")
        fig5a.update_layout(showlegend=False)
        st.plotly_chart(fig5a, use_container_width=True)

    with c2:
        fig5b = px.bar(top_decl, x="Growth %", y="Occupation", orientation="h",
                       color="Occupation",
                       text=top_decl["Growth %"].apply(lambda x: f"{x:.1f}%"),
                       title=f"Top 4 Declining Occupations ({year_min}–{year_max})")
        fig5b.update_traces(textposition="outside")
        fig5b.update_layout(showlegend=False)
        st.plotly_chart(fig5b, use_container_width=True)

    # 6) Gender Distribution — uses selected end year + occ + gender filters 
    st.subheader(f"7️⃣ Gender Distribution by Occupation ({end_year})")
    gender_occ = df[
        (df["Age Group"] == "All Ages") &
        (df["Sex"] != "All") &
        (~df["Occupation"].str.contains("All Occupation", case=False))
    ].copy()
    # CORRECTED: Used selected_jobs instead of selected_occ
    if "All Occupations" not in selected_jobs:
        gender_occ = gender_occ[gender_occ["Occupation"].isin(selected_jobs)]
    # CORRECTED: Used selected_gender instead of selected_sex
    if "All" not in selected_gender:
        gender_occ = gender_occ[gender_occ["Sex"].isin(selected_gender)]

    gender_occ[end_year] = pd.to_numeric(gender_occ[end_year], errors="coerce")
    pivot_gender = gender_occ.pivot_table(index="Occupation", columns="Sex", values=end_year, aggfunc="sum").fillna(0)
    pivot_share_gen = pivot_gender.div(pivot_gender.sum(axis=1), axis=0) * 100

    fig7, ax7 = plt.subplots(figsize=(10, 6))
    pivot_share_gen.plot(kind="barh", stacked=True, color=["#1f77b4", "#d62728"], ax=ax7)
    ax7.set_title(f"Gender Distribution by Occupation ({end_year})")
    ax7.set_xlabel("Share (%)")
    ax7.set_ylabel("Occupation")
    ax7.legend(title="Gender", bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig7)

    # 7) Age × Gender × Occupation — uses end year + occ + gender filters
    st.subheader(f"8️⃣ Age × Gender × Occupation Distribution ({end_year})")

    dist = df[
        (df["Age Group"] != "All Ages") &
        (df["Sex"] != "All") &
        (~df["Occupation"].str.contains("All Occupation", case=False))
    ].copy()

    # Apply filters
    # CORRECTED: Used selected_jobs instead of selected_occ
    if "All Occupations" not in selected_jobs:
        dist = dist[dist["Occupation"].isin(selected_jobs)]
    # CORRECTED: Used selected_gender instead of selected_sex
    if "All" not in selected_gender:
        dist = dist[dist["Sex"].isin(selected_gender)]
    if "All Ages" not in selected_age:
        dist = dist[dist["Age Group"].isin(selected_age)]

    dist[end_year] = pd.to_numeric(dist[end_year], errors="coerce")

    def _age_num(lbl: str):
        m = re.findall(r"\d+", str(lbl))
        return int(m[0]) if m else 999

    age_cat = sorted(dist["Age Group"].unique(), key=_age_num)
    dist["Age Group"] = pd.Categorical(dist["Age Group"], categories=age_cat, ordered=True)

    fig8 = px.bar(
        dist, x="Age Group", y=end_year, color="Sex",
        facet_col="Occupation", facet_col_wrap=2,
        barmode="group",
        title=f"Age × Gender × Occupation Distribution ({end_year})",
        color_discrete_map={"Male": "#1f77b4", "Female": "#e377c2"}
    )
    fig8.update_layout(legend_title_text="Gender")
    fig8.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig8, use_container_width=True)

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