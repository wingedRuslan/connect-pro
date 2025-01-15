"""Schemas and parsers for profile analysis outputs."""

from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class ProfileInsights(BaseModel):
    """Structured output for profile analysis."""

    professional_summary: str = Field(
        description="2-3 sentences highlighting key professional achievements and current role"
    )
    personal_background: str = Field(
        description="1-2 sentences about the person's background and journey"
    )
    interesting_facts: List[str] = Field(   # type: ignore
        description="A few unique or surprising facts about the person",
        min_items=1,
        max_items=5,
    )

    def to_dict(self) -> dict:
        """Convert insights to dictionary format."""
        return {
            "professional_summary": self.professional_summary,
            "personal_background": self.personal_background,
            "interesting_facts": self.interesting_facts,
        }


# Create parser instance
profile_parser = PydanticOutputParser(pydantic_object=ProfileInsights)
