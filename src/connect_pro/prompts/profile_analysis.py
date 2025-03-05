"""Templates for analyzing professional profiles."""

from langchain.prompts.prompt import PromptTemplate

from connect_pro.schemas.profile_insights import profile_parser

PROFILE_ANALYSIS_TEMPLATE = """Based on the following information about a person:
    {profile_information}
    
    Please provide:
    1. Professional Summary (2-3 sentences highlighting their key achievements and role) 
    2. Personal Background (1-2 sentences about their background and journey)
    3. Two Interesting Facts:
        - First unique or surprising fact 
        - Second unique or surprising fact
    
    Focus on being concise yet informative and creative. Include specific details and achievements where available. 
    If certain information is not provided, focus on what is known rather than speculating.

    Generate a structured profile analysis.
    \n{format_instructions}
    """

profile_analysis_prompt = PromptTemplate(
    input_variables=["profile_information"],
    template=PROFILE_ANALYSIS_TEMPLATE,
    validate_template=True,  # ensure all input variables are present in the template
    partial_variables={"format_instructions": profile_parser.get_format_instructions()},
)
