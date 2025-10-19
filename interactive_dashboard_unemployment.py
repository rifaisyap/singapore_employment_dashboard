import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================================== 
# 0. Page Configuration
# ============================================================== 
st.set_page_config(page_title="Singapore Unemployment Insights", layout="wide")
st.title("🔍 Singapore Unemployment Rate Analysis Dashboard (2000–2024)")
st.info("Explore how unemployment rate in Singapore changed across different age groups and qualification between 2000 and 2024.")
st.caption("Data Source: SingStat")
st.divider()

# ============================================================== 
# 1. Sidebar Filters
# ============================================================== 
st.sidebar.header("🔎 Filters")

# Load datasets
df_age = pd.read_csv("unemployment_by_age.csv")
df_sex = pd.read_csv("unemployment_by_sex.csv")
df_qual = pd.read_csv("unemployment_by_qualification.csv")

# Options
year_list = sorted(df_age["Year"].unique())
age_list = sorted(df_age["Age Group"].unique())
gender_list = sorted(df_sex["Sex"].unique())
qual_list = sorted(df_qual["Highest Qualification"].unique())

# Sidebar selections
year_range = st.sidebar.slider("Select Year Range", min_value=int(year_list[0]), max_value=int(year_list[-1]), value=(2000, 2024))
selected_age = st.sidebar.multiselect("Age Group", options=age_list + ["All"], default=["All"])
selected_gender = st.sidebar.multiselect("Gender", options=gender_list + ["All"], default=["All"])
selected_qual = st.sidebar.multiselect("Highest Qualification", options=qual_list + ["All"], default=["All"])

# Sidebar caption
st.sidebar.caption("⚠️ If you select **All**, the other filters for that category won't apply. To choose specific Gender, Age Group, or Highest Qualification, uncheck **All** first.")

# ============================================================== 
# 2. Filter Data
# ============================================================== 
# Age
df_age_f = df_age[(df_age["Year"] >= year_range[0]) & (df_age["Year"] <= year_range[1])]
if "All" not in selected_age:
    df_age_f = df_age_f[df_age_f["Age Group"].isin(selected_age)]

# Sex
df_sex_f = df_sex[(df_sex["Year"] >= year_range[0]) & (df_sex["Year"] <= year_range[1])]
if "All" not in selected_gender:
    df_sex_f = df_sex_f[df_sex_f["Sex"].isin(selected_gender)]

# Qualification
df_qual_f = df_qual[(df_qual["Year"] >= year_range[0]) & (df_qual["Year"] <= year_range[1])]
if "All" not in selected_qual:
    df_qual_f = df_qual_f[df_qual_f["Highest Qualification"].isin(selected_qual)]

# ============================================================== 
# 3. Overall Unemployment Trend
# ============================================================== 
st.header(f"Overall Unemployment Trend ({year_range[0]}–{year_range[1]})")

# Calculate overall unemployment
df_total = df_age_f[df_age_f["Age Group"]=="Total"] if "Total" in df_age_f["Age Group"].values else df_age_f.groupby("Year", as_index=False)["Unemployment"].mean()
df_total = df_total.sort_values("Year")

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(
    x=df_total["Year"], y=df_total["Unemployment"],
    mode='lines+markers',
    name='Unemployment Rate',
    line=dict(color='#e74c3c', width=3),
    marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='white')),
    fill='tozeroy',
    fillcolor='rgba(231, 76, 60, 0.2)'
))
events = {2003:"SARS Pandemic", 2008:"Global Financial Crisis", 2020:"COVID-19 Pandemic"}
for y, txt in events.items():
    if y in df_total["Year"].values:
        fig_total.add_annotation(x=y, y=df_total[df_total["Year"]==y]["Unemployment"].values[0],
                                 text=txt, showarrow=True, arrowhead=2, ax=0, ay=-40)
fig_total.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=500, hovermode="x unified")
st.plotly_chart(fig_total, use_container_width=True)

# Key Metrics for Overall Trend
col1, col2, col3, col4 = st.columns(4)
latest_rate = df_total[df_total["Year"]==year_range[1]]["Unemployment"].values[0] if year_range[1] in df_total["Year"].values else 0
max_rate = df_total["Unemployment"].max()
min_rate = df_total["Unemployment"].min()
avg_rate = df_total["Unemployment"].mean()
with col1:
    st.metric("Latest Rate", f"{latest_rate:.1f}%")
