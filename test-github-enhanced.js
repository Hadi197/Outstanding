// Enhanced GitHub API test with different approaches
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

async function testGitHubAccess() {
    console.log('🔍 Testing GitHub token and repository access...');
    
    try {
        // First, test token validity by getting user info
        console.log('\n1️⃣ Testing token validity...');
        const userResponse = await fetch('https://api.github.com/user', {
            method: 'GET',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Netlify-Function-Debug'
            }
        });
        
        console.log('User API status:', userResponse.status);
        
        if (userResponse.ok) {
            const userData = await userResponse.json();
            console.log('✅ Token valid! User:', userData.login);
            console.log('User type:', userData.type);
            
            // Now test repository access with the actual username
            console.log(`\n2️⃣ Testing repository access for ${userData.login}/Outstanding...`);
            const repoResponse = await fetch(`https://api.github.com/repos/${userData.login}/Outstanding`, {
                method: 'GET',
                headers: {
                    'Authorization': `token ${GITHUB_TOKEN}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'Netlify-Function-Debug'
                }
            });
            
            console.log('Repository access status:', repoResponse.status);
            
            if (repoResponse.ok) {
                const repoData = await repoResponse.json();
                console.log('✅ Repository found!');
                console.log('Repository name:', repoData.name);
                console.log('Repository owner:', repoData.owner.login);
                console.log('Default branch:', repoData.default_branch);
                
                // Test file access
                console.log('\n3️⃣ Testing abai.csv file access...');
                const fileResponse = await fetch(`https://api.github.com/repos/${userData.login}/Outstanding/contents/abai.csv`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `token ${GITHUB_TOKEN}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': 'Netlify-Function-Debug'
                    }
                });
                
                console.log('File access status:', fileResponse.status);
                
                if (fileResponse.ok) {
                    const fileData = await fileResponse.json();
                    console.log('✅ File access successful!');
                    console.log('File SHA:', fileData.sha);
                    console.log('File size:', fileData.size);
                    
                    // Try to decode content
                    const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
                    console.log('File content preview:', content.substring(0, 100) + '...');
                } else {
                    const errorText = await fileResponse.text();
                    console.error('❌ File access error:', errorText);
                }
            } else {
                const errorText = await repoResponse.text();
                console.error('❌ Repository access error:', errorText);
                
                // Try listing user repositories to see what's available
                console.log('\n🔍 Listing available repositories...');
                const reposResponse = await fetch(`https://api.github.com/users/${userData.login}/repos`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `token ${GITHUB_TOKEN}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'User-Agent': 'Netlify-Function-Debug'
                    }
                });
                
                if (reposResponse.ok) {
                    const repos = await reposResponse.json();
                    console.log('Available repositories:');
                    repos.slice(0, 10).forEach(repo => {
                        console.log(`  - ${repo.name} (${repo.private ? 'private' : 'public'})`);
                    });
                }
            }
        } else {
            const errorText = await userResponse.text();
            console.error('❌ Token validation failed:', errorText);
        }
        
    } catch (error) {
        console.error('❌ GitHub API test failed with exception:', error.message);
    }
}

// Run the enhanced test
testGitHubAccess();