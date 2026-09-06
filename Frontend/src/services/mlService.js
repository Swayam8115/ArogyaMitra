import axios from 'axios';

// ML Microservice — ML_Model/app.py running on port 8001.
// Used by the frontend only for fetching /symptoms.
// The main backend's xai_node (not the frontend) calls /predict on this service.
const ML_BASE_URL = import.meta.env.VITE_ML_BASE_URL || 'http://127.0.0.1:8001';

// Main Backend — graph/server.py running on port 8000.
// All /analyze/json calls go to this service (which internally calls the ML microservice).
const GRAPH_BASE_URL = import.meta.env.VITE_GRAPH_BASE_URL || 'http://127.0.0.1:8000';


const mlApi = axios.create({
  baseURL: ML_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

const graphApi = axios.create({
  baseURL: GRAPH_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});


/**
 * Fetch all known symptoms from the ML model
 * @returns {Promise<string[]>} list of symptom strings
 */
export const getSymptoms = async () => {
  const response = await mlApi.get('/symptoms');
  return response.data.symptoms; // string[]
};

/**
 * Run disease prediction (JSON only, from deployed ML model)
 * @param {Object} payload
 * @returns {Promise<Object>} full prediction result
 */
export const predict = async (payload) => {
  const response = await mlApi.post('/predict', payload);
  return response.data;
};

/**
 * Run full LangGraph pipeline: ML model → LLM → PDF generation.
 * Returns JSON with mlResult, llmResult, pdfBase64, and filename.
 * Calls the local graph server at VITE_GRAPH_BASE_URL.
 *
 * @param {Object} payload - { symptoms, patientName, patientAge, patientGender, workerName, location }
 * @returns {Promise<{ mlResult, llmResult, pdfBase64, filename }>}
 */
export const analyzeWithGraph = async (payload) => {
  const response = await graphApi.post('/analyze/json', payload);
  return response.data;
};

/**
 * Download a PDF report of the prediction directly from the ML model.
 * Triggers browser download automatically.
 * @param {Object} payload - same as predict()
 * @param {string} filename - suggested filename
 */
export const downloadPredictPdf = async (payload, filename) => {
  const response = await mlApi.post('/predict/pdf', payload, {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename || 'ArogyaMitra_Report.pdf');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
