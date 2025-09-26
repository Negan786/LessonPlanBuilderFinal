import requests
import sys
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path

class LessonPlanAPITester:
    def __init__(self, base_url="https://lecturepal-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=60)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers, timeout=60)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            details = ""
            
            if not success:
                details = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    details += f" - {error_detail}"
                except:
                    details += f" - Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            return success, response.json() if success and response.content else {}

        except requests.exceptions.Timeout:
            details = "Request timed out"
            self.log_test(name, False, details)
            return False, {}
        except Exception as e:
            details = f"Error: {str(e)}"
            self.log_test(name, False, details)
            return False, {}

    def create_sample_pdf(self):
        """Create a sample PDF for testing with clear lecture-focus mapping structure"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create temporary PDF file
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
            # Create PDF content with clear lecture-focus structure
            c = canvas.Canvas(temp_pdf.name, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Advanced Software Engineering - Unit Outline")
            
            # Subject information
            c.setFont("Helvetica", 12)
            y_pos = height - 100
            c.drawString(50, y_pos, "Subject: Advanced Software Engineering")
            y_pos -= 20
            c.drawString(50, y_pos, "Code: COMP3456")
            
            # Timetable of Activities section
            y_pos -= 40
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_pos, "Timetable of Activities")
            
            y_pos -= 30
            c.setFont("Helvetica", 11)
            
            # Week 1 - Software Architecture
            c.drawString(50, y_pos, "Week 1: Software Architecture Fundamentals")
            y_pos -= 15
            c.drawString(70, y_pos, "• Architectural Patterns")
            y_pos -= 15
            c.drawString(70, y_pos, "• Design Principles")
            y_pos -= 15
            c.drawString(70, y_pos, "• System Design")
            
            y_pos -= 25
            # Week 2 - Database Design
            c.drawString(50, y_pos, "Week 2: Database Design and Optimization")
            y_pos -= 15
            c.drawString(70, y_pos, "• Normalization Techniques")
            y_pos -= 15
            c.drawString(70, y_pos, "• Query Optimization")
            y_pos -= 15
            c.drawString(70, y_pos, "• Indexing Strategies")
            
            y_pos -= 25
            # Week 3 - Testing Methodologies
            c.drawString(50, y_pos, "Week 3: Testing Methodologies")
            y_pos -= 15
            c.drawString(70, y_pos, "• Unit Testing")
            y_pos -= 15
            c.drawString(70, y_pos, "• Integration Testing")
            y_pos -= 15
            c.drawString(70, y_pos, "• Test-Driven Development")
            
            y_pos -= 25
            # Week 4 - DevOps Practices (no specific focus topics)
            c.drawString(50, y_pos, "Week 4: DevOps Practices")
            y_pos -= 15
            c.drawString(70, y_pos, "General overview of DevOps methodologies")
            
            c.save()
            return temp_pdf.name
        except Exception as e:
            print(f"Failed to create sample PDF: {e}")
            return None

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n" + "="*50)
        print("TESTING BASIC ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test options endpoint
        success, response = self.run_test("Get Options", "GET", "options", 200)
        if success:
            required_keys = ['blooms_taxonomy', 'aqf_levels', 'lesson_durations']
            for key in required_keys:
                if key in response and isinstance(response[key], list) and len(response[key]) > 0:
                    self.log_test(f"Options - {key} populated", True)
                else:
                    self.log_test(f"Options - {key} populated", False, f"Missing or empty {key}")

    def test_pdf_upload_and_extraction(self):
        """Test PDF upload and extraction functionality with new lecture_focus_mapping"""
        print("\n" + "="*50)
        print("TESTING PDF UPLOAD & SMART FOCUS MAPPING")
        print("="*50)
        
        # Create sample PDF
        pdf_path = self.create_sample_pdf()
        if not pdf_path:
            self.log_test("PDF Upload", False, "Could not create sample PDF")
            return None
        
        try:
            # Test PDF upload
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': ('test_outline.pdf', pdf_file, 'application/pdf')}
                success, response = self.run_test("PDF Upload & Extraction", "POST", "upload-pdf", 200, files=files)
            
            if success:
                # Validate NEW extraction response structure
                required_fields = ['id', 'filename', 'subject_names', 'lecture_topics', 'lecture_focus_mapping']
                for field in required_fields:
                    if field in response:
                        self.log_test(f"Extraction - {field} present", True)
                    else:
                        self.log_test(f"Extraction - {field} present", False, f"Missing {field}")
                
                # Check if lists have content
                for list_field in ['subject_names', 'lecture_topics']:
                    if list_field in response and isinstance(response[list_field], list):
                        if len(response[list_field]) > 0:
                            self.log_test(f"Extraction - {list_field} has content", True)
                        else:
                            self.log_test(f"Extraction - {list_field} has content", False, f"Empty {list_field}")
                
                # NEW: Validate lecture_focus_mapping structure
                if 'lecture_focus_mapping' in response:
                    mapping = response['lecture_focus_mapping']
                    if isinstance(mapping, dict):
                        self.log_test("lecture_focus_mapping is dict", True)
                        
                        # Check if we have lecture topics as keys
                        if len(mapping) > 0:
                            self.log_test("lecture_focus_mapping has content", True)
                            
                            # Verify structure - each key should map to a list
                            valid_structure = True
                            for lecture_topic, focus_topics in mapping.items():
                                if not isinstance(focus_topics, list):
                                    valid_structure = False
                                    break
                            
                            self.log_test("lecture_focus_mapping has valid structure", valid_structure)
                            
                            # Print mapping for verification
                            print(f"\n📋 Extracted lecture_focus_mapping:")
                            for lecture, focuses in mapping.items():
                                print(f"   '{lecture}': {focuses}")
                                
                        else:
                            self.log_test("lecture_focus_mapping has content", False, "Empty mapping")
                    else:
                        self.log_test("lecture_focus_mapping is dict", False, f"Got {type(mapping)}")
                
                return response
            else:
                return None
                
        finally:
            # Clean up temporary file
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

    def test_lesson_plan_generation(self, extraction_data=None):
        """Test lesson plan generation with smart focus filtering"""
        print("\n" + "="*50)
        print("TESTING LESSON PLAN GENERATION WITH SMART FOCUS")
        print("="*50)
        
        if not extraction_data:
            # Use sample data if extraction failed
            lesson_data = {
                "subject_name": "Advanced Software Engineering",
                "lecture_topic": "Software Architecture Fundamentals",
                "focus_topic": "Architectural Patterns",
                "blooms_taxonomy": "Apply",
                "aqf_level": "AQF Level 7 - Bachelor Degree",
                "lesson_duration": "1 hour"
            }
            success, response = self.run_test("Generate Lesson Plan (Sample Data)", "POST", "generate-lesson-plan", 200, lesson_data)
        else:
            # Test with extracted data and smart focus mapping
            mapping = extraction_data.get('lecture_focus_mapping', {})
            
            # Test 1: Lesson plan with focus topic
            lecture_with_focus = None
            focus_topic = None
            for lecture, focuses in mapping.items():
                if focuses and len(focuses) > 0:
                    lecture_with_focus = lecture
                    focus_topic = focuses[0]
                    break
            
            if lecture_with_focus and focus_topic:
                lesson_data_with_focus = {
                    "subject_name": extraction_data.get('subject_names', ['Test Subject'])[0],
                    "lecture_topic": lecture_with_focus,
                    "focus_topic": focus_topic,
                    "blooms_taxonomy": "Apply",
                    "aqf_level": "AQF Level 7 - Bachelor Degree",
                    "lesson_duration": "1 hour"
                }
                
                success, response = self.run_test("Generate Lesson Plan (With Focus Topic)", "POST", "generate-lesson-plan", 200, lesson_data_with_focus)
                
                if success:
                    # Verify focus topic is mentioned in content
                    content = response.get('content', '')
                    if focus_topic.lower() in content.lower():
                        self.log_test("Lesson Plan - Focus topic mentioned in content", True)
                    else:
                        self.log_test("Lesson Plan - Focus topic mentioned in content", False, "Focus topic not found in content")
            
            # Test 2: Lesson plan without focus topic (empty focus_topic)
            lecture_without_focus = None
            for lecture, focuses in mapping.items():
                if not focuses or len(focuses) == 0:
                    lecture_without_focus = lecture
                    break
            
            if lecture_without_focus:
                lesson_data_no_focus = {
                    "subject_name": extraction_data.get('subject_names', ['Test Subject'])[0],
                    "lecture_topic": lecture_without_focus,
                    "focus_topic": "",  # Empty focus topic
                    "blooms_taxonomy": "Understand",
                    "aqf_level": "AQF Level 7 - Bachelor Degree",
                    "lesson_duration": "1 hour"
                }
                
                success, response = self.run_test("Generate Lesson Plan (No Focus Topic)", "POST", "generate-lesson-plan", 200, lesson_data_no_focus)
            
            # Use the first successful response for further testing
            if not response and extraction_data:
                # Fallback to first available lecture topic
                first_lecture = extraction_data.get('lecture_topics', ['Test Topic'])[0]
                lesson_data = {
                    "subject_name": extraction_data.get('subject_names', ['Test Subject'])[0],
                    "lecture_topic": first_lecture,
                    "focus_topic": "",
                    "blooms_taxonomy": "Apply",
                    "aqf_level": "AQF Level 7 - Bachelor Degree",
                    "lesson_duration": "1 hour"
                }
                success, response = self.run_test("Generate Lesson Plan (Fallback)", "POST", "generate-lesson-plan", 200, lesson_data)
        
        if success and response:
            # Validate lesson plan response
            required_fields = ['id', 'request_data', 'content', 'generated_at']
            for field in required_fields:
                if field in response:
                    self.log_test(f"Lesson Plan - {field} present", True)
                else:
                    self.log_test(f"Lesson Plan - {field} present", False, f"Missing {field}")
            
            # Check content length
            if 'content' in response and len(response['content']) > 100:
                self.log_test("Lesson Plan - Content substantial", True)
            else:
                self.log_test("Lesson Plan - Content substantial", False, "Content too short or missing")
            
            return response
        else:
            return None

    def test_pdf_download(self, lesson_plan_data=None):
        """Test PDF download functionality"""
        print("\n" + "="*50)
        print("TESTING PDF DOWNLOAD")
        print("="*50)
        
        if not lesson_plan_data or 'id' not in lesson_plan_data:
            self.log_test("PDF Download", False, "No lesson plan ID available")
            return
        
        lesson_plan_id = lesson_plan_data['id']
        
        try:
            url = f"{self.api_url}/download-lesson-plan/{lesson_plan_id}"
            response = requests.get(url, timeout=30)
            
            success = response.status_code == 200
            details = ""
            
            if success:
                # Check if response is PDF
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    self.log_test("PDF Download - Content Type", True)
                else:
                    self.log_test("PDF Download - Content Type", False, f"Expected PDF, got {content_type}")
                
                # Check content length
                if len(response.content) > 1000:
                    self.log_test("PDF Download - File Size", True)
                else:
                    self.log_test("PDF Download - File Size", False, "PDF file too small")
            else:
                details = f"Expected 200, got {response.status_code}"
            
            self.log_test("PDF Download", success, details)
            
        except Exception as e:
            self.log_test("PDF Download", False, f"Error: {str(e)}")

    def test_status_endpoints(self):
        """Test status check endpoints"""
        print("\n" + "="*50)
        print("TESTING STATUS ENDPOINTS")
        print("="*50)
        
        # Test create status
        status_data = {"client_name": "test_client"}
        success, response = self.run_test("Create Status Check", "POST", "status", 200, status_data)
        
        # Test get status
        self.run_test("Get Status Checks", "GET", "status", 200)

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting LLM Lesson Plan Builder API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Test basic endpoints
        self.test_basic_endpoints()
        
        # Test PDF upload and extraction
        extraction_data = self.test_pdf_upload_and_extraction()
        
        # Test lesson plan generation
        lesson_plan_data = self.test_lesson_plan_generation(extraction_data)
        
        # Test PDF download
        self.test_pdf_download(lesson_plan_data)
        
        # Test status endpoints
        self.test_status_endpoints()
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return 1

def main():
    tester = LessonPlanAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())