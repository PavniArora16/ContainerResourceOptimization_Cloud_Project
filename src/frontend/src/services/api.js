import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const getMetrics = async () => {
  const response = await API.get("/metrics");
  return response.data;
};

export const getPredictions = async () => {
  const response = await API.get("/predictions");
  return response.data;
};

export const getAllocations = async () => {
  const response = await API.get("/allocations");
  return response.data;
};

export const runOptimization = async () => {
  const response = await API.post("/run-optimization");
  return response.data;
};