from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import asyncio
import tempfile
import shutil
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import textwrap
import jwt
import hashlib

# Import emergentintegrations
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Authentication setup
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# In-memory user storage (for simple demo - in production use proper database)
users_db = {}  # email -> user_data

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize LLM Chat
def get_llm_chat():
    """Initialize LLM client for educational content generation."""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=str(uuid.uuid4()),
        system_message="You are an expert educational content analyzer and lesson plan generator."
    ).with_model("gemini", "gemini-2.0-flash")
    
    return chat

def get_user_llm_chat(api_key: str):
    """Initialize LLM client with user's API key."""
    if not api_key:
        # Fallback to system key
        return get_llm_chat()
    
    chat = LlmChat(
        api_key=api_key,
        session_id=str(uuid.uuid4()),
        system_message="You are an expert educational content analyzer and lesson plan generator."
    ).with_model("gemini", "gemini-2.0-flash")
    
    return chat

# Authentication helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for user."""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user."""
    payload = verify_jwt_token(credentials.credentials)
    user_email = payload.get("email")
    if user_email not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[user_email]

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: str
    lastName: str
    email: str
    institution: str
    department: str
    password_hash: str
    api_key: Optional[str] = None
    newsletter: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserSignup(BaseModel):
    firstName: str
    lastName: str
    email: str
    institution: str
    department: str
    password: str
    newsletter: bool = False

class UserLogin(BaseModel):
    email: str
    password: str

class ApiKeyValidation(BaseModel):
    apiKey: str

class UserResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    institution: str
    department: str
    hasApiKey: bool = False

class AuthResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class PDFExtractionResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    subject_names: List[str]
    lecture_topics: List[str]
    lecture_focus_mapping: Dict[str, List[str]]  # Maps lecture topics to their focus topics
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

class LessonPlanRequest(BaseModel):
    subject_name: str
    lecture_topic: str
    focus_topic: Optional[str] = ""
    blooms_taxonomy: str
    aqf_level: str
    lesson_duration: str

class LessonPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_data: LessonPlanRequest
    content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Standard options
BLOOMS_TAXONOMY_LEVELS = [
    "Remember",
    "Understand", 
    "Apply",
    "Analyze",
    "Evaluate",
    "Create"
]

AQF_LEVELS = [
    "AQF Level 1 - Certificate I",
    "AQF Level 2 - Certificate II",
    "AQF Level 3 - Certificate III",
    "AQF Level 4 - Certificate IV",
    "AQF Level 5 - Diploma",
    "AQF Level 6 - Advanced Diploma/Associate Degree",
    "AQF Level 7 - Bachelor Degree",
    "AQF Level 8 - Bachelor Honours/Graduate Certificate/Graduate Diploma",
    "AQF Level 9 - Masters Degree",
    "AQF Level 10 - Doctoral Degree"
]

LESSON_DURATIONS = [
    "30 minutes",
    "45 minutes",
    "1 hour",
    "1.5 hours",
    "2 hours",
    "2.5 hours",
    "3 hours"
]

# Helper function to extract text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty text
                    text += page_text + "\n"
            except Exception as page_error:
                logger.warning(f"Failed to extract text from page {page_num}: {str(page_error)}")
                continue
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in the PDF. Please ensure the PDF contains text content and is not a scanned image.")
        
        return text
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Unable to process this PDF format. Please try with a different PDF file or ensure the PDF contains readable text. Error: {str(e)}")

# Helper function to generate PDF
def generate_lesson_plan_pdf(lesson_plan: LessonPlan, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    subsection_heading_style = ParagraphStyle(
        'SubsectionHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        leftIndent=20,
        bulletIndent=10,
        spaceBefore=3,
        spaceAfter=3
    )
    
    story = []
    
    # Title
    story.append(Paragraph("LESSON PLAN", title_style))
    story.append(Spacer(1, 20))
    
    # Lesson details table
    data = [
        ["Subject:", lesson_plan.request_data.subject_name],
        ["Lecture Topic:", lesson_plan.request_data.lecture_topic],
        ["Focus Topic:", lesson_plan.request_data.focus_topic or "General Coverage"],
        ["Bloom's Taxonomy Level:", lesson_plan.request_data.blooms_taxonomy],
        ["AQF Level:", lesson_plan.request_data.aqf_level],
        ["Duration:", lesson_plan.request_data.lesson_duration],
        ["Generated:", lesson_plan.generated_at.strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Process content sections
    content_sections = lesson_plan.content.split('\n\n')
    
    for section in content_sections:
        section = section.strip()
        if not section:
            continue
            
        lines = section.split('\n')
        first_line = lines[0].strip()
        
        # Check if first line is a section heading (ALL CAPS)
        if first_line.isupper() and len(first_line) < 100:
            # Add section heading
            story.append(Paragraph(first_line, section_heading_style))
            
            # Process remaining lines in this section
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if it's a subsection heading (starts with capital and ends with minutes)
                if ('(' in line and 'minutes)' in line) or (line.endswith('minutes')):
                    story.append(Paragraph(line, subsection_heading_style))
                elif line.startswith('- '):
                    # Bullet point
                    story.append(Paragraph(f"• {line[2:]}", bullet_style))
                else:
                    # Regular paragraph
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 6))
        else:
            # Regular content block
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('- '):
                    # Bullet point
                    story.append(Paragraph(f"• {line[2:]}", bullet_style))
                else:
                    # Regular paragraph
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 6))
    
    doc.build(story)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "LLM Lesson Plan Builder API"}

