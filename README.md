# ✈️ Airflow + LocalStack S3 — Local Data Pipeline

> A production-style Apache Airflow pipeline integrated with a **LocalStack S3** environment — fully containerized with Docker Compose, designed to simulate real AWS workflows locally.

---

## 📌 Project Overview

This project demonstrates a **local data engineering pipeline** using:

- **Apache Airflow** (SequentialExecutor, custom Docker image) for workflow orchestration
- **PostgreSQL** as the Airflow metadata database — production-grade, no SQLite
- **LocalStack** as a drop-in AWS S3 replacement — no cloud account needed
- **S3 Manager UI** for browsing bucket contents visually
- Full **Docker Compose** orchestration with health checks and service dependencies

The pipeline ingests a sample CSV into a local S3 bucket and processes it through Airflow DAGs — mimicking a real-world ingestion workflow at zero cloud cost.

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Docker Network                          │
│                                                                │
│  ┌─────────────┐     ┌─────────────────┐                       │
│  │  LocalStack │────▶│ localstack-init │                       │
│  │  (S3: 4566) │     │ (bucket + CSV)  │                       │
│  └─────────────┘     └─────────────────┘                       │
│         │                                                      │
│  ┌──────▼──────┐     ┌──────────────────────────────────────┐  │
│  │  S3 Manager │     │           Airflow Stack              │  │
│  │  UI (:8888) │     │                                      │  │
│  └─────────────┘     │  ┌────────────┐   airflow-init       │  │
│                      │  │ PostgreSQL │   airflow-webserver  │  │
│                      │  │  (:5432)   │   airflow-scheduler  │  │
│                      │  └────────────┘                      │  │
│                      └──────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| Apache Airflow | Workflow orchestration (DAG scheduling & execution) |
| PostgreSQL 15 | Airflow metadata database (production-grade) |
| LocalStack | Local AWS S3 emulation |
| AWS CLI | Bucket creation & file upload (init container) |
| S3 Manager | Web UI for browsing S3 buckets |
| Docker Compose | Full stack orchestration |
| Python | DAG authoring & data processing scripts |

---

## 📁 Project Structure

```
.
├── dags/                   # Airflow DAG definitions
├── scripts/                # Helper Python scripts (ETL logic)
├── data/                   # Local data files (input/output)
├── Dockerfile              # Custom Airflow image (with providers)
├── docker-compose.yml      # Full stack definition
├── .env                    # Environment variables (not committed)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/) installed
- (Optional) AWS CLI for manual S3 testing

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 3. Build and start all services

```bash
docker compose up --build
```

This will:
1. Start **PostgreSQL** and wait until it is healthy
2. Build the custom Airflow Docker image
3. Start **LocalStack** and create the `my-data-bucket` S3 bucket
4. Upload a sample CSV to `s3://my-data-bucket/sample/sample.csv`
5. Run `airflow db migrate` against PostgreSQL and create the admin user
6. Start the Airflow webserver and scheduler

### 4. Access the services

| Service | URL | Credentials |
|---|---|---|
| Airflow UI | http://localhost:8080 | `admin` / `admin` |
| S3 Manager UI | http://localhost:8888 | (pre-configured) |


---

## 🧪 Testing the S3 Connection Locally

You can interact with the local S3 bucket using the AWS CLI:

```bash
# List buckets
aws --endpoint-url=http://localhost:4566 \
    --no-sign-request s3 ls

# List files in the bucket
aws --endpoint-url=http://localhost:4566 \
    --no-sign-request s3 ls s3://my-data-bucket/

# Download a file
aws --endpoint-url=http://localhost:4566 \
    --no-sign-request s3 cp s3://my-data-bucket/sample/sample.csv ./sample.csv
```

---

## 🗄️ PostgreSQL — Airflow Metadata DB

Airflow uses PostgreSQL 15 as its metadata database instead of SQLite, which makes it:

- **Concurrent-safe** — no file locking issues between webserver and scheduler
- **Production-realistic** — matches how Airflow is deployed in real environments
- **Persistent** — data survives container restarts via the `postgres_data` Docker volume

Connection string used across all Airflow services:

```
postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
```

To connect to the database directly for inspection:

```bash
docker exec -it airflow-postgres psql -U airflow -d airflow
```

---

## 🔄 Airflow DAGs

DAGs live in the `dags/` directory and are auto-detected by the scheduler once the stack is running.

To trigger a DAG manually via CLI:

```bash
docker exec -it airflow-scheduler airflow dags trigger <dag_id>
```

Or use the **Airflow UI** at http://localhost:8080.

---

## 🛑 Stopping the Stack

```bash
docker compose down
```

To also remove all volumes (full reset including the PostgreSQL database):

```bash
docker compose down -v
```

---

## 🌍 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `AIRFLOW__CORE__EXECUTOR` | Airflow executor type | `SequentialExecutor` |
| `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` | Airflow DB connection string | `postgresql+psycopg2://airflow:airflow@postgres:5432/airflow` |
| `AWS_ACCESS_KEY_ID` | LocalStack dummy key | `test` |
| `AWS_SECRET_ACCESS_KEY` | LocalStack dummy secret | `test` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |

---

## 📈 Skills Demonstrated

- ✅ Docker Compose multi-service orchestration with health checks and dependency ordering
- ✅ Apache Airflow DAG authoring and scheduling
- ✅ PostgreSQL integration as a production-grade metadata database
- ✅ AWS S3 integration patterns (simulated via LocalStack)
- ✅ Custom Airflow Docker image with provider packages
- ✅ Production-style project structure and documentation
- ✅ Local cloud emulation for cost-free development

---

## 🔮 Potential Enhancements

- [ ] Add CeleryExecutor + Redis for parallel task execution
- [ ] Integrate dbt for SQL transformations on ingested data
- [ ] Add Metabase for business intelligence dashboards
- [ ] Add CI/CD pipeline (GitHub Actions) for DAG validation
- [ ] Add a second PostgreSQL instance as a data warehouse target

---

## 👤 Author

**Mohamed** — Data Engineering Portfolio Project  
Built to demonstrate real-world data pipeline skills for logistics & operations analyst roles.

> 💼 Open to Data Analyst / Data Engineer / Operations Analyst opportunities.

---

## 📄 License

MIT License — feel free to use this as a reference for your own projects.