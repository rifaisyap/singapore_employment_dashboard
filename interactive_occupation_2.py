
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import re

# 0)Page configuration
st.set_page_config(page_title="Singapore Employment Dashboard", layout="wide")
st.title("📊 Singapore Employment & Hiring Trends (2000–2024)")
st.caption("Data Source: SingStat | Interactive dashboard combining workforce and occupation insights.")
st.divider()

# 1Load dataset
df = pd.read_csv("clean_data_combined.csv")

# Detect year columns
year_cols = [c for c in df.columns if c.isdigit()]
for c in year_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

year_list = sorted([int(y) for y in year_cols])
latest_year = str(max(year_list))

# 2 Sidebar filters
st.sidebar.header("🔎 Filters")

year_min, year_max = st.sidebar.select_slider(
    "Select Year Range", options=year_list, value=(year_list[0], year_list[-1])
)

sex_opts = sorted(df["Sex"].unique().tolist())
age_opts = sorted(df["Age Group"].unique().tolist())
occ_opts = sorted(df["Occupation"].unique().tolist())

selected_sex = st.sidebar.multiselect("Select Gender", sex_opts, default=["All"])
selected_age = st.sidebar.multiselect("Select Age Group", age_opts, default=["All Ages"])
selected_occ = st.sidebar.multiselect("Select Occupation", occ_opts, default=["All Occupations"])

# Apply filters
filtered = df.copy()
if "All" not in selected_sex:
    filtered = filtered[filtered["Sex"].isin(selected_sex)]
if "All Ages" not in selected_age:
    filtered = filtered[filtered["Age Group"].isin(selected_age)]
if "All Occupations" not in selected_occ:
    filtered = filtered[filtered["Occupation"].isin(selected_occ)]

select_years = [str(y) for y in year_list if year_min <= y <= year_max]

# 3Tabs
tab1, tab2, tab3 = st.tabs([
    "Executive Summary",
    "Demographic Breakdown",
    "Occupation Performance"
])

# TAB 3: Occupation Performance (all charts obey filter logic)
with tab3:
    st.header("📈 Occupation Performance (Interactive)")

    # Helper: year columns within the current selection
    selected_year_cols = [str(y) for y in year_list if year_min <= y <= year_max]
    end_year = str(year_max)                     # for “latest” views
    start_year_for_growth = str(year_min)        # for growth calc

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
    if "All" not in selected_sex:                 # only apply gender filter here
        gsrc = gsrc[gsrc["Sex"].isin(selected_sex)]

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
    if "All Occupations" not in selected_occ:
        occ_src = occ_src[occ_src["Occupation"].isin(selected_occ)]

    occ_melt = occ_src.melt(id_vars=["Occupation"], value_vars=year_cols,
                            var_name="Year", value_name="Employment")
    occ_melt["Year"] = occ_melt["Year"].astype(int)

    fig4 = px.line(occ_melt, x="Year", y="Employment", color="Occupation",
                   markers=True, title="Employment Trend by Occupation (Filtered)")
    st.plotly_chart(fig4, use_container_width=True)

    # 5) Top Growing & Declining — uses selected year range for growth 
    st.subheader(f"5️⃣ Top 4 Growing & Declining Occupations ({year_min}–{year_max})")

    # base = all occupations, All Ages, All sex (so totals make sense)
    growth_base = df[
        (~df["Occupation"].str.contains("All Occupation", case=False)) &
        (df["Age Group"] == "All Ages") &
        (df["Sex"] == "All")
    ].copy()

    # compute growth using the selected window endpoints
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
        formatted_growth = []
        for val in top_grow["Growth %"]:
            formatted_growth.append("{:.1f}%".format(val))
        top_grow["Growth_label"] = formatted_growth

        # Create horizontal bar chart
        fig5a = px.bar(
            top_grow,
            x="Growth %",
            y="Occupation",
            orientation="h",
            color="Occupation",
            text="Growth_label",
            title=f"Top 4 Growing Occupations ({year_min}–{year_max})"
        )
        fig5a.update_traces(textposition="outside")
        fig5a.update_layout(showlegend=False)
        st.plotly_chart(fig5a, use_container_width=True)

    with c2:
        formatted_decline = []
        for val in top_decl["Growth %"]:
            formatted_decline.append("{:.1f}%".format(val))
        top_decl["Growth_label"] = formatted_decline

        # Create horizontal bar chart
        fig5b = px.bar(
            top_decl,
            x="Growth %",
            y="Occupation",
            orientation="h",
            color="Occupation",
            text="Growth_label",
            title=f"Top 4 Declining Occupations ({year_min}–{year_max})"
        )
        fig5b.update_traces(textposition="outside")
        fig5b.update_layout(showlegend=False)
        st.plotly_chart(fig5b, use_container_width=True)


    # 6) Gender Distribution — uses selected end year + occ + gender filters 
    st.subheader(f"6️⃣ Gender Distribution by Occupation ({end_year})")

