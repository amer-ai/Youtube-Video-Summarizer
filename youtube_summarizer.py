import os
import re
import json
import requests
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    # Regular expression pattern for YouTube URLs
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([^&?/]+)',  # Standard YouTube URLs
        r'(?:embed/|v%3D|vi%2F)([^%&?/]+)',  # Embedded URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str) -> str:
    """Fetch transcript from YouTube video using SearchAPI."""
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        "api_key": "ey1hoRoLxjfJxXN5VYVwZLuU"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Combine all transcript segments into one text
        transcript = " ".join(segment["text"] for segment in data["transcripts"])
        return transcript
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transcript: {e}")
        return ""

def generate_summary(transcript: str) -> str:
    """Generate a bullet-point summary using OpenAI's GPT-4 Turbo."""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise bullet-point summaries of video transcripts. Focus on the main points and key takeaways."
                },
                {
                    "role": "user",
                    "content": f"Please create a bullet-point summary of the following transcript:\n\n{transcript}"
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    except Exception as e:
        if "model_not_found" in str(e):
            print("Error: GPT-4 Turbo model not available. Please ensure you have access to GPT-4 models in your OpenAI account.")
        else:
            print(f"Error generating summary: {e}")
        return ""

def main():
    # Get YouTube URL from user
    url = input("Enter YouTube video URL: ")
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print("Invalid YouTube URL")
        return
    
    print("Fetching transcript...")
    transcript = get_transcript(video_id)
    if not transcript:
        print("Failed to fetch transcript")
        return
    
    print("\nGenerating summary...")
    summary = generate_summary(transcript)
    if not summary:
        print("Failed to generate summary")
        return
    
    print("\nSummary:")
    print(summary)

if __name__ == "__main__":
    main()