with col2:
    st.metric("Peak Rate", f"{max_rate:.1f}%")
with col3:
    st.metric("Lowest Rate", f"{min_rate:.1f}%")
with col4:
    st.metric("Average Rate", f"{avg_rate:.1f}%")

st.divider()

# ============================================================== 
# 4. Unemployment by Age Group
# ============================================================== 
st.header(f"Unemployment by Age Group ({year_range[1]})")
df_age_latest = df_age_f[df_age_f["Year"]==year_range[1]]
target_age_groups = ["15 - 24","25 - 29","30 - 39","40 - 49","50 - 59","60 & Over"]
df_age_latest = df_age_latest[df_age_latest["Age Group"].isin(target_age_groups)]
df_age_latest["Age Group"] = pd.Categorical(df_age_latest["Age Group"], categories=target_age_groups, ordered=True)
df_age_latest = df_age_latest.sort_values("Age Group")

fig_age = go.Figure()
colors_list = px.colors.sequential.Turbo
colors_mapped = [colors_list[int(i*len(colors_list)/len(df_age_latest))] for i in range(len(df_age_latest))]
for i in range(len(df_age_latest)):
    fig_age.add_trace(go.Bar(
        x=[df_age_latest.iloc[i]["Age Group"]],
        y=[df_age_latest.iloc[i]["Unemployment"]],
        marker_color=colors_mapped[i],
        name=df_age_latest.iloc[i]["Age Group"],
        showlegend=False
    ))
fig_age.add_trace(go.Scatter(
    x=df_age_latest["Age Group"],
    y=df_age_latest["Unemployment"],
    mode='lines+markers',
    line=dict(color='navy', width=3),
    marker=dict(size=12, color='white', line=dict(width=2.5, color='navy')),
    showlegend=False
))
fig_age.update_layout(xaxis_title="Age Group", yaxis_title="Unemployment Rate (%)", height=450)
st.plotly_chart(fig_age, use_container_width=True)

# Key Metrics Age Group
col1, col2, col3 = st.columns(3)
max_idx = df_age_latest["Unemployment"].idxmax()
min_idx = df_age_latest["Unemployment"].idxmin()
with col1:
    st.metric("Highest Unemployment", f"{df_age_latest.loc[max_idx, 'Age Group']}", f"{df_age_latest.loc[max_idx,'Unemployment']:.1f}%")
with col2:
    st.metric("Lowest Unemployment", f"{df_age_latest.loc[min_idx,'Age Group']}", f"{df_age_latest.loc[min_idx,'Unemployment']:.1f}%")
with col3:
    st.metric("Average Rate", f"{df_age_latest['Unemployment'].mean():.1f}%")

st.divider()

# ============================================================== 
# 5. Youth Unemployment by Gender
# ============================================================== 
st.header(f"Youth Unemployment by Gender (15-24 Age Group, {year_range[0]}–{year_range[1]})")
df_15_24 = df_sex_f[df_sex_f["Category"]=="15-24"]
fig_gender = go.Figure()
colors_gender = {"Males":"#e74c3c","Females":"#3498db"}
for sex in colors_gender.keys():
    df_sex_plot = df_15_24[df_15_24["Sex"]==sex].sort_values("Year")
    fig_gender.add_trace(go.Scatter(
        x=df_sex_plot["Year"], y=df_sex_plot["Unemployment"],
        mode='lines+markers', name=sex,
        line=dict(color=colors_gender[sex], width=3),
        marker=dict(size=6)
    ))
fig_gender.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=450, hovermode="x unified")
st.plotly_chart(fig_gender, use_container_width=True)

# Key Metrics Youth Gender
col1, col2, col3 = st.columns(3)
latest_year = df_15_24["Year"].max()
latest_data = df_15_24[df_15_24["Year"]==latest_year]
males_rate = latest_data[latest_data["Sex"]=="Males"]["Unemployment"].values[0] if len(latest_data[latest_data["Sex"]=="Males"])>0 else 0
females_rate = latest_data[latest_data["Sex"]=="Females"]["Unemployment"].values[0] if len(latest_data[latest_data["Sex"]=="Females"])>0 else 0
males_avg = df_15_24[df_15_24["Sex"]=="Males"]["Unemployment"].mean()
females_avg = df_15_24[df_15_24["Sex"]=="Females"]["Unemployment"].mean()
with col1:
    st.metric("Males Average", f"{males_avg:.1f}%")
