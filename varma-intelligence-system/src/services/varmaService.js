import { searchSymptoms, queryRAG, getVarmaPoints } from './api';

class VarmaService {
  constructor() {
    this.cache = new Map();
  }

  async searchBySymptom(symptom) {
    const cacheKey = `symptom_${symptom.toLowerCase()}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const result = await searchSymptoms(symptom);
      this.cache.set(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Error in searchBySymptom:', error);
      throw error;
    }
  }

  async askQuestion(question) {
    try {
      const result = await queryRAG(question);
      return result;
    } catch (error) {
      console.error('Error in askQuestion:', error);
      throw error;
    }
  }

  async getAllVarmaPoints() {
    const cacheKey = 'all_varma_points';
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const result = await getVarmaPoints();
      this.cache.set(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Error in getAllVarmaPoints:', error);
      throw error;
    }
  }

  clearCache() {
    this.cache.clear();
  }
}

export default new VarmaService();