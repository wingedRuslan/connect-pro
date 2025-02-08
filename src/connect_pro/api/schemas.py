from pydantic import BaseModel
from typing import Dict


class SearchQuery(BaseModel):
    """Input schema for profile search."""
    query: str


class ProfileResponse(BaseModel):
    """Response schema for profile analysis."""
    profile_url: str
    insights: Dict

