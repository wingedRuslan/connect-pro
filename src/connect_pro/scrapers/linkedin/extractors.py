"""Functions for extracting data from LinkedIn profile pages."""

import logging
from typing import Dict, List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def extract_basic_info(driver: webdriver.Chrome) -> Dict:
    """Extract basic profile information from the current page."""
    profile_data = {}
    
    # Extract full name (the main profile heading)
    try:

        selectors = [
            "//h1[contains(@class, 'inline') and contains(@class, 't-24')]",
            "//h1[contains(@class, 'JtDmvATzwQtgDgNLDeDrrAGfeaVHRqsTx')]",
            "//h1"  # Fallback to any h1 as a last resort
        ]

        for selector in selectors:
            try:
                name_element = driver.find_element(By.XPATH, selector)
                if name_element and name_element.text.strip():
                    profile_data["full_name"] = name_element.text.strip()
                    break
            except NoSuchElementException:
                continue
        
        if "full_name" not in profile_data:
            raise NoSuchElementException("No name element found with any selector")
    
    except NoSuchElementException:
        profile_data["full_name"] = ""
        logger.warning("Could not find full name")
        
    # Extract headline (job title/description that appears below the name)
    try:
        profile_data["headline"] = driver.find_element(
            By.XPATH, "//div[contains(@class, 'text-body-medium')]"
        ).text.strip()
    except NoSuchElementException:
        profile_data["headline"] = ""
        logger.warning("Could not find headline")
    
    # Extract location (city/country information)
    try:
        location_selectors = [
            "//span[contains(@class, 'text-body-small') and contains(@class, 'inline') and contains(@class, 't-black--light')]",
            "//span[contains(@class, 'text-body-small')]"
        ]

        for selector in location_selectors:
            try:
                location_element = driver.find_element(By.XPATH, selector)
                if location_element and location_element.text.strip():
                    location_text = location_element.text.strip()
                    
                    # Split location into city and country if possible
                    if "," in location_text:
                        parts = [part.strip() for part in location_text.split(",")]
                        profile_data["city"] = parts[0]
                        profile_data["country"] = parts[1]
                    else:
                        profile_data["location"] = location_text
                    break
            except NoSuchElementException:
                continue
                
    except NoSuchElementException:
        logger.warning("Could not find location")

    
    # Extract about/summary section
    try:
        summary_selectors = [
            "//div[contains(@class, 'inline-show-more-text--is-collapsed-with-line-clamp')]",
            "//div[contains(@class, 'inline-show-more-text')]",
            "//section[.//span[text()='About']]//div[contains(@class, 'break-words')]"
        ]

        for selector in summary_selectors:
            try:
                summary_element = driver.find_element(By.XPATH, selector)
                if summary_element and summary_element.text.strip():
                    profile_data["summary"] = summary_element.text.strip()
                    break
            except NoSuchElementException:
                continue
                
        if "summary" not in profile_data:
            # Try one more approach - find the About section and extract all text
            try:
                about_section = driver.find_element(By.XPATH, "//section[.//span[text()='About']]")
                about_text = about_section.text
                if "About" in about_text:
                    # Remove the "About" heading
                    about_text = about_text.replace("About", "", 1).strip()
                profile_data["summary"] = about_text
            except NoSuchElementException:
                raise NoSuchElementException("No summary element found with any selector")
                
    except NoSuchElementException:
        profile_data["summary"] = ""
        logger.warning("Could not find summary section")
    
    return profile_data

def extract_experiences(driver: webdriver.Chrome) -> List[Dict]:
    """Extract work experiences from the profile."""
    experiences = []
    
    try:
        # Find the experience section
        exp_section = driver.find_element(
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
        logger.warning("No experience section found")
    
    return experiences

def extract_education(driver: webdriver.Chrome) -> List[Dict]:
    """Extract education information from the profile."""
    education = []
    
    try:
        # Find the education section
        edu_section = driver.find_element(
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
        logger.warning("No education section found")
    
    return education

