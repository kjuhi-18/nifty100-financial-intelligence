import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import seaborn as sns
import numpy as np
# --------------------------------------------------
# Paths
# --------------------------------------------------

DB_PATH = "db/nifty100.db"

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ELBOW_PLOT = REPORT_DIR / "elbow_plot.png"
CLUSTER_FILE = OUTPUT_DIR / "cluster_labels.csv"
HEATMAP_FILE = REPORT_DIR / "correlation_heatmap.png"
OUTLIER_FILE = OUTPUT_DIR / "outlier_report.csv"
PORTFOLIO_STATS = OUTPUT_DIR / "portfolio_stats.csv"
FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]
CORRELATION_FEATURES = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score"
]
OUTLIER_FEATURES = CORRELATION_FEATURES
# --------------------------------------------------
# Helper
# --------------------------------------------------


def calculate_cagr(begin, end, years):

    if (
        pd.isna(begin)
        or pd.isna(end)
        or years <= 0
    ):
        return None

    if begin == 0:
        return None

    if begin < 0 or end < 0:
        return None

    return ((end / begin) ** (1 / years) - 1) * 100


# --------------------------------------------------
# Database Loader
# --------------------------------------------------


class ClusterLoader:

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)

    def query(self, sql, params=None):
        return pd.read_sql(sql, self.conn, params=params)

    def close(self):
        self.conn.close()

    def get_latest_company_data(self):

        return self.query(
        """
        SELECT
    c.id AS company_id,
    c.company_name,
    s.broad_sector,

    fr.return_on_equity_pct,
fr.debt_to_equity,
fr.operating_profit_margin_pct,
fr.net_profit_margin_pct,
fr.return_on_capital_employed_pct,
fr.interest_coverage,
fr.asset_turnover,
fr.pat_cagr_5yr,
fr.composite_quality_score

        FROM companies c

        JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
           AND fr.year = (
                SELECT MAX(year)
                FROM financial_ratios f2
                WHERE f2.company_id = c.id
           )

        ORDER BY c.id
        """
    )

    def get_fcf_cagr(self):

        df = self.query(
            """
            SELECT

                company_id,
                year,
                free_cash_flow_cr

            FROM financial_ratios
            """
        )

        # Extract numeric year and sort chronologically
        df["year_num"] = pd.to_numeric(
        df["year"].str.extract(r"(\d{4})")[0],
    errors="coerce"
)

# Drop rows where no valid year could be extracted
        df = df.dropna(subset=["year_num"])

        df["year_num"] = df["year_num"].astype(int)

        df = df.sort_values(
            ["company_id", "year_num"]
        )

        rows = []

        for company_id, group in df.groupby("company_id"):

            group = group.dropna(
                subset=["free_cash_flow_cr"]
            )

            if len(group) < 6:

                rows.append(
                    {
                        "company_id": company_id,
                        "fcf_cagr_5yr": None
                    }
                )

                continue

            latest = group.iloc[-1]
            start = group.iloc[-6]

            value = calculate_cagr(
                start["free_cash_flow_cr"],
                latest["free_cash_flow_cr"],
                5
            )

            rows.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr": value
                }
            )

        return pd.DataFrame(rows)
    def get_revenue_cagr(self):

        df = self.query(
        """
        SELECT
            company_id,
            year,
            sales
        FROM profitandloss
        """
    )

    # Extract year for proper chronological sorting
        # Convert year to string first
        df["year"] = df["year"].astype(str)

# Extract numeric year
        df["year_num"] = pd.to_numeric(
        df["year"].str.extract(r"(\d{4})")[0],
    errors="coerce"
)

# Show rows with invalid years (for debugging)
        invalid = df[df["year_num"].isna()]
        if not invalid.empty:
            print(
        f"Ignoring {len(invalid)} TTM records while calculating Revenue CAGR."
    )
# Remove invalid rows
        df = df.dropna(subset=["year_num"])

# Convert to integer
        df["year_num"] = df["year_num"].astype(int)

# Sort chronologically
        df = df.sort_values(
    ["company_id", "year_num"]
)

        rows = []

        for company_id, group in df.groupby("company_id"):

            group = group.dropna(subset=["sales"])

            if len(group) < 6:

                rows.append({
                "company_id": company_id,
                "revenue_cagr_5yr": None
            })
                continue

            latest = group.iloc[-1]
            start = group.iloc[-6]

            value = calculate_cagr(
            start["sales"],
            latest["sales"],
            5
        )

            rows.append({
            "company_id": company_id,
            "revenue_cagr_5yr": value
        })

        return pd.DataFrame(rows)
# --------------------------------------------------
# Data Preparation
# --------------------------------------------------

def impute_sector_median(df):
    """
    Fill missing values using sector median.
    """

    df = df.copy()

    for column in FEATURES:

        # Force numeric
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Sector median
        df[column] = (
            df.groupby("broad_sector")[column]
            .transform(lambda x: x.fillna(x.median()))
        )

        # Global fallback
        df[column] = df[column].fillna(
            df[column].median()
        )

    return df
def scale_features(df):
    """
    Standardize clustering features.
    """

    scaler = StandardScaler()

    scaled = scaler.fit_transform(df[FEATURES])

    scaled_df = pd.DataFrame(
    scaled,
    columns=FEATURES,
    index=df.index
)

    return scaler, scaled_df
def generate_elbow_plot(data):
    """
    Generate inertia vs K plot.
    """

    inertia = []

    for k in range(2, 11):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        model.fit(data)

        inertia.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(
        range(2, 11),
        inertia,
        marker="o"
    )

    plt.title("KMeans Elbow Method")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")

    plt.grid(True)

    plt.savefig(
        ELBOW_PLOT,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"✓ Saved {ELBOW_PLOT}")