# Authentication routes
@api_router.post("/auth/signup", response_model=AuthResponse)
async def signup(user_data: UserSignup):
    """User registration endpoint."""
    # Check if user already exists
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(
        firstName=user_data.firstName,
        lastName=user_data.lastName,
        email=user_data.email,
        institution=user_data.institution,
        department=user_data.department,
        password_hash=hash_password(user_data.password),
        newsletter=user_data.newsletter
    )
    
    # Store user (in production, save to database)
    users_db[user.email] = user.dict()
    
    # Create JWT token
    token = create_jwt_token(user.dict())
    
    # Return response
    user_response = UserResponse(
        id=user.id,
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        institution=user.institution,
        department=user.department,
        hasApiKey=bool(user.api_key)
    )
    
    return AuthResponse(success=True, token=token, user=user_response)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    """User login endpoint."""
    # Check if user exists
    if login_data.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = users_db[login_data.email]
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    token = create_jwt_token(user)
    
    # Return response
    user_response = UserResponse(
        id=user["id"],
        firstName=user["firstName"],
        lastName=user["lastName"],
        email=user["email"],
        institution=user["institution"],
        department=user["department"],
        hasApiKey=bool(user.get("api_key"))
    )
    
    return AuthResponse(success=True, token=token, user=user_response)

@api_router.post("/auth/validate-api-key")
async def validate_api_key(
    api_data: ApiKeyValidation,
    current_user: dict = Depends(get_current_user)
):
    """Validate and store user's Gemini API key."""
    try:
        # Test the API key by making a simple call
        chat = get_user_llm_chat(api_data.apiKey)
        
        # Try a simple test message
        test_message = UserMessage(text="Hello")
        response = await chat.send_message(test_message)
        
        # If successful, store the API key for the user
        users_db[current_user["email"]]["api_key"] = api_data.apiKey
        
        return {"success": True, "message": "API key validated and saved successfully"}
    
    except Exception as e:
        logger.error(f"API key validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid API key or failed to connect to Gemini API")

@api_router.get("/auth/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user["id"],
        firstName=current_user["firstName"],
        lastName=current_user["lastName"],
        email=current_user["email"],
        institution=current_user["institution"],
        department=current_user["department"],
        hasApiKey=bool(current_user.get("api_key"))
    )

@api_router.get("/options")
async def get_options():
    """Get standard dropdown options"""
    return {
        "blooms_taxonomy": BLOOMS_TAXONOMY_LEVELS,
        "aqf_levels": AQF_LEVELS,
        "lesson_durations": LESSON_DURATIONS
    }

