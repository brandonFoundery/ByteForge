import { ApiClient, ApiError } from '@/lib/api';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:5000');
    mockedAxios.create.mockReturnValue(mockedAxios);
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('token management', () => {
    it('should set and get token', () => {
      const token = 'test-token';
      apiClient.setToken(token);
      
      expect(apiClient.getToken()).toBe(token);
      expect(localStorage.getItem('accessToken')).toBe(token);
    });

    it('should clear token', () => {
      apiClient.setToken('test-token');
      localStorage.setItem('refreshToken', 'refresh-token');
      
      apiClient.clearToken();
      
      expect(apiClient.getToken()).toBeNull();
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });
  });

  describe('HTTP methods', () => {
    it('should make GET request', async () => {
      const responseData = { data: { id: 1, name: 'Test' } };
      mockedAxios.get.mockResolvedValue({ data: responseData });

      const result = await apiClient.get('/test');

      expect(mockedAxios.get).toHaveBeenCalledWith('/test', { params: undefined });
      expect(result).toEqual(responseData.data);
    });

    it('should make POST request', async () => {
      const requestData = { name: 'Test' };
      const responseData = { data: { id: 1, name: 'Test' } };
      mockedAxios.post.mockResolvedValue({ data: responseData });

      const result = await apiClient.post('/test', requestData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/test', requestData);
      expect(result).toEqual(responseData.data);
    });

    it('should handle API errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            message: 'Validation failed',
            errors: ['Name is required']
          }
        }
      };
      mockedAxios.get.mockRejectedValue(errorResponse);

      await expect(apiClient.get('/test')).rejects.toThrow(ApiError);
    });
  });

  describe('health check', () => {
    it('should return true for healthy server', async () => {
      mockedAxios.get.mockResolvedValue({ data: 'OK' });

      const result = await apiClient.ping();

      expect(result).toBe(true);
    });

    it('should return false for unhealthy server', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network error'));

      const result = await apiClient.ping();

      expect(result).toBe(false);
    });
  });
});