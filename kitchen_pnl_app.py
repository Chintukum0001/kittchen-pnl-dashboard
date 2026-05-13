"""
Kittchen Cloud Kitchen - P&L Analytics Dashboard
=================================================
Python  : 3.10+
Streamlit: 1.35+
Pandas  : 2.2+
Plotly  : 5.22+
openpyxl: 3.1+

Run with:
    streamlit run kitchen_pnl_app.py

Place 'Kittchen PNL Data.xlsx' in the same directory as this script.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Kittchen P&L Dashboard",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        color: white; padding: 22px 30px; border-radius: 12px; margin-bottom: 18px;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p  { margin: 4px 0 0; opacity: 0.8; font-size: 0.95rem; }
    .section-title {
        background: #fff8e1; border-left: 5px solid #ffc107;
        padding: 8px 14px; border-radius: 4px;
        font-weight: 700; font-size: 1.05rem; margin: 16px 0 10px;
    }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; }
    .block-container { padding-top: 1.2rem !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kittchen PNL Data.xlsx")


@st.cache_data(ttl=300, show_spinner="Loading P&L data ...")
def load_data(filepath):
    df = pd.read_excel(filepath, header=1)
    df = df.rename(columns={
        "KITCHEN EBITDA": "EBITDA",
        "GROSS MARGIN"  : "GM",
        "ZONE MAPPING"  : "ZONE",
    })
    df["GM%"]       = (df["GM"]      / df["NET REVENUE"] * 100).round(2)
    df["EBITDA%"]   = (df["EBITDA"]  / df["NET REVENUE"] * 100).round(2)
    df["VARIANCE%"] = (df["VARIANCE"] / df["IDEAL FOOD COST"] * 100).round(2)
    df["NET REVENUE (Lacs)"] = (df["NET REVENUE"] / 100_000).round(2)

    rev_bins   = [0, 1_500_000, 2_500_000, 3_500_000, 4_500_000, float("inf")]
    rev_labels = ["(a) Below INR 15 lacs","(b) INR 15 to 25 lacs",
                  "(c) INR 25 to 35 lacs","(d) INR 35 to 45 lacs","(e) Above INR 45 lacs"]
    df["REVENUE CATEGORY"] = pd.cut(df["NET REVENUE"], bins=rev_bins, labels=rev_labels, right=False)

    df["VARIANCE CATEGORY"] = pd.cut(
        df["VARIANCE%"],
        bins=[-np.inf, 2, 3, 5, np.inf],
        labels=["(a) Var < 2%","(b) Var 2% to 3%","(c) Var 3% to 5%","(d) Var > 5%"],
    )
    df["MONTH_DT"] = pd.to_datetime(df["MONTH"], format="%b-%Y")
    df = df.sort_values("MONTH_DT").reset_index(drop=True)
    return df


if not os.path.exists(DATA_FILE):
    st.error(f"Data file not found: {DATA_FILE}")
    st.stop()

df = load_data(DATA_FILE)
SORTED_MONTHS   = list(dict.fromkeys(df.sort_values("MONTH_DT")["MONTH"].tolist()))
REV_CATS_ORDER  = ["(a) Below INR 15 lacs","(b) INR 15 to 25 lacs",
                   "(c) INR 25 to 35 lacs","(d) INR 35 to 45 lacs","(e) Above INR 45 lacs"]
VAR_CATS_ALL    = ["(a) Var < 2%","(b) Var 2% to 3%","(c) Var 3% to 5%","(d) Var > 5%"]

# -----------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🍳 Kittchen Cloud Kitchen - P&amp;L Analytics Dashboard</h1>
    <p>Profit &amp; Loss insights across kitchen stores, cities and months | Data auto-refreshes every 5 minutes</p>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Stores",   f"{df['STORE'].nunique():,}")
k2.metric("Total Cities",   f"{df['CITY'].nunique()}")
k3.metric("Months Covered", f"{df['MONTH'].nunique()}")
k4.metric("Avg GM%",        f"{df['GM%'].mean():.1f}%")
k5.metric("Avg EBITDA%",    f"{df['EBITDA%'].mean():.1f}%")
k6.metric("Avg Variance%",  f"{df['VARIANCE%'].mean():.2f}%")

st.divider()

tab1, tab2 = st.tabs([
    "🏪  Dashboard 1 - Kitchen Level PNL",
    "📊  Dashboard 2 - Variance Level PNL",
])


# =======================================================================
#  DASHBOARD 1 : KITCHEN LEVEL PNL
# =======================================================================
with tab1:
    st.markdown('<div class="section-title">🏪 KITCHEN SNAPSHOT - P&amp;L by Store &amp; Month</div>',
                unsafe_allow_html=True)

    sr1, sr2, sr3 = st.columns(3)
    with sr1:
        ebitda_range = st.slider("Select EBITDA Range (INR)",
            float(df["EBITDA"].min()), float(df["EBITDA"].max()),
            (float(df["EBITDA"].min()), float(df["EBITDA"].max())), format="%.0f")
    with sr2:
        rev_range = st.slider("Select Net Revenue Range (INR)",
            float(df["NET REVENUE"].min()), float(df["NET REVENUE"].max()),
            (float(df["NET REVENUE"].min()), float(df["NET REVENUE"].max())), format="%.0f")
    with sr3:
        gm_range = st.slider("Select GM% Range",
            float(df["GM%"].min()), float(df["GM%"].max()),
            (float(df["GM%"].min()), float(df["GM%"].max())), format="%.1f%%")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1: f_zone  = st.multiselect("Zone",  sorted(df["ZONE"].unique()),  placeholder="All")
    with fc2: f_city  = st.multiselect("City",  sorted(df["CITY"].unique()),  placeholder="All")
    with fc3: f_store = st.multiselect("Store", sorted(df["STORE"].unique()), placeholder="All")
    with fc4: f_month = st.multiselect("Month", SORTED_MONTHS,                placeholder="All")

    fc5, fc6, fc7, fc8 = st.columns(4)
    with fc5: f_rev_cohort    = st.multiselect("Revenue Cohort",  df["REVENUE COHORT"].unique(),  placeholder="All")
    with fc6: f_cm_cohort     = st.multiselect("CM Cohort",       df["CM COHORT"].unique(),        placeholder="All")
    with fc7: f_ebitda_cat    = st.multiselect("EBITDA Category", df["EBITDA CATEGORY"].unique(),  placeholder="All")
    with fc8: f_ebitda_cohort = st.multiselect("EBITDA Cohort",   df["EBITDA COHORT"].unique(),    placeholder="All")

    fdf = df.copy()
    if f_zone:          fdf = fdf[fdf["ZONE"].isin(f_zone)]
    if f_city:          fdf = fdf[fdf["CITY"].isin(f_city)]
    if f_store:         fdf = fdf[fdf["STORE"].isin(f_store)]
    if f_month:         fdf = fdf[fdf["MONTH"].isin(f_month)]
    if f_rev_cohort:    fdf = fdf[fdf["REVENUE COHORT"].isin(f_rev_cohort)]
    if f_cm_cohort:     fdf = fdf[fdf["CM COHORT"].isin(f_cm_cohort)]
    if f_ebitda_cat:    fdf = fdf[fdf["EBITDA CATEGORY"].isin(f_ebitda_cat)]
    if f_ebitda_cohort: fdf = fdf[fdf["EBITDA COHORT"].isin(f_ebitda_cohort)]
    fdf = fdf[fdf["EBITDA"].between(*ebitda_range)
              & fdf["NET REVENUE"].between(*rev_range)
              & fdf["GM%"].between(*gm_range)]

    st.caption(f"Showing **{len(fdf):,}** records | **{fdf['STORE'].nunique()}** stores | "
               f"**{fdf['CITY'].nunique()}** cities | **{fdf['MONTH'].nunique()}** months")

    if fdf.empty:
        st.warning("No data matches the current filters.")
    else:
        st.markdown("#### Kitchen Snapshot Table")
        months_to_show = ([m for m in SORTED_MONTHS if m in fdf["MONTH"].unique()]
                          if not f_month else [m for m in SORTED_MONTHS if m in f_month])

        pivot_rows = []
        for store in sorted(fdf["STORE"].unique()):
            sdf = fdf[fdf["STORE"] == store]
            row = {"Store": store}
            for month in months_to_show:
                mdf = sdf[sdf["MONTH"] == month]
                if not mdf.empty:
                    row[f"{month} | Net Rev"]  = f"INR {mdf['NET REVENUE'].sum():,.0f}"
                    row[f"{month} | GM%"]      = f"{mdf['GM%'].mean():.1f}%"
                    row[f"{month} | EBITDA"]   = f"INR {mdf['EBITDA'].sum():,.0f}"
                    row[f"{month} | EBITDA%"]  = f"{mdf['EBITDA%'].mean():.1f}%"
                else:
                    for s in ("Net Rev","GM%","EBITDA","EBITDA%"):
                        row[f"{month} | {s}"] = "-"
            pivot_rows.append(row)

        pivot_df = pd.DataFrame(pivot_rows).set_index("Store")
        st.dataframe(pivot_df, use_container_width=True, height=420)

        st.markdown("#### Filtered Aggregates")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Net Revenue", f"INR {fdf['NET REVENUE'].sum():,.0f}")
        m2.metric("Total EBITDA",      f"INR {fdf['EBITDA'].sum():,.0f}")
        m3.metric("Avg GM%",           f"{fdf['GM%'].mean():.1f}%")
        m4.metric("Avg EBITDA%",       f"{fdf['EBITDA%'].mean():.1f}%")

        st.markdown("#### Visual Analytics")
        ch1, ch2 = st.columns(2)
        with ch1:
            agg_m = (fdf.groupby("MONTH_DT", sort=True)
                     .agg(NET_REVENUE=("NET REVENUE","sum"), EBITDA=("EBITDA","sum"))
                     .reset_index())
            agg_m["Month"] = agg_m["MONTH_DT"].dt.strftime("%b-%Y")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=agg_m["Month"], y=agg_m["NET_REVENUE"],
                                     name="Net Revenue", marker_color="#2196F3"))
            fig_bar.add_trace(go.Bar(x=agg_m["Month"], y=agg_m["EBITDA"],
                                     name="EBITDA", marker_color="#4CAF50"))
            fig_bar.update_layout(title="Monthly Net Revenue vs EBITDA",
                                  barmode="group", legend_orientation="h",
                                  margin=dict(t=40,b=20), plot_bgcolor="white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch2:
            agg_city = (fdf.groupby("CITY")
                        .agg(EBITDA_PCT=("EBITDA%","mean"))
                        .reset_index().sort_values("EBITDA_PCT", ascending=False))
            fig_city = px.bar(agg_city, x="CITY", y="EBITDA_PCT",
                              color="EBITDA_PCT", color_continuous_scale="RdYlGn",
                              title="Avg EBITDA% by City",
                              labels={"EBITDA_PCT":"EBITDA%"},
                              text=agg_city["EBITDA_PCT"].map(lambda v: f"{v:.1f}%"))
            fig_city.update_layout(margin=dict(t=40,b=20), plot_bgcolor="white")
            fig_city.update_traces(textposition="outside")
            st.plotly_chart(fig_city, use_container_width=True)

        ch3, ch4 = st.columns(2)
        with ch3:
            agg_rev = fdf["REVENUE COHORT"].value_counts().reset_index()
            agg_rev.columns = ["Revenue Cohort","Count"]
            fig_pie = px.pie(agg_rev, names="Revenue Cohort", values="Count",
                             title="Store Distribution by Revenue Cohort",
                             color_discrete_sequence=px.colors.qualitative.Set2, hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch4:
            agg_store = (fdf.groupby("STORE")
                         .agg(GM_PCT=("GM%","mean"), EBITDA_PCT=("EBITDA%","mean"),
                              NET_REV=("NET REVENUE","mean"), CITY=("CITY","first"))
                         .reset_index())
            fig_sc = px.scatter(agg_store, x="GM_PCT", y="EBITDA_PCT",
                                color="CITY", size="NET_REV", hover_name="STORE",
                                title="GM% vs EBITDA% per Store",
                                labels={"GM_PCT":"GM%","EBITDA_PCT":"EBITDA%"}, size_max=30)
            fig_sc.update_layout(margin=dict(t=40,b=20), plot_bgcolor="white")
            st.plotly_chart(fig_sc, use_container_width=True)

        st.markdown("#### EBITDA Category Breakdown by Month")
        agg_ecat = (fdf.groupby(["MONTH","EBITDA CATEGORY"])
                    .agg(Store_Count=("STORE","nunique")).reset_index())
        agg_ecat["MONTH"] = pd.Categorical(agg_ecat["MONTH"], categories=SORTED_MONTHS, ordered=True)
        fig_ecat = px.bar(agg_ecat.sort_values("MONTH"), x="MONTH", y="Store_Count",
                          color="EBITDA CATEGORY", barmode="stack",
                          color_discrete_map={"EBITDA +ve":"#4CAF50","EBITDA -ve":"#f44336"},
                          title="Store Count by EBITDA Category per Month",
                          labels={"Store_Count":"# Stores","MONTH":"Month"})
        fig_ecat.update_layout(margin=dict(t=40,b=20), plot_bgcolor="white")
        st.plotly_chart(fig_ecat, use_container_width=True)


# =======================================================================
#  DASHBOARD 2 : VARIANCE LEVEL PNL
# =======================================================================
with tab2:
    st.markdown('<div class="section-title">📊 VARIANCE BY REVENUE CATEGORY</div>',
                unsafe_allow_html=True)
    st.markdown("> **Variance** = Wastage of food material. Computed as `VARIANCE / IDEAL FOOD COST x 100`.")

    f_var_cat = st.multiselect("Variance Category Filter", VAR_CATS_ALL,
                               default=VAR_CATS_ALL, key="var_cat_filter")
    if not f_var_cat:
        st.warning("Please select at least one variance category.")
        st.stop()

    vdf = df[df["VARIANCE CATEGORY"].astype(str).isin(f_var_cat)].copy()
    st.caption(f"Filtered to **{len(vdf):,}** records across **{vdf['STORE'].nunique()}** stores")

    # -- Sub-dashboard 1 -------------------------------------------------
    st.markdown("---")
    st.markdown("### Sub-dashboard 1 - Average Variance % by Revenue Category")

    pivot1 = (vdf.pivot_table(index="REVENUE CATEGORY", columns="MONTH",
                               values="VARIANCE%", aggfunc="mean", observed=False)
              .reindex(index=REV_CATS_ORDER)
              .reindex(columns=[m for m in SORTED_MONTHS if m in vdf["MONTH"].unique()]))
    pivot1.index.name = "Revenue Category"
    grand1 = (vdf.groupby("MONTH")["VARIANCE%"].mean()
              .reindex([m for m in SORTED_MONTHS if m in vdf["MONTH"].unique()]))
    grand1.name = "Grand Total"
    pivot1 = pd.concat([pivot1, grand1.to_frame().T])

    # Format as strings (no jinja2 needed)
    pivot1_display = pivot1.map(lambda v: f"{v:.1f}%" if pd.notna(v) else "-")
    st.dataframe(pivot1_display, use_container_width=True)

    p1 = pivot1.drop("Grand Total", errors="ignore").reset_index(names="Revenue Category")
    p1.columns = p1.columns.str.strip()
    print(p1.columns)
  
    p1_m = p1.melt(id_vars="Revenue Category", var_name="Month", value_name="Avg Variance%")
    p1_m = p1_m.dropna(subset=["Avg Variance%"])
    p1_m["Month"] = pd.Categorical(p1_m["Month"], categories=SORTED_MONTHS, ordered=True)
    fig_v1 = px.line(p1_m.sort_values("Month"), x="Month", y="Avg Variance%",
                     color="Revenue Category", markers=True,
                     title="Average Variance % Trend by Revenue Category",
                     color_discrete_sequence=px.colors.qualitative.Set1)
    fig_v1.update_layout(margin=dict(t=50,b=20), plot_bgcolor="white",
                         legend_orientation="h", legend_y=-0.2, yaxis_ticksuffix="%")
    st.plotly_chart(fig_v1, use_container_width=True)

    # -- Sub-dashboard 2 -------------------------------------------------
    st.markdown("---")
    st.markdown("### Sub-dashboard 2 - Store Count by Revenue Category")

    pivot2 = (vdf.pivot_table(index="REVENUE CATEGORY", columns="MONTH",
                               values="STORE", aggfunc="nunique", observed=False)
              .reindex(index=REV_CATS_ORDER)
              .reindex(columns=[m for m in SORTED_MONTHS if m in vdf["MONTH"].unique()])
              .fillna(0).astype(int))
    pivot2.index.name = "Revenue Category"
    grand2 = (vdf.groupby("MONTH")["STORE"].nunique()
              .reindex([m for m in SORTED_MONTHS if m in vdf["MONTH"].unique()]))
    grand2.name = "Grand Total"
    pivot2 = pd.concat([pivot2, grand2.to_frame().T.fillna(0).astype(int)])

    st.dataframe(pivot2, use_container_width=True)

    p2 = pivot2.drop("Grand Total", errors="ignore").reset_index(names="Revenue Category")
    p2_m = p2.melt(id_vars="Revenue Category", var_name="Month", value_name="Store Count")
    p2_m["Month"] = pd.Categorical(p2_m["Month"], categories=SORTED_MONTHS, ordered=True)
    fig_v2 = px.bar(p2_m.sort_values("Month"), x="Month", y="Store Count",
                    color="Revenue Category", barmode="stack",
                    title="Store Count by Revenue Category (Stacked)",
                    color_discrete_sequence=px.colors.qualitative.Pastel, text="Store Count")
    fig_v2.update_traces(textposition="inside", textfont_size=11)
    fig_v2.update_layout(margin=dict(t=50,b=20), plot_bgcolor="white",
                         legend_orientation="h", legend_y=-0.2)
    st.plotly_chart(fig_v2, use_container_width=True)

    # -- Bonus heatmap ---------------------------------------------------
    st.markdown("---")
    st.markdown("### Bonus - Variance Heatmap by City & Month")
    heat_df = vdf.groupby(["CITY","MONTH"])["VARIANCE%"].mean().reset_index()
    heat_pivot = heat_df.pivot(index="CITY", columns="MONTH", values="VARIANCE%")
    heat_pivot = heat_pivot.reindex(columns=[m for m in SORTED_MONTHS if m in heat_pivot.columns])
    fig_heat = px.imshow(heat_pivot, color_continuous_scale="YlOrRd", aspect="auto",
                         title="Avg Variance% - City x Month Heatmap", text_auto=".2f")
    fig_heat.update_layout(margin=dict(t=50,b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("### Variance % Distribution by Category")
    fig_box = px.box(vdf, x="VARIANCE CATEGORY", y="VARIANCE%", color="VARIANCE CATEGORY",
                     title="Variance % Distribution per Category",
                     color_discrete_sequence=px.colors.qualitative.Set2, points="outliers")
    fig_box.update_layout(margin=dict(t=50,b=20), plot_bgcolor="white",
                          showlegend=False, yaxis_ticksuffix="%")
    st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------
st.divider()
st.markdown("<small>Kittchen P&amp;L Dashboard | Python 3.11 | Streamlit | Plotly | Pandas</small>",
            unsafe_allow_html=True)
