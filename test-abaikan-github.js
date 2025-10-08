#!/usr/bin/env node

// Test abaikan functionality with new GitHub token
const testData = {
  no_pkk_inaportnet: 'TEST.PKK.12345.TEST',
  timestamp: new Date().toISOString(),
  reason: 'data_duplikat',
  notes: 'Test dari GitHub API baru'
};

console.log('🧪 Testing abaikan functionality with new GitHub token...');
console.log('📄 Test data:', testData);

// Test locally using Node.js to simulate Netlify function
const abaikanHandler = require('./netlify/functions/abaikan.js');

async function testAbaikan() {
  console.log('\n1️⃣ Testing POST request (add to abaikan)...');
  
  const postEvent = {
    httpMethod: 'POST',
    path: '/api/abaikan',
    body: JSON.stringify(testData),
    headers: {
      'Content-Type': 'application/json'
    }
  };

  try {
    const postResponse = await abaikanHandler.handler(postEvent, {});
    console.log('📤 POST Response Status:', postResponse.statusCode);
    
    if (postResponse.statusCode === 200) {
      const postResult = JSON.parse(postResponse.body);
      console.log('✅ POST Success:', postResult.message);
      console.log('📊 Storage type:', postResult.storage_type);
      console.log('🔄 Persistent:', postResult.persistent);
    } else {
      console.log('❌ POST Error:', postResponse.body);
      return;
    }
  } catch (error) {
    console.error('❌ POST Exception:', error.message);
    return;
  }

  console.log('\n2️⃣ Testing GET request (retrieve abai list)...');
  
  const getEvent = {
    httpMethod: 'GET',
    path: '/api/abaikan',
    queryStringParameters: { action: 'list' }
  };

  try {
    const getResponse = await abaikanHandler.handler(getEvent, {});
    console.log('📥 GET Response Status:', getResponse.statusCode);
    
    if (getResponse.statusCode === 200) {
      const getResult = JSON.parse(getResponse.body);
      console.log('✅ GET Success');
      console.log('📊 Total entries:', getResult.total_entries);
      console.log('📍 Source:', getResult.source);
      
      if (getResult.abai_list && getResult.abai_list.length > 0) {
        console.log('📝 Recent entries:');
        getResult.abai_list.slice(-3).forEach((entry, i) => {
          console.log(`   ${i + 1}. ${entry}`);
        });
        
        // Check if our test entry is there
        if (getResult.abai_list.includes(testData.no_pkk_inaportnet)) {
          console.log('🎉 Test entry found in GitHub repository!');
        } else {
          console.log('⚠️ Test entry not found in repository');
        }
      }
    } else {
      console.log('❌ GET Error:', getResponse.body);
    }
  } catch (error) {
    console.error('❌ GET Exception:', error.message);
  }
}

testAbaikan();