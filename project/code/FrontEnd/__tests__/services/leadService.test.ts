import { leadService } from '@/services/leadService';
import { apiClient } from '@/lib/api';
import { LeadDto, DashboardMetrics } from '@/types/api';

// Mock the API client
jest.mock('@/lib/api');
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('LeadService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getLeads', () => {
    it('should fetch leads with default filters', async () => {
      const mockLeads = {
        items: [
          { id: 1, name: 'Test Lead', email: 'test@example.com' }
        ],
        totalCount: 1,
        page: 1,
        pageSize: 20,
        totalPages: 1
      };
      
      mockedApiClient.get.mockResolvedValue(mockLeads);

      const result = await leadService.getLeads();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/leads', new URLSearchParams());
      expect(result).toEqual(mockLeads);
    });

    it('should fetch leads with custom filters', async () => {
      const filters = {
        page: 2,
        pageSize: 10,
        search: 'test',
        source: 'Google',
        status: 'New'
      };
      
      mockedApiClient.get.mockResolvedValue({
        items: [],
        totalCount: 0,
        page: 2,
        pageSize: 10,
        totalPages: 0
      });

      await leadService.getLeads(filters);

      const expectedParams = new URLSearchParams([
        ['page', '2'],
        ['pageSize', '10'],
        ['search', 'test'],
        ['source', 'Google'],
        ['status', 'New']
      ]);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/leads', expectedParams);
    });
  });

  describe('getLead', () => {
    it('should fetch a single lead', async () => {
      const mockLead: LeadDto = {
        id: 1,
        name: 'Test Lead',
        email: 'test@example.com',
        phone: '+1234567890',
        company: 'Test Company',
        source: 'Google',
        status: 'New',
        score: 85,
        isEnriched: false,
        isVetted: false,
        isUpsertedToZoho: false,
        workflowInstanceId: null,
        createdDate: '2023-01-01T00:00:00Z',
        modifiedDate: '2023-01-01T00:00:00Z'
      };
      
      mockedApiClient.get.mockResolvedValue(mockLead);

      const result = await leadService.getLead(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/leads/1');
      expect(result).toEqual(mockLead);
    });
  });

  describe('createLead', () => {
    it('should create a new lead', async () => {
      const leadData = {
        name: 'New Lead',
        email: 'new@example.com',
        phone: '+1234567890',
        company: 'New Company',
        source: 'Manual'
      };
      
      const mockCreatedLead: LeadDto = {
        id: 2,
        ...leadData,
        status: 'New',
        score: null,
        isEnriched: false,
        isVetted: false,
        isUpsertedToZoho: false,
        workflowInstanceId: null,
        createdDate: '2023-01-01T00:00:00Z',
        modifiedDate: '2023-01-01T00:00:00Z'
      };
      
      mockedApiClient.post.mockResolvedValue(mockCreatedLead);

      const result = await leadService.createLead(leadData);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/leads', leadData);
      expect(result).toEqual(mockCreatedLead);
    });
  });

  describe('getMetrics', () => {
    it('should fetch dashboard metrics', async () => {
      const mockMetrics: DashboardMetrics = {
        totalLeads: 100,
        todayLeads: 10,
        weekLeads: 50,
        statusCounts: {
          'New': 20,
          'Processing': 30,
          'Processed': 50
        },
        sourceCounts: {
          'Google': 40,
          'Facebook': 30,
          'LinkedIn': 30
        },
        enrichedLeads: 80,
        vettedLeads: 70,
        zohoLeads: 60,
        averageScore: 75.5,
        lastUpdated: '2023-01-01T00:00:00Z'
      };
      
      mockedApiClient.get.mockResolvedValue(mockMetrics);

      const result = await leadService.getMetrics();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/leads/metrics');
      expect(result).toEqual(mockMetrics);
    });
  });

  describe('bulk operations', () => {
    it('should delete multiple leads', async () => {
      const leadIds = [1, 2, 3];
      mockedApiClient.deleteWithoutData.mockResolvedValue();

      await leadService.bulkDelete(leadIds);

      expect(mockedApiClient.deleteWithoutData).toHaveBeenCalledTimes(3);
      expect(mockedApiClient.deleteWithoutData).toHaveBeenCalledWith('/leads/1');
      expect(mockedApiClient.deleteWithoutData).toHaveBeenCalledWith('/leads/2');
      expect(mockedApiClient.deleteWithoutData).toHaveBeenCalledWith('/leads/3');
    });

    it('should process multiple leads', async () => {
      const leadIds = [1, 2];
      const mockWorkflowResult = {
        workflowInstanceId: 'workflow-123',
        status: 'Started',
        message: 'Workflow started successfully'
      };
      
      mockedApiClient.post.mockResolvedValue(mockWorkflowResult);

      const result = await leadService.bulkProcess(leadIds);

      expect(mockedApiClient.post).toHaveBeenCalledTimes(2);
      expect(mockedApiClient.post).toHaveBeenCalledWith('/leads/1/process');
      expect(mockedApiClient.post).toHaveBeenCalledWith('/leads/2/process');
      expect(result).toEqual([mockWorkflowResult, mockWorkflowResult]);
    });
  });

  describe('export functionality', () => {
    it('should export leads as CSV', async () => {
      const mockLeads = {
        items: [
          {
            id: 1,
            name: 'Test Lead',
            email: 'test@example.com',
            phone: '+1234567890',
            company: 'Test Company',
            source: 'Google',
            status: 'New',
            score: 85,
            isEnriched: false,
            isVetted: false,
            isUpsertedToZoho: false,
            createdDate: '2023-01-01T00:00:00Z',
            modifiedDate: '2023-01-01T00:00:00Z'
          }
        ],
        totalCount: 1,
        page: 1,
        pageSize: 10000,
        totalPages: 1
      };
      
      mockedApiClient.get.mockResolvedValue(mockLeads);

      const result = await leadService.exportLeads();

      expect(result).toBeInstanceOf(Blob);
      expect(result.type).toBe('text/csv;charset=utf-8;');
    });
  });
});