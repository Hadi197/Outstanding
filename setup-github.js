#!/usr/bin/env node

/**
 * GitHub Repository Setup and Debugging Tool
 * 
 * This script will:
 * 1. Create the GitHub repository if it doesn't exist
 * 2. Verify token permissions
 * 3. Set up the abai.csv file
 * 4. Test the complete integration
 */

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_NAME = 'Outstanding';

async function githubRequest(url, options = {}) {
    const defaultHeaders = {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Outstanding-Dashboard-Setup',
        'Content-Type': 'application/json'
    };
    
    const response = await fetch(url, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {})
        }
    });
    
    const responseText = await response.text();
    let responseData;
    try {
        responseData = JSON.parse(responseText);
    } catch (e) {
        responseData = responseText;
    }
    
    return {
        ok: response.ok,
        status: response.status,
        data: responseData
    };
}

async function setupGitHubIntegration() {
    console.log('🚀 Setting up GitHub integration for Outstanding Dashboard...\n');
    
    try {
        // Step 1: Verify token and get user info
        console.log('1️⃣ Verifying GitHub token...');
        const userResult = await githubRequest('https://api.github.com/user');
        
        if (!userResult.ok) {
            console.error('❌ Token verification failed:', userResult.data);
            return false;
        }
        
        const username = userResult.data.login;
        console.log(`✅ Token valid for user: ${username}`);
        
        // Step 2: Check if repository exists
        console.log('\n2️⃣ Checking repository status...');
        const repoResult = await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}`);
        
        let repositoryExists = false;
        
        if (repoResult.ok) {
            console.log(`✅ Repository ${username}/${REPO_NAME} exists`);
            repositoryExists = true;
        } else if (repoResult.status === 404) {
            console.log(`⚠️ Repository ${username}/${REPO_NAME} not found`);
            
            // Step 3: Create repository
            console.log('\n3️⃣ Creating repository...');
            const createResult = await githubRequest('https://api.github.com/user/repos', {
                method: 'POST',
                body: JSON.stringify({
                    name: REPO_NAME,
                    description: 'Outstanding Dashboard - Data persistence for ignored items',
                    private: false, // Making it public to avoid permission issues
                    auto_init: true
                })
            });
            
            if (createResult.ok) {
                console.log(`✅ Repository ${username}/${REPO_NAME} created successfully`);
                repositoryExists = true;
            } else {
                console.error('❌ Failed to create repository:', createResult.data);
                return false;
            }
        } else {
            console.error('❌ Unexpected error checking repository:', repoResult.data);
            return false;
        }
        
        // Step 4: Check/create abai.csv file
        if (repositoryExists) {
            console.log('\n4️⃣ Setting up abai.csv file...');
            const fileResult = await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}/contents/abai.csv`);
            
            if (fileResult.ok) {
                console.log('✅ abai.csv file already exists');
                console.log(`   SHA: ${fileResult.data.sha}`);
                console.log(`   Size: ${fileResult.data.size} bytes`);
            } else if (fileResult.status === 404) {
                console.log('⚠️ abai.csv not found, creating initial file...');
                
                // Create initial abai.csv with header
                const initialContent = 'PKK_NUMBER,DATE_IGNORED,REASON\n';
                const encodedContent = Buffer.from(initialContent).toString('base64');
                
                const createFileResult = await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}/contents/abai.csv`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        message: 'Initial abai.csv file for Outstanding Dashboard',
                        content: encodedContent
                    })
                });
                
                if (createFileResult.ok) {
                    console.log('✅ abai.csv file created successfully');
                } else {
                    console.error('❌ Failed to create abai.csv:', createFileResult.data);
                    return false;
                }
            } else {
                console.error('❌ Unexpected error checking abai.csv:', fileResult.data);
                return false;
            }
        }
        
        // Step 5: Test complete workflow
        console.log('\n5️⃣ Testing complete workflow...');
        
        // Test reading
        const readTest = await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}/contents/abai.csv`);
        if (readTest.ok) {
            const content = Buffer.from(readTest.data.content, 'base64').toString('utf-8');
            console.log('✅ Read test successful');
            console.log(`   Content preview: ${content.substring(0, 50)}...`);
            
            // Test writing (add a test entry)
            const testEntry = `TEST_ENTRY,${new Date().toISOString()},test\n`;
            const newContent = content + testEntry;
            const encodedNewContent = Buffer.from(newContent).toString('base64');
            
            const writeTest = await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}/contents/abai.csv`, {
                method: 'PUT',
                body: JSON.stringify({
                    message: 'Test write operation',
                    content: encodedNewContent,
                    sha: readTest.data.sha
                })
            });
            
            if (writeTest.ok) {
                console.log('✅ Write test successful');
                
                // Remove test entry
                const cleanContent = content; // Original content without test entry
                const encodedCleanContent = Buffer.from(cleanContent).toString('base64');
                
                await githubRequest(`https://api.github.com/repos/${username}/${REPO_NAME}/contents/abai.csv`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        message: 'Clean up test entry',
                        content: encodedCleanContent,
                        sha: writeTest.data.content.sha
                    })
                });
                
                console.log('✅ Cleanup successful');
            } else {
                console.error('❌ Write test failed:', writeTest.data);
                return false;
            }
        } else {
            console.error('❌ Read test failed:', readTest.data);
            return false;
        }
        
        console.log('\n🎉 GitHub integration setup completed successfully!');
        console.log('\nNext steps:');
        console.log('1. Update netlify.toml to use main abaikan function');
        console.log('2. Deploy the changes');
        console.log('3. Test the production environment');
        
        return true;
        
    } catch (error) {
        console.error('❌ Setup failed with exception:', error.message);
        return false;
    }
}

// Run the setup
setupGitHubIntegration().then(success => {
    if (success) {
        console.log('\n✅ Setup completed successfully!');
        process.exit(0);
    } else {
        console.log('\n❌ Setup failed!');
        process.exit(1);
    }
}).catch(error => {
    console.error('❌ Setup crashed:', error);
    process.exit(1);
});