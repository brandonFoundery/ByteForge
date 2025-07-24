const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api/v1';

// Test configuration
const testConfig = {
  baseURL: BASE_URL,
  timeout: 10000,
  validateStatus: function (status) {
    return status < 500; // Allow 4xx errors for testing
  }
};

// Test user credentials
const testUser = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  confirmPassword: 'TestPassword123!'
};

// Test lead data
const testLead = {
  name: 'Test Lead',
  email: 'testlead@example.com',
  phone: '555-123-4567',
  company: 'Test Company',
  source: 'Manual'
};

let authToken = null;

async function testEndpoint(name, testFunction) {
  try {
    console.log(`\n🧪 Testing: ${name}`);
    await testFunction();
    console.log(`✅ ${name} - PASSED`);
  } catch (error) {
    console.log(`❌ ${name} - FAILED`);
    console.log(`   Error: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }
}

async function testHealthCheck() {
  const response = await axios.get('http://localhost:5000/health', testConfig);
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
}

async function testUserRegistration() {
  const response = await axios.post(`${BASE_URL}/auth/register`, testUser, testConfig);
  if (response.status !== 200 && response.status !== 409) {
    throw new Error(`Expected 200 or 409, got ${response.status}`);
  }
}

async function testUserLogin() {
  const response = await axios.post(`${BASE_URL}/auth/login`, {
    email: testUser.email,
    password: testUser.password
  }, testConfig);
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (!response.data.data.accessToken) {
    throw new Error('No access token returned');
  }
  
  authToken = response.data.data.accessToken;
}

async function testGetProfile() {
  const response = await axios.get(`${BASE_URL}/auth/profile`, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (!response.data.data.email) {
    throw new Error('No email in profile response');
  }
}

async function testCreateLead() {
  const response = await axios.post(`${BASE_URL}/leads`, testLead, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 201) {
    throw new Error(`Expected 201, got ${response.status}`);
  }
  
  if (!response.data.data.id) {
    throw new Error('No ID in created lead response');
  }
  
  return response.data.data.id;
}

async function testGetLeads() {
  const response = await axios.get(`${BASE_URL}/leads`, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (!response.data.data.items) {
    throw new Error('No items array in leads response');
  }
}

async function testGetLead(leadId) {
  const response = await axios.get(`${BASE_URL}/leads/${leadId}`, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (!response.data.data.id) {
    throw new Error('No ID in lead response');
  }
}

async function testUpdateLead(leadId) {
  const response = await axios.put(`${BASE_URL}/leads/${leadId}`, {
    name: 'Updated Test Lead'
  }, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (response.data.data.name !== 'Updated Test Lead') {
    throw new Error('Lead name was not updated');
  }
}

async function testGetMetrics() {
  const response = await axios.get(`${BASE_URL}/leads/metrics`, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (typeof response.data.data.totalLeads !== 'number') {
    throw new Error('No totalLeads in metrics response');
  }
}

async function testProcessLead(leadId) {
  const response = await axios.post(`${BASE_URL}/leads/${leadId}/process`, {}, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
  
  if (!response.data.data.workflowInstanceId) {
    throw new Error('No workflowInstanceId in process response');
  }
}

async function testDeleteLead(leadId) {
  const response = await axios.delete(`${BASE_URL}/leads/${leadId}`, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
}

async function testLogout() {
  const response = await axios.post(`${BASE_URL}/auth/logout`, {}, {
    ...testConfig,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected 200, got ${response.status}`);
  }
}

async function runTests() {
  console.log('🚀 Starting API Endpoint Tests...');
  console.log('=====================================');
  
  let leadId = null;
  
  try {
    await testEndpoint('Health Check', testHealthCheck);
    await testEndpoint('User Registration', testUserRegistration);
    await testEndpoint('User Login', testUserLogin);
    await testEndpoint('Get Profile', testGetProfile);
    await testEndpoint('Create Lead', async () => {
      leadId = await testCreateLead();
    });
    await testEndpoint('Get Leads', testGetLeads);
    await testEndpoint('Get Lead', () => testGetLead(leadId));
    await testEndpoint('Update Lead', () => testUpdateLead(leadId));
    await testEndpoint('Get Metrics', testGetMetrics);
    await testEndpoint('Process Lead', () => testProcessLead(leadId));
    await testEndpoint('Delete Lead', () => testDeleteLead(leadId));
    await testEndpoint('Logout', testLogout);
    
    console.log('\n🎉 All API tests completed!');
    console.log('=====================================');
    
  } catch (error) {
    console.log('\n💥 Test suite failed with error:', error.message);
    process.exit(1);
  }
}

// Check if server is running
async function checkServer() {
  try {
    await axios.get('http://localhost:5000/health', { timeout: 5000 });
    console.log('✅ Server is running');
    return true;
  } catch (error) {
    console.log('❌ Server is not running. Please start the server first.');
    console.log('   Run: dotnet run or ./start_bird.ps1');
    return false;
  }
}

// Main execution
async function main() {
  const serverRunning = await checkServer();
  if (serverRunning) {
    await runTests();
  } else {
    process.exit(1);
  }
}

main();