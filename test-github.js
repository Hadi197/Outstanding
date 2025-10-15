#!/usr/bin/env node

// Test GitHub API connection and token permissions
const GITHUB_TOKEN = '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';
const GITHUB_OWNER = 'Hadi197';
const GITHUB_REPO = 'Outstanding';
const FILE_PATH = 'abai.csv';

async function testGitHubConnection() {
  console.log('🔍 Testing GitHub API connection...');
  console.log(`📁 Repository: ${GITHUB_OWNER}/${GITHUB_REPO}`);
  console.log(`📄 File: ${FILE_PATH}`);
  console.log(`🔑 Token: ${GITHUB_TOKEN.substring(0, 20)}...`);
  
  try {
    // Test 0: Check token validity
    console.log('\n0️⃣ Testing token validity...');
    const tokenResponse = await fetch('https://api.github.com/user', {
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Outstanding-Dashboard-Test'
      }
    });
    
    if (tokenResponse.ok) {
      const userData = await tokenResponse.json();
      console.log(`✅ Token valid for user: ${userData.login}`);
    } else {
      console.log(`❌ Token validation failed: ${tokenResponse.status}`);
      const error = await tokenResponse.text();
      console.log(`   Error: ${error}`);
      return;
    }

    // Test 1: Get repository info
    console.log('\n1️⃣ Testing repository access...');
    const repoResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}`, {
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Outstanding-Dashboard-Test'
      }
    });
    
    if (repoResponse.ok) {
      const repoData = await repoResponse.json();
      console.log(`✅ Repository access: OK`);
      console.log(`   - Name: ${repoData.name}`);
      console.log(`   - Private: ${repoData.private}`);
      console.log(`   - Permissions: ${JSON.stringify(repoData.permissions || 'not available')}`);
    } else {
      console.log(`❌ Repository access failed: ${repoResponse.status}`);
      const error = await repoResponse.text();
      console.log(`   Error: ${error}`);
      
      // Continue with file test anyway
      console.log(`⚠️ Continuing with file access test...`);
    }
    
    // Test 2: Check if abai.csv exists
    console.log('\n2️⃣ Testing file access...');
    const fileResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${FILE_PATH}`, {
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Outstanding-Dashboard-Test'
      }
    });
    
    if (fileResponse.ok) {
      const fileData = await fileResponse.json();
      console.log(`✅ File exists: ${FILE_PATH}`);
      console.log(`   - SHA: ${fileData.sha}`);
      console.log(`   - Size: ${fileData.size} bytes`);
      
      // Decode and show content preview
      const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
      const lines = content.split('\n').slice(0, 5);
      console.log(`   - Content preview (first 5 lines):`);
      lines.forEach((line, i) => {
        if (line.trim()) console.log(`     ${i + 1}: ${line}`);
      });
      
    } else if (fileResponse.status === 404) {
      console.log(`⚠️ File does not exist: ${FILE_PATH}`);
      console.log(`   Will be created on first abaikan action`);
    } else {
      console.log(`❌ File access failed: ${fileResponse.status}`);
      const error = await fileResponse.text();
      console.log(`   Error: ${error}`);
    }
    
    // Test 3: Test write permissions by creating/updating a test file
    console.log('\n3️⃣ Testing write permissions...');
    const testFileName = 'test-connection.txt';
    const testContent = `GitHub API connection test\nTimestamp: ${new Date().toISOString()}\nToken: Working\n`;
    
    const writeResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${testFileName}`, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'Outstanding-Dashboard-Test'
      },
      body: JSON.stringify({
        message: 'Test GitHub API write permissions',
        content: Buffer.from(testContent).toString('base64'),
        branch: 'main'
      })
    });
    
    if (writeResponse.ok) {
      const writeData = await writeResponse.json();
      console.log(`✅ Write permissions: OK`);
      console.log(`   - Created file: ${testFileName}`);
      console.log(`   - Commit SHA: ${writeData.commit.sha}`);
      
      // Clean up: delete test file
      console.log(`\n🧹 Cleaning up test file...`);
      const deleteResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${testFileName}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `token ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'User-Agent': 'Outstanding-Dashboard-Test'
        },
        body: JSON.stringify({
          message: 'Clean up test file',
          sha: writeData.content.sha,
          branch: 'main'
        })
      });
      
      if (deleteResponse.ok) {
        console.log(`✅ Test file cleaned up successfully`);
      } else {
        console.log(`⚠️ Failed to clean up test file (not critical)`);
      }
      
    } else {
      console.log(`❌ Write permissions failed: ${writeResponse.status}`);
      const error = await writeResponse.text();
      console.log(`   Error: ${error}`);
    }
    
    console.log('\n🎉 GitHub API test completed!');
    
  } catch (error) {
    console.error('❌ Test failed with exception:', error.message);
  }
}

// Run the test
testGitHubConnection();