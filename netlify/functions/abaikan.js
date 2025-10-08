exports.handler = async (event, context) => {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  // Enhanced logging for debugging
  console.log('Function called:', {
    method: event.httpMethod,
    path: event.path,
    query: event.queryStringParameters
  });

  // GitHub configuration with your token
  const GITHUB_TOKEN = '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';
  const GITHUB_OWNER = 'Hadi197';
  const GITHUB_REPO = 'Outstanding';
  const FILE_PATH = 'abai.csv';

  // Validate GitHub token exists
  if (!GITHUB_TOKEN || GITHUB_TOKEN.length < 10) {
    console.error('Invalid GitHub token');
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'GitHub token configuration invalid',
        debug: 'Token missing or malformed'
      })
    };
  }

  // Helper function to get file content from GitHub
  async function getGitHubFile() {
    try {
      console.log('Attempting to fetch GitHub file:', `${GITHUB_OWNER}/${GITHUB_REPO}/${FILE_PATH}`);
      
      const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${FILE_PATH}`;
      const fetchOptions = {
        headers: {
          'Authorization': `token ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'Outstanding-Dashboard'
        }
      };

      console.log('Making request to GitHub API:', url);
      
      const response = await fetch(url, fetchOptions);
      
      console.log('GitHub API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        const content = Buffer.from(data.content, 'base64').toString('utf-8');
        console.log('Successfully retrieved file, content length:', content.length);
        return { content, sha: data.sha, exists: true };
      } else if (response.status === 404) {
        console.log('File does not exist yet (404), will create new file');
        return { content: '', sha: null, exists: false };
      } else {
        const errorText = await response.text();
        console.error('GitHub API error:', response.status, errorText);
        throw new Error(`GitHub API error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Error in getGitHubFile:', error.message, error.stack);
      throw error;
    }
  }

  // Helper function to update file in GitHub
  async function updateGitHubFile(content, sha = null) {
    try {
      console.log('Attempting to update GitHub file, content length:', content.length);
      
      const body = {
        message: `Update abai.csv - ${new Date().toISOString()}`,
        content: Buffer.from(content).toString('base64'),
        branch: 'main'
      };

      if (sha) {
        body.sha = sha;
        console.log('Using existing file SHA:', sha);
      } else {
        console.log('Creating new file (no SHA provided)');
      }

      const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${FILE_PATH}`;
      const fetchOptions = {
        method: 'PUT',
        headers: {
          'Authorization': `token ${GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'User-Agent': 'Outstanding-Dashboard'
        },
        body: JSON.stringify(body)
      };

      console.log('Making PUT request to GitHub API:', url);

      const response = await fetch(url, fetchOptions);
      
      console.log('GitHub update response status:', response.status);

      if (response.ok) {
        const result = await response.json();
        console.log('Successfully updated GitHub file, new SHA:', result.content.sha);
        return result;
      } else {
        const errorText = await response.text();
        console.error('GitHub update error:', response.status, errorText);
        throw new Error(`Failed to update GitHub file: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Error in updateGitHubFile:', error.message, error.stack);
      throw error;
    }
  }

  // Handle GET request - return list of abai data or status
  if (event.httpMethod === 'GET') {
    try {
      const queryParams = event.queryStringParameters || {};
      const action = queryParams.action;

      if (action === 'list') {
        // Get abai list for frontend filtering
        try {
          console.log('📂 Attempting to get GitHub file for list action...');
          const fileData = await getGitHubFile();
          console.log('📄 GitHub file data received:', { 
            exists: fileData.exists, 
            contentLength: fileData.content ? fileData.content.length : 0 
          });
          
          const abaiList = [];

          if (fileData.exists && fileData.content) {
            const lines = fileData.content.split('\n').filter(line => line.trim());
            console.log(`📋 Processing ${lines.length} lines from GitHub file...`);
            
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i].trim();
              if (line && !line.toLowerCase().includes('no_pkk_inaportnet')) {
                // Extract PKK number (first column)
                const columns = line.split(',');
                if (columns.length > 0 && columns[0].trim()) {
                  abaiList.push(columns[0].trim());
                }
              }
            }
            console.log(`✅ Extracted ${abaiList.length} PKK entries from GitHub`);
          } else {
            console.log('⚠️ GitHub file does not exist or has no content');
          }

          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              abai_list: abaiList,
              total_entries: abaiList.length,
              source: 'github',
              success: true
            })
          };
        } catch (error) {
          console.error('❌ Error getting abai list from GitHub:', error.message);
          console.error('❌ Full error:', error);
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              abai_list: [],
              total_entries: 0,
              source: 'github_error',
              success: false,
              error: error.message,
              github_token_configured: !!GITHUB_TOKEN,
              debug: {
                owner: GITHUB_OWNER,
                repo: GITHUB_REPO,
                file: FILE_PATH,
                timestamp: new Date().toISOString()
              }
            })
          };
        }
      }

      // Regular status check
      try {
        const fileData = await getGitHubFile();
        let totalEntries = 0;

        if (fileData.exists) {
          const lines = fileData.content.split('\n').filter(line => line.trim());
          totalEntries = Math.max(0, lines.length - (lines[0] && lines[0].toLowerCase().includes('no_pkk_inaportnet') ? 1 : 0));
        }

        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            status: 'running',
            storage_type: 'persistent (GitHub)',
            total_entries: totalEntries,
            timestamp: new Date().toISOString(),
            github_configured: true,
            source: 'github'
          })
        };
      } catch (error) {
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            status: 'error',
            storage_type: 'unavailable',
            total_entries: 0,
            timestamp: new Date().toISOString(),
            github_configured: false,
            error: error.message
          })
        };
      }
    } catch (error) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: error.message })
      };
    }
  }

  // Handle POST request - add abaikan data
  if (event.httpMethod === 'POST') {
    try {
      console.log('Processing POST request for abaikan');
      
      // Validate request body
      if (!event.body) {
        console.error('No request body provided');
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Request body is required',
            debug: 'No POST data received'
          })
        };
      }

      let data;
      try {
        data = JSON.parse(event.body);
        console.log('Parsed request data:', { no_pkk_inaportnet: data.no_pkk_inaportnet });
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Invalid JSON in request body',
            debug: parseError.message
          })
        };
      }
      
      if (!data.no_pkk_inaportnet) {
        console.error('Missing no_pkk_inaportnet in request');
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Missing no_pkk_inaportnet',
            debug: 'Required field not provided'
          })
        };
      }

      const timestamp = data.timestamp || new Date().toISOString();
      console.log('Processing abaikan for PKK:', data.no_pkk_inaportnet);
      
      try {
        // Get current file content from GitHub
        console.log('Fetching current GitHub file...');
        const fileData = await getGitHubFile();
        let csvContent = fileData.content || '';
        console.log('Retrieved file data, exists:', fileData.exists, 'content length:', csvContent.length);
        
        // Check for duplicates
        if (csvContent && csvContent.includes(data.no_pkk_inaportnet)) {
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              status: 'success',
              message: 'Data sudah ada dalam abai.csv (GitHub)',
              no_pkk_inaportnet: data.no_pkk_inaportnet,
              timestamp: timestamp,
              storage_type: 'persistent (GitHub)',
              persistent: true,
              duplicate: true
            })
          };
        }

        // Prepare CSV content
        if (!csvContent || csvContent.trim() === '') {
          csvContent = 'no_pkk_inaportnet,timestamp,status\n';
        } else if (!csvContent.endsWith('\n')) {
          csvContent += '\n';
        }
        
        csvContent += `${data.no_pkk_inaportnet},${timestamp},diabaikan\n`;

        // Update GitHub file
        const result = await updateGitHubFile(csvContent, fileData.sha);
        
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            status: 'success',
            message: 'Data berhasil disimpan ke GitHub repository',
            no_pkk_inaportnet: data.no_pkk_inaportnet,
            timestamp: timestamp,
            storage_type: 'persistent (GitHub)',
            persistent: true,
            duplicate: false,
            github_commit: result.commit.sha
          })
        };

      } catch (error) {
        console.error('GitHub operation failed:', error);
        return {
          statusCode: 500,
          headers,
          body: JSON.stringify({
            status: 'error',
            message: 'Gagal menyimpan ke GitHub: ' + error.message,
            no_pkk_inaportnet: data.no_pkk_inaportnet,
            timestamp: timestamp,
            storage_type: 'failed',
            persistent: false,
            error: error.message
          })
        };
      }

    } catch (error) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: error.message })
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: 'Method not allowed' }),
  };
};