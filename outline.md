# **7-Day Data Engineering & Visualization Masterclass**

**Objective**: Transition from data analysis to engineering by building an end-to-end pipeline with PostgreSQL, PySpark, Airflow, Qlik, and Plotly.

---

## **Day 0: Environment Setup & Data Preparation**

### **Core Concepts**

1. **Environment Isolation**:
   - Use Docker for database containers (PostgreSQL)
   - Virtual environments for Python dependencies
2. **Data Engineering Toolkit**:
   - SQL databases, Spark, orchestration tools
3. **Data Organization**:
   - Raw vs. processed data directories

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Validate installations
- **Scripts**: Setup automation

---

### **Step-by-Step Guide**

#### **1. Install Docker & Start PostgreSQL**

```bash
# For Linux/Mac/WSL
docker run --name nyc-taxi-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres
```

#### **2. Set Up Python Environment**

```bash
python -m venv de_env
source de_env/bin/activate  # Linux/Mac
pip install sqlalchemy pyspark pandas plotly apache-airflow google-cloud-bigquery
```

#### **3. Prepare Directory Structure**

```python
# scripts/day0.py
from pathlib import Path

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("notebooks").mkdir(exist_ok=True)
```

#### **4. Install Web Scraping Dependencies**
```bash
pip install beautifulsoup4 requests-html selenium webdriver-manager
```

---

### **Assignment** (`scripts/day0.py`)

**Task**: Create environment validation script.

```python
def check_environment():
    # Verify Docker is running
    if not Path("/var/run/docker.sock").exists():
        raise RuntimeError("Docker not running!")

    # Check Python packages
    required = ["sqlalchemy", "pyspark", "pandas"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Missing package: {pkg}")
```

**Capstone Prep**:

- Download your dataset to `data/raw`
- Add environment variables for cloud services (GCP/AWS)

---

## **Day 1: Databases & SQL**

### **Core Concepts**

1. **OLTP vs. OLAP**:
   - **OLTP** (e.g., PostgreSQL): Handles transactional operations (inserts, updates) for day-to-day apps.
   - **OLAP** (e.g., BigQuery): Optimized for complex analytical queries (e.g., aggregating years of sales data).
2. **Indexes**:
   - Like a book's index, they speed up `WHERE` and `JOIN` queries but slow down writes.
3. **Window Functions**:
   - Perform calculations across rows related to the current row (e.g., running totals, rankings).

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Explore data, test queries, visualize with Plotly.
- **Scripts**: Automate table creation or bulk data loading.

---

### **Step-by-Step Guide**

#### **1. Create a PostgreSQL Database (Notebook)**

```python
# notebooks/day1-sql.ipynb
from sqlalchemy import create_engine
import pandas as pd

# Connect to PostgreSQL
engine = create_engine("postgresql://user:admin@localhost:5432/nyc_taxi")

# Load sample data
df = pd.read_csv("data/raw/taxi_trips.csv")
df.to_sql("trips", engine, if_exists="replace")  # Creates table
```

#### **2. Optimize Queries with Indexes**

```sql
-- Run this in PostgreSQL (pgAdmin or terminal)
CREATE INDEX idx_pickup_time ON trips(pickup_time);
```

#### **3. Window Function Example**

```python
# Calculate cumulative fare per driver
query = """
SELECT
  driver_id,
  pickup_time,
  fare_amount,
  SUM(fare_amount) OVER (PARTITION BY driver_id ORDER BY pickup_time) AS cumulative_fare
FROM trips;
"""
result = pd.read_sql(query, engine)
```

#### **4. Visualize with Plotly**

```python
import plotly.express as px
fig = px.line(result, x="pickup_time", y="cumulative_fare", color="driver_id")
fig.show()
```

---

### **Assignment** (`scripts/day1.py`)

**Task**: Automate table creation and index generation.

```python
from sqlalchemy import create_engine, text

def main():
    engine = create_engine("postgresql://user:admin@localhost:5432/nyc_taxi")
    df = pd.read_csv("data/raw/taxi_trips.csv")
    df.to_sql("trips", engine, if_exists="replace")

    # Create indexes
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX idx_pickup_time ON trips(pickup_time);"))
        conn.execute(text("CREATE INDEX idx_driver_id ON trips(driver_id);"))

if __name__ == "__main__":
    main()
```

**Capstone Prep**:

- Create a table for your dataset and add indexes.

---

## **Day 2: Data Modeling**

### **Core Concepts**

1. **Star Schema**:
   - **Fact Table**: Contains metrics (e.g., `fare_amount`, `trip_distance`).
   - **Dimension Tables**: Descriptive attributes (e.g., `drivers`, `passengers`).
2. **Slowly Changing Dimensions (SCD)**:
   - **Type 1**: Overwrite old data (no history).
   - **Type 2**: Track history with `valid_from` and `valid_to` dates.

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Prototype schemas, test SCD logic.
- **Scripts**: Deploy schema migrations.

---

### **Step-by-Step Guide**

#### **1. Design a Star Schema (Notebook)**

