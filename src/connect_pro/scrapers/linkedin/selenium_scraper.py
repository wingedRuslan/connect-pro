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

    def _extract_experiences(self) -> List[Dict]:
        """Extract work experiences from the profile."""
        experiences = []
        
        try:
            # Find the experience section
            exp_section = self.driver.find_element(
                By.XPATH, "//div[./div/div/span/span[text()='Experience']]"
            )
            
            # Find all experience entries (list items within this section)
            exp_entries = exp_section.find_elements(
                By.XPATH, ".//ul/li"
            )
            
            for entry in exp_entries:
                exp_data = {}
                
                # Extract job title
                try:
                    exp_data["title"] = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 'mr1 t-bold')]"
                    ).text.strip()
                except NoSuchElementException:
                    continue  # Skip if no title found (essential field)
                
                # Extract company name
                try:
                    exp_data["company"] = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal')]"
                    ).text.strip()
                except NoSuchElementException:
                    exp_data["company"] = ""
                
                # Extract dates
                try:
                    date_range = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal t-black--light')]"
                    ).text.strip()
                    
                    # Parse date range like "Jan 2020 - Present"
                    dates = date_range.split(" · ")[0].split(" - ")
                    if len(dates) >= 2:
                        exp_data["start_date"] = dates[0].strip()
                        exp_data["end_date"] = dates[1].strip() if dates[1].lower() != "present" else "Present"
                except NoSuchElementException:
                    pass
                
                # Extract location
                try:
                    location_element = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal t-black--light')][2]"
                    )
                    exp_data["location"] = location_element.text.strip()
                except NoSuchElementException:
                    pass
                
                # Extract description
                try:
                    desc = entry.find_element(
                        By.XPATH, ".//div[contains(@class, 't-14 t-normal')]"
                    ).text.strip()
                    if desc:
                        exp_data["description"] = desc
                except NoSuchElementException:
                    pass
                
                experiences.append(exp_data)
        
        except NoSuchElementException:
            print("Warning: No experience section found")
        
        return experiences
    
    def _extract_education(self) -> List[Dict]:
        """Extract education information from the profile."""
        education = []
        
        try:
            # Find the education section
            edu_section = self.driver.find_element(
                By.XPATH, "//div[./div/div/span/span[text()='Education']]"
            )
            
            # Find all education entries
            edu_entries = edu_section.find_elements(
                By.XPATH, ".//ul/li"
            )
            
            for entry in edu_entries:
                edu_data = {}
                
                # Extract school name
                try:
                    edu_data["school"] = entry.find_element(
                        By.XPATH, ".//h3[contains(@class, 't-16')]"
                    ).text.strip()
                except NoSuchElementException:
                    continue  # Skip if no school found (essential field)
                
                # Extract degree
                try:
                    edu_data["degree"] = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal')]"
                    ).text.strip()
                except NoSuchElementException:
                    pass
                
                # Extract dates
                try:
                    date_range = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal t-black--light')]"
                    ).text.strip()
                    
                    dates = date_range.split(" - ")
                    if len(dates) >= 2:
                        edu_data["start_date"] = dates[0].strip()
                        edu_data["end_date"] = dates[1].strip()
                except NoSuchElementException:
                    pass
                
                # Extract field of study (if separate from degree)
                try:
                    field = entry.find_element(
                        By.XPATH, ".//span[contains(@class, 't-14 t-normal')][2]"
                    ).text.strip()
                    if field and "field of study" in field.lower():
                        edu_data["field_of_study"] = field.split("Field of study ")[1]
                except NoSuchElementException:
                    pass
                
                education.append(edu_data)
        
        except NoSuchElementException:
            print("Warning: No education section found")
        
        return education

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
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'text-heading-xlarge')]|//h1[contains(@class, 'text-heading')]"))
            )

            # Update last scrape time
            self._save_last_scrape_time()

            # Extract profile data
            profile_data = self._extract_basic_profile_data()
            profile_data["experiences"] = self._extract_experiences()
            profile_data["education"] = self._extract_education()
            
            return profile_data

        except Exception as e:
            raise ValueError(f"Failed to scrape LinkedIn profile: {str(e)}")
            
        finally:
            self._close_driver()

