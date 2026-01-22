# Varma Intelligence System

A hybrid intelligent retrieval and visualization system for identifying relevant Varma points based on user-reported symptoms.

## Features

- **3D Interactive Model**: Visualize Varma points on a human body model
- **Symptom Search**: Find relevant Varma points using natural language symptom descriptions
- **RAG-Powered Q&A**: Ask questions about Varma knowledge and get grounded, explainable answers
- **Hybrid Retrieval**: Combines lexical matching and semantic understanding with PubMedBERT
- **Professional UI**: Modern, responsive interface built with React and Tailwind CSS

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure your backend API endpoint in `.env`:
```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

3. Run the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## Building for Production
```bash
npm run build
```

## Project Structure

- `/src/components` - React components
- `/src/services` - API and service integrations
- `/src/utils` - Utility functions and constants
- `/src/styles` - CSS and animation styles
- `/public/unity` - Unity WebGL build files (place your Unity build here)

## Backend Integration

Ensure your backend API provides these endpoints:

- `POST /api/symptom-search` - Symptom to Varma point mapping
- `POST /api/rag-query` - RAG-based question answering
- `GET /api/varma-points` - Get all Varma points

## Technologies Used

- React 18
- Tailwind CSS
- Axios
- Lucide React Icons
- Unity WebGL (for 3D model)
````

## Running the Application

Now run these commands in your terminal:
````bash
cd varma-intelligence-system

# Initialize Tailwind properly
npx tailwindcss init -p

# Start the development server
npm start
````

The application will open at `http://localhost:3000`. You'll need to:

1. **Set up your backend API** - Update the `REACT_APP_API_BASE_URL` in `.env` to point to your actual backend
2. **Integrate your Unity 3D model** - Place your Unity WebGL build files in `public/unity/` directory
3. **Connect your APIs** - Ensure your backend provides the endpoints mentioned in the API service

The UI is now professional, responsive, and ready for integration with your existing symptom search, RAG, and 3D model systems!