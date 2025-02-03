import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep
from io import BytesIO

# Load the .env file
load_dotenv()

# Access the API key
api_key = os.getenv('HuggingFaceAPIKey')
if not api_key:
    raise ValueError("HuggingFaceAPIKey not found in .env file.")

# API details.
API_URL = "https://api-inference.huggingface.co/pipeline/text-to-image/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {api_key}"}

# Ensure the Data folder exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Function to open and display images based on given prompt.
def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    
    # Generate the filenames for the images.
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        
        try:
            # Try to open and display the image.
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
            
        except IOError:
            print(f"Unable to open image: {image_path}")

# Async function to send a query to the Hugging Face API.
async def query(payload):
    while True:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 429:
            # Wait for 60 seconds if rate-limited
            print("Rate limit reached. Waiting for 60 seconds...")
            await asyncio.sleep(60)
            continue
        return response.content

# Async function to generate images based on the given prompt.
async def generate_images(prompt: str):
    tasks = []
    
    # Create 4 image generation tasks.
    for _ in range(4):
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 100,
                "guidance_scale": 10,
                "width": 1080,
                "height": 1080,
            }
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        
    # Wait for all tasks to complete.
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Save the images to the files.
    for i, image_bytes in enumerate(image_bytes_list):
        image_path = fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg"
        print(f"Saving image to: {image_path}")
        
        # Verify the image data
        try:
            img = Image.open(BytesIO(image_bytes))
            img.verify()  # Verify that the image data is valid
            print(f"Image data is valid: {image_path}")
        except Exception as e:
            print(f"Invalid image data for {image_path}: {e}")
            continue  # Skip saving this file
        
        # Save the image
        with open(image_path, "wb") as f:
            f.write(image_bytes)

# Wrapper function to generate and open images.
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

"""Main loop to monitor for images generated.
while True:
    try:
        # Corrected file path
        file_path = r"Frontend\Files\ImageGeneration.data"
        
        # Verify file existence
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}. Creating a new one.")
            with open(file_path, "w") as f:
                f.write("DefaultPrompt,False")  # Initialize with default values

        # Read the file
        with open(file_path, "r") as f:
            Data: str = f.read().strip()  # Use .strip() to remove extra whitespace

        # Check if the data is empty or malformed
        if not Data or "," not in Data:
            print(f"Invalid or empty data in {file_path}. Resetting to default.")
            with open(file_path, "w") as f:
                f.write("DefaultPrompt,False")  # Reset to a default value
            sleep(1)
            continue  # Skip this iteration and retry

        # Split the data into Prompt and Status
        Prompt, Status = Data.split(",")
        
        if Status == "True":
            print("Generating images...")
            GenerateImages(Prompt)  # Pass the prompt as a positional argument
            # Write "False,False" to the file
            with open(file_path, "w") as f:
                f.write("False,False")
            break
            
        else:
            # Ask the user for a prompt
            Prompt = input("Enter a prompt for image generation: ")
            Status = "True"  # Set status to True to trigger image generation

            # Save the prompt and status to the file
            with open(file_path, "w") as f:
                f.write(f"{Prompt},{Status}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sleep(1)"""