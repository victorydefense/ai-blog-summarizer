import requests
from bs4 import BeautifulSoup
from src.config import OPENAI_API_KEY  # Import the API key first
from src.models import SummarizeResponse
from openai import OpenAI  # Then import OpenAI

# Create a client using the new OpenAI interface with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

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

def summarize_blog(url: str) -> SummarizeResponse:
    """
    Extracts text from the blog, sends it to the OpenAI API using ChatCompletion
    to generate a bullet point summary, and returns the summary with references
    and an image suggestion.
    """
    blog_text = extract_blog_text(url)

    if not blog_text:
        return SummarizeResponse(
            bullet_points=["Error extracting content from the provided URL."],
            references=[url],
            image_suggestion="No image suggestion available due to extraction error."
        )

    # Truncate text if too long (adjust limit as needed)
    truncated_text = blog_text[:4000]

    prompt = (
        "You are an expert content summarizer. Given the following blog content, "
        "generate a concise bullet point summary suitable for a LinkedIn post. "
        "Include references (if available) and provide one creative image suggestion. "
        f"Blog content:\n\n{truncated_text}"
    )

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are an expert content summarizer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7)

        summary_text = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        return SummarizeResponse(
            bullet_points=["Error generating summary from OpenAI API."],
            references=[url],
            image_suggestion="No image suggestion available due to API error."
        )

    # Parse the summary output: Look for bullet points (lines starting with "-"),
    # lines containing "Reference:" for references, and a line with "Image:" for image suggestion.
    bullet_points = []
    references = []
    image_suggestion = ""

    for line in summary_text.splitlines():
        line = line.strip()
        if line.startswith("-"):
            bullet_points.append(line[1:].strip())
        elif "Reference:" in line:
            ref = line.split("Reference:")[-1].strip()
            references.append(ref)
        elif "Image:" in line:
            image_suggestion = line.split("Image:")[-1].strip()

    # Fallback if no bullet points were parsed
    if not bullet_points:
        bullet_points = summary_text.split("\n")

    # Ensure defaults for references and image suggestion
    if not references:
        references = [url]
    if not image_suggestion:
        image_suggestion = "Consider using a modern tech-themed graphic with AI imagery."

    return SummarizeResponse(
        bullet_points=bullet_points,
        references=references,
        image_suggestion=image_suggestion
    )