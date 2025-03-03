"""LinkedIn profile scraper using Selenium."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from connect_pro.config.settings import settings
from connect_pro.scrapers.linkedin.extractors import (
    extract_basic_info,
    extract_experiences,
    extract_education,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeleniumLinkedInScraper:
    """LinkedIn scraper using Selenium."""
    
    def __init__(self, username=None, password=None, cooldown_period_sec=120):
        """Initialize the scraper with LinkedIn credentials."""

        self.username = username or settings.LINKEDIN_USERNAME
        self.password = password or settings.LINKEDIN_PASSWORD

        if not self.username or not self.password:
            raise ValueError("LinkedIn username and password are required")
        
        self.driver = None          # holds browser instance
        self.is_logged_in = False

        # Cooldown tracking
        self.cooldown_period_sec = cooldown_period_sec
        self.last_scrape_time = None
        self.cooldown_file = Path(".linkedin_cooldown")
        self._load_last_scrape_time()

    def _load_last_scrape_time(self) -> None:
        """Load the last scrape time from file."""
        if self.cooldown_file.exists():
            try:
                timestamp = self.cooldown_file.read_text().strip()
                self.last_scrape_time = datetime.fromisoformat(timestamp)
                logger.info(f"Last scrape time: {self.last_scrape_time}")
            except Exception as e:
                logger.error(f"Error loading last scrape time: {e}")
                self.last_scrape_time = None

    def _save_last_scrape_time(self) -> None:
        """Save the current time as the last scrape time."""
        try:
            self.last_scrape_time = datetime.now()
            self.cooldown_file.write_text(self.last_scrape_time.isoformat())
            logger.info(f"Updated last scrape time: {self.last_scrape_time}")
        except Exception as e:
            logger.error(f"Error saving last scrape time: {e}")
    
    def _respect_cooldown(self) -> None:
        """Wait for cooldown period between requests to avoid rate limiting."""
        if self.last_scrape_time:
            elapsed_seconds = (datetime.now() - self.last_scrape_time).total_seconds()
            if elapsed_seconds < self.cooldown_period_sec:
                wait_time = self.cooldown_period_sec - elapsed_seconds
                logger.info(f"Waiting {wait_time:.1f} seconds for cooldown...")
                time.sleep(wait_time)
    
    def _setup_driver(self) -> None:
        """Create and configure a Chrome browser instance."""

        options = Options()

        # Run in headless mode (no visible browser window)
        options.add_argument("--headless")
        
        # Additional settings to make browser stable and realistic
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Set a realistic window size to make the browser behave like a desktop browser
        options.add_argument("--window-size=1920,1080")
        
        # Use a realistic user agent (browser identification)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")        

        # Use webdriver_manager to automatically download the correct driver
        service = Service(ChromeDriverManager().install())
        
        # Create the browser instance
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Set implicit wait time (seconds to wait when looking for elements)
        self.driver.implicitly_wait(10)

    def _close_driver(self) -> None:
        """Close the browser properly."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False

    def _login(self) -> bool:
        """Log in to LinkedIn."""
        if self.is_logged_in:
            return True
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(5)

            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(self.username)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click sign in
            signin_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            signin_button.click()
            
            # Wait for login to complete
            time.sleep(5)

            # Check if login was successful
            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url or "/in/" in self.driver.current_url:
                logger.info(f"Successfully logged in as {self.username}")
                self.is_logged_in = True
                return True
            else:
                logger.warning(f"Login failed for {self.username}")
                return False
        
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to login to LinkedIn: {str(e)}")
            return False

    def get_profile(self, linkedin_profile_url: str, mock: bool = False) -> Dict:
        """Fetch LinkedIn profile data.
        
        Args:
            linkedin_profile_url: URL of the LinkedIn profile to scrape
            mock: If True, return mock data instead of scraping
            
        Returns:
            Dict containing profile data
        """
        if mock:
            return {"Full Name": "Test Test", "Status": "Success"}

        # Respect the cooldown period
        self._respect_cooldown()

        try:
            # Set up the browser
            if not self.driver:
                self._setup_driver()

            # Attempt login
            if not self._login():
                logger.error("Failed to log in to LinkedIn")
                self._close_driver()
                return {}
            
             # Navigate to the profile
            self.driver.get(linkedin_profile_url)
            time.sleep(5)
            
            # Wait for the profile to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//h1"))
            )

            # Extract Profile data
            profile_data = extract_basic_info(self.driver)
            profile_data["experiences"] = extract_experiences(self.driver)
            profile_data["education"] = extract_education(self.driver)

            # Update last scrape time
            self._save_last_scrape_time()

            return profile_data

        except Exception as e:
            raise ValueError(f"Failed to scrape LinkedIn profile: {str(e)}")
            
        finally:
            self._close_driver()

    def __del__(self) -> None:
        """Ensure the driver is closed."""
        self._close_driver()

