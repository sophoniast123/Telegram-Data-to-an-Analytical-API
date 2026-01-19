# Ethiopian Medical Telegram Analytics Pipeline

A comprehensive data pipeline for scraping, processing, and analyzing Telegram channels related to Ethiopian medical and pharmaceutical products. The system collects messages, images, and metadata from public Telegram channels, enriches the data with AI-powered image analysis, and provides analytics through a REST API.

## Project Overview

This project implements an end-to-end data pipeline that:

1. **Scrapes** public Telegram channels for medical product information
2. **Stores** raw data in a structured data lake (JSON, CSV, images)
3. **Loads** data into PostgreSQL for structured querying
4. **Transforms** data using dbt for analytics-ready models
5. **Enriches** images with YOLO object detection
6. **Serves** analytics through a FastAPI REST API
7. **Orchestrates** the entire pipeline with Dagster

## Architecture

```
Telegram Channels → Scraper → Data Lake → PostgreSQL → dbt Models → API
                     ↓
                  YOLO Detection
```

### Components

- **Telegram Scraper** (`src/telegram.py`): Uses Telethon to scrape messages, images, and metadata
- **Data Lake** (`src/datalake.py`): Organizes raw data by date partitions
- **Database Loader** (`scripts/postgres.py`): Loads JSON data into PostgreSQL
- **Data Transformations** (`models/`): dbt models for analytics
- **Image Analysis** (`src/yolo.py`): YOLOv8 object detection on product images
- **API Service** (`api/main.py`): FastAPI endpoints for analytics
- **Pipeline Orchestration** (`src/pipeline.py`): Dagster jobs for workflow management

## Data Flow

1. **Raw Data Collection**: Messages stored as JSON by channel/date, images by channel/message_id
2. **Structured Storage**: PostgreSQL tables for relational queries
3. **Data Modeling**: dbt creates fact/dimension tables for analytics
4. **Enrichment**: YOLO detects objects in images and adds metadata
5. **API Serving**: REST endpoints provide aggregated insights

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Telegram API credentials (API_ID, API_HASH)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KAIM_week8
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install telethon python-dotenv psycopg2-binary fastapi uvicorn sqlalchemy pydantic ultralytics dagster pandas
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=medical_warehouse
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   ```

## Usage

### 1. Scrape Telegram Data

Run the scraper to collect messages from medical channels:

```bash
python src/telegram.py --path data --limit 500
```

**Parameters:**
- `--path`: Base data directory (default: `data`)
- `--limit`: Max messages per channel (default: 100)
- `--message-delay`: Delay between messages in seconds (default: 1.0)
- `--channel-delay`: Delay between channels in seconds (default: 3.0)

**Output Structure:**
```
data/
├── raw/
│   ├── csv/YYYY-MM-DD/telegram_data.csv
│   ├── images/{channel_name}/{message_id}.jpg
│   └── telegram_messages/YYYY-MM-DD/
│       ├── {channel_name}.json
│       └── _manifest.json
```

### 2. Load Data to PostgreSQL

Load scraped JSON data into the database:

```bash
python scripts/postgres.py
```

This creates the `raw.telegram_messages` table and populates it with message data.

### 3. Run dbt Transformations

Transform raw data into analytics-ready models:

```bash
dbt run --project-dir models
```

### 4. Run YOLO Image Analysis

Detect objects in scraped images:

```bash
python src/yolo.py
```

This generates `data/yolo_detections.csv` with detection results.

### 5. Start the API Server

Serve analytics via REST API:

```bash
uvicorn api.main:app --reload
```

**API Endpoints:**
- `GET /api/reports/top-products?limit=10`: Get most mentioned products

### 6. Run Full Pipeline (Dagster)

Orchestrate the entire pipeline:

```bash
python src/pipeline.py
```

This runs the complete workflow: scrape → load → transform → enrich.

## Target Channels

Currently configured to scrape:
- `@cheMed123` - CheMed medical products
- `@lobelia4cosmetics` - Lobelia cosmetics and health products
- `@tikvahpharma` - Tikvah Pharma pharmaceuticals

## Data Schema

### Raw Message Structure
```json
{
  "message_id": 123,
  "channel_name": "cheMed123",
  "channel_title": "CheMed",
  "message_date": "2023-01-01T12:00:00+00:00",
  "message_text": "Product description...",
  "has_media": true,
  "image_path": "data/raw/images/cheMed123/123.jpg",
  "views": 1500,
  "forwards": 5
}
```

### Database Tables
- `raw.telegram_messages`: Raw message data
- `fct_messages`: Fact table for messages
- `dim_channels`: Dimension table for channels
- `fct_messages_products`: Product mentions

### YOLO Detections
```csv
message_id,channel_name,detected_class,confidence_score
123,cheMed123,0,0.85
```

## Configuration

### Telegram API Setup
1. Go to [my.telegram.org](https://my.telegram.org)
2. Create an app to get API_ID and API_HASH
3. Add to `.env` file

### Database Setup
Create PostgreSQL database:
```sql
CREATE DATABASE medical_warehouse;
```

### YOLO Model
The system uses YOLOv8 nano model (`yolov8n.pt`) for object detection. For custom training, replace the model file.

## Development

### Project Structure
```
KAIM_week8/
├── api/                 # FastAPI application
├── data/                # Data lake storage
├── logs/                # Application logs
├── models/              # dbt transformation models
├── scripts/             # Utility scripts
├── src/                 # Source code
│   ├── datalake.py      # Data lake utilities
│   ├── pipeline.py      # Dagster orchestration
│   ├── telegram.py      # Telegram scraper
│   └── yolo.py          # Image analysis
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Adding New Channels
Edit the `target_channels` list in `src/telegram.py`:
```python
target_channels = [
    '@cheMed123',
    '@lobelia4cosmetics',
    '@tikvahpharma',
    '@new_channel'  # Add new channels here
]
```

### Customizing YOLO Detection
Modify `src/yolo.py` to use different models or detection parameters.

## Monitoring & Logging

- Logs are written to `logs/scrape_YYYY-MM-DD.log`
- Manifest files track scraping metadata
- Dagster provides pipeline execution monitoring

## Security Notes

- Never commit `.env` file or session files
- Telegram API credentials are sensitive
- Database credentials should be secured

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Use meaningful commit messages

## License

[Add license information here]

## Support

For issues or questions, please [add contact information or issue tracker].