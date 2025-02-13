from pydantic import BaseModel
from typing import Dict, Optional


class SearchQuery(BaseModel):
    """Input schema for profile search."""
    query: str
    user_information: str = ""  


class ProfileResponse(BaseModel):
    """Response schema for profile analysis."""
    profile_url: str
    insights: Dict
    common_ground: Optional[str] = None

