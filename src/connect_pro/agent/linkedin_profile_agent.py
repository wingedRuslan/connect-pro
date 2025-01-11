from typing import Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from connect_pro.config.settings import settings
from connect_pro.search.tavily_search import get_profile_data_search_tavily


class LinkedInProfileAgent:
    """Agent for retrieving LinkedIn profile URLs based on search criteria."""

    def __init__(self, llm: Optional[ChatOpenAI] = None, verbose: bool = False):
        """Initialize the LinkedIn Profile Agent.

        Args:
            llm: Language model to use (defaults to ChatOpenAI with specific settings)
            verbose: Whether to print detailed execution information
        """
        self.llm = llm or ChatOpenAI(
            temperature=0,
            model_name=settings.OPENAI_MODEL_NAME,
        )
        self.verbose = verbose
        self._setup_prompt()
        self._setup_tools()
        self._setup_agent()

    def _setup_prompt(self) -> None:
        """Set up the prompt template for the agent."""
        self.prompt_template = PromptTemplate(
            template="""Given the search query {search_query}, find this person's LinkedIn profile URL. 
                        IMPORTANT: Return ONLY the raw URL without any markdown formatting, brackets, or additional text.
                        Return only the URL, without any additional text.""",
            input_variables=["search_query"],
        )

    def _setup_tools(self) -> None:
        """Set up the tools available to the agent."""
        self.tools = [
            Tool(
                name="LinkedIn Profile Search",
                func=get_profile_data_search_tavily,
                description="Searches for LinkedIn profile URLs based on name, company, position, or other identifying information",
            )
        ]

    def _setup_agent(self) -> None:
        """Set up the ReAct agent with tools and prompt."""

        # @ langchain.hub.pull("hwchase17/react")
        react_prompt = PromptTemplate(
            template="""
                Answer the following questions as best you can. You have access to the following tools:

                {tools}

                Use the following format:

                Question: the input question you must answer
                Thought: you should always think about what to do
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

                Question: {input}
                Thought:{agent_scratchpad} 
                """,
            input_variables=["agent_scratchpad", "input", "tool_names", "tools"],
        )

        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=react_prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, tools=self.tools, verbose=self.verbose
        )

    def find_profile(self, search_query: str) -> str:
        """
        Find a LinkedIn profile URL based on search criteria.
        
        Args:
            search_query: Search string that can include name, company, position,
                          or other identifying information (e.g., "John Smith Software Engineer, Google, London") 
            
        Returns:
            str: LinkedIn profile URL
            
        Raises:
            ValueError: If no valid LinkedIn profile URL is found
        """
        result = self.agent_executor.invoke(
            input={"input": self.prompt_template.format_prompt(search_query=search_query)}
        )

        profile_url = result.get("output", "").strip()
        if not profile_url or "linkedin.com" not in profile_url:
            return None

        return profile_url

