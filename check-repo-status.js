// Test repository creation and access permissions
const GITHUB_TOKEN = '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';

async function checkRepositoryStatus() {
    console.log('🔍 Checking repository status and permissions...');
    
    try {
        // Check if we can access private repos
        console.log('\n1️⃣ Checking private repository access...');
        const reposResponse = await fetch('https://api.github.com/user/repos?type=all&per_page=50', {
            method: 'GET',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Netlify-Function-Debug'
            }
        });
        
        console.log('User repos API status:', reposResponse.status);
        
        if (reposResponse.ok) {
            const repos = await reposResponse.json();
            console.log(`Found ${repos.length} repositories:`);
            
            // Look for Outstanding repository
            const outstandingRepo = repos.find(repo => 
                repo.name.toLowerCase().includes('outstanding') || 
                repo.name === 'Outstanding'
            );
            
            if (outstandingRepo) {
                console.log('✅ Outstanding repository found!');
                console.log('Repository details:');
                console.log(`  Name: ${outstandingRepo.name}`);
                console.log(`  Full name: ${outstandingRepo.full_name}`);
                console.log(`  Private: ${outstandingRepo.private}`);
                console.log(`  Default branch: ${outstandingRepo.default_branch}`);
                console.log(`  URL: ${outstandingRepo.html_url}`);
                
                // Try to access the file in this repo
                console.log('\n2️⃣ Testing file access in found repository...');
                const fileResponse = await fetch(`https://api.github.com/repos/${outstandingRepo.full_name}/contents/abai.csv`, {
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
                    console.log(`File SHA: ${fileData.sha}`);
                    console.log(`File size: ${fileData.size} bytes`);
                } else {
                    const errorText = await fileResponse.text();
                    console.log('❌ File access failed:', errorText);
                    
                    // List all files in root directory
                    console.log('\n3️⃣ Listing root directory contents...');
                    const contentsResponse = await fetch(`https://api.github.com/repos/${outstandingRepo.full_name}/contents`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `token ${GITHUB_TOKEN}`,
                            'Accept': 'application/vnd.github.v3+json',
                            'User-Agent': 'Netlify-Function-Debug'
                        }
                    });
                    
                    if (contentsResponse.ok) {
                        const contents = await contentsResponse.json();
                        console.log('Repository root contents:');
                        contents.forEach(item => {
                            console.log(`  ${item.type === 'dir' ? '📁' : '📄'} ${item.name}`);
                        });
                    }
                }
                
            } else {
                console.log('❌ Outstanding repository not found in user repositories');
                console.log('\nAvailable repositories:');
                repos.slice(0, 20).forEach(repo => {
                    console.log(`  - ${repo.name} (${repo.private ? 'private' : 'public'})`);
                });
            }
        } else {
            const errorText = await reposResponse.text();
            console.error('❌ Failed to fetch user repositories:', errorText);
        }
        
    } catch (error) {
        console.error('❌ Repository check failed:', error.message);
    }
}

checkRepositoryStatus();