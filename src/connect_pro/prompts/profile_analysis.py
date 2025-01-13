"""Templates for analyzing professional profiles."""

from langchain.prompts.prompt import PromptTemplate

PROFILE_ANALYSIS_TEMPLATE = """Based on the following information about a person:
    {information}
    
    Please provide:
    1. Professional Summary (2-3 sentences highlighting their key achievements and role) 
    2. Personal Background (1-2 sentences about their background and journey)
    3. Two Interesting Facts:
        - First unique or surprising fact 
        - Second unique or surprising fact
    
    Focus on being concise yet informative. Include specific details and achievements where available. 
    If certain information is not provided, focus on what is known rather than speculating.
    """

profile_analysis_prompt = PromptTemplate(
    input_variables=["information"],
    template=PROFILE_ANALYSIS_TEMPLATE,
    validate_template=True,  # ensure all input variables are present in the template
)