with col2:
    st.metric("Females Average", f"{females_avg:.1f}%")
with col3:
    st.metric("Avg Gender Gap", f"{abs(males_avg-females_avg):.1f}%")

st.divider()

# ============================================================== 
# 6. Unemployment by Qualification
# ============================================================== 
st.header(f"Unemployment by Highest Qualification ({year_range[0]}–{year_range[1]})")
qual_unique = sorted(df_qual_f["Highest Qualification"].unique())
colors_qual = px.colors.qualitative.Set2
fig_qual = go.Figure()
for idx, qual in enumerate(qual_unique):
    df_qual_plot = df_qual_f[df_qual_f["Highest Qualification"]==qual].sort_values("Year")
    fig_qual.add_trace(go.Scatter(
        x=df_qual_plot["Year"], y=df_qual_plot["Unemployment"],
        mode='lines+markers', name=qual,
        line=dict(color=colors_qual[idx%len(colors_qual)], width=2.5),
        marker=dict(size=5)
    ))
fig_qual.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=600, hovermode="x unified", legend_title="Qualification")
st.plotly_chart(fig_qual, use_container_width=True)

# 2024 Comparison
st.subheader("2024 Unemployment by Qualification")
df_2024_qual = df_qual_f[df_qual_f["Year"]==year_range[1]].sort_values("Unemployment", ascending=False)
col1, col2 = st.columns([2,1])
with col1:
    fig_bar = px.bar(df_2024_qual, x="Unemployment", y="Highest Qualification", orientation='h', color="Unemployment", color_continuous_scale="RdYlGn_r", title="2024 Unemployment Rate by Qualification")
    fig_bar.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)
with col2:
    st.markdown("#### 2024 Rankings")
    for idx, row in df_2024_qual.iterrows():
        st.metric(row["Highest Qualification"], f"{row['Unemployment']:.1f}%")

