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
            Varma Point Identification and Visualization System
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
      </div>
    </div>
  );
};

export default LandingView;