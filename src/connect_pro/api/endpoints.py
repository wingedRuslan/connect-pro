from fastapi import APIRouter, HTTPException

from connect_pro.api.schemas import SearchQuery, ProfileResponse
from connect_pro.main import generate_profile_insights

router = APIRouter()

@router.post("/analyze", response_model=ProfileResponse)
async def analyze_profile(search_query: SearchQuery):
    """Analyze a LinkedIn profile based on search query."""
    try:
        result = generate_profile_insights(
            search_query=search_query.query,
            verbose=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        return ProfileResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

