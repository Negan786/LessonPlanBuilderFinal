import requests
import sys
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path

class AuthenticatedLessonPlanTester:
    def __init__(self, base_url="https://lecturepal-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_token = None
        self.user_data = None

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

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {'Authorization': f'Bearer {self.auth_token}'}
        return {}

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required:
            headers.update(self.get_auth_headers())
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if auth_required:
            print(f"   Auth: {'✅ Token present' if self.auth_token else '❌ No token'}")
        
        try:
            if method == 'GET':
                if auth_required:
                    headers.pop('Content-Type', None)  # Remove content-type for GET
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    headers.pop('Content-Type', None)  # Let requests set multipart boundary
                    response = requests.post(url, files=files, headers=headers, timeout=60)
                else:
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

    def test_user_signup(self):
        """Test user registration"""
        print("\n" + "="*50)
        print("TESTING USER AUTHENTICATION - SIGNUP")
        print("="*50)
        
        # Generate unique test user
        timestamp = datetime.now().strftime("%H%M%S")
        signup_data = {
            "firstName": "Test",
            "lastName": "User",
            "email": f"testuser_{timestamp}@example.com",
            "institution": "University of Canberra",
            "department": "Information Technology",
            "password": "TestPassword123!",
            "newsletter": False
        }
        
        success, response = self.run_test("User Signup", "POST", "auth/signup", 200, signup_data)
        
        if success:
            # Validate response structure
            required_fields = ['success', 'token', 'user']
            for field in required_fields:
                if field in response:
                    self.log_test(f"Signup Response - {field} present", True)
                else:
                    self.log_test(f"Signup Response - {field} present", False, f"Missing {field}")
            
            # Store auth token and user data
            if 'token' in response:
                self.auth_token = response['token']
                self.user_data = response.get('user', {})
                self.log_test("Auth Token Stored", True)
            else:
                self.log_test("Auth Token Stored", False, "No token in response")
            
            return response
        else:
            return None

    def test_user_login(self):
        """Test user login (alternative to signup)"""
        print("\n" + "="*50)
        print("TESTING USER AUTHENTICATION - LOGIN")
        print("="*50)
        
        if not self.user_data:
            self.log_test("User Login", False, "No user data from signup")
            return None
        
        login_data = {
            "email": self.user_data.get('email'),
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        
        if success:
            # Update auth token
            if 'token' in response:
                self.auth_token = response['token']
                self.log_test("Login Token Updated", True)
            
            return response
        else:
            return None

    def test_profile_access(self):
        """Test authenticated profile access"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATED PROFILE ACCESS")
        print("="*50)
        
        success, response = self.run_test("Get User Profile", "GET", "auth/profile", 200, auth_required=True)
        
        if success:
            # Validate profile data
            expected_fields = ['id', 'firstName', 'lastName', 'email', 'institution', 'department']
            for field in expected_fields:
                if field in response:
                    self.log_test(f"Profile - {field} present", True)
                else:
                    self.log_test(f"Profile - {field} present", False, f"Missing {field}")
        
        return success

    def create_sample_pdf(self):
        """Create a sample PDF for testing"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
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
            
            c.save()
            return temp_pdf.name
        except Exception as e:
            print(f"Failed to create sample PDF: {e}")
            return None

    def test_authenticated_pdf_upload(self):
        """Test PDF upload with authentication"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATED PDF UPLOAD")
        print("="*50)
        
        pdf_path = self.create_sample_pdf()
        if not pdf_path:
            self.log_test("Authenticated PDF Upload", False, "Could not create sample PDF")
            return None
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': ('test_outline.pdf', pdf_file, 'application/pdf')}
                success, response = self.run_test("Authenticated PDF Upload", "POST", "upload-pdf", 200, files=files, auth_required=True)
            
            if success:
                # Validate extraction response
                required_fields = ['id', 'filename', 'subject_names', 'lecture_topics', 'lecture_focus_mapping']
                for field in required_fields:
                    if field in response:
                        self.log_test(f"PDF Extraction - {field} present", True)
                    else:
                        self.log_test(f"PDF Extraction - {field} present", False, f"Missing {field}")
                
                return response
            else:
                return None
                
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

    def test_authenticated_lesson_plan_generation(self, extraction_data=None):
        """Test lesson plan generation with authentication"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATED LESSON PLAN GENERATION")
        print("="*50)
        
        if extraction_data:
            lesson_data = {
                "subject_name": extraction_data.get('subject_names', ['Test Subject'])[0],
                "lecture_topic": extraction_data.get('lecture_topics', ['Test Topic'])[0],
                "focus_topic": "",
                "blooms_taxonomy": "Apply",
                "aqf_level": "AQF Level 7 - Bachelor Degree",
                "lesson_duration": "1 hour"
            }
        else:
            lesson_data = {
                "subject_name": "Advanced Software Engineering",
                "lecture_topic": "Software Architecture Fundamentals",
                "focus_topic": "Architectural Patterns",
                "blooms_taxonomy": "Apply",
                "aqf_level": "AQF Level 7 - Bachelor Degree",
                "lesson_duration": "1 hour"
            }
        
        success, response = self.run_test("Authenticated Lesson Plan Generation", "POST", "generate-lesson-plan", 200, lesson_data, auth_required=True)
        
        if success:
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

    def test_authenticated_pdf_download(self, lesson_plan_data=None):
        """Test PDF download with authentication - MAIN FOCUS"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATED PDF DOWNLOAD - MAIN FOCUS")
        print("="*50)
        
        if not lesson_plan_data or 'id' not in lesson_plan_data:
            self.log_test("Authenticated PDF Download", False, "No lesson plan ID available")
            return
        
        lesson_plan_id = lesson_plan_data['id']
        
        try:
            url = f"{self.api_url}/download-lesson-plan/{lesson_plan_id}"
            headers = self.get_auth_headers()
            
            print(f"   Downloading PDF for lesson plan: {lesson_plan_id}")
            print(f"   Auth headers: {bool(headers)}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
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
                content_length = len(response.content)
                print(f"   PDF file size: {content_length} bytes")
                
                if content_length > 1000:
                    self.log_test("PDF Download - File Size", True)
                else:
                    self.log_test("PDF Download - File Size", False, f"PDF file too small: {content_length} bytes")
                
                # Check filename in headers
                content_disposition = response.headers.get('content-disposition', '')
                if 'filename=' in content_disposition:
                    self.log_test("PDF Download - Filename Header", True)
                else:
                    self.log_test("PDF Download - Filename Header", False, "No filename in content-disposition")
                
                # Try to save the PDF to verify it's valid
                try:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    temp_file.write(response.content)
                    temp_file.close()
                    
                    # Check if file exists and has content
                    if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                        self.log_test("PDF Download - File Validity", True)
                    else:
                        self.log_test("PDF Download - File Validity", False, "Downloaded file is empty or invalid")
                    
                    # Clean up
                    os.unlink(temp_file.name)
                    
                except Exception as e:
                    self.log_test("PDF Download - File Validity", False, f"Error saving PDF: {str(e)}")
                
            else:
                details = f"Expected 200, got {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', 'No error detail')}"
                    except:
                        details += f" - Response: {response.text[:200]}"
            
            self.log_test("Authenticated PDF Download", success, details)
            
        except Exception as e:
            self.log_test("Authenticated PDF Download", False, f"Error: {str(e)}")

    def test_unauthenticated_access(self):
        """Test that protected endpoints require authentication"""
        print("\n" + "="*50)
        print("TESTING UNAUTHENTICATED ACCESS (SHOULD FAIL)")
        print("="*50)
        
        # Temporarily remove auth token
        original_token = self.auth_token
        self.auth_token = None
        
        # Test endpoints that should require auth
        endpoints_to_test = [
            ("auth/profile", "GET"),
            ("upload-pdf", "POST"),
            ("generate-lesson-plan", "POST"),
        ]
        
        for endpoint, method in endpoints_to_test:
            success, response = self.run_test(f"Unauthenticated {endpoint}", method, endpoint, 401, auth_required=False)
            # For these tests, success means getting 401 (unauthorized)
            if not success:
                self.log_test(f"Security - {endpoint} requires auth", True)
            else:
                self.log_test(f"Security - {endpoint} requires auth", False, "Endpoint accessible without auth")
        
        # Restore auth token
        self.auth_token = original_token

    def run_all_tests(self):
        """Run all authentication-focused tests"""
        print("🚀 Starting Authenticated LLM Lesson Plan Builder Tests")
        print(f"Testing against: {self.base_url}")
        print("🎯 FOCUS: PDF Download with Authentication")
        
        # Test user signup and authentication
        signup_response = self.test_user_signup()
        if not signup_response:
            print("❌ Cannot proceed without authentication")
            return 1
        
        # Test profile access
        self.test_profile_access()
        
        # Test unauthenticated access (security check)
        self.test_unauthenticated_access()
        
        # Test authenticated PDF upload
        extraction_data = self.test_authenticated_pdf_upload()
        
        # Test authenticated lesson plan generation
        lesson_plan_data = self.test_authenticated_lesson_plan_generation(extraction_data)
        
        # Test authenticated PDF download - MAIN FOCUS
        self.test_authenticated_pdf_download(lesson_plan_data)
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Specific focus on PDF download
        pdf_download_tests = [result for result in self.test_results if 'PDF Download' in result['test_name']]
        pdf_success = sum(1 for test in pdf_download_tests if test['success'])
        pdf_total = len(pdf_download_tests)
        
        print(f"\n🎯 PDF DOWNLOAD FOCUS:")
        print(f"   PDF Download tests: {pdf_success}/{pdf_total}")
        
        if pdf_success == pdf_total and pdf_total > 0:
            print("✅ PDF Download functionality is working correctly!")
        else:
            print("❌ PDF Download functionality has issues!")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return 1

def main():
    tester = AuthenticatedLessonPlanTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())