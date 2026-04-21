"""
Web Analytics Dashboard - Flask App
Author: Data Analysis Project
Description: Loads, cleans, analyzes web analytics data and serves a dashboard
"""

import os
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from flask import Flask, render_template, jsonify
from scipy import stats as scipy_stats

app = Flask(__name__)

# ─────────────────────────────────────────────
# 1. DATA LOADING
# ─────────────────────────────────────────────
def load_dataset(path):
    """Auto-detect CSV or Excel and load into DataFrame."""
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.xlsx', '.xls']:
        return pd.read_excel(path)
    else:
        return pd.read_csv(path)

# ─────────────────────────────────────────────
# 2. DATA CLEANING
# ─────────────────────────────────────────────
def clean_data(df):
    """Clean: remove duplicates, fix types, handle missing values."""
    df = df.drop_duplicates()

    # Strip commas from numeric-looking string columns and convert
    numeric_cols = ['Users', 'New Users', 'Sessions', 'Pageviews',
                    'Transactions', 'Revenue', 'Quantity Sold']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Strip % from Bounce Rate and Conversion Rate and convert
    pct_cols = ['Bounce Rate', 'Conversion Rate (%)']
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert Avg. Session Duration (HH:MM:SS) to total seconds
    if 'Avg. Session Duration' in df.columns:
        def duration_to_seconds(d):
            try:
                parts = str(d).split(':')
                if len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                elif len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
            except:
                return np.nan
        df['Avg. Session Duration'] = df['Avg. Session Duration'].apply(duration_to_seconds)

    # Fill remaining numeric NaN with column median
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].median())

    return df

# ─────────────────────────────────────────────
# 3. CHART HELPERS
# ─────────────────────────────────────────────
# Consistent dark palette
PALETTE = {
    'bg':     '#0d1117',
    'card':   '#161b22',
    'accent': '#58a6ff',
    'accent2':'#3fb950',
    'text':   '#e6edf3',
    'muted':  '#8b949e',
    'grid':   '#21262d',
}

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                facecolor=fig.get_facecolor(), dpi=120)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def style_axes(ax, title='', xlabel='', ylabel=''):
    """Apply uniform dark styling to any Axes."""
    ax.set_facecolor(PALETTE['card'])
    ax.set_title(title, color=PALETTE['text'], fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, color=PALETTE['muted'], fontsize=10)
    ax.set_ylabel(ylabel, color=PALETTE['muted'], fontsize=10)
    ax.tick_params(colors=PALETTE['muted'])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE['grid'])
    ax.grid(color=PALETTE['grid'], linewidth=0.7, linestyle='--', alpha=0.6)

# ─────────────────────────────────────────────
# 4. VISUALIZATION GENERATORS
# ─────────────────────────────────────────────
def plot_histogram(df):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    sns.histplot(df['Sessions'], bins=25, kde=True, ax=ax,
                 color=PALETTE['accent'], edgecolor=PALETTE['bg'], linewidth=0.4)
    ax.lines[0].set_color(PALETTE['accent2'])
    style_axes(ax, 'Distribution of Sessions', 'Sessions', 'Frequency')
    return fig_to_base64(fig)

