import axios from 'axios';
import type { GenerationSummary } from '../types';

const API_BASE_URL = 'http://localhost:8001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchSummary = async (): Promise<GenerationSummary> => {
  try {
    const response = await apiClient.get<GenerationSummary>('/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching summary:', error);
    throw error;
  }
};

export const fetchLogs = async (lastN: number = 100): Promise<string[]> => {
  try {
    const response = await apiClient.get<{ logs: string[] }>('/logs', {
      params: { last_n: lastN },
    });
    return response.data.logs;
  } catch (error) {
    console.error('Error fetching logs:', error);
    throw error;
  }
};

export default {
  fetchSummary,
  fetchLogs,
};