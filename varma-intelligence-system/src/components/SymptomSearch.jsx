import React, { useState } from 'react';
import { Search, AlertCircle, Loader, X, Maximize2 } from 'lucide-react';
import UnityModel3DViewer from './UnityModel3DViewer';
import LoadingSpinner from './LoadingSpinner';
import varmaService from '../services/varmaService';
import { CONFIDENCE_LEVELS } from '../utils/constants';

const SymptomSearch = () => {
  const [symptomQuery, setSymptomQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [highlightedPoints, setHighlightedPoints] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [isModelExpanded, setIsModelExpanded] = useState(false);

  const getConfidenceLevel = (score) => {
    if (score >= CONFIDENCE_LEVELS.HIGH.min) return CONFIDENCE_LEVELS.HIGH;
    if (score >= CONFIDENCE_LEVELS.MEDIUM.min) return CONFIDENCE_LEVELS.MEDIUM;
    return CONFIDENCE_LEVELS.LOW;
  };

  const handleSearch = () => {
    if (!symptomQuery.trim()) {
      setError('Please enter a symptom');
      return;
    }

    setIsSearching(true);
    setError(null);
    setResults(null);
    setSelectedPoint(null);
    setHighlightedPoints([]);
    setIsModelExpanded(false);

    varmaService.searchBySymptom(symptomQuery)
      .then(response => {
        console.log('API Response:', response);
        setResults(response);

        if (response.varma_points && response.varma_points.length > 0) {
          const pointsToHighlight = response.varma_points.map(point => ({
            name: point.name,
            unity_name: point.unity_name || point.name,
            id: point.id
          }));
          setHighlightedPoints(pointsToHighlight);
          console.log('Points to highlight:', pointsToHighlight);
        }
      })
      .catch(err => {
        console.error('Full error:', err);
        setError(err.message || 'An error occurred during search');
      })
      .finally(() => {
        setIsSearching(false);
      });
  };

  const clearSearch = () => {
    setSymptomQuery('');
    setResults(null);
    setError(null);
    setHighlightedPoints([]);
    setSelectedPoint(null);
    setIsModelExpanded(false);
  };

  const handlePointClick = (point) => {
    setSelectedPoint(point);
  };

  const commonSymptoms = [
    'Headache',
    'Joint pain',
    'Back pain',
    'Neck stiffness',
    'Fatigue',
    'Dizziness',
    'Muscle tension',
    'Shoulder pain'
  ];

  const toggleModelExpansion = () => {
    setIsModelExpanded(!isModelExpanded);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-3">
            Symptom to Varma Point Mapping
          </h2>
          <p className="text-lg text-gray-600">
            Enter your symptoms to discover relevant Varma points using our hybrid
            lexical and semantic retrieval system powered by PubMedBERT
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={symptomQuery}
              onChange={(e) => setSymptomQuery(e.target.value)}
              onKeyDown={(e) => {
                e.stopPropagation();
                if (e.key === 'Enter' && !isSearching && symptomQuery.trim()) {
                  handleSearch();
                }
              }}
              placeholder="Enter symptoms (e.g., headache, joint pain, fatigue)..."
              className="flex-1 px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-600 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all"
              disabled={isSearching}
              autoComplete="off"
              style={{ pointerEvents: 'auto', position: 'relative', zIndex: 10 }}
            />
            {symptomQuery && (
              <button
                onClick={clearSearch}
                className="px-4 py-4 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                disabled={isSearching}
              >
                <X className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={handleSearch}
              disabled={isSearching || !symptomQuery.trim()}
              className="px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center font-medium"
            >
              {isSearching ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  Search
                </>
              )}
            </button>
          </div>

          {/* Common Symptoms Suggestions */}
          {!results && !isSearching && (
            <div>
              <p className="text-sm font-medium text-gray-700 mb-3">Common symptoms:</p>
              <div className="flex flex-wrap gap-2">
                {commonSymptoms.map((symptom, index) => (
                  <button
                    key={index}
                    onClick={() => setSymptomQuery(symptom)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-blue-600 hover:text-white transition-all duration-200 border border-gray-300 hover:border-blue-600"
                  >
                    {symptom}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900">Error</h4>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {isSearching && (
          <div className="bg-white rounded-2xl shadow-xl p-12">
            <LoadingSpinner size="lg" message="Analyzing symptoms with lexical matching and semantic understanding..." />
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Processing query through PubMedBERT embeddings...
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && !isSearching && (
          <div>
            <div className="grid lg:grid-cols-2 gap-8">
              {/* 3D Model with Highlights */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-2xl font-semibold text-gray-900">
                    Visual Representation
                  </h3>
                  <div className="flex items-center gap-2">
                    {selectedPoint && (
                      <button
                        onClick={() => setSelectedPoint(null)}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                      >
                        <X className="w-4 h-4 mr-1" />
                        Clear
                      </button>
                    )}
                    <button
                      onClick={toggleModelExpansion}
                      className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      <Maximize2 className="w-4 h-4 mr-1" />
                      {isModelExpanded ? 'Exit' : 'Fullscreen'}
                    </button>
                  </div>
                </div>
                <UnityModel3DViewer
                  isExpanded={isModelExpanded}
                  highlightedPoints={highlightedPoints}
                  selectedPoint={selectedPoint}
                  onExpandChange={setIsModelExpanded}
                />
              </div>

              {/* Results Details */}
              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-gray-900">
                  Identified Varma Points
                </h3>

                {results.varma_points && results.varma_points.length > 0 ? (
                  <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                    {results.varma_points.map((point, index) => {
                      const confidence = getConfidenceLevel(point.confidence_score);
                      const isSelected = selectedPoint?.id === point.id;

                      return (
                        <div
                          key={index}
                          onClick={() => handlePointClick(point)}
                          className={`
                            bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 
                            border-l-4 cursor-pointer transform hover:scale-[1.02]
                            ${isSelected ? 'border-blue-600 ring-2 ring-blue-300' : 'border-blue-500'}
                          `}
                        >
                          {/* Header */}
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h4 className="text-xl font-bold text-gray-900 mb-1">
                                {point.name.replace(/_/g, ' ')}
                              </h4>
                            </div>
                            <span className={`
                              px-4 py-2 rounded-full text-sm font-bold shadow-md
                              ${confidence.bg} ${confidence.color}
                            `}>
                              {(point.confidence_score * 100).toFixed(1)}%
                            </span>
                          </div>

                          {/* Description */}
                          <p className="text-gray-700 mb-4 leading-relaxed">
                            {point.description}
                          </p>

                          {/* Matched Symptoms */}
                          {point.matched_symptoms && point.matched_symptoms.length > 0 && (
                            <div className="mb-4">
                              <p className="text-sm font-semibold text-gray-700 mb-2">
                                Matched Symptoms:
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {point.matched_symptoms.map((symptom, idx) => (
                                  <span
                                    key={idx}
                                    className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-200"
                                  >
                                    {symptom}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-lg">
                    <div className="flex items-start">
                      <AlertCircle className="w-6 h-6 text-yellow-500 mr-3 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-semibold text-yellow-900 text-lg mb-1">
                          No Matches Found
                        </h4>
                        <p className="text-yellow-700">
                          No Varma points matched your symptoms. Try:
                        </p>
                        <ul className="mt-2 text-sm text-yellow-700 space-y-1">
                          <li>• Using different symptom terms</li>
                          <li>• Being more specific about the location</li>
                          <li>• Trying common symptoms from suggestions</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SymptomSearch;