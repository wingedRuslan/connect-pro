"""Template for identifying common ground between a LinkedIn profile and user information."""

from langchain.prompts.prompt import PromptTemplate

COMMON_GROUND_TEMPLATE = \
    """
    You are an expert at finding meaningful connections between people. 
    Your goal is to identify potential common ground that could serve as conversation starters.

    LinkedIn Profile Information:
    {profile_information}

    User Information:
    {user_information}

    Based on the information above, identify potential common ground, shared interests, experiences, or values between the LinkedIn profile and the user.
    Focus on specific, meaningful connections rather than generic similarities. 
    The common ground should be personalized and feel like a genuine observation about what these two individuals might connect over.

    Consider:
    - Professional experiences (companies, industries, roles)
    - Educational background (schools, degrees, fields of study)
    - Skills and expertise areas
    - Geographic locations (current or past)
    - Potential shared interests, values, views

    Be concise yet insightful. Think step by step and provide 1-3 specific points of potential connection.
    If there is very little obvious common ground, focus on complementary aspects or potential areas of mutual interest.
    """

common_ground_prompt = PromptTemplate(
    input_variables=["profile_information", "user_information"],
    template=COMMON_GROUND_TEMPLATE,
    validate_template=True,  # ensure all input variables are present in the template
)

