# PSA Crawler

An asynchronous web crawler designed to discover and extract potential **Public Service Announcements (PSAs)** from government and institutional websites.

The crawler is optimized for:

- Government ministries
- Public agencies
- Health organizations
- Disaster response portals
- Public information websites

It extracts:

- H1-H4 headlines
- Page metadata
- Surrounding context
- Government organizations
- PSA-related keywords
- Emergency indicators
- Action language
- Explainable PSA relevance scores

The output is designed for **manual validation and dataset creation**.

---

# Features

## Crawling

- Async crawling using `aiohttp`
- Priority-based URL scheduling
- Same-domain crawling
- Configurable depth limits
- Configurable concurrency
- URL normalization
- Duplicate detection
- Crawl resume support

---

## Content Extraction

Extracts:

- H1
- H2
- H3
- H4

For every heading:

- Page URL
- Website
- Page title
- Meta description
- Previous heading
- Next heading
- Surrounding paragraphs

---

## PSA Detection

The crawler enriches extracted content with:

### Categories

- Health
- Emergency
- Security
- Weather
- Agriculture
- Education
- Transport
- Finance
- Civic information

### Signals

- Emergency terms
- Public communication terms
- Government organizations
- Citizen action verbs
- Publication dates

---

## Explainable Scoring

Every record receives a PSA likelihood score.

Example:

```json
{
  "heading": "Flood Warning",
  "score": 32,
  "explanations": [
    "+8 Heading pattern 'warning'",
    "+5 Emergency term 'flood'",
    "+4 Government domain",
    "+3 Action verb 'avoid'"
  ]
}
```

The score is not intended to replace human validation.

It is used to prioritize which records humans review first.

---

# Architecture

```
                  START URLS
                       |
                       |
                       v
              Priority Queue
                       |
                       |
              Async Workers
                       |
        +--------------+--------------+
        |                             |
        v                             v
    Robots Check                  Fetcher
                                      |
                                      |
                                      v
                                  Parser
                                      |
                                      |
                                      v
                                Extractor
                                      |
                                      |
                                      v
                                  Scorer
                                      |
                                      |
                                      v
                              JSONL Writer
                                      |
                                      |
                                      v

                         output/headings.jsonl
```

---

# Installation

## Clone repository

```bash
git clone <repository-url>

cd psa-crawler
```

---

## Install dependencies

Using Poetry:

```bash
poetry install
```

Activate environment:

```bash
poetry shell
```

---

# Configuration

Most crawler behaviour is controlled through:

```
config.py
```

---

## Starting websites

Edit:

```python
START_URLS = [
    "https://www.health.go.ke/",
    "https://www.interior.go.ke/",
]
```

---

## Crawl limits

Example:

```python
MAX_DEPTH = 8

MAX_TOTAL_PAGES = 100000

CONCURRENT_REQUESTS = 20
```

---

## Robots.txt

By default:

```python
RESPECT_ROBOTS = True
```

Disable:

```python
RESPECT_ROBOTS = False
```

---

# Running the crawler

From the Poetry environment:

```bash
python crawler.py
```

Example:

```
2026-07-22 10:15:01 INFO Loaded 0 URLs

2026-07-22 10:15:20 INFO Pages crawled: 100

2026-07-22 11:10:22 INFO Pages crawled: 10000

2026-07-22 13:40:11 INFO Finished crawl
```

---

# Output

Generated files:

```
output/

├── headings.jsonl
├── visited.json
└── crawler.log
```

---

# JSONL Format

Each line represents one extracted heading.

Example:

```json
{
  "website": "health.go.ke",

  "url": "https://health.go.ke/cholera-alert",

  "heading_level": "H1",

  "heading": "Cholera Outbreak Alert",

  "following_text":
  "Residents are advised to seek medical attention...",

  "keywords_found": [
    "cholera",
    "health",
    "alert"
  ],

  "emergency_terms": [
    "cholera",
    "alert"
  ],

  "organizations": [
    "Ministry"
  ],

  "score": 34,

  "explanations": [
    "+8 Heading pattern 'alert'",
    "+5 Emergency term 'cholera'",
    "+4 Government domain"
  ]
}
```

---

# Adding Keywords

Keywords are stored in:

```
keywords.json
```

Example:

```json
{
  "health": [
    "cholera",
    "vaccination",
    "malaria"
  ]
}
```

Add new categories:

```json
{
  "cybersecurity": [
    "cyber attack",
    "data breach",
    "online safety"
  ]
}
```

No Python changes are required.

---

# Adjusting PSA Scores

Scoring rules are stored in:

```
scoring_rules.json
```

Example:

```json
{
  "heading_patterns": {
    "public notice": 8,
    "warning": 8,
    "advisory": 7
  }
}
```

Increase or decrease weights depending on your research goals.

---

# Manual Annotation Workflow

The recommended workflow:

## Step 1

Run crawler:

```bash
python crawler.py
```

---

## Step 2

Load JSONL:

Python:

```python
import pandas as pd

df = pd.read_json(
    "output/headings.jsonl",
    lines=True
)
```

---

## Step 3

Filter likely PSAs:

```python
psa_candidates = df[
    df["score"] >= 15
]
```

---

## Step 4

Human validation

Add labels:

```text
1 = PSA
0 = Not PSA
```

Example:

| Heading | Score | Label |
|-|-|-|
| Cholera Alert | 34 | 1 |
| About Ministry | 0 | 0 |

---

# Scaling

For small crawls:

```
JSON state
+
JSONL output
```

is sufficient.

For large-scale monitoring:

Recommended upgrades:

## Replace state.json

With:

```
SQLite
PostgreSQL
Redis
```

Store:

- URL
- crawl status
- timestamp
- HTTP status
- checksum

---

## Distributed crawling

Possible architecture:

```
                 Scheduler

                     |
        +------------+------------+

        Worker 1    Worker 2    Worker 3

             |
             |
        Message Queue

             |
             |
        Storage Layer
```

Possible technologies:

- Redis Queue
- Celery
- Kafka
- RabbitMQ

---

# Future Improvements

Possible extensions:

## Machine Learning Classification

Train a classifier using manually labelled records:

Features:

- heading text
- context embeddings
- keyword categories
- government domain
- organization
- score

Models:

- Logistic Regression
- XGBoost
- Sentence Transformers
- BERT classifiers

---

## Multilingual Support

Add:

```
keywords/

├── english.json
├── swahili.json
├── french.json
└── arabic.json
```

Useful for:

- African government portals
- UN agencies
- International organizations

---

## Monitoring Mode

Instead of one-time crawling:

```
Daily crawl
      |
      |
Compare changes
      |
      |
Detect new PSAs
      |
      |
Send alerts
```

---

# Project Status

Current capabilities:

✅ Async crawler  
✅ Government website crawling  
✅ H1-H4 extraction  
✅ Context extraction  
✅ PSA keyword detection  
✅ Explainable scoring  
✅ JSONL dataset generation  
✅ Crawl resume support  

Future:

⬜ ML classifier  
⬜ Dashboard  
⬜ Multilingual detection  
⬜ Continuous monitoring  

---

# License

For research and educational use.
