import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Web Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #0c1a2e 50%, #0f2027 100%);
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 20, 40, 0.7) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    h1 {
        background: linear-gradient(45deg, #38bdf8, #818cf8, #38bdf8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        animation: gradient_text 4s ease infinite;
    }

    @keyframes gradient_text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    h2, h3, h4, h5 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    p, label, .stMarkdown p, .stMarkdown li {
        color: #e2e8f0 !important;
    }

    .block-container {
        padding-top: 2rem !important;
    }

    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin: 2.5rem 0;
    }

    .kpi-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🌐 Web Analytics Dashboard")
st.markdown("<p style='color: #94a3b8; font-size: 1.15rem; font-weight: 300;'>Automated loading, cleaning, and visualization of website analytics & e-commerce metrics.</p>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOADING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(selected_file):
    data_dir = "data"
    file_path = os.path.join(data_dir, selected_file)

    try:
        # For very large files, let's suggest sampling or limit rows
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_path.lower().endswith('.csv'):
            if file_size_mb > 50:
                # We can't use st.info inside a cached function without replay, 
                # but for simplicity we'll just do the sampling.
                df = pd.read_csv(file_path, nrows=50000)
            else:
                df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, engine='openpyxl')

        df.dropna(axis=0, how='all', inplace=True)

        # Parse date-like columns
        for col in df.columns:
            if any(k in col.lower() for k in ['date', 'time', 'month', 'year']):
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass

        # Clean numeric columns (remove commas, %, and handle whitespace)
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    # Remove commas, percentage signs, and dollar signs
                    cleaned = df[col].astype(str).str.replace(r'[%,$]', '', regex=True).str.strip()
                    # Try converting to numeric, if it fails it will stay as object
                    converted = pd.to_numeric(cleaned, errors='coerce')
                    # If conversion was mostly successful (not all NaNs), update the column
                    if not converted.isna().all():
                        df[col] = converted
                except Exception:
                    pass

        return df, selected_file
    except Exception as e:
        return None, f"Error loading data: {e}"


# File Selection Logic (Outside cache)
data_dir = "data"
if not os.path.exists(data_dir):
    st.error(f"The '{data_dir}' folder is missing. Please create it and add your dataset.")
    st.stop()

valid_extensions = ('.csv', '.xlsx', '.xls')
files = [f for f in os.listdir(data_dir) if f.lower().endswith(valid_extensions)]

if not files:
    st.warning("No CSV or Excel dataset found in the 'data' folder.")
    st.stop()

if len(files) > 1:
    selected_file = st.sidebar.selectbox("📂 Select Dataset", options=files, index=0)
else:
    selected_file = files[0]

# Load Data
df_raw, load_msg = load_data(selected_file)

