import datetime
import requests
import fitz
import pyttsx3
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from typing import Union

def read_pdf_from_url(pdf_url):
    # Step 1: Download PDF from URL
    response = requests.get(pdf_url);
    if response.status_code != 200:
        print("Failed to Fetch PDF");
        return;
    # Step 2: Load PDF into Memory
    pdf_data = response.content
    pdf_doc = fitz.open(stream=pdf_data,filetype="pdf")
    
    # Step 3: Extract Data
    full_text = ""
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        full_text += page.get_text()
        
    pdf_doc.close()
    return full_text

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate',150)
    engine.setProperty('volume',0.9)
    engine.say(text)
    engine.runAndWait()

def read_text(url:str) -> dict:
    """Read out the PDF for User A user will provide the Link for PDF.
    
    Args:
        pdf_url: This will be the Link of the PDF
    
    """
    text = read_pdf_from_url(url)
    if text:
        speak_text(text[:1000])
    return {
            "status": "success",
            "report": f"Reading the first 1000 characters from the PDF at {url}"
        }
        
def get_sum(a: float, b: float) -> dict:
    """Retreives the Sum of two Numbers.
    
    Args:
        a float: The First Argument User will Pass
        b float: The Second Argument User will 
        
    Returns:
        Union[int,float]: status and result or error msg.
    """
    return {
            "status": "success",
            "report": (
                "The Sum of {a}! and {b}! is {a+b}!"
            )
        }
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:   
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time,get_sum,read_text],
)