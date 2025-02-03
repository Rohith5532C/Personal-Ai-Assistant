# Import necessary libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import re

# Register Chrome as the browser to use
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Default Chrome installation path
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Load environment variables from .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define a user agent for making web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client with the API key
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages
messages = []

# System message to provide context to the chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]

# Function to perform a Google search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save to file
def Content(Topic):
    # Nested function to open a file in Notepad
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])
        
    # Nested function to generate content using AI
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        
        # Process streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("content ", "")
    ContentByAI = ContentWriterAI(Topic)
    
    # Save content to a file
    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
        
    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")
    return True

# Function to search for a topic on YouTube
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.get('chrome').open(Url4Search)  # Use Chrome to open the link
    return True

# Function to play a video on YouTube
def PlayYouTube(query):
    playonyt(query)
    return True

# Function to open an application or webpage
def OpenApp(app, sess=requests.session()):
    try:
        # Try to open the app using AppOpener
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # If the app is not installed, search for it on Google and open the first result
        def extract_links(html):
            if html is None:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all search result links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith("/url?q="):  # Google search result links start with /url?q=
                    href = href.split("/url?q=")[1].split("&")[0]  # Extract the actual URL
                    if "http" in href and "google.com" not in href:  # Filter out Google's own links
                        links.append(href)
            
            return links
        
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results")
            return None
        
        # Perform a Google search for the app
        html = search_google(app)
        
        if html:
            links = extract_links(html)
            if links:
                # Open the first valid search result in Chrome
                try:
                    print(f"Opening link: {links[0]}")  # Debugging: Print the link being opened
                    webbrowser.get('chrome').open(links[0])  # Use Chrome to open the link
                    return True
                except Exception as e:
                    print(f"Failed to open the link: {e}")
                    return False
            else:
                print("No search results found.")
                return False
        else:
            print("Failed to retrieve search results.")
            return False

# Function to close an application
def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# Function to execute system-level commands
def System(command):
    # Nested function to mute
    def mute():
        keyboard.press_and_release("volume mute")
        
    # Nested function to unmute
    def unmute():
        keyboard.press_and_release("volume unmute")
        
    # Nested function to increase volume
    def volume_up():
        keyboard.press_and_release("volume up")
        
    # Nested function to decrease volume
    def volume_down():
        keyboard.press_and_release("volume down")
     
    # Execute the command   
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
        
    return True

# Asynchronous function to translate and execute commands
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    
    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
                
        elif command.startswith("general "):
            pass
        
        elif command.startswith("realtime "):
            pass
        
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
            
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)
            
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
            
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
            
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
            
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        
        else:
            print(f"No Function Found for {command}")
            
    results = await asyncio.gather(*funcs)
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate command execution
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

#Example usage
"""if __name__ == "__main__":
    commands = [
        "open settings",
        "youtube search Powerstar craze",  # This will open the first Google search result
        "play chuttamalle",
        "google search Python programming",
        "open whatsapp",
        "content application for sick leave",
        "open file explorer"
    ]
    
    asyncio.run(Automation(commands))"""