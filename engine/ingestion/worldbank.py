import requests
import time
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorldBankIngestor")

class WorldBankIngestor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("data_sources", {}).get("worldbank", {})
        self.base_url = self.config.get("base_url")
        self.delay = self.config.get("rate_limit", {}).get("delay_seconds", 1.0)
        self.max_retries = self.config.get("rate_limit", {}).get("max_retries", 3)

    def fetch_gdp(self, country_code: str, year: int = 2023) -> Optional[float]:
        """
        Fetches the GDP for a specific country and year from the World Bank API.
        Includes rate limiting and error handling.
        """
        endpoint = self.config.get("endpoints", {}).get("gdp", "")
        # The endpoint in config is generic; we need to construct it properly
        # Example: /country/USA/indicator/NY.GDP.MKTP.CD?date=2023&format=json
        url = f"{self.base_url}/country/{country_code}/indicator/NY.GDP.MKTP.CD"
        params = {
            "date": str(year),
            "format": "json"
        }

        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f"Fetching GDP for {country_code} ({year}) from {url}")
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 429:
                    logger.warning("Rate limit hit (429). Backing off...")
                    time.sleep(self.delay * (2 ** retries))
                    retries += 1
                    continue

                response.raise_for_status()
                data = response.json()

                # World Bank API returns [metadata, [records]]
                if len(data) > 1 and data[1]:
                    gdp_value = data[1][0].get("value")
                    if gdp_value:
                        return float(gdp_value)
                
                logger.warning(f"No GDP data found for {country_code} in {year}")
                return None

            except requests.exceptions.RequestException as e:
                logger.error(f"API Error fetching GDP for {country_code}: {e}")
                retries += 1
                if retries <= self.max_retries:
                    time.sleep(self.delay)
            
        return None

    def refresh_all_economies(self, country_codes: List[str]) -> Dict[str, float]:
        """
        Iterates through a list of countries and fetches their latest GDP.
        """
        results = {}
        for code in country_codes:
            gdp = self.fetch_gdp(code)
            if gdp:
                results[code] = gdp / 1e9  # Convert to USD Billion
            time.sleep(self.delay)  # Mandatory rate limit enforcement
        return results

if __name__ == "__main__":
    # Simple test mock implementation
    import sys
    if "--test-mock" in sys.argv:
        print("Running Mock World Bank Test...")
        mock_config = {
            "data_sources": {
                "worldbank": {
                    "base_url": "https://api.worldbank.org/v2",
                    "rate_limit": {"delay_seconds": 0.1, "max_retries": 1}
                }
            }
        }
        ingestor = WorldBankIngestor(mock_config)
        # USA 2023 GDP is roughly 27 Trillion
        print(f"Mock Result for USA: {ingestor.fetch_gdp('USA', 2023)}")
