import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats as scipy_stats

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="Web Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── CUSTOM CSS ──
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .block-container { padding: 2rem 3rem; }
    h1, h2, h3 { color: #e6edf3; font-family: 'Segoe UI', sans-serif; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stMetric { background: #161b22; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# ── PALETTE ──
PALETTE = {
    'bg':     '#0d1117',
    'card':   '#161b22',
    'accent': '#58a6ff',
    'accent2':'#3fb950',
    'text':   '#e6edf3',
    'muted':  '#8b949e',
    'grid':   '#21262d',
}

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('Web_Analytic_Dataset.csv')

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean numeric columns
    numeric_cols = ['Users', 'New Users', 'Sessions', 'Pageviews',
                    'Transactions', 'Revenue', 'Quantity Sold']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean percentage columns
    for col in ['Bounce Rate', 'Conversion Rate (%)']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert duration to seconds
    def to_seconds(d):
        try:
            parts = str(d).split(':')
            if len(parts) == 3:
                return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        except:
            return np.nan
        return np.nan

    if 'Avg. Session Duration' in df.columns:
        df['Avg. Session Duration'] = df['Avg. Session Duration'].apply(to_seconds)

    # Fill missing values
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].median())

    return df

df = load_data()

# ─────────────────────────────────────────────
# 2. CHART STYLE HELPER
# ─────────────────────────────────────────────
def style_axes(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(PALETTE['card'])
    ax.set_title(title, color=PALETTE['text'], fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, color=PALETTE['muted'], fontsize=10)
    ax.set_ylabel(ylabel, color=PALETTE['muted'], fontsize=10)
    ax.tick_params(colors=PALETTE['muted'])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE['grid'])
    ax.grid(color=PALETTE['grid'], linewidth=0.7, linestyle='--', alpha=0.6)

# ─────────────────────────────────────────────
# 3. HEADER
# ─────────────────────────────────────────────
st.markdown("# 📊 Web Analytics Dashboard")
st.markdown("**Web Traffic · Revenue · Conversion · Sessions**")
st.divider()

# ─────────────────────────────────────────────
# 4. KPI CARDS
# ─────────────────────────────────────────────
st.markdown("## 🔢 Key Metrics")
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("💰 Total Revenue",    f"${int(df['Revenue'].sum()):,}")
k2.metric("📊 Total Sessions",   f"{int(df['Sessions'].sum()):,}")
k3.metric("👥 Total Users",      f"{int(df['Users'].sum()):,}")
k4.metric("🎯 Avg Conversion",   f"{df['Conversion Rate (%)'].mean():.2f}%")
k5.metric("↩️ Avg Bounce Rate",  f"{df['Bounce Rate'].mean():.2f}%")
k6.metric("🛒 Transactions",     f"{int(df['Transactions'].sum()):,}")

st.divider()

# ─────────────────────────────────────────────
# 5. REVENUE STATISTICS
# ─────────────────────────────────────────────
st.markdown("## 📈 Revenue Statistics")
s1, s2, s3, s4 = st.columns(4)

rev = df['Revenue']
mode_val = scipy_stats.mode(rev, keepdims=True).mode[0]

s1.metric("Mean Revenue",   f"${rev.mean():,.2f}")
s2.metric("Median Revenue", f"${rev.median():,.2f}")
s3.metric("Mode Revenue",   f"${mode_val:,.2f}")
s4.metric("Dataset Size",   f"{df.shape[0]} × {df.shape[1]}")

st.divider()

# ─────────────────────────────────────────────
# 6. REVENUE TREND (full width)
# ─────────────────────────────────────────────
st.markdown("## 📉 Revenue Trend Over Time")

trend = df.groupby(['Year', 'Month of the year'])['Revenue'].sum().reset_index()
trend['Period'] = trend['Year'].astype(str) + '-' + trend['Month of the year'].astype(str).str.zfill(2)
trend = trend.sort_values('Period')

fig, ax = plt.subplots(figsize=(14, 4), facecolor=PALETTE['bg'])
ax.plot(trend['Period'], trend['Revenue'],
        color=PALETTE['accent'], linewidth=2, marker='o', markersize=3)
