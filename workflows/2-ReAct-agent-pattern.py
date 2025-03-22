import openai # pip install openai
import re # regular expressions
import os
import logging
import requests
from typing import List, Dict, Any, Optional, Callable
from dotenv import load_dotenv
from openai import OpenAI
from brave import Brave # pip install brave-search
import time # because Brave free plan has a 1 request per second limit

#-----------------------------------------------------------------------------
# A ReAct (Reasoning and Acting) agent Think, Act and Observe within a loop
# Has access to tools (functions inside this code)
# Making multiple calls to the LLM as it loops, keeping a history
#-----------------------------------------------------------------------------

# Note: Brave requires a login and API key https://api-dashboard.search.brave.com/app/keys

# setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logging.getLogger("openai").setLevel(logging.WARNING)

# Load .env file or env vars
load_dotenv()


MAX_STEPS=5
API_KEY=os.getenv("API_KEY")
INFERNENCE_SERVER_URL=os.getenv("INFERENCE_SERVER_URL")
MODEL_NAME=os.getenv("MODEL_NAME")

logger.info(f"MODEL_NAME: {MODEL_NAME}")
logger.info(f"INFERNENCE_SERVER_URL: {INFERNENCE_SERVER_URL}")

BRAVE_API_KEY=os.getenv("BRAVE_API_KEY")
WEB_SEARCH_NUM_RESULTS=5


client = OpenAI(
    api_key=API_KEY,
    base_url=INFERNENCE_SERVER_URL
    )

