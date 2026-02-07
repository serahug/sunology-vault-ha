"""Constants for Sunology VAULT integration."""

DOMAIN = "sunology_vault"

BASE_URL = "https://backend-mobile.stream.sunology.eu"

API_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "App-Version": "2.2.4",
    "Content-Type": "application/json",
    "User-Agent": "App/127 CFNetwork/3860.300.31 Darwin/25.2.0",
}

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 300

BATTERY_CAPACITY_WH = 700

MIN_THRESHOLD = 210
MAX_THRESHOLD = 450
