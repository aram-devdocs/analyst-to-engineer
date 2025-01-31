# 🚀 7-Day Data Engineering & Visualization Intensive

**Transform raw data into actionable insights** through a complete pipeline built with modern tools. Designed for analysts transitioning to engineering roles.

![Data Pipeline Diagram](https://example.com/pipeline-diagram.png) _(Replace with actual diagram URL)_

## 🔑 Key Technologies

| Tool           | Role in Project                          |
| -------------- | ---------------------------------------- |
| **PostgreSQL** | OLTP Database for transactional data     |
| **PySpark**    | Distributed processing of large datasets |
| **Airflow**    | Pipeline orchestration & scheduling      |
| **Qlik**       | Business intelligence dashboards         |
| **Plotly**     | Interactive data visualizations          |
| **Docker**     | Containerized database environments      |
| **BigQuery**   | Cloud data warehousing                   |

## 🎯 Learning Objectives

By the end of this intensive, you'll be able to:

✅ Design efficient database schemas (Star Schema, SCD)  
✅ Build robust ETL pipelines with error handling  
✅ Process big data using PySpark distributed computing  
✅ Orchestrate workflows with Airflow DAGs  
✅ Create production-ready dashboards in Qlik  
✅ Develop interactive reports with Plotly

## 📚 Tutorial Overview

### **Days 1-3: Core Foundations**

- **Relational Databases**: OLTP vs OLAP, indexing, window functions
- **Data Modeling**: Star schema, slowly changing dimensions (Type 1/2)
- **ETL Development**: API ingestion, incremental loading, data validation

### **Days 4-5: Scaling & Cloud**

- **Distributed Computing**: PySpark DataFrames, partitioning
- **Cloud Architecture**: GCS storage, BigQuery analytics, Parquet format

### **Days 6-7: Productionization**

- **Workflow Orchestration**: Airflow DAGs with sensors/operators
- **Visualization**: Qlik dashboards, Plotly interactive reports

## 📖 Core Vocabulary

**Essential terms you'll master during this intensive:**

| Term             | Definition                                                     |
| ---------------- | -------------------------------------------------------------- |
| **ETL**          | Extract-Transform-Load process for moving data between systems |
| **OLTP**         | Transactional databases optimized for writes (e.g. PostgreSQL) |
| **OLAP**         | Analytical databases optimized for reads (e.g. BigQuery)       |
| **Star Schema**  | Fact table + dimension tables data model                       |
| **SCD**          | Slowly Changing Dimensions (Type 1/2/3)                        |
| **DAG**          | Directed Acyclic Graph (Airflow workflow structure)            |
| **Data Lake**    | Raw data storage (GCS/S3) before processing                    |
| **Data Mart**    | Subset of data warehouse for specific use cases                |
| **Parquet**      | Columnar storage format for efficient analytics                |
| **Partitioning** | Splitting data by time/type for faster queries                 |
| **Idempotency**  | Designing pipelines to handle reruns safely                    |
| **Data Drift**   | Schema/statistical changes in production data                  |

**Visualization Terms:**

- **Measure** → Quantitative metrics (e.g. fare amount)
- **Dimension** → Categorical attributes (e.g. payment type)
- **Calculated Field** → Derived metrics from raw data
- **Heatmap** → Density visualization using color gradients

## 🏆 Capstone Project

**Build an end-to-end NYC Taxi Analytics Pipeline** (or use your own dataset):

```mermaid
graph LR
A[API/CSV] --> B{PostgreSQL}
B --> C[PySpark Processing]
C --> D[[BigQuery]]
D --> E[Qlik Dashboard]
D --> F[Plotly Report]
```

## 🛠️ Prerequisites

- Basic Python & SQL knowledge
- Docker Desktop installed ([guide](https://www.docker.com/products/docker-desktop/))
- Python 3.8+ with virtual environments
- (Optional) GCP/AWS account for cloud modules

## 🚦 Getting Started

1. **Set Up Environment**:

```bash
# Day 0 Setup
docker run --name nyc-taxi-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres
python -m venv de_env && source de_env/bin/activate
pip install -r requirements.txt
```

2. **Download Dataset**:

```bash
wget -P data/raw https://example.com/nyc-taxi.csv  # Replace with actual dataset
```

## 📦 End Products

1. **GitHub Repository**:

   - Production-grade ETL scripts
   - Jupyter notebooks with exploration
   - Airflow DAG definitions
   - Documentation (schema designs, pipeline diagram)

2. **Qlik Dashboard**:

   - Real-time taxi metrics
   - Driver performance analytics
   - Revenue trends by time period

3. **Plotly Report**:
   - Interactive fare analysis
   - Geospatial visualization of trips
   - Hourly demand heatmaps

---