```python
# notebooks/day2-modeling.ipynb
from sqlalchemy import text

# Fact Table
engine.execute(text("""
  CREATE TABLE fact_trips (
    trip_id SERIAL PRIMARY KEY,
    driver_id INT,
    passenger_id INT,
    fare_amount DECIMAL,
    pickup_time TIMESTAMP
  );
"""))

# Dimension Table: Drivers (SCD Type 2)
engine.execute(text("""
  CREATE TABLE dim_drivers (
    driver_id INT PRIMARY KEY,
    name VARCHAR(100),
    valid_from DATE,
    valid_to DATE DEFAULT '9999-12-31'
  );
"""))
```

#### **2. Populate Dimension Tables**

```python
drivers = pd.DataFrame({
    "driver_id": [1, 2],
    "name": ["Alice", "Bob"],
    "valid_from": ["2024-01-01", "2024-01-01"]
})
drivers.to_sql("dim_drivers", engine, if_exists="append", index=False)
```

#### **3. Query Star Schema**

```python
query = """
SELECT
  d.name AS driver_name,
  SUM(f.fare_amount) AS total_fares
FROM fact_trips f
JOIN dim_drivers d ON f.driver_id = d.driver_id
GROUP BY d.name;
"""
result = pd.read_sql(query, engine)
```

---

### **Assignment** (`scripts/day2.py`)

**Task**: Automate SCD Type 2 updates.

```python
def update_driver(driver_id, new_name, valid_date):
    # Expire old record
    engine.execute(text(f"""
      UPDATE dim_drivers
      SET valid_to = '{valid_date}'
      WHERE driver_id = {driver_id} AND valid_to = '9999-12-31';
    """))

    # Insert new record
    engine.execute(text(f"""
      INSERT INTO dim_drivers (driver_id, name, valid_from)
      VALUES ({driver_id}, '{new_name}', '{valid_date}');
    """))
```

**Capstone Prep**:

- Design a star schema for your dataset.

---

## **Day 3: ETL & Web Scraping Pipelines**

### **Core Concepts**

1. **Web Scraping Best Practices**:
   - Legal compliance (robots.txt, terms of service)
   - Rate limiting & request throttling
   - Handling dynamic content with headless browsers
   - Data cleaning & validation

2. **ETL Patterns**:
   - Incremental loading strategies
   - Data quality checks
   - Error handling & retry mechanisms

### **When to Use Web Scraping**
- **Use When**: No API available, public data aggregation
- **Avoid For**: Protected/personal data, high-frequency requests

---

### **Step-by-Step Guide**

#### **1. Extract Data from API (Notebook)**

```python
# notebooks/day3-etl.ipynb
import requests

response = requests.get("https://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=NYC")
weather_data = response.json()

# Flatten nested JSON
transformed = {
    "timestamp": weather_data["location"]["localtime"],
    "temp_c": weather_data["current"]["temp_c"],
    "humidity": weather_data["current"]["humidity"]
}
```

#### **2. Load into PostgreSQL**

```python
weather_df = pd.DataFrame([transformed])
weather_df.to_sql("weather", engine, if_exists="append", index=False)
```

#### **3. Web Scraping with BeautifulSoup (Notebook)**
```python
# notebooks/day3-etl.ipynb
from bs4 import BeautifulSoup
import requests
import time

def scrape_taxi_zones():
    url = "https://www.nyc.gov/site/tlc/about/taxi-zones.page"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    zones = []
    for row in soup.select('table.zones-table tbody tr'):
        cells = row.find_all('td')
        zones.append({
            'zone_id': cells[0].text.strip(),
            'zone_name': cells[1].text.strip(),
            'borough': cells[2].text.strip()
        })
        time.sleep(0.5)  # Rate limiting
    
    return pd.DataFrame(zones)

zones_df = scrape_taxi_zones()
zones_df.to_sql('taxi_zones', engine, if_exists='replace')
```

#### **4. Handling JavaScript-Rendered Pages**
```python
# For sites requiring JS execution
from requests_html import HTMLSession

session = HTMLSession()
r = session.get('https://example-js-site.com')
r.html.render(sleep=2)  # Let JavaScript execute
print(r.html.find('#dynamic-content', first=True).text)
```

---

### **Assignment** (`scripts/day3.py`)

**Task**: Build a resilient web scraper with:
- Retry logic for failed requests
- HTML cleanup functions
- Ethical scraping practices

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def clean_html(text):
    # Remove unwanted characters/whitespace
    return ' '.join(text.strip().split())

def ethical_scrape(url):
    # Check robots.txt first (simplified example)
    robots = requests.get(f"{url}/robots.txt").text
    if "Disallow: /data" in robots:
        raise Exception("Scraping disallowed by robots.txt")
    
    session = get_session()
    response = session.get(url, timeout=10)
    response.raise_for_status()
    
    return clean_html(response.text)
