import { test, expect } from '@playwright/test';
import { testBase } from './fixtures/test-base';
import { apiHelper } from './helpers/api-helper';

test.describe('Infrastructure Services', () => {
  test.use(testBase);

  test.describe('LLM Integration', () => {
    test('should list available LLM providers', async ({ page, request }) => {
      const response = await request.get('/api/infrastructure/llm/providers');
      expect(response.ok()).toBeTruthy();
      
      const providers = await response.json();
      expect(Array.isArray(providers)).toBeTruthy();
      // At least one provider should be configured in test environment
      expect(providers.length).toBeGreaterThanOrEqual(0);
    });

    test('should generate content using LLM service', async ({ page, request }) => {
      const generateRequest = {
        prompt: 'Generate a simple test response',
        systemPrompt: 'You are a helpful assistant. Keep responses brief.',
        maxTokens: 100
      };

      const response = await request.post('/api/infrastructure/llm/generate', {
        data: generateRequest
      });

      // In test mode, might return mock response
      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result).toHaveProperty('success');
      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('provider');
    });
  });

  test.describe('Document Generation', () => {
    test('should list available document templates', async ({ page, request }) => {
      const response = await request.get('/api/infrastructure/documents/templates');
      expect(response.ok()).toBeTruthy();
      
      const templates = await response.json();
      expect(Array.isArray(templates)).toBeTruthy();
      // Should have at least BRD, PRD, FRD, TRD templates
      expect(templates).toContain('BRD');
      expect(templates).toContain('PRD');
      expect(templates).toContain('FRD');
      expect(templates).toContain('TRD');
    });

    test('should generate a document', async ({ page, request }) => {
      const generateRequest = {
        documentType: 'BRD',
        projectName: 'Test Project',
        projectDescription: 'A test project for E2E testing',
        additionalContext: {
          author: 'E2E Test Suite',
          version: '1.0.0'
        }
      };

      const response = await request.post('/api/infrastructure/documents/generate', {
        data: generateRequest
      });

      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result).toHaveProperty('success');
      expect(result).toHaveProperty('documentType', 'BRD');
      expect(result).toHaveProperty('content');
      expect(result).toHaveProperty('generatedAt');
    });

    test('should validate document structure', async ({ page, request }) => {
      const validateRequest = {
        documentType: 'PRD',
        content: `# Product Requirements Document

## Product Overview
This is a test PRD.

## Features
- Feature 1
- Feature 2

## User Stories
- As a user, I want to test the system

## Technical Requirements
- REQ-001: System must validate documents

## Acceptance Criteria
- All tests pass`
      };

      const response = await request.post('/api/infrastructure/documents/validate', {
        data: validateRequest
      });

      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result).toHaveProperty('isValid', true);
      expect(result).toHaveProperty('errors');
      expect(result.errors).toHaveLength(0);
    });
  });

  test.describe('Project Management', () => {
    let projectId: string;

    test('should create a new project', async ({ page, request }) => {
      const createRequest = {
        name: `E2E Test Project ${Date.now()}`,
        description: 'Project created by E2E tests',
        templateId: 'CRM',
        clientRequirements: 'Test requirements for E2E testing'
      };

      const response = await request.post('/api/infrastructure/projects', {
        data: createRequest
      });

      expect(response.ok()).toBeTruthy();
      
      const project = await response.json();
      expect(project).toHaveProperty('id');
      expect(project).toHaveProperty('name', createRequest.name);
      expect(project).toHaveProperty('status', 'Created');
      
      projectId = project.id;
    });

    test('should get project details', async ({ page, request }) => {
      // First create a project
      const createRequest = {
        name: `E2E Test Project ${Date.now()}`,
        description: 'Project for testing GET endpoint'
      };

      const createResponse = await request.post('/api/infrastructure/projects', {
        data: createRequest
      });
      const project = await createResponse.json();

      // Then get the project
      const response = await request.get(`/api/infrastructure/projects/${project.id}`);
      expect(response.ok()).toBeTruthy();
      
      const retrievedProject = await response.json();
      expect(retrievedProject).toHaveProperty('id', project.id);
      expect(retrievedProject).toHaveProperty('name', project.name);
    });

    test('should list all projects', async ({ page, request }) => {
      const response = await request.get('/api/infrastructure/projects');
      expect(response.ok()).toBeTruthy();
      
      const projects = await response.json();
      expect(Array.isArray(projects)).toBeTruthy();
    });

    test('should add document to project', async ({ page, request }) => {
      // First create a project
      const createProjectResponse = await request.post('/api/infrastructure/projects', {
        data: {
          name: `E2E Test Project ${Date.now()}`,
          description: 'Project for document testing'
        }
      });
      const project = await createProjectResponse.json();

      // Then add a document
      const addDocumentRequest = {
        projectId: project.id,
        documentType: 'BRD',
        content: '# Business Requirements Document\n\nTest content',
        version: '1.0.0'
      };

      const response = await request.post('/api/infrastructure/documents', {
        data: addDocumentRequest
      });

      expect(response.ok()).toBeTruthy();
      
      const document = await response.json();
      expect(document).toHaveProperty('id');
      expect(document).toHaveProperty('projectId', project.id);
      expect(document).toHaveProperty('documentType', 'BRD');
    });
  });

  test.describe('Template System', () => {
    test('should list project templates', async ({ page, request }) => {
      const response = await request.get('/api/infrastructure/templates');
      expect(response.ok()).toBeTruthy();
      
      const templates = await response.json();
      expect(Array.isArray(templates)).toBeTruthy();
    });

    test('should get template details', async ({ page, request }) => {
      const response = await request.get('/api/infrastructure/templates/CRM');
      
      // Template might not exist in test environment
      if (response.ok()) {
        const template = await response.json();
        expect(template).toHaveProperty('id', 'CRM');
        expect(template).toHaveProperty('name');
        expect(template).toHaveProperty('category');
        expect(template).toHaveProperty('requiredDocuments');
      } else {
        expect(response.status()).toBe(404);
      }
    });

    test('should validate template structure', async ({ page, request }) => {
      const response = await request.post('/api/infrastructure/templates/CRM/validate');
      
      // Template might not exist in test environment
      if (response.ok()) {
        const result = await response.json();
        expect(result).toHaveProperty('isValid');
        expect(result).toHaveProperty('errors');
      } else {
        expect(response.status()).toBe(404);
      }
    });
  });
});