def run_kmeans(df, scaled_df):
    """
    Fit KMeans model and assign clusters.
    """

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10
    )

    clusters = model.fit_predict(scaled_df)

    result = df.copy()

    result["cluster_id"] = clusters

    # Distance from assigned centroid
    distances = model.transform(scaled_df)

    result["distance_from_centroid"] = [
        distances[i, cluster]
        for i, cluster in enumerate(clusters)
    ]

    # Temporary names
    result["cluster_name"] = (
        "Cluster " +
        result["cluster_id"].astype(str)
    )

    return result, model
def profile_clusters(clustered):
    """
    Compute mean and median for each cluster.
    """

    summary = (
        clustered
        .groupby("cluster_id")[FEATURES]
        .agg(["mean", "median"])
        .round(2)
    )

    print("\n========== Cluster Profile ==========\n")
    print(summary)

    return summary
def assign_cluster_names(clustered):
    """
    Assign descriptive names to clusters.
    Update these names after reviewing the companies if required.
    """

    cluster_names = {
        0: "Stable Compounders",
        1: "Highly Leveraged Growth",
        2: "Exceptional ROE Leaders",
        3: "Cash Flow Champions",
        4: "High Growth Opportunities",
    }

    clustered["cluster_name"] = clustered["cluster_id"].map(cluster_names)

    return clustered
def generate_portfolio_stats(df):
    """
    Generate portfolio statistics for all KPIs.
    """

    stats = []

    for feature in FEATURES:
        values = pd.to_numeric(df[feature], errors="coerce").dropna()

        stats.append({
            "Metric": feature,
            "P10": values.quantile(0.10),
            "P25": values.quantile(0.25),
            "P50": values.quantile(0.50),
            "P75": values.quantile(0.75),
            "P90": values.quantile(0.90),
            "Mean": values.mean(),
            "Std": values.std()
        })

    portfolio = pd.DataFrame(stats).round(2)

    portfolio.to_csv(PORTFOLIO_STATS, index=False)

    print(f"✓ Saved {PORTFOLIO_STATS}")
def generate_correlation_heatmap(df):
    """
    Generate Pearson Correlation Heatmap.
    """

    corr_df = df[CORRELATION_FEATURES].copy()

    corr_df = corr_df.apply(
        pd.to_numeric,
        errors="coerce"
    )

    corr = corr_df.corr(method="pearson")

    plt.figure(figsize=(12, 10))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        linewidths=0.5,
        fmt=".2f"
    )

    plt.title("Pearson Correlation Heatmap")

    plt.tight_layout()

    plt.savefig(
        HEATMAP_FILE,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"✓ Saved {HEATMAP_FILE}")
def generate_outlier_report(df):
    """
    Detect sector-wise outliers using Z-score.
    """

    outliers = []

    data = df.copy()

    for feature in OUTLIER_FEATURES:

        data[feature] = pd.to_numeric(
            data[feature],
            errors="coerce"
        )

    for sector, group in data.groupby("broad_sector"):

        for feature in OUTLIER_FEATURES:

            values = group[feature]

            std = values.std()

            if pd.isna(std) or std == 0:
                continue

            mean = values.mean()

            z_scores = (values - mean) / std

            flagged = group.loc[
                z_scores.abs() > 3,
                ["company_id", "company_name", "broad_sector"]
            ].copy()

            flagged["metric"] = feature
            flagged["value"] = values[z_scores.abs() > 3].values
            flagged["z_score"] = z_scores[z_scores.abs() > 3].values

            outliers.append(flagged)

    if outliers:
        report = pd.concat(outliers, ignore_index=True)
    else:
        report = pd.DataFrame(
            columns=[
                "company_id",
                "company_name",
                "broad_sector",
                "metric",
                "value",
                "z_score"
            ]
        )

    report = report.round(2)

    report.to_csv(
        OUTLIER_FILE,
        index=False
    )

    print(f"✓ Saved {OUTLIER_FILE}")
# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    loader = ClusterLoader()

    latest = loader.get_latest_company_data()

    fcf = loader.get_fcf_cagr()
    revenue = loader.get_revenue_cagr()

    latest = latest.merge(
    fcf,
    on="company_id",
    how="left"
)

    latest = latest.merge(
    revenue,
    on="company_id",
    how="left"
)

    print(f"Rows before imputation : {len(latest)}")

    latest = impute_sector_median(latest)
    print("\nMissing values after imputation:")
    print(latest[FEATURES].isna().sum())

    print("\nData types:")
    print(latest[FEATURES].dtypes)

    print("\nFirst five rows:")
    print(latest[FEATURES].head())
    scaler, scaled = scale_features(latest)

    print("\nScaled shape :", scaled.shape)

    generate_elbow_plot(scaled)
    clustered, model = run_kmeans(
    latest,
    scaled
)

    generate_portfolio_stats(latest)
    generate_correlation_heatmap(latest)
    generate_outlier_report(latest)
    profile = profile_clusters(clustered)


    print(f"✓ Updated {CLUSTER_FILE} with descriptive cluster names")
    output = clustered[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid"
    ]
]

    output.to_csv(
    CLUSTER_FILE,
    index=False
)   
    print("\nCluster Distribution:\n")
    print(
    output["cluster_id"]
    .value_counts()
    .sort_index()
)
    print(f"✓ Saved {CLUSTER_FILE}")
    print("\nCompanies with extreme ROE (>100%)")
    print(
    clustered.loc[
        clustered["return_on_equity_pct"] > 100,
        ["company_name", "return_on_equity_pct"]
    ]
)

    print("\nCompanies with extreme Operating Margin")
    print(
    clustered.loc[
        clustered["operating_profit_margin_pct"].abs() > 100,
        ["company_name", "operating_profit_margin_pct"]
    ]
)
    loader.close()