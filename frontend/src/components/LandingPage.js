import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { GraduationCap, Brain, Search, Database, Download, Shield, Globe, ChartLine, Users, Laptop, CheckCircle } from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-b border-slate-200 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <GraduationCap className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-slate-800">AI Lesson Planner</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button onClick={() => scrollToSection('home')} className="text-slate-600 hover:text-blue-600 transition-colors">
                Home
              </button>
              <button onClick={() => scrollToSection('about')} className="text-slate-600 hover:text-blue-600 transition-colors">
                About
              </button>
              <button onClick={() => scrollToSection('features')} className="text-slate-600 hover:text-blue-600 transition-colors">
                Features
              </button>
              <button onClick={() => scrollToSection('contact')} className="text-slate-600 hover:text-blue-600 transition-colors">
                Contact
              </button>
              <div className="flex items-center space-x-4 ml-8">
                <Button variant="outline" onClick={() => navigate('/login')} data-testid="nav-login-btn">
                  Login
                </Button>
                <Button onClick={() => navigate('/signup')} data-testid="nav-signup-btn">
                  Sign Up
                </Button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="pt-20 pb-16 bg-gradient-to-br from-blue-50 to-slate-50">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                AI-Powered Lesson Plan Generator
              </h1>
              <p className="text-xl text-slate-600 leading-relaxed">
                Transform your teaching with intelligent lesson planning designed specifically for University of Canberra's Master of Information Technology and Systems program
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg" 
                  className="text-lg px-8 py-4"
                  onClick={() => navigate('/login')}
                  data-testid="hero-get-started-btn"
                >
                  Get Started
                </Button>
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="text-lg px-8 py-4"
                  onClick={() => scrollToSection('about')}
                >
                  Learn More
                </Button>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="relative">
                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
                    <Brain className="w-12 h-12 text-blue-600 mb-4" />
                    <h3 className="font-semibold text-slate-800">AI-Powered</h3>
                    <p className="text-slate-600 text-sm">Advanced algorithms</p>
                  </div>
                  <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200 mt-8">
                    <GraduationCap className="w-12 h-12 text-green-600 mb-4" />
                    <h3 className="font-semibold text-slate-800">UC Aligned</h3>
                    <p className="text-slate-600 text-sm">University standards</p>
                  </div>
                  <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200 -mt-4">
                    <ChartLine className="w-12 h-12 text-purple-600 mb-4" />
                    <h3 className="font-semibold text-slate-800">Quality Assured</h3>
                    <p className="text-slate-600 text-sm">AQF Level 9 compliant</p>
                  </div>
                  <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200 mt-4">
                    <Laptop className="w-12 h-12 text-orange-600 mb-4" />
                    <h3 className="font-semibold text-slate-800">Easy to Use</h3>
                    <p className="text-slate-600 text-sm">Intuitive interface</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">About Our Platform</h2>
            <p className="text-xl text-slate-600">Revolutionizing IT education through intelligent lesson planning</p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold text-slate-900 mb-4">Addressing the Challenge</h3>
                <p className="text-slate-600 leading-relaxed">
                  The current Information Technology Education landscape faces significant challenges in curriculum delivery and lesson plan development. Educators in IT programs, especially at the graduate level, face critical challenges like time constraints and resource limitations when creating comprehensive and industry-aligned curriculum.
                </p>
              </div>
              
              <div>
                <h3 className="text-2xl font-semibold text-slate-900 mb-4">Our Solution</h3>
                <p className="text-slate-600 leading-relaxed">
                  This project develops an AI-driven Web Application that leverages Large Language Models (LLM) and Retrieval-Augmented Generation (RAG) technology for building comprehensive lesson plans for IT education at graduate level, specifically targeting the University of Canberra's Master of Information Technology and Systems Program.
                </p>
              </div>
            </div>
            
            <div className="bg-slate-50 rounded-2xl p-8">
              <div className="grid grid-cols-3 gap-8 text-center">
                <div>
                  <div className="text-3xl font-bold text-blue-600 mb-2">60-70%</div>
                  <p className="text-slate-600 text-sm">Reduction in preparation time</p>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-600 mb-2">2-3 min</div>
                  <p className="text-slate-600 text-sm">Complete lesson plan generation</p>
                </div>
                <div>
                  <div className="text-3xl font-bold text-purple-600 mb-2">3 Units</div>
                  <p className="text-slate-600 text-sm">Semester 1, Year 1 coverage</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Key Features</h2>
            <p className="text-xl text-slate-600">Everything you need for comprehensive lesson planning</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <Search className="w-12 h-12 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">RAG-based Content Generation</h3>
              <p className="text-slate-600 leading-relaxed">Sophisticated retrieval system that searches curated educational content databases to provide context for LLM-powered lesson plan generation.</p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <Globe className="w-12 h-12 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Responsive Web Interface</h3>
              <p className="text-slate-600 leading-relaxed">User-friendly web application enabling educators to specify subjects, topics, learning objectives, and assessment preferences.</p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <Database className="w-12 h-12 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Content Database Management</h3>
              <p className="text-slate-600 leading-relaxed">Comprehensive database consisting of lesson plan examples, curriculum standards, and best teaching practices in IT education.</p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <FileExport className="w-12 h-12 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Document Export</h3>
              <p className="text-slate-600 leading-relaxed">Generate and export lesson plans in PDF and Word formats for easy sharing and implementation.</p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <Shield className="w-12 h-12 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Quality Assurance</h3>
              <p className="text-slate-600 leading-relaxed">Content validation system ensuring generated lesson plans meet educational standards (AQF, ACS, SFIA).</p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="mb-6">
                <GraduationCap className="w-12 h-12 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">MITS Program Focus</h3>
              <p className="text-slate-600 leading-relaxed">Specifically designed for Introduction to IT, Data Science, and Statistics courses in Semester 1, Year 1.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Transform Your Teaching?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join educators who are already saving 60-70% of their lesson planning time with our AI-powered platform
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary" 
              className="text-lg px-8 py-4"
              onClick={() => navigate('/signup')}
              data-testid="cta-signup-btn"
            >
              Start Free Trial
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-blue-600"
              onClick={() => navigate('/login')}
            >
              Login to Account
            </Button>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Contact Us</h2>
            <p className="text-xl text-slate-600">Get in touch with our team</p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            <div className="space-y-8">
              <div className="flex items-start space-x-4">
                <GraduationCap className="w-8 h-8 text-blue-600 mt-1" />
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">University of Canberra</h3>
                  <p className="text-slate-600">
                    Faculty of Science and Technology<br />
                    Master of Information Technology and Systems Program
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <Users className="w-8 h-8 text-green-600 mt-1" />
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">Email Support</h3>
                  <p className="text-slate-600">support@lessonplanner.uc.edu.au</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <ChartLine className="w-8 h-8 text-purple-600 mt-1" />
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">Phone Support</h3>
                  <p className="text-slate-600">+61 2 6201 5111</p>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-50 rounded-2xl p-8">
              <form className="space-y-6">
                <div>
                  <input 
                    type="text" 
                    placeholder="Your Name" 
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required 
                  />
                </div>
                <div>
                  <input 
                    type="email" 
                    placeholder="Your Email" 
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required 
                  />
                </div>
                <div>
                  <textarea 
                    placeholder="Your Message" 
                    rows="5" 
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <Button className="w-full" size="lg">
                  Send Message
                </Button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <GraduationCap className="w-8 h-8 text-blue-400" />
                <span className="text-xl font-bold">AI Lesson Planner</span>
              </div>
              <p className="text-slate-400">
                Transforming IT education through intelligent lesson planning at the University of Canberra.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li><button onClick={() => scrollToSection('home')} className="text-slate-400 hover:text-white transition-colors">Home</button></li>
                <li><button onClick={() => scrollToSection('about')} className="text-slate-400 hover:text-white transition-colors">About</button></li>
                <li><button onClick={() => scrollToSection('features')} className="text-slate-400 hover:text-white transition-colors">Features</button></li>
                <li><button onClick={() => navigate('/login')} className="text-slate-400 hover:text-white transition-colors">Login</button></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Documentation</a></li>
                <li><button onClick={() => scrollToSection('contact')} className="text-slate-400 hover:text-white transition-colors">Contact</button></li>
                <li><a href="#" className="text-slate-400 hover:text-white transition-colors">Privacy Policy</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Connect</h3>
              <div className="flex space-x-4">
                <a href="#" className="text-slate-400 hover:text-white transition-colors">
                  <Users className="w-5 h-5" />
                </a>
                <a href="#" className="text-slate-400 hover:text-white transition-colors">
                  <ChartLine className="w-5 h-5" />
                </a>
                <a href="#" className="text-slate-400 hover:text-white transition-colors">
                  <GraduationCap className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
          
          <div className="border-t border-slate-800 mt-12 pt-8 text-center">
            <p className="text-slate-400">
              &copy; 2024 University of Canberra - Faculty of Science and Technology. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;