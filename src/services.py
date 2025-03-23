import os
from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
from src.models import SummarizeResponse

# Get your Hugging Face API token from the environment
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("HF_API_TOKEN environment variable is not set!")

# Define the Hugging Face Inference API endpoint for the BART model
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def extract_blog_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try to locate an <article> element first.
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
            text = "\n".join([p.get_text() for p in paragraphs])
            if text.strip():
                return text.strip()
        
        # If no <article> was found or text is empty,
        # try to find the div with the class "text-rich-text-blog"
        blog_div = soup.find("div", class_="text-rich-text-blog")
        if blog_div:
            paragraphs = blog_div.find_all("p")
            text = "\n".join([p.get_text() for p in paragraphs])
            if text.strip():
                return text.strip()
        
        # Fallback: get all paragraphs in the page
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs])
        return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return ""

def summarize_text_hf(text: str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": text}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        # Expected output: a list of dictionaries with a key "summary_text"
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("summary_text", "").strip()
        else:
            return ""
    except Exception as e:
        print(f"Error from Hugging Face API: {e}")
        return ""

def summarize_blog(url: str) -> SummarizeResponse:
    """
    Extracts text from the blog, sends it to the Hugging Face Inference API using
    the facebook/bart-large-cnn model, and returns the summary with references
    and an image suggestion.
    """
    blog_text = extract_blog_text(url)
    
    if not blog_text:
        return SummarizeResponse(
            bullet_points=["Error extracting content from the provided URL."],
            references=[url],
            image_suggestion="No image suggestion available due to extraction error."
        )
    
    # Truncate text if too long; bart-large-cnn works best with shorter inputs
    truncated_text = blog_text[:1024]
    
    summary_text = summarize_text_hf(truncated_text)
    
    if not summary_text:
        return SummarizeResponse(
            bullet_points=["Error generating summary from Hugging Face API."],
            references=[url],
            image_suggestion="No image suggestion available due to API error."
        )
    
    # Here you can parse the summary_text if needed.
    # For simplicity, we'll assume the returned summary is a single block of text.
    bullet_points = summary_text.split("\n")
    if not bullet_points:
        bullet_points = [summary_text]
    
    references = [url]
    image_suggestion = "Consider using a modern tech-themed graphic with AI imagery."
    
    return SummarizeResponse(
        bullet_points=bullet_points,
        references=references,
        image_suggestion=image_suggestion
    )