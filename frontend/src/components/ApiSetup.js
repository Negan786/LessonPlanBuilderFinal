import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Alert, AlertDescription } from "./ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { GraduationCap, Key, ExternalLink, Copy, CheckCircle, AlertCircle, ArrowRight, Info, Globe } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ApiSetup = () => {
  const navigate = useNavigate();
  const [apiKey, setApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [copied, setCopied] = useState(false);

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const validateApiKey = async () => {
    if (!apiKey.trim()) {
      setError("Please enter your Gemini API key");
      return;
    }

    setIsValidating(true);
    setError("");
    setSuccess("");

    try {
      const response = await axios.post(`${API}/auth/validate-api-key`, {
        apiKey: apiKey.trim()
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.data.success) {
        setSuccess("API key validated successfully!");
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      }
    } catch (error) {
      console.error('API key validation error:', error);
      setError(error.response?.data?.detail || "Invalid API key. Please check your key and try again.");
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateApiKey();
  };

  const handleSkip = () => {
    // Continue with a demo/limited mode (using system API key)
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="w-full max-w-4xl">
        <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur">
          <CardHeader className="text-center pb-8">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <GraduationCap className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-slate-800">AI Lesson Planner</h1>
            </div>
            <CardTitle className="text-3xl text-slate-900">API Key Setup</CardTitle>
            <CardDescription className="text-slate-600 mt-2">
              Welcome {user.firstName}! Configure your Gemini API key to get started with AI-powered lesson planning.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-8">
            <Tabs defaultValue="setup" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="setup">Setup API Key</TabsTrigger>
                <TabsTrigger value="instructions">How to Get API Key</TabsTrigger>
              </TabsList>

              <TabsContent value="setup" className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <div className="flex items-start space-x-3">
                    <Info className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold text-blue-900 mb-2">Why do I need my own API key?</h3>
                      <ul className="text-blue-800 text-sm space-y-1">
                        <li>• Control your own usage and costs</li>
                        <li>• Higher rate limits for better performance</li>
                        <li>• Direct access to latest Gemini AI features</li>
                        <li>• Your data stays secure with your own credentials</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  {error && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  {success && (
                    <Alert className="border-green-200 bg-green-50">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-800">{success}</AlertDescription>
                    </Alert>
                  )}

                  <div className="space-y-3">
                    <Label htmlFor="apiKey" className="flex items-center space-x-2 text-base">
                      <Key className="w-5 h-5 text-slate-600" />
                      <span>Gemini API Key</span>
                    </Label>
                    <Input
                      id="apiKey"
                      type="password"
                      placeholder="Enter your Gemini API key (e.g., AIzaSyC...)"
                      value={apiKey}
                      onChange={(e) => {
                        setApiKey(e.target.value);
                        setError("");
                        setSuccess("");
                      }}
                      className="h-12 font-mono text-sm"
                      data-testid="api-key-input"
                    />
                    <p className="text-sm text-slate-600">
                      Your API key will be securely stored and used only for your lesson plan generation.
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button
                      type="submit"
                      className="flex-1 h-12"
                      disabled={isValidating || !apiKey.trim()}
                      data-testid="validate-api-key-btn"
                    >
                      {isValidating ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Validating...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="w-5 h-5" />
                          <span>Validate & Continue</span>
                        </div>
                      )}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleSkip}
                      className="h-12"
                      data-testid="skip-api-key-btn"
                    >
                      Skip for Now
                    </Button>
                  </div>

                  <div className="text-center">
                    <p className="text-sm text-slate-500">
                      Don't have an API key yet?{" "}
                      <button 
                        type="button"
                        onClick={() => document.querySelector('[data-value="instructions"]').click()}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Learn how to get one →
                      </button>
                    </p>
                  </div>
                </form>
              </TabsContent>

              <TabsContent value="instructions" className="space-y-6">
                <div className="space-y-8">
                  <div>
                    <h3 className="text-xl font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                      <Globe className="w-6 h-6 text-blue-600" />
                      <span>How to Get Your Free Gemini API Key</span>
                    </h3>
                    <p className="text-slate-600 mb-6">
                      Follow these simple steps to get your free Gemini API key from Google AI Studio:
                    </p>
                  </div>

                  <div className="space-y-6">
                    {[
                      {
                        step: 1,
                        title: "Visit Google AI Studio",
                        description: "Go to Google AI Studio to access the Gemini API",
                        link: "https://aistudio.google.com/",
                        linkText: "Open Google AI Studio"
                      },
                      {
                        step: 2,
                        title: "Sign in with Google Account",
                        description: "Use your existing Google account or create a new one if needed"
                      },
                      {
                        step: 3,
                        title: "Get API Key",
                        description: "Click 'Get API key' button in the top navigation bar"
                      },
                      {
                        step: 4,
                        title: "Create New Key",
                        description: "Select 'Create API key in new project' or use an existing project"
                      },
                      {
                        step: 5,
                        title: "Copy Your Key", 
                        description: "Copy the generated API key (it will look like: AIzaSyC...)"
                      },
                      {
                        step: 6,
                        title: "Paste Here",
                        description: "Return to this page and paste your API key in the setup tab"
                      }
                    ].map((item) => (
                      <div key={item.step} className="flex items-start space-x-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">
                          {item.step}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-900 mb-1">{item.title}</h4>
                          <p className="text-slate-600 text-sm mb-2">{item.description}</p>
                          {item.link && (
                            <a
                              href={item.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                            >
                              <span>{item.linkText}</span>
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-6 h-6 text-amber-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <h4 className="font-semibold text-amber-900 mb-2">Important Notes:</h4>
                        <ul className="text-amber-800 text-sm space-y-1">
                          <li>• The Gemini API offers generous free usage limits</li>
                          <li>• Keep your API key secure and don't share it publicly</li>
                          <li>• You can always change your API key later in settings</li>
                          <li>• If you skip this step, you can use our demo mode with limited features</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center">
                    <Button
                      onClick={() => document.querySelector('[data-value="setup"]').click()}
                      className="flex items-center space-x-2"
                    >
                      <ArrowRight className="w-5 h-5" />
                      <span>Got it! Let me set up my API key</span>
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ApiSetup;