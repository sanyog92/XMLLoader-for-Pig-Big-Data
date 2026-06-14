"""
ZEE5 content integration — scrapes trending FIFA 2026 videos from ZEE5.

Uses Selenium + Chrome to:
  1. Auto-login with credentials from .env
  2. Search for FIFA 2026 content
  3. Extract video metadata (title, thumbnail, quality)
  4. Download via direct link (if available) or browser automation
"""

from __future__ import annotations

import time
from typing import Optional
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import ZEE5_EMAIL, ZEE5_PASSWORD
from utils.logger import logger
from crawler.youtube_crawler import VideoMeta


class ZEE5Crawler:
    """Scrapes ZEE5 for FIFA 2026 Sports content."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.logged_in = False

    def discover(self) -> list[VideoMeta]:
        """Login, search for FIFA content, extract videos."""
        try:
            self._init_driver()
            self._login()
            videos = self._search_fifa_content()
            return videos
        except Exception as exc:
            logger.error(f"ZEE5 crawl failed: {exc}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    # ── Selenium helpers ──────────────────────────────────────

    def _init_driver(self) -> None:
        chrome_opts = Options()
        if self.headless:
            chrome_opts.add_argument("--headless=new")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        chrome_opts.add_argument("--disable-gpu")
        chrome_opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64)")

        # Try to find ChromeDriver
        try:
            self.driver = webdriver.Chrome(options=chrome_opts)
        except Exception:
            logger.warning("ChromeDriver not found. Install: pip install chromedriver-binary")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=20))
    def _login(self) -> None:
        """Auto-login to ZEE5."""
        if not ZEE5_EMAIL or not ZEE5_PASSWORD:
            logger.warning("ZEE5_EMAIL / ZEE5_PASSWORD not set in .env")
            return

        logger.info("Logging into ZEE5...")
        self.driver.get("https://www.zee5.com/login")
        time.sleep(2)

        try:
            # Email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
            )
            email_field.send_keys(ZEE5_EMAIL)

            # Password field
            pwd_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
            pwd_field.send_keys(ZEE5_PASSWORD)

            # Submit button
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            submit_btn.click()

            # Wait for redirect to home
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'home')]"))
            )
            self.logged_in = True
            logger.info("Successfully logged into ZEE5")
        except Exception as exc:
            logger.error(f"ZEE5 login failed: {exc}")
            raise

    def _search_fifa_content(self) -> list[VideoMeta]:
        """Search for FIFA / Sports content on ZEE5."""
        search_queries = ["FIFA 2026", "World Cup", "Football Highlights", "Sports"]
        all_videos: list[VideoMeta] = []

        for query in search_queries:
            try:
                search_url = f"https://www.zee5.com/search?q={quote(query)}"
                self.driver.get(search_url)
                time.sleep(2)

                # Extract video cards
                video_elements = self.driver.find_elements(By.XPATH, "//div[@class='video-card']")
                logger.info(f"Found {len(video_elements)} results for '{query}'")

                for elem in video_elements[:10]:
                    try:
                        title = elem.find_element(By.XPATH, ".//h3").text
                        link = elem.find_element(By.XPATH, ".//a").get_attribute("href")
                        thumbnail = elem.find_element(By.XPATH, ".//img").get_attribute("src")

                        video = VideoMeta(
                            id=f"zee5_{hash(link) % 10**8}",
                            url=link,
                            title=title,
                            channel="ZEE5",
                            duration=0.0,
                            view_count=0,
                            like_count=0,
                            upload_date="",
                            thumbnail_url=thumbnail,
                            viral_score=0.5,
                        )
                        all_videos.append(video)
                    except Exception as exc:
                        logger.debug(f"Could not parse video element: {exc}")

            except Exception as exc:
                logger.warning(f"Search for '{query}' failed: {exc}")

        return all_videos
