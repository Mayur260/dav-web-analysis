"""
Web Analytics Dashboard
Combines original dataset logic with professional UI from reference project.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats as scipy_stats
from scipy.stats import gaussian_kde

# ══════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Web Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    h1, h2, h3, h4, h5, h6    { font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; }

    .main { background-color: #0E1117; }
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2.5rem !important; max-width: 1440px; }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #1A1C24;
        border: 1px solid #2D3748;
        padding: 20px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s ease-in-out, border-color 0.2s;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-4px); border-color: #00E6FF; }
    div[data-testid="stMetricLabel"] {
        color: #A0AEC0 !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 13px;
    }
    div[data-testid="stMetricValue"] { color: #00E6FF !important; font-weight: 700; font-size: 28px; }
    div[data-testid="stMetricDelta"] { color: #00E396 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        padding: 10px 18px;
        color: #A0AEC0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #00E6FF !important;
        color: #00E6FF !important;
        font-weight: 700 !important;
    }

    /* Stat cards */
    .stat-card {
        background-color: #1A1C24;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        transition: border-color 0.2s, transform 0.2s;
    }
    .stat-card:hover { border-color: #00E6FF; transform: translateY(-3px); }
    .stat-label { color: #A0AEC0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
    .stat-value { color: #00E6FF; font-size: 1.4rem; font-weight: 700; }

    hr { border-color: #2D3748 !important; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MATPLOTLIB DARK THEME
# ══════════════════════════════════════════════
plt.style.use('dark_background')
sns.set_style("darkgrid", {
    "axes.facecolor": "#1A1C24",
    "grid.color": "#2D3748",
    "figure.facecolor": "#0E1117"
})

PAL = {
    'bg':     '#0E1117',
    'card':   '#1A1C24',
    'border': '#2D3748',
    'cyan':   '#00E6FF',
    'green':  '#00E396',
    'purple': '#775DD0',
    'orange': '#FEB019',
    'red':    '#FF4560',
    'text':   '#FAFAFA',
    'muted':  '#A0AEC0',
    'grid':   '#2D3748',
}

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def style_ax(fig, ax, title='', xlabel='', ylabel=''):
    fig.patch.set_facecolor(PAL['bg'])
    ax.set_facecolor(PAL['card'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PAL['border'])
    ax.spines['bottom'].set_color(PAL['border'])
    ax.tick_params(colors=PAL['muted'], labelsize=9)
    ax.xaxis.label.set_color(PAL['muted'])
    ax.yaxis.label.set_color(PAL['muted'])
    if title:
        ax.set_title(title, color=PAL['text'], fontsize=13, fontweight='bold', pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

def make_fig(w=10, h=5):
    return plt.subplots(figsize=(w, h), facecolor=PAL['bg'])

def stat_card(label, value):
    return (
        f"<div class='stat-card'>"
        f"<div class='stat-label'>{label}</div>"
        f"<div class='stat-value'>{value}</div>"
        f"</div>"
    )

# ══════════════════════════════════════════════
# LOAD & CLEAN DATA
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv('Web_Analytic_Dataset.csv')
    df = df.drop_duplicates()

    numeric_cols = ['Users', 'New Users', 'Sessions', 'Pageviews',
                    'Transactions', 'Revenue', 'Quantity Sold']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', '', regex=False),
                errors='coerce'
            )

    for col in ['Bounce Rate', 'Conversion Rate (%)']:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace('%', '', regex=False),
                errors='coerce'
            )

    def to_seconds(d):
        try:
            h, m, s = str(d).split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)
        except Exception:
            return np.nan

    if 'Avg. Session Duration' in df.columns:
        df['Avg. Session Duration'] = df['Avg. Session Duration'].apply(to_seconds)

    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].median())

    return df


@st.cache_data
def load_raw_for_duplicates():
    """Used only for duplicate count in the quality tab."""
    try:
        return int(pd.read_csv('Web_Analytic_Dataset.csv').duplicated().sum())
    except Exception:
        return 0


df     = load_data()
num_df = df.select_dtypes(include='number').drop(columns=['Year'], errors='ignore')

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div style='margin-bottom:1.5rem; padding-top:0.5rem;'>
    <h1 style='display:flex; align-items:center; gap:12px; font-size:38px;
               font-weight:700; margin-bottom:8px; color:#FAFAFA;'>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none"
             stroke="#00E6FF" stroke-width="2.5"
             stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6"  y1="20" x2="6"  y2="14"/>
        </svg>
        <span><span style='color:#00E6FF;'>Web</span> Analytics Dashboard</span>
    </h1>
    <p style='font-size:15px; color:#A0AEC0; margin-top:0; padding-left:46px;'>
        Traffic &nbsp;·&nbsp; Revenue &nbsp;·&nbsp; Conversion &nbsp;·&nbsp; Sessions
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("💰 Total Revenue",   f"${int(df['Revenue'].sum()):,}")
k2.metric("📊 Total Sessions",  f"{int(df['Sessions'].sum()):,}")
k3.metric("👥 Total Users",     f"{int(df['Users'].sum()):,}")
k4.metric("🎯 Avg Conversion",  f"{df['Conversion Rate (%)'].mean():.2f}%")
k5.metric("↩️ Avg Bounce Rate", f"{df['Bounce Rate'].mean():.2f}%")
k6.metric("🛒 Transactions",    f"{int(df['Transactions'].sum()):,}")

st.markdown("<div style='margin-bottom:2rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📈  Overview & Trends",
    "📊  Visualizations",
    "🔍  EDA & Statistics",
])

# ─────────────────────────────────────────────
# TAB 1 — OVERVIEW & TRENDS
# ─────────────────────────────────────────────
with tab1:
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # Revenue stat cards
    rev      = df['Revenue']
    mode_val = scipy_stats.mode(rev, keepdims=True).mode[0]

    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(stat_card("Mean Revenue",   f"${rev.mean():,.2f}"),      unsafe_allow_html=True)
    s2.markdown(stat_card("Median Revenue", f"${rev.median():,.2f}"),    unsafe_allow_html=True)
    s3.markdown(stat_card("Mode Revenue",   f"${mode_val:,.2f}"),        unsafe_allow_html=True)
    s4.markdown(stat_card("Dataset Size",   f"{df.shape[0]} × {df.shape[1]}"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # Revenue trend
    st.subheader("Revenue Trend Over Time")
    trend = (
        df.groupby(['Year', 'Month of the year'])['Revenue']
        .sum().reset_index()
    )
    trend['Period'] = (
        trend['Year'].astype(str) + '-' +
        trend['Month of the year'].astype(str).str.zfill(2)
    )
    trend = trend.sort_values('Period').reset_index(drop=True)

    fig, ax = make_fig(14, 5)
    x    = range(len(trend))
    step = max(1, len(trend) // 10)
    ax.plot(x, trend['Revenue'], color=PAL['cyan'], linewidth=2.5,
            marker='o', markersize=4, markerfacecolor=PAL['bg'],
            markeredgewidth=2, zorder=3)
    ax.fill_between(x, trend['Revenue'], alpha=0.1, color=PAL['cyan'])
    ax.set_xticks(list(x)[::step])
    ax.set_xticklabels(trend['Period'].iloc[::step], rotation=30, ha='right', fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
    ax.grid(True, color=PAL['grid'], alpha=0.5, linestyle='--')
    style_ax(fig, ax, xlabel='Period', ylabel='Revenue ($)')
    st.pyplot(fig)
    plt.close()

    st.divider()

    # Sessions trend
    st.subheader("Sessions Trend Over Time")
    s_trend = (
        df.groupby(['Year', 'Month of the year'])['Sessions']
        .sum().reset_index()
    )
    s_trend['Period'] = (
        s_trend['Year'].astype(str) + '-' +
        s_trend['Month of the year'].astype(str).str.zfill(2)
    )
    s_trend = s_trend.sort_values('Period').reset_index(drop=True)

    fig, ax = make_fig(14, 5)
    x2    = range(len(s_trend))
    step2 = max(1, len(s_trend) // 10)
    ax.fill_between(x2, s_trend['Sessions'], color=PAL['red'], alpha=0.12)
    ax.plot(x2, s_trend['Sessions'], color=PAL['red'], linewidth=2.5, alpha=0.9)
    ax.set_xticks(list(x2)[::step2])
    ax.set_xticklabels(s_trend['Period'].iloc[::step2], rotation=30, ha='right', fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.grid(True, color=PAL['grid'], alpha=0.5, linestyle='--')
    style_ax(fig, ax, xlabel='Period', ylabel='Sessions')
    st.pyplot(fig)
    plt.close()

# ─────────────────────────────────────────────
# TAB 2 — VISUALIZATIONS
# ─────────────────────────────────────────────
with tab2:
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # Row 1
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.subheader("Distribution of Sessions")
        fig, ax = make_fig()
        sns.histplot(df['Sessions'], bins=28, kde=True, ax=ax,
                     color=PAL['purple'], edgecolor=PAL['bg'], linewidth=0.3, alpha=0.8)
        if ax.lines:
            ax.lines[0].set_color(PAL['cyan'])
            ax.lines[0].set_linewidth(2.2)
        ax.set_xlabel('Sessions', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.grid(True, color=PAL['grid'], alpha=0.5, linestyle='--')
        style_ax(fig, ax)
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("Top 10 Sources by Revenue")
        top = (
            df.groupby('Source / Medium')['Revenue']
            .sum().nlargest(10).reset_index()
        )
        fig, ax = make_fig()
        bar_colors = [PAL['cyan'] if i < 3 else PAL['muted'] for i in range(len(top))]
        ax.barh(top['Source / Medium'], top['Revenue'],
                color=bar_colors, alpha=0.85, height=0.6)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
        ax.grid(True, axis='x', color=PAL['grid'], alpha=0.5, linestyle='--')
        for i, val in enumerate(top['Revenue']):
            ax.text(val + top['Revenue'].max() * 0.01, i,
                    f'${val:,.0f}', va='center', fontsize=8,
                    color=PAL['cyan'], fontweight='bold')
        style_ax(fig, ax, xlabel='Revenue ($)')
        st.pyplot(fig)
        plt.close()

    st.divider()

    # Row 2
    col3, col4 = st.columns(2, gap="medium")

    with col3:
        st.subheader("Sessions vs Revenue")
        fig, ax = make_fig()
        sc = ax.scatter(df['Sessions'], df['Revenue'],
                        c=df['Conversion Rate (%)'],
                        cmap='plasma', alpha=0.65, s=30, edgecolors='none')
        cbar = fig.colorbar(sc, ax=ax)
        cbar.ax.tick_params(colors=PAL['muted'], labelsize=8)
        cbar.set_label('Conversion Rate (%)', color=PAL['muted'], fontsize=9)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
        ax.grid(True, color=PAL['grid'], alpha=0.5, linestyle='--')
        style_ax(fig, ax, xlabel='Sessions', ylabel='Revenue ($)')
        st.pyplot(fig)
        plt.close()

    with col4:
        st.subheader("Box Plot – Sessions vs Pageviews")
        fig, ax = make_fig()
        bp = ax.boxplot(
            [df['Sessions'].dropna().values, df['Pageviews'].dropna().values],
            patch_artist=True, labels=['Sessions', 'Pageviews'],
            medianprops=dict(color=PAL['cyan'], linewidth=2)
        )
        for patch, c in zip(bp['boxes'], [PAL['purple'], PAL['orange']]):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        for w   in bp['whiskers']: w.set_color(PAL['muted'])
        for cap in bp['caps']:     cap.set_color(PAL['muted'])
        for fl  in bp['fliers']:
            fl.set(marker='o', color=PAL['red'], alpha=0.5, markersize=4)
        ax.grid(True, axis='y', color=PAL['grid'], alpha=0.5, linestyle='--')
        style_ax(fig, ax, ylabel='Value')
        st.pyplot(fig)
        plt.close()

    st.divider()

    # Correlation heatmap (full width)
    st.subheader("Correlation Heatmap")
    corr = num_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    fig, ax = plt.subplots(
        figsize=(max(8, len(corr.columns) * 0.9), max(6, len(corr.columns) * 0.7)),
        facecolor=PAL['bg']
    )
    sns.heatmap(
        corr, mask=mask,
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        vmin=-1, vmax=1, center=0,
        annot=True, fmt='.2f',
        linewidths=0.5, linecolor=PAL['border'],
        square=True, cbar_kws={"shrink": 0.8},
        ax=ax, annot_kws={'size': 9, 'color': PAL['text']}
    )
    ax.set_title('Feature Correlation Matrix',
                 color=PAL['text'], fontsize=13, fontweight='bold', pad=14)
    ax.tick_params(colors=PAL['muted'], labelsize=9)
    ax.set_facecolor(PAL['card'])
    st.pyplot(fig)
    plt.close()

# ─────────────────────────────────────────────
# TAB 3 — EDA & STATISTICS
# ─────────────────────────────────────────────
with tab3:
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # Data quality KPIs
    st.subheader("Data Quality Overview")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Total Rows",      f"{df.shape[0]:,}")
    q2.metric("Total Columns",   f"{df.shape[1]}")
    q3.metric("Duplicate Rows",  f"{load_raw_for_duplicates():,}")
    q4.metric("Missing Values",  f"{int(df.isnull().sum().sum()):,}")

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Column quality table
    st.markdown("##### Column-wise Quality Summary")
    col_records = [
        {
            "Column":        col,
            "Data Type":     str(df[col].dtype),
            "Missing Values": int(df[col].isnull().sum()),
            "Missing %":     round(df[col].isnull().sum() / len(df) * 100, 2),
            "Unique Values": int(df[col].nunique()),
        }
        for col in df.columns
    ]
    col_summary = pd.DataFrame(col_records)
    st.dataframe(
        st.dataframe(col_summary, use_container_width=True)
        .background_gradient(subset=["Missing %"], cmap="YlOrRd", vmin=0, vmax=100)
        .format({"Missing %": "{:.2f}%"}),
        use_container_width=True, hide_index=True,
        height=min(len(col_summary) * 38 + 40, 500)
    )

    st.divider()

    # Descriptive statistics
    st.subheader("Descriptive Statistics — Numeric Columns")
    stat_records = [
        {
            "Column":  col,
            "Mean":    round(num_df[col].mean(), 4),
            "Median":  round(num_df[col].median(), 4),
            "Mode":    round(scipy_stats.mode(num_df[col], keepdims=True).mode[0], 4),
            "Std Dev": round(num_df[col].std(), 4),
            "Min":     round(num_df[col].min(), 4),
            "Max":     round(num_df[col].max(), 4),
        }
        for col in num_df.columns
    ]
    stat_df = pd.DataFrame(stat_records)
    st.dataframe(
        stat_df.style
        .format({c: "{:.4f}" for c in ["Mean", "Median", "Mode", "Std Dev", "Min", "Max"]})
        .set_properties(**{"text-align": "right"}),
        use_container_width=True, hide_index=True,
        height=min(len(stat_df) * 38 + 40, 400)
    )

    st.divider()

    # Advanced visualizations
    st.subheader("Advanced Visualizations")
    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    viz_l, viz_r = st.columns(2, gap="medium")

    with viz_l:
        st.markdown("**Missing Values by Column**")
        missing_s = df.isnull().sum()
        missing_s = missing_s[missing_s > 0].sort_values(ascending=True)
        if missing_s.empty:
            st.success("No missing values detected in any column.")
        else:
            fig, ax = make_fig(7, max(4, len(missing_s) * 0.5))
            bars = ax.barh(missing_s.index, missing_s.values,
                           color=PAL['orange'], alpha=0.85, height=0.6)
            ax.set_xlabel('Missing Count', fontsize=10)
            ax.grid(True, axis='x', color=PAL['grid'], alpha=0.5, linestyle='--')
            for bar, val in zip(bars, missing_s.values):
                ax.text(val + missing_s.max() * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f'{val:,}', va='center', fontsize=9,
                        color=PAL['cyan'], fontweight='bold')
            style_ax(fig, ax)
            st.pyplot(fig)
            plt.close()

    with viz_r:
        st.markdown("**Distribution Plot — Select Column**")
        selected_col = st.selectbox("Column", options=num_df.columns.tolist(), key="dist_sel")
        fig, ax = make_fig(7, 4)
        data = num_df[selected_col].dropna()
        ax.hist(data, bins=40, color=PAL['green'], alpha=0.45,
                edgecolor=PAL['card'], density=True, label='Histogram')
        try:
            kde_x = np.linspace(data.min(), data.max(), 300)
            kde   = gaussian_kde(data)
            ax.plot(kde_x, kde(kde_x), color=PAL['cyan'], linewidth=2.5, label='KDE')
        except Exception:
            pass
        ax.set_xlabel(selected_col, fontsize=10)
        ax.set_ylabel('Density', fontsize=10)
        ax.legend(facecolor=PAL['card'], edgecolor=PAL['border'], labelcolor=PAL['muted'])
        ax.grid(True, axis='y', color=PAL['grid'], alpha=0.5, linestyle='--')
        style_ax(fig, ax)
        st.pyplot(fig)
        plt.close()

    st.divider()

    # Dataset Explorer sub-tabs
    st.subheader("Dataset Explorer")
    etab1, etab2, etab3 = st.tabs(
        ["📋 Summary Statistics", "🗂️ Raw Data Preview", "❓ Missing Values"]
    )
    with etab1:
        st.dataframe(num_df.describe().round(2), use_container_width=True)
    with etab2:
        st.dataframe(df.head(25), use_container_width=True)
    with etab3:
        mv = df.isnull().sum().reset_index()
        mv.columns = ['Column', 'Missing Values']
        mv['Status'] = mv['Missing Values'].apply(
            lambda x: '✅ Complete' if x == 0 else f'⚠️ {x} missing'
        )
        st.dataframe(mv, use_container_width=True)

# ── Footer ──
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#2D3748; font-size:0.8rem;'>"
    "Web Analytics Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Matplotlib"
    "</p>",
    unsafe_allow_html=True
)