# Data filtering 
gender_occ = df[
    (df["Age Group"] == "All Ages") &
    (df["Sex"] != "All") &
    (~df["Occupation"].str.contains("All Occupation", case=False))
].copy()

# Filter by selected occupations and genders if not "All"
if "All Occupations" not in selected_occ:
    gender_occ = gender_occ[gender_occ["Occupation"].isin(selected_occ)]
if "All" not in selected_sex:
    gender_occ = gender_occ[gender_occ["Sex"].isin(selected_sex)]

#  Data cleaning and preparation 
gender_occ[end_year] = pd.to_numeric(gender_occ[end_year], errors="coerce")

# Pivot the table to get total counts by occupation and gender
pivot_gender = gender_occ.pivot_table(
    index="Occupation", columns="Sex", values=end_year, aggfunc="sum"
).fillna(0)

# Calculate percentage share by gender within each occupation
pivot_share_gen = pivot_gender.div(pivot_gender.sum(axis=1), axis=0) * 100

# Convert wide format to long format for Plotly Express
pivot_share_gen = pivot_share_gen.reset_index().melt(
    id_vars="Occupation", var_name="Gender", value_name="Share (%)"
)

# Plot with Plotly Express
fig6 = px.bar(
    pivot_share_gen,
    x="Share (%)",
    y="Occupation",
    color="Gender",
    orientation="h",
    text="Share (%)",
    color_discrete_map={"Male": "#004C99", "Female": "#FF9999"},
    title=f"Gender Distribution by Occupation ({end_year})"
)

# Style and layout adjustments
fig6.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="inside"
)
fig6.update_layout(
    barmode="stack",                      # Show male/female stacked horizontally
    xaxis_title="Share (%)",
    yaxis_title="Occupation",
    plot_bgcolor="white",
    showlegend=True,
    legend_title_text="Gender",
    margin=dict(l=80, r=60, t=60, b=40)
)

# Display in Streamlit 
st.plotly_chart(fig6, use_container_width=True)


# 7) Age × Gender × Occupation — uses end year + occ + gender filters
st.subheader(f"7️⃣ Age × Gender × Occupation Distribution ({end_year})")

dist = df[
    (df["Age Group"] != "All Ages") &
    (df["Sex"] != "All") &
    (~df["Occupation"].str.contains("All Occupation", case=False))
].copy()

# Apply filters
if "All Occupations" not in selected_occ:
    dist = dist[dist["Occupation"].isin(selected_occ)]
if "All" not in selected_sex:
    dist = dist[dist["Sex"].isin(selected_sex)]
if "All Ages" not in selected_age:
    dist = dist[dist["Age Group"].isin(selected_age)]  

# Convert values to numeric
dist[end_year] = pd.to_numeric(dist[end_year], errors="coerce")

# Sort age groups numerically for nicer x-order
def _age_num(lbl: str):
    m = re.findall(r"\d+", str(lbl))
    return int(m[0]) if m else 999

age_cat = sorted(dist["Age Group"].unique(), key=_age_num)
dist["Age Group"] = pd.Categorical(dist["Age Group"], categories=age_cat, ordered=True)

# Plot
fig8 = px.bar(
    dist,
    x="Age Group",
    y=end_year,
    color="Sex",
    facet_col="Occupation",
    facet_col_wrap=3,
    facet_col_spacing=0.08,
    facet_row_spacing=0.12,
    height=1200,
    barmode="group",
    title=f"Age × Gender × Occupation Distribution ({end_year})",
    color_discrete_map={"Male": "#004C99", "Female": "#FF9999"}
)
fig8.update_xaxes(title_text="Age Group", showgrid=True, matches=None)
fig8.update_yaxes(title_text="Employed Persons (thousands)", showgrid=True, matches=None)

#Unified layout and axis formatting
fig8.update_layout(
    margin=dict(l=60, r=40, t=80, b=60),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(size=13),
    legend_title_text="Gender",
    
)

for annotation in fig8.layout.annotations:
    if "Occupation=" in annotation.text:
        annotation.text = annotation.text.split("=")[-1]

st.plotly_chart(fig8, use_container_width=True)