ax.fill_between(range(len(trend)), trend['Revenue'], alpha=0.15, color=PALETTE['accent'])
ax.set_xticks(range(0, len(trend), max(1, len(trend)//10)))
ax.set_xticklabels(trend['Period'].iloc[::max(1, len(trend)//10)], rotation=30, ha='right')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
style_axes(ax, 'Revenue Trend Over Time', 'Period', 'Revenue ($)')
st.pyplot(fig)
plt.close()

st.divider()

# ─────────────────────────────────────────────
# 7. CHART GRID
# ─────────────────────────────────────────────
st.markdown("## 📊 Visualizations")

col1, col2 = st.columns(2)

# Histogram
with col1:
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    sns.histplot(df['Sessions'], bins=25, kde=True, ax=ax,
                 color=PALETTE['accent'], edgecolor=PALETTE['bg'], linewidth=0.4)
    ax.lines[0].set_color(PALETTE['accent2'])
    style_axes(ax, 'Distribution of Sessions', 'Sessions', 'Frequency')
    st.pyplot(fig)
    plt.close()

# Bar Chart
with col2:
    top = df.groupby('Source / Medium')['Revenue'].sum().nlargest(10).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    colors = [PALETTE['accent'] if i < 3 else PALETTE['muted'] for i in range(len(top))]
    sns.barplot(data=top, x='Source / Medium', y='Revenue', ax=ax,
                palette=colors, hue='Source / Medium', legend=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    style_axes(ax, 'Top 10 Sources by Revenue', 'Source', 'Revenue ($)')
    plt.xticks(rotation=30, ha='right')
    st.pyplot(fig)
    plt.close()

col3, col4 = st.columns(2)

# Scatter Plot
with col3:
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    sc = ax.scatter(df['Sessions'], df['Revenue'],
                    c=df['Conversion Rate (%)'],
                    cmap='viridis', alpha=0.7, s=30, edgecolors='none')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.ax.tick_params(colors=PALETTE['muted'])
    cbar.set_label('Conversion Rate (%)', color=PALETTE['muted'], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    style_axes(ax, 'Sessions vs Revenue', 'Sessions', 'Revenue ($)')
    st.pyplot(fig)
    plt.close()

# Box Plot
with col4:
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    box_data = [df['Sessions'].dropna().values, df['Pageviews'].dropna().values]
    bp = ax.boxplot(box_data, patch_artist=True, labels=['Sessions', 'Pageviews'],
                    medianprops=dict(color=PALETTE['accent2'], linewidth=2))
    for patch, c in zip(bp['boxes'], [PALETTE['accent'], '#f78166']):
        patch.set_facecolor(c); patch.set_alpha(0.7)
    for w in bp['whiskers']: w.set_color(PALETTE['muted'])
    for c in bp['caps']:     c.set_color(PALETTE['muted'])
    for f in bp['fliers']:   f.set(marker='o', color=PALETTE['muted'], alpha=0.5, markersize=4)
    style_axes(ax, 'Box Plot – Sessions vs Pageviews')
    st.pyplot(fig)
    plt.close()

st.divider()

# ─────────────────────────────────────────────
# 8. HEATMAP (full width)
# ─────────────────────────────────────────────
st.markdown("## 🔥 Correlation Heatmap")

num_df = df.select_dtypes(include='number').drop(columns=['Year'], errors='ignore')
corr = num_df.corr()
fig, ax = plt.subplots(figsize=(10, 6), facecolor=PALETTE['bg'])
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, ax=ax, annot=True, fmt='.2f', mask=mask,
            cmap='coolwarm', center=0, linewidths=0.5,
            linecolor=PALETTE['bg'],
            annot_kws={'size': 8, 'color': PALETTE['text']})
ax.set_title('Correlation Heatmap', color=PALETTE['text'], fontsize=13, fontweight='bold')
ax.tick_params(colors=PALETTE['muted'])
st.pyplot(fig)
plt.close()

st.divider()

# ─────────────────────────────────────────────
# 9. EDA TABLE
# ─────────────────────────────────────────────
st.markdown("## 🔍 Exploratory Data Analysis")

tab1, tab2, tab3 = st.tabs(["📋 Summary Statistics", "🗂️ Raw Data Preview", "❓ Missing Values"])

with tab1:
    st.dataframe(
        num_df.describe().round(2),
        use_container_width=True
    )

with tab2:
    st.dataframe(df.head(20), use_container_width=True)

with tab3:
    missing = df.isnull().sum().reset_index()
    missing.columns = ['Column', 'Missing Values']
    st.dataframe(missing, use_container_width=True)