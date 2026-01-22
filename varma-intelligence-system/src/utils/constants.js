export const API_ENDPOINTS = {
  SYMPTOM_SEARCH: '/api/symptom-search',
  RAG_QUERY: 'http://localhost:5004/api/rag/query',
  VARMA_POINTS: '/api/varma-points',
};

export const VARMA_CATEGORIES = {
  HEAD: 'Head & Neck',
  UPPER_BODY: 'Upper Body',
  LOWER_BODY: 'Lower Body',
  EXTREMITIES: 'Extremities',
};

export const CONFIDENCE_LEVELS = {
  HIGH: { min: 0.8, color: 'text-green-600', bg: 'bg-green-100' },
  MEDIUM: { min: 0.5, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  LOW: { min: 0, color: 'text-red-600', bg: 'bg-red-100' },
};

export const ANIMATION_DURATION = 500;