import React, { useState } from 'react';
import UnityModel3DViewer from './UnityModel3DViewer';
import { Maximize2, Minimize2, Info } from 'lucide-react';

const LandingView = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleExpandToggle = () => {
    setIsExpanded(!isExpanded);
  };

  const handleExpandChange = (expanded) => {
    setIsExpanded(expanded);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Varma Point Intelligence System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Advanced hybrid retrieval system combining lexical matching, semantic understanding,
            and biomedical intelligence for precise Varma point identification
          </p>
        </div>

        {/* Main 3D Model */}
        <div className="mb-8 animate-slide-up">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800">
              Interactive 3D Human Model
            </h2>
            <button
              onClick={handleExpandToggle}
              className="flex items-center px-4 py-2 bg-varma-primary text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
            >
              {isExpanded ? (
                <>
                  <Minimize2 className="w-5 h-5 mr-2" />
                  Exit Fullscreen
                </>
              ) : (
                <>
                  <Maximize2 className="w-5 h-5 mr-2" />
                  Explore Fullscreen
                </>
              )}
            </button>
          </div>
          
          <UnityModel3DViewer 
            isExpanded={isExpanded} 
            onExpandChange={handleExpandChange}
          />
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Info className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Lexical Matching
            </h3>
            <p className="text-gray-600">
              Fast and interpretable matches using keyword extraction, fuzzy similarity,
              and character-level matching for exact symptom terms.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Info className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Semantic Understanding
            </h3>
            <p className="text-gray-600">
              PubMedBERT-powered semantic expansion identifies related symptoms
              even when exact wording differs, with lexical verification.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Info className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              RAG-Powered Insights
            </h3>
            <p className="text-gray-600">
              Get grounded, explainable answers about Varma points through
              our advanced Retrieval-Augmented Generation pipeline.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingView;