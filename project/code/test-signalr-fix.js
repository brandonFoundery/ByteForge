// Simple Node.js script to test SignalR connection
// Run with: node test-signalr-fix.js

const { HubConnectionBuilder, LogLevel } = require('@microsoft/signalr');

async function testSignalRConnection() {
    console.log('🔌 Testing SignalR Connection Fix...');
    console.log('===================================');
    
    const connection = new HubConnectionBuilder()
        .withUrl('http://localhost:5000/leadHub')
        .withAutomaticReconnect()
        .configureLogging(LogLevel.Information)
        .build();

    try {
        // Test connection
        console.log('📡 Attempting to connect to SignalR hub...');
        await connection.start();
        console.log('✅ Connected successfully!');
        console.log('📊 Connection State:', connection.state);
        console.log('🆔 Connection ID:', connection.connectionId);

        // Test joining dashboard group
        console.log('\n🏠 Testing dashboard group join...');
        await connection.invoke('JoinDashboard');
        console.log('✅ Successfully joined dashboard group');

        // Test joining lead group (use a test lead ID)
        const testLeadId = 1;
        console.log(`\n👤 Testing lead group join (Lead ID: ${testLeadId})...`);
        await connection.invoke('JoinLeadGroup', testLeadId);
        console.log(`✅ Successfully joined lead group for lead ${testLeadId}`);

        // Test leaving lead group
        console.log(`\n👋 Testing lead group leave (Lead ID: ${testLeadId})...`);
        await connection.invoke('LeaveLeadGroup', testLeadId);
        console.log(`✅ Successfully left lead group for lead ${testLeadId}`);

        // Test with string lead ID (should work with parseInt)
        const stringLeadId = "123";
        console.log(`\n🔤 Testing with string lead ID: "${stringLeadId}"...`);
        await connection.invoke('JoinLeadGroup', parseInt(stringLeadId, 10));
        console.log(`✅ Successfully joined lead group with string ID converted to number`);
        
        await connection.invoke('LeaveLeadGroup', parseInt(stringLeadId, 10));
        console.log(`✅ Successfully left lead group with string ID converted to number`);

        console.log('\n🎉 All SignalR tests passed!');
        console.log('\n🔧 Key fixes implemented:');
        console.log('   • Fixed frontend to use hook methods instead of direct connection.invoke()');
        console.log('   • Added proper type conversion (string → int) for lead IDs');
        console.log('   • Added connection state checking before invoking methods');
        console.log('   • Added comprehensive error handling and user feedback');
        console.log('   • Added logging for debugging connection issues');

    } catch (error) {
        console.error('❌ SignalR test failed:', error.message);
        console.log('\n🔍 Troubleshooting steps:');
        console.log('   1. Make sure the backend is running (dotnet run)');
        console.log('   2. Check that the SignalR hub is properly configured');
        console.log('   3. Verify the hub URL is correct (http://localhost:5000/leadHub)');
        console.log('   4. Check for any CORS issues');
        console.log('   5. Ensure the LeadHub class has the required methods');
    } finally {
        // Clean up
        if (connection.state === 'Connected') {
            await connection.stop();
            console.log('\n🔌 Connection closed');
        }
    }
}

// Run the test
testSignalRConnection().catch(console.error);