"""LinkedIn profile scraper using Selenium."""

import os
import time
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from connect_pro.config.settings import settings


class SeleniumLinkedInScraper:
    """LinkedIn scraper using Selenium."""
    
    def __init__(self, username=None, password=None, cooldown_period=60):
        """Initialize the scraper with LinkedIn credentials."""

        self.username = username or settings.LINKEDIN_USERNAME
        self.password = password or settings.LINKEDIN_PASSWORD

        if not self.username or not self.password:
            raise ValueError("LinkedIn username and password are required")
        
        self.driver = None          # holds browser instance
        self.is_logged_in = False
        self.cooldown_period = cooldown_period
        self.last_request_time = None

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

    def _login(self):
        """Log in to LinkedIn.

            Go to LinkedIn login page
            Find and fill the username field
            Find and fill the password field
            Click the login button
            Wait until we're redirected to a logged-in page
        """
        if self.is_logged_in:
            return
        
        if not self.driver:
            self._setup_driver()
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for username field to be visible and enter username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_input.send_keys(self.username)
            
            # Find password field and enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.password)
            
            # Click the login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(@class, 'login')]"
            )
            login_button.click()
            
            # Wait for successful login (the URL contains "feed" or "/in/")
            WebDriverWait(self.driver, 15).until(
                lambda d: "feed" in d.current_url.lower() or 
                          "/in/" in d.current_url.lower()
            )
            
            print("Successfully logged in to LinkedIn")
            self.is_logged_in = True
            
        except (TimeoutException, NoSuchElementException) as e:
            self._close_driver()
            raise ValueError(f"Failed to login to LinkedIn: {str(e)}")

    def _respect_cooldown(self):
        """Wait for cooldown period between requests to avoid rate limiting."""
        if self.last_request_time:
            elapsed_time = time.time() - self.last_request_time
            if elapsed_time < self.cooldown_period:
                wait_time = self.cooldown_period - elapsed_time
                print(f"Waiting {wait_time:.1f} seconds for cooldown...")
                time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _extract_basic_profile_data(self) -> Dict:
        """Extract basic profile information from the current page."""
        profile_data = {}
        
        # Extract full name (the main profile heading)
        try:
            profile_data["full_name"] = self.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'text-heading')]"
            ).text.strip()
        except NoSuchElementException:
            profile_data["full_name"] = ""
            print("Warning: Could not find full name")
        
        # Extract headline (job title/description that appears below the name)
        try:
            profile_data["headline"] = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'text-body-medium')]"
            ).text.strip()
        except NoSuchElementException:
            profile_data["headline"] = ""
            print("Warning: Could not find headline")
        
        # Extract location (city/country information)
        try:
            location_text = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'text-body-small') and contains(text(), ',')]"
            ).text.strip()
            
            # Split location into city and country if possible
            if "," in location_text:
                parts = [part.strip() for part in location_text.split(",")]
                profile_data["city"] = parts[0]
                profile_data["country"] = parts[1]
            else:
                profile_data["location"] = location_text
        except NoSuchElementException:
            print("Warning: Could not find location")
        
        # Extract about/summary section
        try:
            about_section = self.driver.find_element(
                By.XPATH, "//div[./div/div/span/span[text()='About']]/following-sibling::div"
            )
            profile_data["summary"] = about_section.text.strip()
        except NoSuchElementException:
            profile_data["summary"] = ""
            print("Warning: Could not find summary section")
        
        return profile_data

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

        # Set up the browser
        if not self.driver:
            self._setup_driver()
        
        try:
            self._login()

            # Navigate to the profile URL
            self.driver.get(linkedin_profile_url)

            # Wait for the profile to load (wait for the name to appear)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'text-heading')]"))
            )

            # Extract basic profile data
            profile_data = self._extract_basic_profile_data()
            
            return profile_data

        except Exception as e:
            raise ValueError(f"Failed to scrape LinkedIn profile: {str(e)}")
            
        finally:
            self._quit_driver()

