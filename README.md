# Intelligent Online Retail Customer Segmentation & Marketing Recommendation System (PySpark)

[![PySpark](https://img.shields.io/badge/Apache%20Spark-4.2-E25A1C?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Parquet](https://img.shields.io/badge/Format-Apache%20Parquet-00D4B2?style=flat)](https://parquet.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Business Question:** *Who are our customers, how valuable are they, who is about to churn, and what specific marketing action and product should the business recommend to each individual customer?*

This project processes **1+ million raw transactions** from the **UCI Online Retail II** dataset (UK online gift retailer, Dec 2009 – Dec 2011) using **Apache Spark (PySpark)** and the **Medallion Data Lakehouse Architecture**. It turns raw invoice lines into an actionable, 360-degree per-customer intelligence engine:

| Customer ID | Segment | Customer Value Score (0–100) | Churn Risk | Priority | Recommended Action | Recommended Products (Top 3) |
|---|---|---|---|---|---|---|
| `14911` | Champions | 98 (Very High) | Low | P3 | VIP loyalty reward + early seasonal access | Regency Cakestand, Teatime Towels, Tea Light Holder |
| `12347` | Loyal | 84 (Very High) | Low | P3 | Cross-category bundle on favourite category | Storage Tins, Jam Jars, Retro Clocks |
| `17850` | At-Risk | 62 (High) | High | P1 | Personal win-back: account manager outreach + voucher | Hanging Heart T-Light, Cake Stand, Vintage Mirror |

An interactive **Streamlit dashboard** sits on top to serve non-technical commercial stakeholders with zero Spark runtime latency.

---

## Architecture & Data Flow

```
 online_retail_II.xlsx ──► CSV ──► [1] Ingestion (explicit StructType schema) ──► bronze/ (Parquet)
                                        │
                                   [2] Cleaning & validation ──► silver/ (Parquet, partitioned Year/Month)
                                        │                          + data-quality funnel audit
                     ┌──────────────────┼─────────────────────────────────┐
                     ▼                  ▼                                 ▼
             [3] Spark SQL EDA    [4] Features (gold/)               [8] FP-Growth Market Basket
             • 9 SQL queries      • RFM + 8 behavioral features       • Distributed itemset mining
             • KPIs, monthly run  • lag() window inter-purchase       • Confidence, lift, support
                                        │                                 │
                                   [5] log1p → Scaler → K-Means           │
                                        │  K sweep (2..8), silhouette     │
                                   [6] Profiling → Dynamic naming         │
                                        │  (Champions, Loyal, At-Risk...) │
                                   [7] Value Score + Churn Risk           │
                                        │                                 │
             [9] Category mix ────►[10] Rule-based recommendation engine ◄┘
                                        │  (Action, Channel, Offer, Priority + Top 3 items)
                                        ▼
                     outputs/final/customer_intelligence.parquet & .csv
                                        │
                     ┌──────────────────┼──────────────────┐
                     ▼                  ▼                  ▼
             [12] 13 Charts (PNG)   Streamlit Dashboard   Walkthrough Notebook
```

---

## Quick Start

### 🪟 Windows Setup & Run

#### 1. Setup Environment
Open PowerShell as Administrator to install dependencies:
```powershell
# Installs OpenJDK 21 and fast uv package manager
winget install --id Microsoft.OpenJDK.21 --accept-source-agreements --accept-package-agreements --exact
winget install --id astral-sh.uv --accept-source-agreements --accept-package-agreements --exact

# Run automated setup script
powershell -ExecutionPolicy Bypass -File scripts/setup_env.ps1
```

#### 2. Download Dataset & Ingest
```powershell
.venv\Scripts\python.exe scripts/download_data.py
```

#### 3. Run the Full PySpark Pipeline
```powershell
.venv\Scripts\python.exe -m src.pipeline
# Or run without the scalability benchmark to execute faster (~2-3 mins):
.venv\Scripts\python.exe -m src.pipeline --skip-benchmark
```
*Or double-click `run_pipeline.bat`.*

#### 4. Launch the Interactive Dashboard
```powershell
.venv\Scripts\streamlit.exe run app/streamlit_app.py
```
*Or double-click `run_dashboard.bat` to launch `http://localhost:8501`.*

#### 5. Run Unit Tests
```powershell
.venv\Scripts\pytest.exe -q
```

---

### 🍎 macOS / Linux Setup & Run

```bash
# Automated environment setup (Java 21 + Python 3.12 venv + dependencies)
./scripts/setup_env.sh
source .venv/bin/activate
export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"

python scripts/download_data.py              # Download + CSV conversion (~1 min)
python -m src.pipeline                       # Full pipeline (~3-5 mins)
pytest -q                                    # Unit tests (10 passed)
streamlit run app/streamlit_app.py           # Launch dashboard at http://localhost:8501
jupyter notebook notebooks/Customer_Segmentation_PySpark.ipynb
```

---

## Big Data Analytics (BDA) Core Concepts Implemented

| Big Data Concept | Implementation in this Project | Why It Matters at Scale |
|:---|:---|:---|
| **Medallion Lakehouse** | Bronze (Raw Parquet) $\rightarrow$ Silver (Partitioned `Year/Month`) $\rightarrow$ Gold (Customer Features) | Eliminates dirty reads, isolates cleaning stages, and supports atomic parquet writes. |
| **Columnar Storage & Partitioning** | Apache Parquet with Snappy compression; partitioned by invoice year & month. | Saves **>70% disk space** and enables partition pruning + column projection pushdown. |
| **Distributed Window Functions** | `F.lag("InvoiceDate", 1).over(Window.partitionBy("CustomerID").orderBy("InvoiceDate"))` | Computes rolling purchase cadence and inter-purchase velocity across worker partitions in parallel. |
| **Explicit Schema Ingestion** | `StructType` definitions with fixed column data types for raw files. | Prevents costly two-pass `inferSchema` scans across millions of transaction rows. |
| **Distributed MLlib Clustering** | `VectorAssembler` $\rightarrow$ `StandardScaler` $\rightarrow$ `KMeans` ($K=2..8$) with `ClusteringEvaluator` and `PCA`. | Clusters high-dimensional customers without single-node memory saturation (OOM). |
| **Distributed Market Basket Mining** | Spark MLlib `FPGrowth` on invoice transaction sets with an adaptive support ladder. | Scales pattern-mining through distributed FP-Trees, avoiding Apriori combinatorial explosion ($2^N$). |
| **Scalability Benchmarking** | Aggregated identical RFM logic in Pandas vs. PySpark from $1\times$ to $40\times$ (**30.8M rows**). | **Proves Big Data superiority:** PySpark ran in **2.07s** vs Pandas **7.60s** at 30.8M rows. |

---

## Customer Segmentation Results ($K=5$)

By combining the **Silhouette Score** (0.36) and business interpretability within the $K=4..6$ range, the pipeline dynamic-profiling engine established 5 distinct segments:

| Cluster | Segment Name | Customer Count | Revenue Share | Median Recency | Median Orders | Median Spend | Strategic Action |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `2` | **🏆 Champions** | 1,026 (17.6%) | **71.8%** | **18 days** | 14 | **£5,617** | VIP concierge, exclusive early product access, reward loyalty. |
| `0` | **💙 Loyal** | 1,521 (26.1%) | **15.3%** | **41 days** | 5 | **£1,403** | Cross-sell category bundles, referral incentives. |
| `3` | **⚠️ At-Risk** | 883 (15.1%) | **6.4%** | **236 days** | 3 | **£854** | **P1 Urgent Win-Back**: Account manager outreach + category voucher. |
| `4` | **💤 Hibernating** | 1,354 (23.2%) | **5.4%** | **318 days** | 1 | **£469** | High-discount re-engagement campaigns via email. |
| `1` | **❌ Lost** | 1,055 (18.1%) | **1.2%** | **337 days** | 1 | **£156** | Low-cost seasonal newsletter only; avoid paid ad spend. |

---

## Scalability Benchmark (Pandas vs PySpark)

Tests were run executing identical RFM aggregation on synthetic scaled copies of the cleaned transactions:

| Scale Factor | Total Row Count | Pandas Runtime | PySpark Runtime | Speedup / Observation |
|:---:|:---:|:---:|:---:|:---|
| **$1\times$** | 770,417 rows | 0.14s | 0.31s | Pandas is faster on small in-memory data (no JVM overhead). |
| **$5\times$** | 3,852,085 rows | 0.61s | 0.42s | PySpark catches up as parallel workers utilize cores. |
| **$10\times$** | 7,704,170 rows | 1.20s | 0.56s | PySpark is **$2.1\times$ faster**. |
| **$20\times$** | 15,408,340 rows | 2.59s | 0.91s | PySpark is **$2.8\times$ faster**. |
| **$40\times$** | **30,816,680 rows** | **7.60s** | **2.07s** | PySpark is **$3.7\times$ faster** with stable memory allocation. |

---

## Streamlit Dashboard Overview

The web application (`app/streamlit_app.py`) provides 6 dedicated pages:

1. **Overview**: Executive KPIs (£17.7M revenue, 5,839 customers, revenue at risk), monthly trend charts, and segment distribution.
2. **Segments**: Segment-level deep-dives with PCA 2D projections, top products purchased, category mix, and churn distributions.
3. **Customer Search**: Drill down into any individual Customer ID to view their full RFM profile, CVS band, churn risk score, priority, and personalized top-3 product recommendations.
4. **Market Basket**: Interactive FP-Growth association rules explorer with dynamic sliders for minimum confidence, lift, and product keyword search.
5. **Model & Data Quality**: Funnel charts tracking rows dropped per cleaning step, alongside K-Means silhouette and elbow curves.
6. **Action List**: Priority-sorted marketing task table with one-click export for CRM campaign execution.

---

## Project Layout

```
├── .streamlit/
│   └── config.toml               # Streamlit theme & layout configuration
├── app/
│   └── streamlit_app.py          # Multi-page interactive Streamlit dashboard
├── docs/
│   ├── images/dashboard/        # High-resolution dashboard screenshots
│   ├── report.md                 # Full project report chapters
│   ├── presentation_outline.md   # Slide deck outline
│   └── viva_qa.md                # 20+ comprehensive Viva examination Q&A
├── notebooks/
│   └── Customer_Segmentation_PySpark.ipynb  # Interactive walkthrough notebook
├── outputs/
│   ├── charts/                   # 13 generated analytical PNG charts (00 to 12)
│   ├── eda/                      # Spark SQL aggregated query results (CSV/JSON)
│   ├── final/                    # Final customer intelligence tables & rules
│   └── models/                   # K-Means sweep & FP-Growth model metadata
├── scripts/
│   ├── download_data.py          # UCI Online Retail II dataset downloader
│   ├── setup_env.ps1             # Windows PowerShell automated setup
│   ├── setup_env.sh              # macOS/Linux Bash automated setup
│   └── build_notebook.py         # Notebook sync utility
├── src/
│   ├── config.py                 # Paths, Spark configurations, and thresholds
│   ├── spark_session.py          # Auto-detecting Java/Hadoop SparkSession builder
│   ├── ingestion.py              # StructType explicit schema ingestion (Bronze)
│   ├── cleaning.py               # 5-step retail cleaning funnel (Silver)
│   ├── eda.py                    # 9 distributed Spark SQL queries
│   ├── features.py               # RFM, lag window functions & behavioral features (Gold)
│   ├── clustering.py             # MLlib log1p + StandardScaler + KMeans + PCA
│   ├── profiling.py              # Dynamic median-based cluster naming
│   ├── scoring.py                # CVS (0-100) and personal churn risk scoring
│   ├── basket.py                 # MLlib FP-Growth association rules
│   ├── product_behaviour.py      # Keyword category affinity heuristics
│   ├── recommender.py            # Hybrid marketing action matrix & cross-sell engine
│   ├── benchmark.py              # Scalability benchmark (Pandas vs PySpark)
│   ├── visualization.py          # 13 report figure generators
│   └── pipeline.py               # Master pipeline orchestrator (Stages 1–12)
├── tests/
│   ├── conftest.py               # Shared Spark test fixtures
│   ├── test_cleaning.py          # Unit tests for data cleaning rules
│   ├── test_features.py          # Unit tests for feature aggregations
│   ├── test_profiling.py         # Unit tests for segment assignment
│   ├── test_recommender.py       # Unit tests for recommendation matrix
│   └── test_scoring.py           # Unit tests for CVS and churn scoring
├── run_dashboard.bat             # 1-click Windows Streamlit launcher
├── run_pipeline.bat              # 1-click Windows PySpark pipeline launcher
└── requirements.txt              # Core project dependencies
```

---

## Deliverables & Key Outputs

- `outputs/final/customer_intelligence.csv`: One row per customer with assigned segment, scores, actions, channel, and top 3 recommended products.
- `outputs/final/segment_profiles.csv`: Per-segment statistics, median RFM metrics, and revenue share.
- `outputs/final/association_rules.csv`: Market basket rules with support, confidence, and lift.
- `outputs/final/run_summary.json`: Headline numbers and audit summary from the latest pipeline run.
- `outputs/charts/*.png`: 13 report-ready publication figures.
