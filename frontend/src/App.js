import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

// Shadcn UI Components
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Label } from "./components/ui/label";
import { Progress } from "./components/ui/progress";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Separator } from "./components/ui/separator";
import { Badge } from "./components/ui/badge";

// Lucide Icons
import { Upload, FileText, Download, BookOpen, Clock, GraduationCap, Lightbulb, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LessonPlanBuilder = () => {
  // State management
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [options, setOptions] = useState({
    blooms_taxonomy: [],
    aqf_levels: [],
    lesson_durations: []
  });
  const [formData, setFormData] = useState({
    subject_name: "",
    lecture_topic: "",
    focus_topic: "",
    blooms_taxonomy: "",
    aqf_level: "",
    lesson_duration: ""
  });
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  // Load standard options on component mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await axios.get(`${API}/options`);
        setOptions(response.data);
      } catch (error) {
        setError("Failed to load options");
      }
    };
    fetchOptions();
  }, []);

  // File upload handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError("Please select a PDF file");
      return;
    }

    setIsUploading(true);
    setError("");
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setUploadedFile(file);
      setExtractedData(response.data);
      setCurrentStep(2);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to upload and process PDF");
    } finally {
      setIsUploading(false);
    }
  };

  // Helper function to get focus topics for selected lecture topic
  const getFocusTopicsForLecture = () => {
    if (!extractedData || !formData.lecture_topic) {
      return [];
    }
    return extractedData.lecture_focus_mapping[formData.lecture_topic] || [];
  };

  // Form handlers
  const handleFormChange = (field, value) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // Reset focus topic when lecture topic changes
      if (field === 'lecture_topic') {
        newData.focus_topic = "";
      }
      
      return newData;
    });
  };

  const isFormValid = () => {
    const requiredFields = ['subject_name', 'lecture_topic', 'blooms_taxonomy', 'aqf_level', 'lesson_duration'];
    const basicFieldsValid = requiredFields.every(field => formData[field] !== "");
    
    // Focus topic is optional, but if there are focus topics available for the lecture, user should select one
    const focusTopicsAvailable = getFocusTopicsForLecture();
    const focusTopicValid = focusTopicsAvailable.length === 0 || formData.focus_topic !== "";
    
    return basicFieldsValid && focusTopicValid;
  };

  const handleGeneratePlan = async () => {
    if (!isFormValid()) {
      setError("Please fill in all required fields");
      return;
    }

    setIsGenerating(true);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-lesson-plan`, formData);
      setGeneratedPlan(response.data);
      setCurrentStep(3);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to generate lesson plan");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!generatedPlan) return;

    try {
      const response = await axios.get(`${API}/download-lesson-plan/${generatedPlan.id}`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `lesson_plan_${generatedPlan.request_data.subject_name}_${generatedPlan.id.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError("Failed to download PDF");
    }
  };

  const resetForm = () => {
    setCurrentStep(1);
    setUploadedFile(null);
    setExtractedData(null);
    setFormData({
      subject_name: "",
      lecture_topic: "",
      focus_topic: "",
      blooms_taxonomy: "",
      aqf_level: "",
      lesson_duration: ""
    });
    setGeneratedPlan(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <div className="flex items-center justify-center gap-3 mb-2">
                <GraduationCap className="w-8 h-8 text-blue-600" />
                <h1 className="text-3xl font-bold text-slate-800">LLM Powered Lesson Plan Builder</h1>
              </div>
              <p className="text-slate-600">University of Canberra - Master of Information Technology and Systems</p>
            </div>
          </div>
          
          {/* Progress indicator */}
          <div className="mt-6">
            <div className="flex items-center justify-center space-x-8">
              <div className={`flex items-center gap-2 ${currentStep >= 1 ? 'text-blue-600' : 'text-slate-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-slate-200'}`}>
                  {currentStep > 1 ? <CheckCircle className="w-5 h-5" /> : '1'}
                </div>
                <span className="font-medium">Upload PDF</span>
              </div>
              <div className="w-16 h-0.5 bg-slate-200">
                <div className={`h-full bg-blue-600 transition-all duration-300 ${currentStep >= 2 ? 'w-full' : 'w-0'}`} />
              </div>
              <div className={`flex items-center gap-2 ${currentStep >= 2 ? 'text-blue-600' : 'text-slate-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-slate-200'}`}>
                  {currentStep > 2 ? <CheckCircle className="w-5 h-5" /> : '2'}
                </div>
                <span className="font-medium">Configure Plan</span>
              </div>
              <div className="w-16 h-0.5 bg-slate-200">
                <div className={`h-full bg-blue-600 transition-all duration-300 ${currentStep >= 3 ? 'w-full' : 'w-0'}`} />
              </div>
              <div className={`flex items-center gap-2 ${currentStep >= 3 ? 'text-blue-600' : 'text-slate-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 3 ? 'bg-blue-600 text-white' : 'bg-slate-200'}`}>
                  {currentStep >= 3 ? <CheckCircle className="w-5 h-5" /> : '3'}
                </div>
                <span className="font-medium">Generated Plan</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Form */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                Create Your Lesson Plan
              </CardTitle>
              <CardDescription>
                Upload a unit outline, verify the details, and generate a lesson plan with AI.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Error Alert */}
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Step 1: PDF Upload */}
              {currentStep === 1 && (
                <div className="space-y-4">
                  <Label className="text-base font-medium">Unit Outline PDF</Label>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      dragActive
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-slate-300 hover:border-slate-400'
                    } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <div className="flex flex-col items-center gap-4">
                      {isUploading ? (
                        <>
                          <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                          <p className="text-lg font-medium text-slate-600">Processing PDF...</p>
                          <p className="text-sm text-slate-500">Extracting subject information using AI</p>
                        </>
                      ) : (
                        <>
                          <Upload className="w-12 h-12 text-slate-400" />
                          <div>
                            <p className="text-lg font-medium text-slate-600">Upload a PDF file</p>
                            <p className="text-sm text-slate-500">Drag and drop or click to upload</p>
                            <p className="text-xs text-slate-400 mt-2">Supports text-based PDFs with subject outlines containing timetable of activities</p>
                          </div>
                          <Button variant="outline" asChild>
                            <label>
                              <input
                                type="file"
                                accept=".pdf"
                                className="hidden"
                                onChange={handleFileSelect}
                              />
                              Choose File
                            </label>
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Form Configuration */}
              {currentStep === 2 && extractedData && (
                <div className="space-y-6">
                  {/* Extracted data summary */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-medium text-green-800">PDF Processed Successfully</span>
                    </div>
                    <p className="text-sm text-green-600">
                      Extracted {extractedData.subject_names.length} subject(s), 
                      {extractedData.lecture_topics.length} lecture topic(s), 
                      and {Object.keys(extractedData.lecture_focus_mapping).length} lecture-focus mappings
                    </p>
                  </div>

                  {/* Form fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="subject_name">Subject Name</Label>
                      <Select value={formData.subject_name} onValueChange={(value) => handleFormChange('subject_name', value)}>
                        <SelectTrigger data-testid="subject-select">
                          <SelectValue placeholder="Select subject" />
                        </SelectTrigger>
                        <SelectContent>
                          {extractedData.subject_names.map((subject, index) => (
                            <SelectItem key={index} value={subject}>{subject}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="lesson_duration">Lesson Duration</Label>
                      <Select value={formData.lesson_duration} onValueChange={(value) => handleFormChange('lesson_duration', value)}>
                        <SelectTrigger data-testid="duration-select">
                          <SelectValue placeholder="Select duration" />
                        </SelectTrigger>
                        <SelectContent>
                          {options.lesson_durations.map((duration, index) => (
                            <SelectItem key={index} value={duration}>{duration}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="lecture_topic">Lecture Content</Label>
                      <Select value={formData.lecture_topic} onValueChange={(value) => handleFormChange('lecture_topic', value)}>
                        <SelectTrigger data-testid="lecture-select">
                          <SelectValue placeholder="Select lecture content" />
                        </SelectTrigger>
                        <SelectContent>
                          {extractedData.lecture_topics.map((topic, index) => (
                            <SelectItem key={index} value={topic}>{topic}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="focus_topic">Focus Topic</Label>
                      <Select 
                        value={formData.focus_topic} 
                        onValueChange={(value) => handleFormChange('focus_topic', value)}
                        disabled={!formData.lecture_topic}
                      >
                        <SelectTrigger data-testid="focus-select">
                          <SelectValue 
                            placeholder={
                              !formData.lecture_topic 
                                ? "Select lecture content first" 
                                : getFocusTopicsForLecture().length === 0
                                  ? "No focus topics available"
                                  : "Select focus topic"
                            } 
                          />
                        </SelectTrigger>
                        <SelectContent>
                          {getFocusTopicsForLecture().map((topic, index) => (
                            <SelectItem key={index} value={topic}>{topic}</SelectItem>
                          ))}
                          {getFocusTopicsForLecture().length === 0 && formData.lecture_topic && (
                            <SelectItem value="general" disabled>No specific focus topics found</SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                      {formData.lecture_topic && getFocusTopicsForLecture().length === 0 && (
                        <p className="text-xs text-amber-600">
                          No specific focus topics found for this lecture. You can proceed without selecting a focus topic.
                        </p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="blooms_taxonomy">Bloom's Taxonomy Level</Label>
                      <Select value={formData.blooms_taxonomy} onValueChange={(value) => handleFormChange('blooms_taxonomy', value)}>
                        <SelectTrigger data-testid="blooms-select">
                          <SelectValue placeholder="Select level" />
                        </SelectTrigger>
                        <SelectContent>
                          {options.blooms_taxonomy.map((level, index) => (
                            <SelectItem key={index} value={level}>{level}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="aqf_level">AQF Level</Label>
                      <Select value={formData.aqf_level} onValueChange={(value) => handleFormChange('aqf_level', value)}>
                        <SelectTrigger data-testid="aqf-select">
                          <SelectValue placeholder="Select AQF level" />
                        </SelectTrigger>
                        <SelectContent>
                          {options.aqf_levels.map((level, index) => (
                            <SelectItem key={index} value={level}>{level}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button variant="outline" onClick={resetForm} className="flex-1">
                      Start Over
                    </Button>
                    <Button 
                      onClick={handleGeneratePlan} 
                      disabled={!isFormValid() || isGenerating}
                      className="flex-1"
                      data-testid="generate-plan-btn"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Lightbulb className="w-4 h-4 mr-2" />
                          Generate Lesson Plan
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}

              {/* Step 3: Success */}
              {currentStep === 3 && generatedPlan && (
                <div className="space-y-4 text-center">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-green-800 mb-2">Lesson Plan Generated!</h3>
                    <p className="text-green-600">Your AI-powered lesson plan is ready for download.</p>
                  </div>
                  
                  <div className="flex gap-3">
                    <Button variant="outline" onClick={resetForm} className="flex-1">
                      Create Another Plan
                    </Button>
                    <Button onClick={handleDownloadPDF} className="flex-1" data-testid="download-pdf-btn">
                      <Download className="w-4 h-4 mr-2" />
                      Download PDF
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Right Panel - Generated Plan Preview */}
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Generated Plan
              </CardTitle>
              <CardDescription>
                {generatedPlan ? "Your AI-crafted lesson plan will appear here." : "Generate a plan to see it displayed here."}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!generatedPlan ? (
                <div className="text-center py-12">
                  <FileText className="w-24 h-24 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-500 text-lg mb-2">Generate a plan to see it displayed here.</p>
                  <p className="text-slate-400">Upload a PDF and complete the form to get started.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Plan metadata */}
                  <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-600">Subject:</span>
                        <p className="font-medium">{generatedPlan.request_data.subject_name}</p>
                      </div>
                      <div>
                        <span className="text-slate-600">Duration:</span>
                        <p className="font-medium">{generatedPlan.request_data.lesson_duration}</p>
                      </div>
                      <div>
                        <span className="text-slate-600">Lecture Topic:</span>
                        <p className="font-medium">{generatedPlan.request_data.lecture_topic}</p>
                      </div>
                      <div>
                        <span className="text-slate-600">Focus:</span>
                        <p className="font-medium">{generatedPlan.request_data.focus_topic}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant="secondary">{generatedPlan.request_data.blooms_taxonomy}</Badge>
                      <Badge variant="outline">{generatedPlan.request_data.aqf_level}</Badge>
                    </div>
                  </div>

                  <Separator />

                  {/* Plan content preview */}
                  <div className="space-y-4">
                    <h4 className="font-semibold">Lesson Plan Content</h4>
                    <div className="bg-white border rounded-lg p-6 max-h-96 overflow-y-auto">
                      <div className="space-y-4">
                        {generatedPlan.content.split('\n\n').map((section, index) => {
                          const trimmedSection = section.trim();
                          if (!trimmedSection) return null;
                          
                          // Check if this is a heading (ALL CAPS words)
                          const isHeading = /^[A-Z\s]+(?:\([^)]*\))?$/.test(trimmedSection.split('\n')[0]) && 
                                          trimmedSection.split('\n')[0].length < 100;
                          
                          if (isHeading) {
                            return (
                              <div key={index} className="border-b border-slate-200 pb-2">
                                <h5 className="text-lg font-bold text-slate-800 mb-2">
                                  {trimmedSection.split('\n')[0]}
                                </h5>
                                {trimmedSection.split('\n').slice(1).map((line, lineIndex) => {
                                  const cleanLine = line.trim();
                                  if (!cleanLine) return null;
                                  return (
                                    <p key={lineIndex} className="text-slate-700 ml-4 mb-1">
                                      {cleanLine}
                                    </p>
                                  );
                                })}
                              </div>
                            );
                          } else {
                            // Regular content
                            return (
                              <div key={index} className="text-slate-700">
                                {trimmedSection.split('\n').map((line, lineIndex) => {
                                  const cleanLine = line.trim();
                                  if (!cleanLine) return null;
                                  
                                  // Check if it's a bullet point
                                  if (cleanLine.startsWith('- ')) {
                                    return (
                                      <div key={lineIndex} className="flex items-start mb-2">
                                        <span className="text-blue-600 mr-2 mt-1.5 flex-shrink-0">•</span>
                                        <span className="text-slate-700">{cleanLine.substring(2)}</span>
                                      </div>
                                    );
                                  } else {
                                    // Regular paragraph
                                    return (
                                      <p key={lineIndex} className="mb-2 text-slate-700">
                                        {cleanLine}
                                      </p>
                                    );
                                  }
                                })}
                              </div>
                            );
                          }
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <LessonPlanBuilder />
    </div>
  );
}

export default App;