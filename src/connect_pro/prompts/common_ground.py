"""Template for identifying common ground between a LinkedIn profile and user information."""

from langchain.prompts.prompt import PromptTemplate

COMMON_GROUND_TEMPLATE = """
    You are an expert at finding meaningful connections between people. 
    Your goal is to identify common ground between two people based on their professional profiles.

    LinkedIn Profile Information:
    {profile_information}

    Information about the reader:
    {user_information}

    Your task:
    Identify specific, factual points of common ground (shared interests, experiences, or values) between the LinkedIn profile person and the reader.    
    Focus on specific, meaningful connections rather than generic similarities. 
    
    Important guidelines:
    - Refer to the LinkedIn profile person by their full name initially, then by first name only
    - Address the reader as "you" directly (never as "the user" or "the reader")
    - Focus ONLY on concrete, specific connections (shared experiences, skills, education, interests, locations)
    - If discussing industry experience, be specific about the exact technology, domain, or skill
    - Avoid vague statements like "you both seem interested in technology"
    - Do NOT invent information - if there's insufficient data to find common ground, only reply "More information would be needed to identify specific common ground"
    
    Be concise yet insightful. Think step by step and write 1-3 sentences total, with each sentence containing personalized similarities.
    """

common_ground_prompt = PromptTemplate(
    input_variables=["profile_information", "user_information"],
    template=COMMON_GROUND_TEMPLATE,
    validate_template=True,  # ensure all input variables are present in the template
)