# TAB 6: Unemployment Trend
with tab6:
    st.header("Unemployment Trend Analysis")
    st.info("This section analyzes unemployment rates using specialized datasets for age, gender, and education.")

    # --- 1. Initial Data Preparation for this Tab ---
    # First, filter all unemployment datasets by the main year slider from the sidebar
    df_age_filtered = df_age[(df_age['Year'] >= year_min) & (df_age['Year'] <= year_max)]
    df_sex_filtered = df_sex[(df_sex['Year'] >= year_min) & (df_sex['Year'] <= year_max)]
    df_qual_filtered = df_qual[(df_qual['Year'] >= year_min) & (df_qual['Year'] <= year_max)]

    # --- 2. Create In-Tab Filters for Age and Qualification ---
    st.subheader("🔎 Refine Unemployment Data")
    col1, col2 = st.columns(2)

    with col1:
        # Get available age groups from the already year-filtered data
        age_options = sorted(df_age_filtered["Age Group"].unique())
        # Create a multiselect filter for age group
        selected_age_unemployment = st.multiselect(
            "Filter by Age Group",
            options=age_options,
            default=age_options # Select all by default
        )

    with col2:
        # Get available qualifications from the already year-filtered data
        qual_options = sorted(df_qual_filtered["Highest Qualification"].unique())
        # Create a multiselect filter for qualification
        selected_qual = st.multiselect(
            "Filter by Qualification",
            options=qual_options,
            default=qual_options # Select all by default
        )
    
    st.divider()

    # --- 3. Apply In-Tab Filters ---
    # Now, apply the selections from the in-tab filters to our dataframes
    df_age_final = df_age_filtered[df_age_filtered["Age Group"].isin(selected_age_unemployment)]
    df_qual_final = df_qual_filtered[df_qual_filtered["Highest Qualification"].isin(selected_qual)]

    # ============================================================== 
    # Chart 1: Overall Unemployment Trend (Not affected by in-tab filters)
    # ============================================================== 
    st.subheader(f"Overall Unemployment Trend ({year_min}–{year_max})")
    
    # Use the year-filtered data before the in-tab age filter is applied for a true total
    df_total = df_age_filtered[df_age_filtered["Age Group"]=="Total"] if "Total" in df_age_filtered["Age Group"].values else df_age_filtered.groupby("Year", as_index=False)["Unemployment"].mean()
    df_total = df_total.sort_values("Year")

    if not df_total.empty:
        fig_total = go.Figure()
        fig_total.add_trace(go.Scatter(
            x=df_total["Year"], y=df_total["Unemployment"],
            mode='lines+markers', name='Unemployment Rate',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='white')),
            fill='tozeroy', fillcolor='rgba(231, 76, 60, 0.2)'
        ))
        # Add annotations for major economic events
        events = {2003:"SARS", 2008:"Global Financial Crisis", 2020:"COVID-19"}
        for y, txt in events.items():
            if y in df_total["Year"].values:
                fig_total.add_annotation(x=y, y=df_total[df_total["Year"]==y]["Unemployment"].values[0],
                                         text=txt, showarrow=True, arrowhead=2, ax=0, ay=-40)
        fig_total.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=500, hovermode="x unified")
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.warning("No overall unemployment data to display for the selected period.")

    st.divider()

    # ============================================================== 
    # Chart 2: Unemployment by Age Group (Uses the new Age filter)
    # ============================================================== 
    st.subheader(f"Unemployment by Age Group ({year_max})")
    
    # Proceed only if an age group has been selected in our new filter
    if not selected_age_unemployment:
        st.info("Please select at least one age group to see the breakdown.")
    else:
        df_age_latest = df_age_final[df_age_final["Year"]== year_max].sort_values("Age Group")
        
        fig_age = px.bar(
            df_age_latest,
            x="Age Group",
            y="Unemployment",
            color="Age Group",
            text="Unemployment",
            title=f"Unemployment Rate by Age Group in {year_max}"
        )
        fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_age.update_layout(xaxis_title="Age Group", yaxis_title="Unemployment Rate (%)", showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

    st.divider()

    # ============================================================== 
    # Chart 3: Youth Unemployment by Gender (Specific, not affected by filters)
    # ============================================================== 
    st.subheader(f"Youth (15-24) Unemployment by Gender ({year_min}–{year_max})")
    df_15_24 = df_sex_filtered[df_sex_filtered["Category"]=="15-24"]

    if not df_15_24.empty:
        fig_gender = px.line(
            df_15_24.sort_values("Year"),
            x="Year", y="Unemployment", color="Sex",
            markers=True,
            color_discrete_map={"Males":"#3498db", "Females":"#e74c3c"}
        )
        fig_gender.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=450, hovermode="x unified", legend_title="Gender")
        st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.warning("No youth unemployment data available for this period.")

    st.divider()

    # ============================================================== 
    # Chart 4: Unemployment by Qualification (Uses the new Qualification filter)
    # ============================================================== 
    st.subheader(f"Unemployment by Highest Qualification ({year_min}–{year_max})")
    
    # Proceed only if a qualification has been selected in our new filter
    if not selected_qual:
        st.info("Please select at least one qualification to see the trend.")
    else:
        fig_qual = px.line(
            df_qual_final.sort_values("Year"),
            x="Year", y="Unemployment", color="Highest Qualification",
            markers=True,
            title="Unemployment Rate Trends by Qualification"
        )
        fig_qual.update_layout(xaxis_title="Year", yaxis_title="Unemployment Rate (%)", height=500, hovermode="x unified", legend_title="Qualification")
        st.plotly_chart(fig_qual, use_container_width=True)
        
        # Comparison for the latest year
        st.subheader(f"Snapshot of Unemployment by Qualification ({year_max})")
        df_latest_qual = df_qual_final[df_qual_final["Year"]==year_max].sort_values("Unemployment", ascending=False)
        
        if not df_latest_qual.empty:
            fig_bar_qual = px.bar(
                df_latest_qual, x="Unemployment", y="Highest Qualification",
                orientation='h', color="Unemployment", color_continuous_scale="RdYlGn_r",
                title=f"{year_max} Unemployment Rate by Qualification"
            )
            fig_bar_qual.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar_qual, use_container_width=True)
        else:
            st.warning(f"No qualification data available for the year {year_max}.")
