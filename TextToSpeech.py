import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables from .env file.
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")  # Default voice
print(f"AssistantVoice: {AssistantVoice}, Type: {type(AssistantVoice)}")  # Debug statement

# Initialize Pygame and the mixer once at the start of the program.
pygame.init()
pygame.mixer.init()

# Asynchronous function to convert text to audio.
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    
    # Stop and unload any currently playing music to release the file lock.
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    
    # Wait for a short delay to ensure the file is released.
    pygame.time.delay(100)  # 100ms delay
    
    # Check if the file exists and delete it if it does.
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError as e:
            print(f"Failed to delete file: {e}")
            return
        
    # Ensure AssistantVoice is a string.
    if not isinstance(AssistantVoice, str):
        raise ValueError("AssistantVoice must be a string")
        
    # Create the communication object to generate speech.
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')  # Fixed pitch format
    await communicate.save(file_path)
    
# Function to manage text-to-speech (TTS) functionality.
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to audio.
            asyncio.run(TextToAudioFile(Text))
            
            # Load the audio file into pygame mixer.
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()
            
            # Loop until the audio is playing.
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)
                
            return True
        
        except Exception as e:
            print(f"Error in TTS: {e}")
            return False
        
        finally:
            try:
                # Call the provided function with False to signal the end of TTS.
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                
            except Exception as e:
                print(f"Error in finally block: {e}")
                
# Function to manage text-to-speech with additional responses.
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    # List of predefined responses for cases where the text is too long.
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    
    # If the text is very long.
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
        
    # Otherwise, just play the whole text.
    else:
        TTS(Text, func)
        
# Main execution loop.
if __name__ == "__main__":
    try:
        while True:
            # Prompt user for input and pass it to the TTS function.
            TextToSpeech(input("Enter the text: "))
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        # Clean up Pygame and the mixer when the program exits.
        pygame.mixer.quit()
        pygame.quit()