class ReActAgent:
    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize a ReAct agent with available tools.
        
        Args:
            tools: Dictionary of tool names to tool functions that the agent can use
        """
        self.tools = tools
        self.thought_history = []
        self.action_history = []
        self.observation_history = []
        logger.info("agent initialized")

    def think(self, query:str, max_steps: int = MAX_STEPS) -> str:
        """
        Execute the ReAct pattern to solve a problem
        
        Args:
            query: The user's query or problem to be solved, a prompt
            max_steps: Maximum number of think-act-observe cycles to perform

        Returns:
            Final answer or response to the query            
        """

        # initial the reasoning process
        self.thought_history = []
        self.action_history = []
        self.observation_history = []

        step = 1
        for step in range(1,max_steps):
            # Think
            thought = self._reason(query, step)
            self.thought_history.append(thought)
            logger.info(f"step: {step} reason/thought:{thought}")

            if "Final Answer:" in thought:
                final_answer = re.search(r"Final Answer: (.*)", thought).group(1)
                return final_answer

            # Act
            action_name, action_input = self._extract_action(thought)            
            if not action_name:
                # If no valid action can be extracted, generate best and final answer
                self.thought_history.append("I need to provide a final answer based on what I know at this time.")
                self._generate_best_answer(query, step)
                break

            logger.info(f"step: {step} action_name: {action_name}({action_input})")
            action_result = self._execute_action(action_name, action_input)            
            self.action_history.append((action_name, action_input))

            # Observe
            self.observation_history.append(action_result)
            logger.info(f"step: {step} action_result/observation: {action_result}")

            step += 1

        # If we've used all steps and don't have a final answer, provide best guess
        return self._generate_best_answer(query, step)

    def _reason(self, query: str, step: int) -> str:
        """
        Reasoning step
        """
        # the prompt is the original user query + histories
        prompt = self._format_prompt(query)

        try: 
            response = client.chat.completions.create(
                model=MODEL_NAME,  
                messages=[
                    {"role": "system", "content": """
                    You are a reasoning agent that solves problems step-by-step.
                    Follow these rules:
                    1. Think through the problem carefully.
                    2. Use available tools when needed by writing "Action: tool_name(input)".
                    3. When you have the final answer, write "Final Answer: [your answer]".
                    4. Available tools: """ + ', '.join(self.tools.keys())
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            ) # completions
            thought = response.choices[0].message.content.strip()
            return thought
        except Exception as e:
            return f"I encountered an error while reasoning: {str(e)}"

    
    def _format_prompt(self, query: str) -> str:
        """
        Format the prompt with the query and history for the LLM.
        
        Args:
            query: The original user query
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Task: {query}\n\n"
        
        # Add the history of thoughts, actions, and observations
        for i in range(len(self.thought_history)):
            prompt += f"Thought {i+1}: {self.thought_history[i]}\n"
            
            if i < len(self.action_history):
                action_name, action_input = self.action_history[i]
                prompt += f"Action {i+1}: {action_name}({action_input})\n"
                
            if i < len(self.observation_history):
                prompt += f"Observation {i+1}: {self.observation_history[i]}\n"
            
            prompt += "\n"
        
        # Add instructions for the next step
        prompt += "Based on the above, provide your next thought. "
        
        if len(self.thought_history) >= 4:  # If we've already done several steps
            prompt += "Consider whether you have enough information to provide a Final Answer."
        else:
            prompt += "If you need more information, use one of the available tools."
            
        return prompt


    def _extract_action(self, thought: str) -> tuple:
        """
        Extract the action and input from the thought text.
        
        Args:
            thought: The reasoning text from which to extract an action
            
        Returns:
            Tuple of (action_name, action_input)
        """

       # Look for the pattern "Action: tool_name(action_input)"
        action_match = re.search(r"Action: (\w+)\(([^)]*)\)", thought)
        if action_match:
            action_name = action_match.group(1)
            action_input = action_match.group(2)
            
            # Verify that the action exists in available tools
            if action_name in self.tools:
                return action_name, action_input

        return None, None

    def _execute_action(self, action_name: str, action_input: str) -> str:
        """
        Execute the specified action with the given input.
        
        Args:
            action_name: Name of the tool to use
            action_input: Input to pass to the tool
            
        Returns:
            Result of the action as a string
        """
        try:
            tool_function = self.tools[action_name]
            result = tool_function(action_input)
            return str(result)
        except Exception as e:
            return f"Error executing {action_name}: {str(e)}"

    def _generate_best_answer(self, query: str, step: int) -> str:
        """
        Generate the best possible answer based on collected information
        when max steps are reached without a final answer.
        """
        logger.info(f"Max steps: {step} therefore _generate_best_answer based on the following prompt")

        # the prompt is the original user query + histories
        prompt = self._format_prompt(query)
        logger.info("-------------------------------------------")
        logger.info(f"{prompt}")
        logger.info("-------------------------------------------")

        try: 
            response = client.chat.completions.create(
                model=MODEL_NAME,  
                messages=[
                    {"role": "system", "content": """
                    You are a reviewer agent that reviews the work of thinking, actions and observations of another
                    agent and provides the your best answer based on the provided and only the provided user content.
                    """ 
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=500
            ) # completions
            best_answer = response.choices[0].message.content.strip()
            return best_answer
        except Exception as e:
            return f"I encountered an error while generating the best answer: {str(e)}"


#-----------------------------------------------------------------------------
# Define tools
#-----------------------------------------------------------------------------

def weather_tool(location: str) -> str:
    """ Uses api.open-meteo.com """
    logger.info(f"weather_tool invoked: {location}")
    # there are "cheaper" ways to get a lat/long but why not use a LLM :-)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,  
            messages=[
                {"role": "system", "content": """
                You are a knowledgeable assistant capable of providing geographical coordinates. 
                When given the name of a city or state, respond with its approximate 
                latitude and longitude in decimal degrees.
                formatted as 'Latitude: [latitude], Longitude: [longitude]'.
                """ 
                },
                {"role": "user", "content": location}
            ],
            temperature=0.0,
            max_tokens=500
        ) # completions
        lat_long = response.choices[0].message.content.strip()
        logger.info(f"weather_tool lat_long: {lat_long}")
        # Regular expression to extract latitude and longitude
        match = re.search(r"Latitude:\s*([-+]?\d*\.\d+|\d+),\s*Longitude:\s*([-+]?\d*\.\d+|\d+)", lat_long)

        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            logger.info(f"Latitude: {latitude}, Longitude: {longitude}")

            # now that we have the lat and long we can invoke the weather API
            response = requests.get(
                # celsius, metric 
                # f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
                # fahrenheit, imperial
                f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph"
            )
            weather_data = response.json()
            logger.info(f"weather_data: {weather_data['current']}")
            return weather_data["current"]

        else:
            logger.info(f"weather_tool could NOT extract coordinates for {location}")
            return f"weather_tool could NOT extract coordinates for {location}"
    except Exception as e:
        return f"I encountered an error in the weather tool while finding the lat/long: {str(e)}"


    return f"Weather in {location}: Sunny, 72°F"


def calculator_tool(expression: str) -> str:
    """Calculator tool that evaluates mathematical expressions."""
    try:
        logger.info(f"calculator_tool invoked: {expression}")
        return str(eval(expression))
    except:
        return "Error: Could not evaluate the expression."            

def search_wikipedia(query: str) -> str:
    # ToDo: URL argument formatting needed
    query = query.strip('"')
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    logger.info(f"search_wikipedia: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('extract', 'No information found.')
    else:
        return f'Error fetching data from Wikipedia: {response.status.code}'


def web_search(query: str) -> str:
    query = query.strip('"')
    brave = Brave(BRAVE_API_KEY)
    # time.sleep(0.5) # slow things down due to 1 request per second limit on free plan
    try: 
        search_results = brave.search(q=query, count=WEB_SEARCH_NUM_RESULTS)
        web_search_results = search_results.web_results
        logger.info(f"web_search_results: {web_search_results}")
        return web_search_results
    except Exception as e:
        return f"I encountered an error in the web_search tool: {str(e)}"

# ToDo: Wondering if I need a way to "deep dive" into a page
def web_page_scraper(query: str) -> str:
    logger.info("**************************************")
    logger.info(f"web_page_scrapper: {query}")
    logger.info("**************************************")
    return "No results from web_page_scrapper"

    
# note: this is not the "formal" OpenAI way to define tools
tools = {    
    "calculate": calculator_tool,
    "weather": weather_tool,
    "search_wikipedia": search_wikipedia,
    "web_search" : web_search
}

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ReActAgent(tools)

    # OK: gpt4o
    # OK: qwen2.5-coder:14b-instruct-fp16
    query = "What's the temperature in Raleigh, NC and what's 25 * 4?"
    answer = agent.think(query, max_steps=3)

    # OK: gpt4o
    # OK: qwen2.5-coder:14b-instruct-fp16
    # query = "What's the weather in New York and what's 25 * 4?"
    # answer = agent.think(query, max_steps=5)

    # OK: gpt4o
    # OK: qwen2.5-coder:14b-instruct-fp16
    # should use the weather and wikipedia tool
    # query = "What's the temperature in Raleigh, NC and what is Archaeoacoustics?"
    # answer = agent.think(query, max_steps=3)

    # OK: gpt4o
    # NO: qwen2.5-coder:14b-instruct-fp16
    # query = "What is the top speed of a leopard in kilometers per hour?"
    # answer = agent.think(query, max_steps=3)

    # OK: gpt4o
    # NO: qwen2.5-coder:14b-instruct-fp16
    # query = "What length of the Pont des Arts in meters?"
    # answer = agent.think(query, max_steps=3)

    # OK: gpt4o
    # NO: qwen2.5-coder:14b-instruct-fp16
    # query = "How many seconds would it take for a leopard at full speed to run through Pont des Arts?"
    # answer = agent.think(query, max_steps=5)

    # Best when out of steps, Final when the LLM thinks it is done
    logger.info(f"{query}\nUltimate Answer: {answer}")