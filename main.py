from fastapi import FastAPI, UploadFile, File
import shutil
import os
import pdfplumber
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

UPLOAD_DIR = "uploads"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"message": "CareerPath AI backend is running!"}

@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    extracted_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text()

    # Send to Gemini for analysis
    prompt = f"""You are a career advisor. Analyze the following resume text and identify key skill gaps for a software developer role. Keep the answer short and in bullet points.

Resume:
{extracted_text}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    analysis = response.text

    return {
        "filename": file.filename,
        "message": "Resume analyzed successfully",
        "skill_gap_analysis": analysis
    }
@app.post("/generate-roadmap")
def generate_roadmap(skill_gaps: str):
    prompt = f"""You are a career mentor. Based on the following skill gaps, create a detailed week-by-week learning roadmap for the next 8 weeks. Be specific about what to learn each week.

Skill Gaps:
{skill_gaps}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return {"roadmap": response.text}