import logging
import requests
from typing import Collection

logger = logging.getLogger(__name__)

def check_urls(urls: Collection[str], timeout: int = 5) -> dict[str, str]:
    """
    Checks a list of urls

    Args:
        urls: A list of URLs to check.
        timeout: Maximum time to wait for a response from each URL.

    Returns:
        dict[str, str]: A dictionary mapping each URL to its status
    """

    logger.info(
        "Starting URL checks for %d URLs with a timeout of %d seconds",
        len(urls),
        timeout,
    )

    results: dict[str, str] = {}

    for url in urls:
        status = "Unknown"

        try:
            logger.debug("Checking URL: %s", url)
            response = requests.get(url, timeout=timeout)

            if response.ok:
                status = f"{response.status_code} OK"
            else:
                status = f"{response.status_code} {response.reason}"
        except requests.exceptions.Timeout:
            status = "Timeout"
            logger.warning("Timeout occurred for URL: %s", url)
        except requests.exceptions.ConnectionError:
            status = "Connection Error"
            logger.warning("Connection error occurred for URL: %s", url)
        except requests.exceptions.RequestException as e:
            status = f"Request Exception: {type(e).__name__}"
            logger.error("Request exception for URL %s: %s", url, str(e), exc_info=True)

        results[url] = status
        logger.debug(f"Checked: {url:<40} Status: {status}")

    logger.info("Completed URL checks.")
    return results