```

**Capstone Prep**:

- Add web scraping component to your ETL pipeline
- Store raw HTML + cleaned structured data
- Implement scraping monitoring (success rate, data freshness)

---

## **Day 4: PySpark & Distributed Processing**

### **Core Concepts**

1. **Apache Spark**:
   - Framework for distributed data processing (handles large datasets).
2. **DataFrames**:
   - Distributed collection of data with named columns (similar to pandas).
3. **Partitioning**:
   - Split data into chunks (e.g., by date) for parallel processing.

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Prototype Spark logic.
- **Scripts**: Run batch jobs (e.g., daily aggregations).

---

### **Step-by-Step Guide**

#### **1. Analyze Data with PySpark (Notebook)**

```python
# notebooks/day4-pyspark.ipynb
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TaxiAnalysis").getOrCreate()
df = spark.read.csv("data/raw/trips.csv", header=True, inferSchema=True)

# Average fare by passenger count
df.groupBy("passenger_count").avg("fare_amount").show()
```

#### **2. Save Partitioned Data**

```python
df.write.partitionBy("passenger_count").parquet("data/processed/trips_partitioned")
```

---

### **Assignment** (`scripts/day4.py`)

**Task**: Calculate hourly trip counts.

```python
from pyspark.sql.functions import hour

def main():
    df = spark.read.csv("data/raw/trips.csv", header=True, inferSchema=True)
    df = df.withColumn("pickup_hour", hour("pickup_time"))
    hourly_counts = df.groupBy("pickup_hour").count()
    hourly_counts.write.parquet("data/processed/hourly_counts")
```

**Capstone Prep**:

- Process your dataset with PySpark.

---

## **Day 5: Cloud Data Warehousing**

### **Core Concepts**

1. **Data Lake vs. Warehouse**:
   - **Lake** (e.g., S3/GCS): Stores raw, unstructured data.
   - **Warehouse** (e.g., BigQuery): Stores processed, query-ready data.
2. **Parquet**:
   - Columnar storage format optimized for analytics (faster queries, smaller size).

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Explore BigQuery, test queries.
- **Scripts**: Automate GCS/BigQuery workflows.

---

### **Step-by-Step Guide**

#### **1. Upload Data to BigQuery (Notebook)**

```python
# notebooks/day5-bigquery.ipynb
from google.cloud import bigquery

client = bigquery.Client()
table_ref = client.dataset("nyc_taxi").table("trips")

# Load Parquet data from GCS
job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET)
load_job = client.load_table_from_uri("gs://your-bucket/trips.parquet", table_ref, job_config=job_config)
load_job.result()
```

---

### **Assignment** (`scripts/day5.py`)

**Task**: Automate GCS uploads.

```python
from google.cloud import storage

def upload_to_gcs(local_path, gcs_path):
    client = storage.Client()
    bucket = client.get_bucket("your-bucket")
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)

upload_to_gcs("data/processed/hourly_counts.parquet", "hourly_counts.parquet")
```

**Capstone Prep**:

- Load your dataset into BigQuery.

---

## **Day 6: Orchestration with Airflow**

### **Core Concepts**

1. **DAG (Directed Acyclic Graph)**:
   - Workflow with tasks and dependencies (no loops).
2. **Operators**:
   - Actions like running Python code (`PythonOperator`) or Bash commands.
3. **Sensors**:
   - Wait for external events (e.g., a file arriving in S3).

### **When to Use Notebooks vs. Scripts**

- **Notebooks**: Prototype DAG logic.
- **Scripts**: Deploy production DAGs.

---

### **Step-by-Step Guide**

#### **1. Create a DAG (Notebook)**

```python
# notebooks/day6-airflow.ipynb
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG("taxi_pipeline", start_date=datetime(2024, 1, 1), schedule="@daily")

def run_etl():
    print("Running ETL...")

etl_task = PythonOperator(task_id="run_etl", python_callable=run_etl, dag=dag)
```

---

### **Assignment** (`scripts/day6.py`)

**Task**: Schedule ETL with error handling.

```python
from airflow.operators.email import EmailOperator

def validate_data():
    result = pd.read_sql("SELECT COUNT(*) FROM trips", engine)
    if result.iloc[0][0] == 0:
        raise ValueError("No data found!")

validate_task = PythonOperator(task_id="validate_data", python_callable=validate_data)
alert_task = EmailOperator(task_id="alert", to="you@example.com", subject="Pipeline Failed")

etl_task >> validate_task >> alert_task
```

**Capstone Prep**:

- Automate your pipeline with Airflow.

---

## **Day 7: Capstone Project**

### **Enhanced Pipeline Architecture**

```mermaid
graph LR
A[Web Scraping] --> B{PostgreSQL}
C[API/CSV] --> B
B --> D[PySpark Processing]
D --> E[[BigQuery]]
E --> F[Qlik Dashboard]
E --> G[Plotly Report]
```

### **Required Deliverables**

1. **Web Scraping Components**:
   - Legal compliance checklist
   - Data quality reports
   - Rate limiting implementation
   
2. **Pipeline Documentation**:
   - Schema designs (ER diagrams)
   - Airflow DAG definitions
   - Data dictionary

---

This structure ensures the student **learns concepts first**, **practices with code**, and **applies everything to a real project**. Each day's work feeds into the capstone, and the mix of notebooks/scripts mirrors real-world workflows.