@api_router.post("/upload-pdf", response_model=PDFExtractionResult)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload PDF and extract subject information using LLM"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(temp_file_path)
        
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Use LLM to extract structured information (use user's API key if available)
        user_api_key = current_user.get("api_key")
        chat = get_user_llm_chat(user_api_key)
        
        extraction_prompt = f"""
        Analyze the following academic subject outline PDF content and extract the required information in JSON format.
        
        PDF Content:
        {pdf_text[:8000]}  # Limit to first 8000 characters
        
        Please extract and return ONLY a JSON object with the following structure:
        {{
            "subject_names": ["list of subject names found"],
            "lecture_topics": ["list of lecture topics from timetable of activities"],
            "lecture_focus_mapping": {{
                "Lecture Topic 1": ["focus topic 1.1", "focus topic 1.2"],
                "Lecture Topic 2": ["focus topic 2.1", "focus topic 2.2"],
                "etc": ["etc"]
            }}
        }}
        
        Instructions:
        1. Look for subject names in headers, titles, or course information
        2. Find lecture topics in the timetable of activities section
        3. For each lecture topic, identify its corresponding focus topics (subtopics/subdivisions mentioned for that specific lecture/week)
        4. Create a mapping where each lecture topic maps to its specific focus topics only
        5. If a lecture topic has no specific focus topics, map it to an empty array []
        6. Return clean, readable names without extra formatting
        7. Return ONLY the JSON object, no other text
        """
        
        user_message = UserMessage(text=extraction_prompt)
        response = await chat.send_message(user_message)
        
        # Parse LLM response
        try:
            # Clean the response and extract JSON
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            import json
            extracted_data = json.loads(response_text)
            
            # Validate extracted data
            subject_names = extracted_data.get('subject_names', [])
            lecture_topics = extracted_data.get('lecture_topics', [])
            lecture_focus_mapping = extracted_data.get('lecture_focus_mapping', {})
            
            # Ensure we have at least some data
            if not any([subject_names, lecture_topics]):
                raise HTTPException(status_code=400, detail="Could not extract meaningful data from PDF")
            
            # Validate mapping structure
            if not isinstance(lecture_focus_mapping, dict):
                lecture_focus_mapping = {}
            
            # Create extraction result
            result = PDFExtractionResult(
                filename=file.filename,
                subject_names=subject_names,
                lecture_topics=lecture_topics,
                lecture_focus_mapping=lecture_focus_mapping
            )
            
            # Save to database
            await db.pdf_extractions.insert_one(result.dict())
            
            return result
            
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@api_router.post("/generate-lesson-plan", response_model=LessonPlan)
async def generate_lesson_plan(
    request: LessonPlanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate lesson plan using LLM"""
    try:
        # Use user's API key if available
        user_api_key = current_user.get("api_key")
        chat = get_user_llm_chat(user_api_key)
        
        generation_prompt = f"""
        Create a detailed lesson plan based on the following parameters:
        
        Subject: {request.subject_name}
        Lecture Topic: {request.lecture_topic}
        Focus Topic: {request.focus_topic if request.focus_topic else "General coverage of the lecture topic"}
        Bloom's Taxonomy Level: {request.blooms_taxonomy}
        AQF Level: {request.aqf_level}
        Duration: {request.lesson_duration}
        
        Please create a comprehensive lesson plan with professional formatting. Use proper headings, bullet points, and structure. DO NOT use markdown symbols like #, *, or other formatting characters. Format it as follows:
        
        LEARNING OBJECTIVES
        - Clear, measurable objectives aligned with the {request.blooms_taxonomy} level of Bloom's taxonomy
        
        LEARNING OUTCOMES
        - What students will achieve, appropriate for {request.aqf_level}
        
        PRE-REQUISITES
        - Required knowledge or skills
        
        MATERIALS AND RESOURCES
        - What's needed for the lesson
        
        LESSON STRUCTURE ({request.lesson_duration})
        
        Introduction/Hook (X minutes)
        - Engage students activities
        
        Main Content Delivery (X minutes)
        - Explanation and demonstration activities
        
        Active Learning Activities (X minutes)
        - Hands-on, discussion, and practice activities
        
        Assessment/Evaluation (X minutes)
        - Formative assessment aligned with Bloom's level
        
        Conclusion/Summary (X minutes)
        - Wrap-up activities
        
        ASSESSMENT CRITERIA
        - How student understanding will be measured
        
        EXTENSION ACTIVITIES
        - For advanced students
        
        DIFFERENTIATION STRATEGIES
        - For diverse learning needs
        
        Focus Area: {f"Emphasize {request.focus_topic} within the broader {request.lecture_topic} context" if request.focus_topic else f"Provide comprehensive coverage of {request.lecture_topic}"}
        
        Ensure the content is:
        - Age and level appropriate for {request.aqf_level}
        - {"Focused specifically on '" + request.focus_topic + "'" if request.focus_topic else "Comprehensively covering '" + request.lecture_topic + "'"}
        - Designed to achieve {request.blooms_taxonomy} level cognitive skills
        - Realistic for the {request.lesson_duration} timeframe
        - Engaging and interactive
        - Professionally formatted without markdown symbols
        
        Format the response as clean, professional text with clear section headings in ALL CAPS and proper bullet points using hyphens.
        """
        
        user_message = UserMessage(text=generation_prompt)
        response = await chat.send_message(user_message)
        
        # Create lesson plan object
        lesson_plan = LessonPlan(
            request_data=request,
            content=response
        )
        
        # Save to database
        await db.lesson_plans.insert_one(lesson_plan.dict())
        
        return lesson_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lesson plan: {str(e)}")

@api_router.get("/download-lesson-plan/{lesson_plan_id}")
async def download_lesson_plan(lesson_plan_id: str):
    """Download lesson plan as PDF"""
    try:
        # Get lesson plan from database
        lesson_plan_doc = await db.lesson_plans.find_one({"id": lesson_plan_id})
        if not lesson_plan_doc:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        lesson_plan = LessonPlan(**lesson_plan_doc)
        
        # Generate PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        generate_lesson_plan_pdf(lesson_plan, temp_pdf.name)
        
        # Return file
        filename = f"lesson_plan_{lesson_plan.request_data.subject_name}_{lesson_plan_id[:8]}.pdf"
        return FileResponse(
            temp_pdf.name,
            media_type="application/pdf",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()