import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("netflix_titles.csv")

# Basic cleaning
df = df.dropna(subset=["date_added"])
df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"] = df["date_added"].dt.year

# 1. Movies vs TV Shows
type_counts = df["type"].value_counts()
print("Content Type:\n", type_counts)

type_counts.plot(kind="bar", title="Movies vs TV Shows")
plt.savefig("type_distribution.png")
plt.clf()

# 2. Content added per year
year_counts = df["year_added"].value_counts().sort_index()
year_counts.plot(title="Content Added Over Time")
plt.savefig("content_per_year.png")
plt.clf()

# 3. Top genres
df["listed_in"] = df["listed_in"].str.split(", ")
genres = df.explode("listed_in")

top_genres = genres["listed_in"].value_counts().head(10)
print("\nTop Genres:\n", top_genres)

top_genres.plot(kind="barh", title="Top 10 Genres")
plt.savefig("top_genres.png")
plt.clf()

print("\nAnalysis complete. Charts saved.")