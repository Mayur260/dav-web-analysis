import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats as scipy_stats

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
    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .main { background-color: #0d1117; }
    .block-container { padding: 1.8rem 3rem 3rem 3rem; }

    /* ── Header banner ── */
    .dash-header {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 28px 36px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .dash-header h1 {
        color: #e6edf3;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .dash-header p {
        color: #8b949e;
        font-size: 0.95rem;
        margin: 4px 0 0 0;
    }

    /* ── Section titles ── */
    .section-title {
        color: #e6edf3;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin: 0 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #21262d;
    }

    /* ── KPI cards ── */
    .kpi-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 16px 16px 16px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #58a6ff; }
    .kpi-icon  { font-size: 1.6rem; margin-bottom: 6px; }
    .kpi-label { color: #8b949e; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
    .kpi-value { color: #e6edf3; font-size: 1.45rem; font-weight: 700; }

    /* ── Stat cards ── */
    .stat-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
    }
    .stat-label { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .stat-value { color: #58a6ff; font-size: 1.3rem; font-weight: 700; }

    /* ── Chart wrapper ── */
    .chart-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #8b949e;
        padding: 6px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: #21262d;
        border-color: #58a6ff;
        color: #e6edf3 !important;
    }

    /* ── Divider ── */
    hr { border-color: #21262d !important; }

    /* ── Dataframe ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# COLOUR PALETTE (shared by all charts)
# ══════════════════════════════════════════════
PAL = {
    'bg':      '#0d1117',
    'card':    '#161b22',
    'border':  '#30363d',
    'accent':  '#58a6ff',
    'green':   '#3fb950',
    'orange':  '#f0883e',
    'red':     '#f85149',
    'text':    '#e6edf3',
    'muted':   '#8b949e',
    'grid':    '#21262d',
}

# ══════════════════════════════════════════════
# HELPER – STYLE CHART AXES
# ══════════════════════════════════════════════
def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PAL['card'])
    ax.set_title(title, color=PAL['text'], fontsize=12, fontweight='bold', pad=14)
    ax.set_xlabel(xlabel, color=PAL['muted'], fontsize=9)
    ax.set_ylabel(ylabel, color=PAL['muted'], fontsize=9)
    ax.tick_params(colors=PAL['muted'], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(PAL['grid'])
    ax.grid(color=PAL['grid'], linewidth=0.6, linestyle='--', alpha=0.7)

def make_fig(w=7, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=PAL['bg'])
    return fig, ax

def kpi(icon, label, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>"""

def stat_card(label, value):
    return f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
    </div>"""

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

df = load_data()
num_df = df.select_dtypes(include='number').drop(columns=['Year'], errors='ignore')

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
    <div>
        <h1>📊 Web Analytics Dashboard</h1>
        <p>Traffic · Revenue · Conversion · Sessions — all in one place</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SECTION 1 – KPI CARDS
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📌 Key Performance Indicators</p>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)
cards = [
    (c1, "💰", "Total Revenue",    f"${int(df['Revenue'].sum()):,}"),
    (c2, "📊", "Total Sessions",   f"{int(df['Sessions'].sum()):,}"),
    (c3, "👥", "Total Users",      f"{int(df['Users'].sum()):,}"),
    (c4, "🎯", "Avg Conversion",   f"{df['Conversion Rate (%)'].mean():.2f}%"),
    (c5, "↩️", "Avg Bounce Rate",  f"{df['Bounce Rate'].mean():.2f}%"),
    (c6, "🛒", "Transactions",     f"{int(df['Transactions'].sum()):,}"),
]
for col, icon, label, val in cards:
    col.markdown(kpi(icon, label, val), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════
# SECTION 2 – REVENUE STATISTICS
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📈 Revenue Statistics</p>', unsafe_allow_html=True)

rev = df['Revenue']
mode_val = scipy_stats.mode(rev, keepdims=True).mode[0]
dataset_shape = f"{df.shape[0]} rows × {df.shape[1]} cols"

s1, s2, s3, s4 = st.columns(4)
s1.markdown(stat_card("Mean Revenue",   f"${rev.mean():,.2f}"), unsafe_allow_html=True)
s2.markdown(stat_card("Median Revenue", f"${rev.median():,.2f}"), unsafe_allow_html=True)
s3.markdown(stat_card("Mode Revenue",   f"${mode_val:,.2f}"), unsafe_allow_html=True)
s4.markdown(stat_card("Dataset Size",   dataset_shape), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════
# SECTION 3 – REVENUE TREND (full width)
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📉 Revenue Trend Over Time</p>', unsafe_allow_html=True)

trend = (
    df.groupby(['Year', 'Month of the year'])['Revenue']
    .sum()
    .reset_index()
)
trend['Period'] = (
    trend['Year'].astype(str) + '-' +
    trend['Month of the year'].astype(str).str.zfill(2)
)
trend = trend.sort_values('Period').reset_index(drop=True)

fig, ax = make_fig(14, 4)
x = range(len(trend))
ax.plot(x, trend['Revenue'], color=PAL['accent'], linewidth=2.2,
        marker='o', markersize=3.5, zorder=3)
ax.fill_between(x, trend['Revenue'], alpha=0.12, color=PAL['accent'])

step = max(1, len(trend) // 10)
ax.set_xticks(list(x)[::step])
ax.set_xticklabels(trend['Period'].iloc[::step], rotation=30, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
style_ax(ax, 'Revenue Trend Over Time', 'Period', 'Revenue ($)')
st.pyplot(fig)
plt.close()

st.divider()

# ══════════════════════════════════════════════
# SECTION 4 – VISUALIZATIONS GRID
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">📊 Visualizations</p>', unsafe_allow_html=True)

# ── Row 1 ──────────────────────────────────────
col_l, col_r = st.columns(2, gap="medium")

with col_l:
    st.markdown("**Distribution of Sessions**")
    fig, ax = make_fig()
    sns.histplot(df['Sessions'], bins=28, kde=True, ax=ax,
                 color=PAL['accent'], edgecolor=PAL['bg'], linewidth=0.3)
    if ax.lines:
        ax.lines[0].set_color(PAL['green'])
    style_ax(ax, xlabel='Sessions', ylabel='Frequency')
    st.pyplot(fig)
    plt.close()

with col_r:
    st.markdown("**Top 10 Sources by Revenue**")
    top = (
        df.groupby('Source / Medium')['Revenue']
        .sum()
        .nlargest(10)
        .reset_index()
    )
    fig, ax = make_fig()
    bar_colors = [PAL['accent'] if i < 3 else PAL['muted'] for i in range(len(top))]
    sns.barplot(data=top, x='Source / Medium', y='Revenue', ax=ax,
                palette=bar_colors, hue='Source / Medium', legend=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
    style_ax(ax, xlabel='Source / Medium', ylabel='Revenue ($)')
    plt.xticks(rotation=32, ha='right', fontsize=8)
    st.pyplot(fig)
    plt.close()

# ── Row 2 ──────────────────────────────────────
col_l2, col_r2 = st.columns(2, gap="medium")

with col_l2:
    st.markdown("**Sessions vs Revenue (coloured by Conversion Rate)**")
    fig, ax = make_fig()
    sc = ax.scatter(df['Sessions'], df['Revenue'],
                    c=df['Conversion Rate (%)'],
                    cmap='plasma', alpha=0.65, s=28, edgecolors='none')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.ax.tick_params(colors=PAL['muted'], labelsize=8)
    cbar.set_label('Conversion Rate (%)', color=PAL['muted'], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:,.0f}'))
    style_ax(ax, xlabel='Sessions', ylabel='Revenue ($)')
    st.pyplot(fig)
    plt.close()

with col_r2:
    st.markdown("**Box Plot – Sessions vs Pageviews**")
    fig, ax = make_fig()
    bp = ax.boxplot(
        [df['Sessions'].dropna().values, df['Pageviews'].dropna().values],
        patch_artist=True,
        labels=['Sessions', 'Pageviews'],
        medianprops=dict(color=PAL['green'], linewidth=2)
    )
    box_colors = [PAL['accent'], PAL['orange']]
    for patch, c in zip(bp['boxes'], box_colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    for w in bp['whiskers']: w.set_color(PAL['muted'])
    for cap in bp['caps']:   cap.set_color(PAL['muted'])
    for fl in bp['fliers']:
        fl.set(marker='o', color=PAL['muted'], alpha=0.45, markersize=4)
    style_ax(ax, ylabel='Value')
    st.pyplot(fig)
    plt.close()

st.divider()

# ══════════════════════════════════════════════
# SECTION 5 – CORRELATION HEATMAP (full width)
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">🔥 Correlation Heatmap</p>', unsafe_allow_html=True)

corr = num_df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(11, 6), facecolor=PAL['bg'])
sns.heatmap(
    corr, ax=ax,
    annot=True, fmt='.2f',
    mask=mask,
    cmap='coolwarm', center=0,
    linewidths=0.5, linecolor=PAL['bg'],
    annot_kws={'size': 8, 'color': PAL['text']}
)
ax.set_title('Feature Correlation Matrix', color=PAL['text'], fontsize=13, fontweight='bold', pad=14)
ax.tick_params(colors=PAL['muted'], labelsize=9)
st.pyplot(fig)
plt.close()

st.divider()

# ══════════════════════════════════════════════
# SECTION 6 – EDA TABS
# ══════════════════════════════════════════════
st.markdown('<p class="section-title">🔍 Exploratory Data Analysis</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Summary Statistics", "🗂️ Raw Data Preview", "❓ Missing Values"])

with tab1:
    st.dataframe(num_df.describe().round(2), use_container_width=True)

with tab2:
    st.dataframe(df.head(25), use_container_width=True)

with tab3:
    missing = df.isnull().sum().reset_index()
    missing.columns = ['Column', 'Missing Values']
    missing['Status'] = missing['Missing Values'].apply(
        lambda x: '✅ Complete' if x == 0 else f'⚠️ {x} missing'
    )
    st.dataframe(missing, use_container_width=True)

# ── Footer ──────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#30363d; font-size:0.8rem;'>"
    "Web Analytics Dashboard · Built with Streamlit & Matplotlib"
    "</p>",
    unsafe_allow_html=True
)