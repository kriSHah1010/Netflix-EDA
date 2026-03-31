# Streaming Content Insights

A polished exploratory data analysis and Streamlit dashboard project using the Netflix titles dataset.

## What this project shows
- Data cleaning and feature engineering in a notebook
- An interactive Streamlit dashboard for exploration
- Clear charts, KPIs, and filtering logic
- A reusable repo structure that looks good on GitHub

## Project structure

```text
netflix_insights/
├── app.py
├── requirements.txt
├── README.md
├── notebooks/
│   └── 01_data_cleaning_and_eda.ipynb
├── data/
│   ├── raw/
│   │   └── netflix_titles.csv
│   └── processed/
│       └── netflix_clean.csv
```

## Setup

1. Put the Kaggle dataset in `data/raw/netflix_titles.csv`
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the notebook

Open:

```bash
jupyter notebook notebooks/01_data_cleaning_and_eda.ipynb
```

## Run the Streamlit app

```bash
streamlit run app.py
```

## Dataset

Use the Netflix titles dataset from Kaggle or any CSV with similar columns:
- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `listed_in`
- `description`

## Portfolio angle

This project demonstrates:
- data cleaning
- missing value handling
- feature engineering
- exploratory analysis
- dashboard building
- communicating insights clearly

## Suggested GitHub repo title

`streaming-content-insights`
