"""
LinkedIn Profile Analyzer: Generates professional summaries and conversation points
from LinkedIn profiles through automated search and analysis.
"""

import logging
from typing import Dict

from dotenv import load_dotenv

from connect_pro.agent.linkedin_profile_agent import LinkedInProfileAgent
from connect_pro.config.settings import settings
from connect_pro.llm.models import get_openai_llm
from connect_pro.prompts.profile_analysis import profile_analysis_prompt
from connect_pro.prompts.common_ground import common_ground_prompt
from connect_pro.schemas.profile_insights import ProfileInsights, profile_parser
from connect_pro.scrapers.linkedin.proxycurl import ProxyCurlClient
from connect_pro.scrapers.linkedin.selenium_scraper import SeleniumLinkedInScraper


logger = logging.getLogger(__name__)


def get_linkedin_client():
    """Get the appropriate LinkedIn client based on settings.
    
    Returns:
        A LinkedIn client instance with compatible interface
    """
    scraper_type = getattr(settings, "LINKEDIN_SCRAPER_TYPE", "proxycurl").lower()
    
    if scraper_type == "proxycurl":
        logger.info("Using ProxyCurl LinkedIn client")
        return ProxyCurlClient()
    elif scraper_type == "selenium":
        logger.info("Using Selenium LinkedIn scraper")
        return SeleniumLinkedInScraper()
    else:
        logger.warning(f"Unknown scraper type: {scraper_type}, defaulting to Proxycurl")
        return ProxyCurlClient()
    

def generate_profile_insights(
    search_query: str, verbose: bool = False
) -> Dict[str, str]:
    """
    Generate professional insights and conversation points based on a LinkedIn profile.

    Args:
        search_query: Search terms to find the person (name, company, position, etc.)
        verbose: Whether to print detailed progress information

    Returns:
        Dict containing profile_url and insights
    """
    try:
        # Find LinkedIn profile
        linkedin_agent = LinkedInProfileAgent(verbose=verbose)
        profile_url = linkedin_agent.find_profile(search_query=search_query)
        if verbose:
            logger.info(f"Found LinkedIn profile: {profile_url}")

        if not profile_url:
            return None

        # Scrape profile data
        linkedin_client = get_linkedin_client()

        profile_data = linkedin_client.get_profile(
            linkedin_profile_url=profile_url, mock=False
        )
        if not profile_data:
            raise ValueError(f"Could not scrape profile data from {profile_url}")

        # Generate insights
        llm = get_openai_llm(temperature=0)
        chain = profile_analysis_prompt | llm | profile_parser

        insights: ProfileInsights = chain.invoke(input={"profile_information": profile_data})

        return {
            "profile_url": profile_url, 
            "insights": insights.to_dict()
        }

    except Exception as e:
        if verbose:
            logger.info(f"Error generating profile insights: {str(e)}")
        raise


def generate_common_ground(
    profile_url: str, user_information: str, verbose: bool = False
) -> str:
    """
    Generate insights about common ground between a LinkedIn profile and user information.

    Args:
        profile_url: LinkedIn profile URL
        user_information: Information provided by the user about themselves
        verbose: Whether to print detailed progress information

    Returns:
        Common ground insights as a string
    """
    try:
        # Get Profile Data
        linkedin_client = get_linkedin_client()
        profile_data = linkedin_client.get_profile(
            linkedin_profile_url=profile_url, mock=False
        )
        if not profile_data:
            raise ValueError(f"Could not scrape profile data from {profile_url}")

        # Find out common ground
        llm = get_openai_llm(temperature=0.5)        
        chain = common_ground_prompt | llm
        
        common_ground = chain.invoke(
            input={
                "profile_information": profile_data,
                "user_information": user_information
            }
        )
        return common_ground.content

    except Exception as e:
        if verbose:
            logger.info(f"Error generating common ground: {str(e)}")
        raise


def main():
    """Generate insights from LinkedIn profiles."""
    load_dotenv()

    logger.info("\n=== LinkedIn Profile Analyzer ===\n")

    search_query = "Ruslan Yermak IBM"

    try:
        result = generate_profile_insights(search_query=search_query, verbose=True)

        logger.info("\nLinkedIn Profile:", result["profile_url"])
        logger.info("\nProfile Insights:")
        logger.info(result["insights"])

    except ValueError as e:
        logger.info(f"Error: {e}")
    except Exception as e:
        logger.info(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