def plot_bar(df):
    top = df.groupby('Source / Medium')['Revenue'].sum().nlargest(10).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    colors = [PALETTE['accent'] if i < 3 else PALETTE['muted'] for i in range(len(top))]
    sns.barplot(data=top, x='Source / Medium', y='Revenue', ax=ax,
                palette=colors, hue='Source / Medium', legend=False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    style_axes(ax, 'Top 10 Sources by Revenue', 'Source / Medium', 'Total Revenue ($)')
    plt.xticks(rotation=30, ha='right')
    return fig_to_base64(fig)

def plot_boxplot(df):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    box_data = [df[col].dropna().values for col in ['Sessions', 'Pageviews']]
    bp = ax.boxplot(box_data, patch_artist=True, labels=['Sessions', 'Pageviews'],
                    medianprops=dict(color=PALETTE['accent2'], linewidth=2))
    colors_box = [PALETTE['accent'], '#f78166']
    for patch, c in zip(bp['boxes'], colors_box):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    for whisker in bp['whiskers']:
        whisker.set_color(PALETTE['muted'])
    for cap in bp['caps']:
        cap.set_color(PALETTE['muted'])
    for flier in bp['fliers']:
        flier.set(marker='o', color=PALETTE['muted'], alpha=0.5, markersize=4)
    style_axes(ax, 'Box Plot – Sessions vs Pageviews')
    return fig_to_base64(fig)

def plot_scatter(df):
    fig, ax = plt.subplots(figsize=(7, 4), facecolor=PALETTE['bg'])
    sc = ax.scatter(df['Sessions'], df['Revenue'],
                    c=df['Conversion Rate (%)'],
                    cmap='viridis', alpha=0.7, s=30, edgecolors='none')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.ax.tick_params(colors=PALETTE['muted'])
    cbar.set_label('Conversion Rate (%)', color=PALETTE['muted'], fontsize=9)
    style_axes(ax, 'Sessions vs Revenue (colored by Conversion Rate)',
               'Sessions', 'Revenue ($)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    return fig_to_base64(fig)

def plot_heatmap(df):
    num_df = df.select_dtypes(include='number').drop(columns=['Year'], errors='ignore')
    corr = num_df.corr()
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=PALETTE['bg'])
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, ax=ax, annot=True, fmt='.2f', mask=mask,
                cmap='coolwarm', center=0, linewidths=0.5,
                linecolor=PALETTE['bg'],
                annot_kws={'size': 8, 'color': PALETTE['text']},
                cbar_kws={'shrink': 0.8})
    ax.set_title('Correlation Heatmap', color=PALETTE['text'],
                 fontsize=13, fontweight='bold', pad=12)
    ax.tick_params(colors=PALETTE['muted'])
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=PALETTE['muted'])
    return fig_to_base64(fig)

def plot_revenue_trend(df):
    trend = df.groupby(['Year', 'Month of the year'])['Revenue'].sum().reset_index()
    trend['Period'] = trend['Year'].astype(str) + '-' + trend['Month of the year'].astype(str).str.zfill(2)
    trend = trend.sort_values('Period')
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=PALETTE['bg'])
    ax.plot(trend['Period'], trend['Revenue'], color=PALETTE['accent'],
            linewidth=2, marker='o', markersize=3)
    ax.fill_between(range(len(trend)), trend['Revenue'],
                    alpha=0.15, color=PALETTE['accent'])
    ax.set_xticks(range(0, len(trend), max(1, len(trend)//10)))
    ax.set_xticklabels(trend['Period'].iloc[::max(1, len(trend)//10)],
                       rotation=30, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    style_axes(ax, 'Revenue Trend Over Time', 'Period', 'Revenue ($)')
    return fig_to_base64(fig)

# ─────────────────────────────────────────────
# 5. STATISTICS
# ─────────────────────────────────────────────
def compute_stats(df):
    """Compute mean, median, mode and key KPIs."""
    rev = df['Revenue'].dropna()
    sess = df['Sessions'].dropna()
    mode_val = scipy_stats.mode(rev, keepdims=True).mode[0]
    return {
        'revenue_mean':   round(float(rev.mean()), 2),
        'revenue_median': round(float(rev.median()), 2),
        'revenue_mode':   round(float(mode_val), 2),
        'total_revenue':  int(rev.sum()),
        'total_sessions': int(sess.sum()),
        'total_users':    int(df['Users'].sum()),
        'avg_bounce':     round(float(df['Bounce Rate'].mean()), 2),
        'avg_conversion': round(float(df['Conversion Rate (%)'].mean()), 2),
        'total_transactions': int(df['Transactions'].sum()),
        'row_count':      len(df),
        'col_count':      len(df.columns),
    }

# ─────────────────────────────────────────────
# 6. ROUTES
# ─────────────────────────────────────────────
# Load + clean once at startup
RAW_DF = load_dataset('Web_Analytic_Dataset.csv')
DF = clean_data(RAW_DF.copy())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    return jsonify(compute_stats(DF))

@app.route('/api/charts')
def api_charts():
    return jsonify({
        'histogram':    plot_histogram(DF),
        'bar':          plot_bar(DF),
        'boxplot':      plot_boxplot(DF),
        'scatter':      plot_scatter(DF),
        'heatmap':      plot_heatmap(DF),
        'trend':        plot_revenue_trend(DF),
    })

@app.route('/api/eda')
def api_eda():
    """Return basic EDA info as JSON."""
    num_df = DF.select_dtypes(include='number')
    desc = num_df.describe().round(2).to_dict()
    missing = DF.isnull().sum().to_dict()
    return jsonify({
        'shape': list(DF.shape),
        'columns': list(DF.columns),
        'describe': desc,
        'missing': missing,
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
