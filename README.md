# dav-web-analysis# 🌐 Web Analytics Dashboard

A modern **Flask-based data analysis and visualization dashboard** built to analyze web traffic and user behavior. This project provides statistical insights and multiple visualizations through a clean, responsive web interface.

---

## 🚀 Features

* **Interactive Dashboard UI**
  Clean and structured web interface built using HTML, CSS, and Flask templating.

* **Statistical Analysis**
  Automatically calculates:

  * Mean
  * Median
  * Mode

* **Data Cleaning Pipeline**

  * Handles missing values
  * Removes duplicates
  * Fixes data types

* **Data Visualization**
  Includes multiple graph types:

  * Histogram
  * Bar Chart
  * Box Plot
  * Scatter Plot
  * Correlation Heatmap

* **Organized Layout**

  * Statistics displayed in cards
  * Graphs arranged in grid format
  * Simple and readable dashboard

---

## 🛠️ Technology Stack

* **Backend**: Flask (Python)
* **Frontend**: HTML, CSS, JavaScript
* **Data Processing**: Pandas, NumPy
* **Visualization**: Matplotlib, Seaborn

---

## 📂 Project Structure

```text
web_analytics/
│
├── app.py                      # Main Flask application
├── Web_Analytic_Dataset.csv   # Dataset file
├── requirements.txt            # Dependencies
│
├── templates/
│   └── index.html              # Frontend UI
│
├── static/
│   ├── style.css               # Styling
│   ├── histogram.png
│   ├── bar.png
│   ├── scatter.png
│   ├── boxplot.png
│   └── heatmap.png
```

---

## ⚙️ Getting Started

Follow these steps to run the project locally.

### 1. Navigate to project folder

```bash
cd web_analytics
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run the application

```bash
python app.py
```

---

### 4. Open in browser

```text
http://127.0.0.1:5000/
```

---

## 📊 Dataset

The project uses a web analytics dataset containing user behavior metrics such as:

* Page views
* Traffic sources
* Sessions
* User interactions

---

## 🧠 Project Workflow

1. Load dataset using Pandas
2. Clean and preprocess data
3. Perform statistical analysis
4. Generate visualizations
5. Display results on web dashboard

---

## 💡 Key Insights

* Identifies trends in user activity
* Highlights most common traffic sources
* Shows distribution and relationships between variables

---

## 📌 Future Improvements

* Add interactive charts using JavaScript libraries
* Add user input filters
* Deploy the dashboard online

---

## 🎯 Conclusion

This project demonstrates how data analysis and visualization can be integrated into a web application using Flask, making insights more accessible and user-friendly.

---

## 👨‍💻 Author

Mayur
