// Test GitHub API connection for debugging
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = 'Hadi197';
const GITHUB_REPO = 'Outstanding';

async function testGitHubAPI() {
    console.log('🧪 Testing GitHub API connection...');
    
    try {
        // Test repository access
        const repoResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}`, {
            method: 'GET',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Netlify-Function-Debug'
            }
        });
        
        console.log('Repository access status:', repoResponse.status);
        
        if (!repoResponse.ok) {
            const errorText = await repoResponse.text();
            console.error('Repository access error:', errorText);
            return;
        }
        
        // Test file access
        const fileResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/abai.csv`, {
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
            console.log('✅ GitHub API connection successful!');
            console.log('File SHA:', fileData.sha);
            console.log('File size:', fileData.size);
        } else {
            const errorText = await fileResponse.text();
            console.error('File access error:', errorText);
        }
        
    } catch (error) {
        console.error('❌ GitHub API test failed:', error);
    }
}

// Run the test
testGitHubAPI();