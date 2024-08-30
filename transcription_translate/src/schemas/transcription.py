from pydantic import BaseModel


# Model for transcription request
class TranscriptionRequest(BaseModel):
    videoUrl: str
    language: str
    translateLanguage: str
