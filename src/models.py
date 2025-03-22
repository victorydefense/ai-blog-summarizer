from pydantic import BaseModel

class SummarizeRequest(BaseModel):
    url: str

class SummarizeResponse(BaseModel):
    bullet_points: list[str]
    references: list[str]
    image_suggestion: str