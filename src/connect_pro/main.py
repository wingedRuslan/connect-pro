"""
LinkedIn Profile Analyzer: Generates professional summaries and conversation points
from LinkedIn profiles through automated search and analysis.
"""

from typing import Dict
from dotenv import load_dotenv

from connect_pro.agent.linkedin_profile_agent import LinkedInProfileAgent
from connect_pro.config.settings import settings
from connect_pro.scrapers.linkedin.proxycurl import LinkedInClient
from connect_pro.llm.models import get_openai_llm
from connect_pro.prompts.profile_analysis import profile_analysis_prompt


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
            print(f"Found LinkedIn profile: {profile_url}")

        if not profile_url:
            return None

        # Scrape profile data
        profile_data = LinkedInClient().get_profile(linkedin_profile_url=profile_url, mock=True)
        if not profile_data:
            raise ValueError(f"Could not scrape profile data from {profile_url}")

        # Generate insights
        llm = get_openai_llm(temperature=0)
        chain = profile_analysis_prompt | llm
        result = chain.invoke(input={"information": profile_data})

        return {
            "profile_url": profile_url, 
            "insights": result.content
        }

    except Exception as e:
        if verbose:
            print(f"Error generating profile insights: {str(e)}")
        raise


def main():
    """Generate insights from LinkedIn profiles."""
    load_dotenv()

    print("\n=== LinkedIn Profile Analyzer ===\n")

    search_query = "Ruslan Yermakov IBM"

    try:
        result = generate_profile_insights(search_query=search_query, verbose=True)

        print("\nLinkedIn Profile:", result["profile_url"])
        print("\nProfile Insights:")
        print(result["insights"])

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
