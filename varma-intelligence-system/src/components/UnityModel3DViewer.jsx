import React, { useEffect, useRef, useState } from 'react';
import { Maximize2, Minimize2, RotateCcw, Loader } from 'lucide-react';
import { mapBackendToUnityNames } from '../utils/varmaNameMapping';

const UnityModel3DViewer = ({ isExpanded, highlightedPoints = [], selectedPoint, onExpandChange }) => {
  const [iframeLoaded, setIframeLoaded] = useState(false);
  const containerRef = useRef(null);
  const iframeRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Use our custom wrapper which loads the files from public/Web_text/Build
  // This wrapper is served by the main React app (port 3000) from the public folder
  const unityUrl = '/unity_wrapper.html';

  // Listen for load message from the wrapper
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'UNITY_LOADED') {
        console.log("Unity Wrapper reported ready.");
        setIframeLoaded(true);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Helper send function
  const sendToUnity = (type, payload) => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      console.log(`Sending to Unity [${type}]:`, payload);
      iframeRef.current.contentWindow.postMessage({ type, payload }, '*');
    }
  };

  // Handle highlighted points
  useEffect(() => {
    if (iframeLoaded) {
      if (highlightedPoints.length > 0) {
        // Prepare list of names
        const names = highlightedPoints.map(p => p.unity_name || p.name);
        const mappedNames = mapBackendToUnityNames(names);
        // Create JSON payload matching C# PointList class
        const jsonPayload = JSON.stringify({ points: mappedNames });

        sendToUnity('HighlightPointsList', jsonPayload);
      } else {
        // If empty, clear everything (though HighlightPointsList would also clear if sent empty list, this is explicit)
        sendToUnity('ClearAllHighlights', '');
      }
    }
  }, [highlightedPoints, iframeLoaded]);

  // Handle selected point
  useEffect(() => {
    if (iframeLoaded && selectedPoint) {
      const pointName = selectedPoint.unity_name || selectedPoint.name;
      sendToUnity('SelectPoint', pointName);
    }
  }, [selectedPoint, iframeLoaded]);

  const handleResetView = () => {
    sendToUnity('ResetCamera', '');
  };

  // Handle fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement
      );
      setIsFullscreen(isCurrentlyFullscreen);
      if (!isCurrentlyFullscreen && onExpandChange) {
        onExpandChange(false);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
    };
  }, [onExpandChange]);

  // Toggle fullscreen when isExpanded changes
  useEffect(() => {
    if (isExpanded && !isFullscreen) {
      containerRef.current?.requestFullscreen?.();
    } else if (!isExpanded && isFullscreen) {
      document.exitFullscreen?.();
    }
  }, [isExpanded]);

  return (
    <div
      ref={containerRef}
      className={`
        relative bg-gray-900 rounded-2xl shadow-2xl overflow-hidden transition-all duration-500
        ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : isExpanded ? 'h-[600px]' : 'h-[400px]'}
      `}
    >
      <div className="absolute top-4 right-4 z-10 flex space-x-2">
        <button
          onClick={handleResetView}
          className="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-5 h-5 text-gray-700" />
        </button>
      </div>

      <iframe
        ref={iframeRef}
        src={unityUrl}
        title="Unity 3D Viewer"
        width="100%"
        height="100%"
        style={{ border: 'none', display: 'block' }}
      />
    </div>
  );
};

export default UnityModel3DViewer;