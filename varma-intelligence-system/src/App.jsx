import React, { useState } from 'react';
import Navigation from './components/Navigation';
import LandingView from './components/LandingView';
import SymptomSearch from './components/SymptomSearch';
import RAGChat from './components/RAGChat';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('landing');

  const renderActiveView = () => {
    switch (activeTab) {
      case 'landing':
        return <LandingView />;
      case 'symptom':
        return <SymptomSearch />;
      case 'rag':
        return <RAGChat />;
      default:
        return <LandingView />;
    }
  };

  return (
    <div className="App min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="transition-all duration-300">
        {renderActiveView()}
      </main>
    </div>
  );
}

export default App;