
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from connect_pro.api.schemas import SearchQuery, ProfileResponse
from connect_pro.main import generate_profile_insights, generate_common_ground

load_dotenv()

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
        
        # Add common_ground to result if user_information is provided
        if search_query.user_information:            
            result["common_ground"] = generate_common_ground(
                profile_url=result["profile_url"],
                user_information=search_query.user_information,
                verbose=True
            )
        
        return ProfileResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

