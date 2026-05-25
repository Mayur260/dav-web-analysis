# 🎬 QUICK INTERVIEW SCRIPTS
## One-Liner Explanations for Each Graph

---

## GRAPH 1: KPI CARDS
**Quick Explanation:**
"KPI cards show the most important metrics at a glance. They're designed for executives who don't have time to read reports - they just want 6 big numbers that tell them how the business is doing."

**Key Points:**
- Sum = totals (for counts, revenue, clicks)
- Mean = averages (for rates, percentages, times)
- Format with currency if metric name contains "revenue", "price", "cost"

**Sample Answer:**
"When I see a KPI card showing 'Pageviews: 3.2M', I know the website had 3.2 million total page views. If another card shows 'Bounce Rate: 42%', I know that on average, 42% of visitors leave immediately. Together, these 6 cards tell me the overall health of the website."

---

## GRAPH 2: TRENDS OVER TIME (LINE CHART)
**Quick Explanation:**
"Line charts show how something changes over time. The X-axis represents time progression, and the Y-axis shows the metric value. If the line goes up, the metric is improving (for positive metrics like revenue) or getting worse (for negative metrics like churn)."

**Key Points:**
- X-axis = independent variable (time)
- Y-axis = dependent variable (what we're measuring)
- Uptrend good for revenue, bad for bounce rate
- Look for seasonality, spikes, and sustained patterns

**Sample Answer:**
"This line chart shows pageviews increasing from 2014 to 2023. The steady upward slope tells me the website traffic is growing year-over-year. If the line had dipped sharply in one year, I'd investigate what happened (site redesign? marketing change?). The fact it's consistently up means the website strategy is working."

---

## GRAPH 3 & 4: BAR CHART vs PIE CHART
**Quick Explanation for BAR CHART:**
"Bar charts compare frequencies across categories. The taller the bar, the more common that category is. Use bar charts when you want to rank categories or compare exact counts."

**Quick Explanation for PIE CHART:**
"Pie charts show proportions of a total. If a slice is 40% of the pie, that category represents 40% of all records. Use pie charts to show 'market share' or 'what fraction of the total?'"

**Key Points:**
- Bar = absolute comparison (which is biggest?)
- Pie = relative comparison (what %?)
- Bar better for ranking
- Pie better for showing dominance

**Sample Answer:**
"I have the same data in two formats. The bar chart shows www.brla.gov has 245 records, compared to data.brla.gov's 156 records - a clear ranking. The pie chart shows www.brla.gov is 49% of all records, meaning half the data comes from that one website. The bar helps me rank; the pie helps me see that one website dominates the market."

---

## GRAPH 5: HISTOGRAM (with marginal box plot)
**Quick Explanation:**
"Histograms show the distribution of numeric values. The histogram shows SHAPE (is it bell-shaped? skewed?), and the box plot on the side shows STATISTICS (median, quartiles, outliers). Together they give a complete picture of how data is distributed."

**Key Points:**
- Histogram = frequency of each range
- Box plot = quartiles + outliers + median
- Normal distribution = bell curve
- Skewed distribution = tail on one side
- Outliers = dots beyond whiskers

**Sample Answer:**
"This histogram shows pageviews are NOT normally distributed. Most pages have 100K-200K views (the tall bars), but a few pages have way more (the tail extending right). The box plot confirms this - it shows the median is 98.5K, but there's a dot way out at 3.3M (the homepage), which is an outlier. This tells me traffic is concentrated on a few popular pages."

---

## GRAPH 6: BOX PLOT (standalone)
**Quick Explanation:**
"A box plot is a statistical summary. The line in the middle is the median (50th percentile). The box contains the middle 50% of data. Whiskers extend to normal range. Dots beyond whiskers are outliers that need investigating."

**Key Points:**
- Median = middle value (robust to outliers)
- Box = middle 50% of data
- Whiskers = normal range
- Dots = outliers or unusual values
- Long whisker = skewed data

**Sample Answer:**
"This box plot shows bounce rates. The median is around 42%, and the middle 50% of pages have bounce rates between 28% and 58%. There are two pages with bounce rates above 80% (shown as dots), which is unusual. I'd investigate those pages - they might have technical issues or poor content that's causing visitors to leave immediately."

---

## GRAPH 7: SCATTER PLOT with TRENDLINE
**Quick Explanation:**
"Scatter plots show relationships between two numeric variables. Each dot is one data point. If dots form an upward-right pattern, there's positive correlation (they move together). If downward-right, negative correlation (as one increases, the other decreases). The trendline shows the overall pattern."

**Key Points:**
- X = independent variable (cause)
- Y = dependent variable (effect)
- Upward trendline = positive correlation
- Downward trendline = negative correlation
- Flat trendline = no relationship
- Dots far from line = outliers/anomalies

**Sample Answer:**
"This scatter plot shows sessions vs. revenue. The dots form an upward-right pattern with a strong trendline, showing positive correlation - more website traffic leads to more revenue. One dot far from the line might be a data error or a special bulk order. The correlation coefficient is 0.87, indicating a strong relationship. This tells me our marketing campaigns that drive traffic are effective at generating revenue."

---

## GRAPH 8: CORRELATION HEATMAP
**Quick Explanation:**
"A correlation heatmap shows relationships between ALL numeric variables at once using colors. Red means strong positive correlation (variables move together). Blue means strong negative correlation (they move opposite). White means no relationship. This is a 'cheat sheet' to see what matters most."

**Key Points:**
- Red/hot = strong positive correlation
- Blue/cold = strong negative correlation
- White = no correlation
- Diagonal = always 1.0 (variable vs itself)
- Look for unexpected correlations

**Sample Answer:**
"Looking at this heatmap, I can immediately see that Pageviews and Unique Pageviews are deep red (0.92 correlation) - they move together perfectly, so they're measuring essentially the same thing. Bounce Rate and Exit Rate are also deep red (0.78), which makes sense. But I notice Bounce Rate and Avg. Time on Page are also correlated (0.55), which is interesting - pages with longer content have slightly higher bounce rates. This might mean dense content confuses users, or they read it fully then leave."

---

## GRAPH 9: SUMMARY STATISTICS TABLE
**Quick Explanation:**
"This table shows mean, median, mode, standard deviation, minimum, and maximum for each numeric column. Mean is average (affected by outliers). Median is middle value (robust to outliers). Std Dev shows spread. If mean >> median, data is skewed with outliers."

**Key Points:**
- Mean = average (affected by outliers)
- Median = middle (robust)
- Mode = most frequent value
- Std Dev = spread (higher = more variation)
- Min/Max = range
- Compare mean vs median to spot skewness

**Sample Answer:**
"Looking at this statistics table, pageviews have a mean of 487K but a median of only 98.5K. This huge difference tells me data is heavily skewed - a few very popular pages pull the average way up. The standard deviation of 826K is huge, confirming data is all over the place. For bounce rate, mean (52.34%) and median (48.50%) are close, suggesting bounce rates are more evenly distributed across pages. This table gives me a complete statistical snapshot without needing to calculate anything."

---

# 🎤 FULL INTERVIEW SCENARIOS

## Scenario 1: "Explain All Graphs in 5 Minutes"

"Our dashboard has 9 visualizations that work together:

**Layer 1 - Overview**: KPI cards show 6 key metrics (total pageviews, average bounce rate, etc.). This is the 'executive summary'.

**Layer 2 - Trends**: The line chart shows how key metrics change over time. If traffic is growing year-by-year, the line goes up.

**Layer 3 - Distribution**: Bar and pie charts show the breakdown of categorical data. For example, which website gets most traffic? The bar chart ranks them; the pie chart shows percentages.

**Layer 4 - Value Distribution**: Histograms show the spread of numeric values across their range. Is pageview count normally distributed or skewed? The histogram shows the shape. The box plot shows statistical summary.

**Layer 5 - Relationships**: The scatter plot reveals if two metrics are related. More traffic = more revenue? The scatter plot shows correlation. The heatmap shows all possible correlations at once.

**Layer 6 - Details**: The summary statistics table provides exact mean, median, standard deviation, and range for every numeric column.

Together, these 9 views cover: what happened (KPI), when it happened (trend), what categories matter (bar/pie), how values distribute (histogram/box), which metrics correlate (scatter/heatmap), and what the statistics are (table)."

---

## Scenario 2: "Why So Many Visualizations?"

"Different visualizations answer different questions:

- **KPI Cards**: 'What's the big picture?' (Answer: 6 key numbers)
- **Line Chart**: 'Is it improving?' (Answer: Trend)
- **Bar/Pie Charts**: 'Where should we focus?' (Answer: Top categories)
- **Histogram**: 'Is data normal or weird?' (Answer: Distribution shape)
- **Box Plot**: 'Are there outliers?' (Answer: Statistical summary + anomalies)
- **Scatter Plot**: 'Does one metric drive another?' (Answer: Correlation)
- **Heatmap**: 'Which relationships matter?' (Answer: All correlations)
- **Table**: 'What are exact values?' (Answer: Statistics)

Each visualization is optimized for a specific insight. Together they provide complete analysis."

---

## Scenario 3: "Which Graph Would You Use For..."

**Q: "...show customers our website traffic growth?"**
A: "Line chart showing pageviews over months/years. Executive love seeing the upward trend."

**Q: "...identify which products sell most?"**
A: "Bar chart of product categories by sales volume. Instantly shows ranking."

**Q: "...show what fraction of sales come from each region?"**
A: "Pie chart with region slices. Instantly shows market concentration."

**Q: "...check if our data has errors?"**
A: "Box plot with histogram. Outliers in the box plot reveal data quality issues."

**Q: "...prove marketing spend drives sales?"**
A: "Scatter plot of marketing spend (X) vs revenue (Y) with trendline. Shows correlation."

**Q: "...find all relationships between metrics?"**
A: "Correlation heatmap. One view shows which variables matter and relate to each other."

---

## Scenario 4: "What Does This Trend Mean?"

**Upward trend in pageviews:**
"Traffic is growing. Marketing campaigns are working. Invest more."

**Downward trend in bounce rate:**
"Good! Visitors stay longer. Website content is improving."

**Flat line in revenue:**
"Concerning. Despite traffic, revenue isn't growing. Maybe conversion rate is dropping?"

**Spiky line (sharp peaks and valleys):**
"Volatile. Something is unstable. Check if it's seasonal (expected) or anomaly (investigate)."

---

## Scenario 5: "Interpret This Correlation Coefficient"

**r = 0.95 (near perfect positive):**
"These variables almost perfectly move together. One might predict the other. Or they're measuring the same thing - consider removing one."

**r = 0.35 (weak positive):**
"Slight relationship, but not strong. One doesn't reliably predict the other. Probably multiple factors at play."

**r = 0.0 (no correlation):**
"No relationship whatsoever. These variables are independent. Changing one doesn't affect the other."

**r = -0.72 (strong negative):**
"When one goes up, the other goes down. Example: traffic (up) vs bounce rate (down). Inverse relationship."

---

## Scenario 6: "Red Flag" Questions

**Q: "Why is this one data point way off the line?"**
A: "That's an outlier shown in the box plot. Either it's a data error (data quality issue), or it represents a special case worth investigating (like a bulk order or viral page)."

**Q: "Mean and median are very different. What's wrong?"**
A: "Data is skewed, not normally distributed. Likely a few extreme values pulling the mean. The median is more representative of typical values."

**Q: "The histogram shows two peaks instead of one?"**
A: "Bimodal distribution. There might be two different populations in the data. Example: female heights and male heights mixed together would show two peaks."

**Q: "This scatter plot has points but no clear trendline?"**
A: "Weak or no correlation. These variables aren't related. Can't use one to predict the other."

---

# 📚 TECHNICAL DETAILS FOR DEEP DIVES

## Correlation Coefficient Formula
```
r = Σ[(x - mean_x) × (y - mean_y)] / √[Σ(x - mean_x)² × Σ(y - mean_y)²]

Ranges:
- r = 1.0: Perfect positive correlation
- r = 0.0: No correlation
- r = -1.0: Perfect negative correlation

Strength interpretation:
- 0.7 to 1.0: Strong
- 0.4 to 0.7: Moderate
- 0.0 to 0.4: Weak
```

## Standard Deviation Formula
```
σ = √[Σ(x - mean)² / n]

Or for sample:
s = √[Σ(x - mean)² / (n-1)]
```

## Box Plot IQR Calculation
```
IQR = Q3 - Q1 (Interquartile Range)

Whisker ranges:
- Upper whisker: Q3 + 1.5 × IQR
- Lower whisker: Q1 - 1.5 × IQR

Values outside whiskers are marked as outliers
```

---

# 🏆 INTERVIEW TIPS

1. **Don't memorize definitions.** Explain WHY each graph exists and WHAT insight it provides.

2. **Use real examples.** Say "When we had 3M pageviews, we made $500K revenue" instead of generic "scatter plot shows correlation."

3. **Tell a story.** "First we look at KPI cards to get the big picture. Then we check trends to see if things are improving. Then we drill into categories to find what matters. Then we look at relationships using scatter plots and heatmaps."

4. **Mention business impact.** "This histogram shows most customers spend $20-50. That tells us our pricing strategy should focus on that range."

5. **Show you understand limitations.** "Correlation doesn't mean causation. Just because two metrics correlate doesn't mean one causes the other."

6. **Ask clarifying questions.** "What question are you trying to answer? That determines which graph is best."

---

**END OF QUICK REFERENCE**
