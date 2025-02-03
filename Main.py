from Frontend.GUI import (
    GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen, 
    TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, 
    QueryModifier, GetMicrophoneStatus, GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.ImageGeneration import GenerateImages
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# Initialize default chat logs if none exist
def ShowDefaultChatIfNoChats():
    File = open(r'Data\Chatlog.json', "r", encoding="utf-8")
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Response.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

# Read chat logs from JSON file
def ReadChatLogJson():
    with open(r'Data\Chatlog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

# Integrate chat logs into the GUI
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Display chat logs on the GUI
def ShowChatOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        File.close()
        File = open(TempDirectoryPath('Response.data'), 'w', encoding='utf-8')
        File.write(Data)
        File.close()

# Initial setup
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

InitialExecution()

# Main execution logic
def MainExecution():
    SetAssistantStatus("Listening...")
    
    Query = SpeechRecognition()  # Capture voice input
    print(f"Captured Query: {Query}")

    if not Query or Query.strip() == "":
        print("No voice input detected!")
        SetAssistantStatus("Available...")
        return

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")

    # ===== NEW IMAGE GENERATION HANDLING =====
    if "generate image" in Query.lower() or "create image" in Query.lower():
        prompt = Query.lower().replace("generate image", "").replace("create image", "").strip()
        if prompt:
            try:
                SetAssistantStatus("Generating Images...")
                GenerateImages(prompt)
                Answer = "I've generated the images based on your description."
            except Exception as e:
                Answer = f"Failed to generate images: {str(e)}"
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            SetAssistantStatus("Available...")
            return
        else:
            Answer = "Please describe what you want me to generate."
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            SetAssistantStatus("Available...")
            return

    Decision = FirstLayerDMM(Query)
    print(f"Decision from FirstLayerDMM: {Decision}")

    # ===== NEW AUTOMATION COMMAND HANDLING =====
    AutomationFunctions = ["open", "close", "play", "system", 
                          "content", "google search", "youtube search"]
    automation_commands = [cmd for cmd in Decision if any(
        cmd.startswith(func) for func in AutomationFunctions)]

    if automation_commands:
        try:
            SetAssistantStatus("Processing Commands...")
            run(Automation(automation_commands))
            Answer = "Commands executed successfully."
        except Exception as e:
            Answer = f"Failed to execute commands: {str(e)}"
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        TextToSpeech(Answer)
        SetAssistantStatus("Available...")
        return

    # ... (rest of original processing remains the same below)

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)
    
    Merged_Query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_Query))
    else:
        for Queries in Decision:
            if "general" in Queries:
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                break
            elif "realtime" in Queries:
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                break
            elif "exit" in Queries:
                Answer = "Okay, Bye!"
                TextToSpeech(Answer)
                os._exit(1)
    
    if Answer:
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
    else:
        SetAssistantStatus("Available...")

# ... (rest of the code remains the same below)

# Thread to handle microphone status and execution
def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

# Thread to handle the GUI
def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()