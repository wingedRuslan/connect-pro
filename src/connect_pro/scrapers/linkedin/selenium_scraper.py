"""LinkedIn profile scraper using Selenium."""

import os
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from connect_pro.config.settings import settings


class SeleniumLinkedInScraper:
    """LinkedIn scraper using Selenium."""
    
    def __init__(self, username=None, password=None):
        """Initialize the scraper with LinkedIn credentials."""

        self.username = username or settings.LINKEDIN_USERNAME
        self.password = password or settings.LINKEDIN_PASSWORD

        if not self.username or not self.password:
            raise ValueError("LinkedIn username and password are required")
        
        self.driver = None          # holds browser instance
        self.is_logged_in = False   
    

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


    def get_profile(self, linkedin_profile_url: str, mock: bool = False) -> Dict:
        """Fetch LinkedIn profile data.
        
        Args:
            linkedin_profile_url: URL of the LinkedIn profile to scrape
            mock: If True, return mock data instead of scraping
            
        Returns:
            Dict containing profile data
        """
        pass