if df_raw is not None:
    file_name = load_msg
    st.success(f"✅ Loaded: **{file_name}** — {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")

    df = df_raw.copy()

    # Auto-fill missing values
    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns

    if len(num_cols) > 0:
        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
    for c in cat_cols:
        df[c] = df[c].fillna("Unknown")

    # Drop duplicates
    dup = df.duplicated().sum()
    if dup > 0:
        df = df.drop_duplicates()

    # -------------------------------------------------------------------------
    # 3. SIDEBAR FILTERS
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 Dashboard Filters")

    # Year filter
    year_col = next((c for c in df.columns if c.lower() in ['year']), None)
    if year_col and df[year_col].dtype in [np.int64, np.float64, object]:
        years = sorted(df[year_col].dropna().unique().tolist())
        selected_years = st.sidebar.multiselect("📅 Year", options=years, default=years)
        df = df[df[year_col].isin(selected_years)]

    # Source / Medium filter
    source_col = next((c for c in df.columns if 'source' in c.lower() or 'medium' in c.lower()), None)
    if source_col:
        sources = sorted(df[source_col].dropna().unique().tolist())
        selected_sources = st.sidebar.multiselect(f"📡 {source_col}", options=sources, default=sources)
        df = df[df[source_col].isin(selected_sources)]

    # Other categorical filters (max 40 unique values)
    cat_cols_current = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    skip_cols = {source_col, year_col} if source_col or year_col else set()
    for col in cat_cols_current:
        if col in skip_cols:
            continue
        unique_vals = df[col].dropna().unique()
        if 1 < len(unique_vals) <= 40:
            selected = st.sidebar.multiselect(f"Select {col}", options=unique_vals, default=unique_vals)
            df = df[df[col].isin(selected)]

    # Re-evaluate after filtering
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols_current = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    # -------------------------------------------------------------------------
    # 4. KPI CARDS
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("📊 Key Performance Indicators")

    def find_col(keywords):
        for kw in keywords:
            for c in df.columns:
                if kw in c.lower():
                    return c
        return None

    rev_col   = find_col(['revenue'])
    sess_col  = find_col(['session'])
    user_col  = find_col(['user'])
    conv_col  = find_col(['conversion'])
    bounce_col= find_col(['bounce'])
    trans_col = find_col(['transaction'])
    rating_col= find_col(['overall', 'rating', 'score'])
    sent_col  = find_col(['sentiment'])

    # Force numeric conversion for analysis columns
    for c in [rev_col, sess_col, user_col, conv_col, bounce_col, trans_col]:
        if c:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    with kpi1:
        if rev_col:
            val_num = pd.to_numeric(df[rev_col], errors='coerce').sum()
            val = f"${val_num:,.0f}"
        else:
            val = "N/A"
        st.metric("💰 Total Revenue", val)

    with kpi2:
        if sess_col:
            val_num = pd.to_numeric(df[sess_col], errors='coerce').sum()
            val = f"{val_num:,.0f}"
        else:
            val = "N/A"
        st.metric("🖥️ Total Sessions", val)

    with kpi3:
        if user_col:
            val_num = pd.to_numeric(df[user_col], errors='coerce').sum()
            val = f"{val_num:,.0f}"
        else:
            val = "N/A"
        st.metric("👤 Total Users", val)

    with kpi4:
        if conv_col:
            val_num = pd.to_numeric(df[conv_col], errors='coerce').mean()
            val = f"{val_num:.2f}%"
        else:
            val = "N/A"
        st.metric("🎯 Avg Conversion Rate", val)

    with kpi5:
        if bounce_col:
            val_num = pd.to_numeric(df[bounce_col], errors='coerce').mean()
            val = f"{val_num:.2f}%"
        else:
            val = "N/A"
        st.metric("⚡ Avg Bounce Rate", val)

    with kpi6:
        if trans_col:
            val_num = pd.to_numeric(df[trans_col], errors='coerce').sum()
            val = f"{val_num:,.0f}"
            st.metric("🛒 Total Transactions", val)
        elif rating_col:
            val_num = df[rating_col].mean()
            val = f"{val_num:.2f} ⭐"
            st.metric("⭐ Avg Rating", val)
        else:
            st.metric("🛒 Total Transactions", "N/A")

    # -------------------------------------------------------------------------
    # 5. EDA SECTION
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("🔬 Exploratory Data Analysis")

    eda1, eda2 = st.columns(2)

    with eda1:
        st.subheader("📋 Summary Statistics")
        if num_cols:
            summary = df[num_cols].describe().T
            summary['mode'] = df[num_cols].mode().iloc[0]
            summary = summary[['mean', '50%', 'mode', 'std', 'min', 'max']].rename(columns={'50%': 'median'})
            st.dataframe(summary.round(2), use_container_width=True)

    with eda2:
        st.subheader("🕳️ Missing Values Analysis")
        mv = df_raw.isnull().sum().reset_index()
        mv.columns = ['Column', 'Missing Count']
        mv['Missing %'] = (mv['Missing Count'] / len(df_raw) * 100).round(2)
        mv = mv[mv['Missing Count'] > 0]
        if mv.empty:
            st.success("No missing values detected in the dataset.")
        else:
            st.dataframe(mv, use_container_width=True)

    st.subheader("🔎 Raw Data Preview")
    st.dataframe(df, use_container_width=True)

    st.subheader("🧹 Data Cleaning Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate Rows Removed", dup)
    c2.metric("Remaining Records", f"{len(df):,}")
    c3.metric("Columns", df.shape[1])

    # -------------------------------------------------------------------------
    # 6. VISUALIZATIONS
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("📈 Data Visualizations")

    PLOTLY_THEME = "plotly_dark"

    # --- A. Revenue Trend Over Time ---
    if rev_col:
        st.subheader("💹 Revenue Trend Over Time")

        # Try date columns first
        time_col = date_cols[0] if date_cols else None

        # Fallback: use Month + Year if present
        month_col = find_col(['month'])
        if time_col is None and month_col and year_col:
            try:
                df['_date_combined'] = pd.to_datetime(
                    df[year_col].astype(int).astype(str) + '-' +
                    df[month_col].astype(int).astype(str).str.zfill(2) + '-01'
                )
                time_col = '_date_combined'
            except Exception:
                pass

        if time_col:
            df_time = df.dropna(subset=[time_col]).copy()
            trend = df_time.groupby(time_col)[rev_col].sum().reset_index()
            fig_rev = px.line(trend, x=time_col, y=rev_col,
                              title="Revenue Over Time", markers=True,
                              template=PLOTLY_THEME,
                              color_discrete_sequence=['#38bdf8'])
            fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rev, use_container_width=True)
        elif year_col:
            trend = df.groupby(year_col)[rev_col].sum().reset_index()
            fig_rev = px.bar(trend, x=year_col, y=rev_col,
                             title="Revenue by Year",
                             template=PLOTLY_THEME,
                             color_discrete_sequence=['#818cf8'])
            fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.info("No date or year column detected for revenue trend.")

    # --- B. Bar Charts for Categorical Columns ---
    st.subheader("📊 Category Distributions")
    for col in cat_cols_current:
        unique_count = df[col].nunique()
        if 1 < unique_count <= 25:
            counts_df = df[col].value_counts().reset_index()
            counts_df.columns = [col, 'Count']
            b1, b2 = st.columns(2)
            with b1:
                fig_bar = px.bar(counts_df, x=col, y='Count',
                                 title=f"{col} — Bar Chart", color=col,
                                 template=PLOTLY_THEME)
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)
            with b2:
                fig_pie = px.pie(counts_df, names=col, values='Count',
                                 title=f"{col} — Pie Chart",
                                 template=PLOTLY_THEME)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)

    # --- C. Histograms & Box Plots ---
    if num_cols:
        st.subheader("📉 Distributions & Box Plots")
        for col_name in num_cols:
            if col_name.startswith('_'):
                continue
            h1, h2 = st.columns(2)
            with h1:
                fig_hist = px.histogram(df, x=col_name,
                                        title=f"Histogram — {col_name}",
                                        marginal="box", opacity=0.8,
                                        template=PLOTLY_THEME,
                                        color_discrete_sequence=['#38bdf8'])
                fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist, use_container_width=True)
            with h2:
                fig_box = px.box(df, y=col_name,
                                 title=f"Box Plot — {col_name}",
                                 template=PLOTLY_THEME,
                                 color_discrete_sequence=['#818cf8'])
                fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_box, use_container_width=True)

    # --- D. Scatter Plot ---
    if len(num_cols) > 1:
        st.subheader("🔵 Scatter Plot")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            x_axis = st.selectbox("X-axis", options=num_cols, index=0, key="scatter_x")
        with sc2:
            y_axis = st.selectbox("Y-axis", options=num_cols,
                                  index=1 if len(num_cols) > 1 else 0, key="scatter_y")
        with sc3:
            color_opts = ["None"] + [c for c in cat_cols_current if df[c].nunique() <= 15]
            color_col = st.selectbox("Color by", options=color_opts, key="scatter_color")

        try:
            fig_scatter = px.scatter(df, x=x_axis, y=y_axis,
                                     color=color_col if color_col != "None" else None,
                                     trendline="ols",
                                     title=f"{x_axis} vs {y_axis}",
                                     template=PLOTLY_THEME, opacity=0.7)
        except Exception:
            fig_scatter = px.scatter(df, x=x_axis, y=y_axis,
                                     color=color_col if color_col != "None" else None,
                                     title=f"{x_axis} vs {y_axis}",
                                     template=PLOTLY_THEME, opacity=0.7)
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- E. Correlation Heatmap ---
    if len(num_cols) > 1:
        st.subheader("🧩 Correlation Heatmap")
        safe_num = [c for c in num_cols if not c.startswith('_')]
        corr = df[safe_num].corr()
        fig_corr, ax = plt.subplots(figsize=(10, 6))
        fig_corr.patch.set_facecolor('#0f172a')
        ax.set_facecolor('#1e293b')
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f",
                    linewidths=0.5, ax=ax,
                    annot_kws={"color": "#e2e8f0"},
                    linecolor='#0f172a')
        ax.tick_params(colors='#94a3b8')
        plt.tight_layout()
        st.pyplot(fig_corr)
        plt.close(fig_corr)

    # --- F. Source / Medium Revenue Breakdown ---
    if source_col and rev_col:
        st.subheader("📡 Revenue by Source / Medium")
        src_rev = df.groupby(source_col)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False)
        fig_src = px.bar(src_rev, x=source_col, y=rev_col,
                         title=f"Revenue by {source_col}",
                         template=PLOTLY_THEME,
                         color=rev_col,
                         color_continuous_scale='Blues')
        fig_src.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_src, use_container_width=True)

    # --- G. Conversion Rate & Bounce Rate by Source ---
    if source_col and conv_col and bounce_col:
        st.subheader("🎯 Conversion Rate vs Bounce Rate by Source")
        try:
            # Ensure numeric before mean
            df_perf = df.copy()
            df_perf[conv_col] = pd.to_numeric(df_perf[conv_col], errors='coerce')
            df_perf[bounce_col] = pd.to_numeric(df_perf[bounce_col], errors='coerce')
            
            perf = df_perf.groupby(source_col)[[conv_col, bounce_col]].mean().reset_index()
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Bar(
                x=perf[source_col], y=perf[conv_col],
                name='Avg Conversion Rate', marker_color='#38bdf8'
            ))
            fig_perf.add_trace(go.Bar(
                x=perf[source_col], y=perf[bounce_col],
                name='Avg Bounce Rate', marker_color='#f472b6'
            ))
            fig_perf.update_layout(
                barmode='group',
                template=PLOTLY_THEME,
                title=f"Conversion vs Bounce by {source_col}",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        except Exception as e:
            st.error(f"Could not generate performance chart: {e}")

    # --- H. Sessions vs Revenue Funnel ---
    if sess_col and user_col and trans_col:
        st.subheader("🔻 Analytics Funnel")
        funnel_data = {
            'Stage': ['Sessions', 'Users', 'Transactions'],
            'Count': [df[sess_col].sum(), df[user_col].sum(), df[trans_col].sum()]
        }
        fig_funnel = px.funnel(
            pd.DataFrame(funnel_data), x='Count', y='Stage',
            title="Sessions → Users → Transactions Funnel",
            template=PLOTLY_THEME,
            color_discrete_sequence=['#38bdf8', '#818cf8', '#f472b6']
        )
        fig_funnel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_funnel, use_container_width=True)

    # -------------------------------------------------------------------------
    # 7. MEAN / MEDIAN / MODE TABLE
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("📐 Descriptive Statistics: Mean, Median & Mode")

    if num_cols:
        safe_num = [c for c in num_cols if not c.startswith('_')]
        stats_df = pd.DataFrame({
            'Column': safe_num,
            'Mean': [df[c].mean() for c in safe_num],
            'Median': [df[c].median() for c in safe_num],
            'Mode': [df[c].mode().iloc[0] if not df[c].mode().empty else np.nan for c in safe_num],
            'Std Dev': [df[c].std() for c in safe_num],
            'Min': [df[c].min() for c in safe_num],
            'Max': [df[c].max() for c in safe_num],
        }).set_index('Column')
        st.dataframe(stats_df.round(3), use_container_width=True)
    else:
        st.info("No numeric columns available for statistics.")

else:
    if load_msg and ("missing" in load_msg.lower() or "no csv" in load_msg.lower()):
        st.warning(f"⚠️ {load_msg}")
    elif load_msg and "error" in load_msg.lower():
        st.error(f"❌ {load_msg}")
    else:
        st.info("Awaiting dataset... Drop a `.csv` or `.xlsx` file inside the `data` folder to power the dashboard.")