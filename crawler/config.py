"""
Configuration for the PSA crawler.

All crawler behaviour should be configurable from this file.
"""

from pathlib import Path

###############################################################################
# DIRECTORIES
###############################################################################

BASE_DIR = Path(__file__).parent

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

JSONL_FILE = OUTPUT_DIR / "headings.jsonl"
STATE_FILE = OUTPUT_DIR / "visited.json"
LOG_FILE = OUTPUT_DIR / "crawler.log"

###############################################################################
# START URLS
###############################################################################

START_URLS = [
    "https://www.mfa.go.ke/",
    "https://www.interior.go.ke/",
    "https://www.education.go.ke/",
    "https://psckjobs.go.ke/",
    "https://www.publicservice.go.ke/",
    "https://www.kepsa.or.ke/",
    "https://www.agrico.co.ke/",
    "https://www.mps.go.ke/",
    "https://kpsa.education/",
    "https://www.who.int/",
    "https://gaa.go.ke/",
    "https://competitiontribunal.go.ke/",
    "https://www.kra.go.ke/",
    "https://www.treasury.go.ke/",
    "https://www.knbs.or.ke/",
    "https://ict.go.ke/",
    "https://nairobi.go.ke/",
    "https://www.governmentpress.go.ke/",
    "https://accounts.ecitizen.go.ke/"
]

###############################################################################
# CRAWLING
###############################################################################

# Number of concurrent workers.
CONCURRENT_REQUESTS = 20

# Seconds before an HTTP request times out.
REQUEST_TIMEOUT = 20

# Maximum retries before abandoning a page.
MAX_RETRIES = 3

# Initial delay used for exponential backoff.
BACKOFF_FACTOR = 1.5

# Respect robots.txt
RESPECT_ROBOTS = True

# Delay (seconds) between requests made by the same worker.
REQUEST_DELAY = 0.25

###############################################################################
# LIMITS
###############################################################################

# Maximum crawl depth.
MAX_DEPTH = 8

# Maximum pages per domain.
MAX_PAGES_PER_DOMAIN = 5000

# Maximum total pages.
MAX_TOTAL_PAGES = 100000

###############################################################################
# URL FILTERS
###############################################################################

SKIP_EXTENSIONS = {
    ".pdf",
    ".zip",
    ".rar",
    ".7z",
    ".gz",
    ".tar",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".csv",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".mp4",
    ".avi",
    ".mov",
    ".mp3",
    ".wav",
    ".ogg",
}

SKIP_PATHS = [
    "/login",
    "/logout",
    "/signin",
    "/admin",
    "/feed",
    "/rss",
    "/search",
    "/wp-json",
]

###############################################################################
# HTML EXTRACTION
###############################################################################

HEADING_TAGS = [
    "h1",
    "h2",
    "h3",
    "h4",
]

# Number of sibling paragraphs to capture after a heading.
FOLLOWING_PARAGRAPHS = 2

###############################################################################
# USER AGENT
###############################################################################

USER_AGENT = (
    "PSAResearchCrawler/1.0 "
    "(Academic Research; contact: info@usiu.ac.ke)"
)

###############################################################################
# PRIORITY KEYWORDS
###############################################################################

URL_PRIORITY_KEYWORDS = [
    "notice",
    "announcement",
    "announcements",
    "alert",
    "alerts",
    "bulletin",
    "press",
    "news",
    "media",
    "advisory",
    "covid",
    "health",
    "public",
    "warning",
    "emergency",
]

###############################################################################
# LOGGING
###############################################################################

LOG_LEVEL = "INFO"
