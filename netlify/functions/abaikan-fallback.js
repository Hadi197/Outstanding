const fs = require('fs').promises;
const path = require('path');

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

  // GitHub API Configuration
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const GITHUB_REPO = process.env.GITHUB_REPO || 'Hadi197/Outstanding';
  const GITHUB_FILE_PATH = 'abai.csv';
  const GITHUB_API_BASE = 'https://api.github.com';

  console.log('GitHub Token available:', !!GITHUB_TOKEN);
  console.log('GitHub Repo:', GITHUB_REPO);

  // Helper function to get file from GitHub
  async function getFileFromGitHub() {
    if (!GITHUB_TOKEN) {
      console.log('No GitHub token available');
      return { content: '', sha: null, exists: false, error: 'No GitHub token' };
    }

    try {
      console.log('Fetching from GitHub...');
      const response = await fetch(
        `${GITHUB_API_BASE}/repos/${GITHUB_REPO}/contents/${GITHUB_FILE_PATH}`,
        {
          headers: {
            'Authorization': `Bearer ${GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Outstanding-Dashboard'
          }
        }
      );

      console.log('GitHub API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        const content = Buffer.from(data.content, 'base64').toString('utf-8');
        console.log('Successfully fetched from GitHub, content length:', content.length);
        return { content, sha: data.sha, exists: true };
      } else if (response.status === 404) {
        console.log('File not found in GitHub, will create new');
        return { content: '', sha: null, exists: false };
      } else {
        const errorText = await response.text();
        console.log('GitHub API error:', response.status, errorText);
        throw new Error(`GitHub API error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Error fetching from GitHub:', error);
      return { content: '', sha: null, exists: false, error: error.message };
    }
  }

  // Helper function to update file in GitHub
  async function updateFileInGitHub(content, sha = null) {
    if (!GITHUB_TOKEN) {
      console.log('No GitHub token for update');
      return { success: false, error: 'No GitHub token' };
    }

    try {
      console.log('Updating GitHub file...');
      const body = {
        message: `Update abai.csv - ${new Date().toISOString()}`,
        content: Buffer.from(content).toString('base64'),
        branch: 'main'
      };

      if (sha) {
        body.sha = sha;
      }

      const response = await fetch(
        `${GITHUB_API_BASE}/repos/${GITHUB_REPO}/contents/${GITHUB_FILE_PATH}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'Outstanding-Dashboard'
          },
          body: JSON.stringify(body)
        }
      );

      console.log('GitHub update response status:', response.status);

      if (response.ok) {
        const result = await response.json();
        console.log('Successfully updated GitHub');
        return { success: true, sha: result.content.sha };
      } else {
        const errorText = await response.text();
        console.log('GitHub update error:', response.status, errorText);
        return { success: false, error: `GitHub update failed: ${response.status}` };
      }
    } catch (error) {
      console.error('Error updating GitHub:', error);
      return { success: false, error: error.message };
    }
  }

  // Handle GET request - status check and get abai data
  if (event.httpMethod === 'GET') {
    try {
      const url = new URL(event.rawUrl || `https://example.com${event.path}`);
      const action = url.searchParams.get('action');

      if (action === 'list') {
        // Return list of abai data for frontend filtering
        console.log('Getting abai list...');
        
        const fileData = await getFileFromGitHub();
        const abaiList = [];

        if (fileData.exists && fileData.content) {
          console.log('Processing GitHub content for list...');
          const lines = fileData.content.split('\n').filter(line => line.trim());
          for (let i = 1; i < lines.length; i++) { // Skip header
            const columns = lines[i].split(',');
            if (columns.length > 0 && columns[0].trim()) {
              abaiList.push(columns[0].trim());
            }
          }
        }

        console.log('Returning abai list:', abaiList.length, 'items');
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            abai_list: abaiList,
            total_entries: abaiList.length,
            source: fileData.exists ? 'github' : 'empty',
            github_available: !!GITHUB_TOKEN,
            error: fileData.error || null
          })
        };
      }

      // Regular status check
      let totalEntries = 0;
      let source = 'empty';

      if (GITHUB_TOKEN) {
        const fileData = await getFileFromGitHub();
        if (fileData.exists && fileData.content) {
          const lines = fileData.content.split('\n').filter(line => line.trim());
          totalEntries = Math.max(0, lines.length - 1);
          source = 'github';
        }
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'running',
          storage_type: GITHUB_TOKEN ? 'persistent (GitHub)' : 'fallback (localStorage)',
          total_entries: totalEntries,
          timestamp: new Date().toISOString(),
          github_configured: !!GITHUB_TOKEN,
          source: source,
          message: GITHUB_TOKEN ? 'GitHub integration active' : 'Using fallback storage - setup GitHub token for persistence'
        }),
      };
    } catch (error) {
      console.error('GET request error:', error);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: error.message,
          github_available: !!GITHUB_TOKEN
        }),
      };
    }
  }

  // Handle POST request - abaikan data
  if (event.httpMethod === 'POST') {
    try {
      const data = JSON.parse(event.body);
      console.log('POST request data:', data);
      
      if (!data.no_pkk_inaportnet) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ error: 'Missing no_pkk_inaportnet' }),
        };
      }

      const timestamp = data.timestamp || new Date().toISOString();
      let success = false;
      let storageType = 'fallback';
      let message = '';

      // Try GitHub first if token available
      if (GITHUB_TOKEN) {
        try {
          console.log('Attempting GitHub storage...');
          const fileData = await getFileFromGitHub();
          let csvContent = fileData.content;
          
          // Check for duplicates
          if (csvContent && csvContent.includes(data.no_pkk_inaportnet)) {
            console.log('Duplicate found in GitHub');
            return {
              statusCode: 200,
              headers,
              body: JSON.stringify({
                status: 'success',
                message: 'Data sudah ada dalam abai.csv (GitHub)',
                no_pkk_inaportnet: data.no_pkk_inaportnet,
                timestamp: timestamp,
                storage_type: 'persistent (GitHub)',
                persistent: true
              }),
            };
          }

          // Prepare CSV content
          if (!fileData.exists || !csvContent) {
            csvContent = 'no_pkk_inaportnet,timestamp,status\n';
          }
          csvContent += `${data.no_pkk_inaportnet},${timestamp},diabaikan\n`;

          // Update GitHub
          const updateResult = await updateFileInGitHub(csvContent, fileData.sha);
          if (updateResult.success) {
            success = true;
            storageType = 'persistent (GitHub)';
            message = 'Data tersimpan permanen di GitHub';
            console.log('Successfully saved to GitHub');
          } else {
            console.log('GitHub save failed:', updateResult.error);
            throw new Error(updateResult.error);
          }
        } catch (error) {
          console.error('GitHub operation failed:', error);
          success = false;
          message = `GitHub gagal: ${error.message}. Data akan disimpan di localStorage.`;
        }
      }

      // If GitHub failed or not available, indicate localStorage usage
      if (!success) {
        storageType = 'fallback (localStorage)';
        message = GITHUB_TOKEN ? 
          'GitHub tidak tersedia, gunakan localStorage untuk sementara' : 
          'Menggunakan localStorage (setup GitHub token untuk persistence)';
        success = true; // We'll handle it in frontend
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'success',
          message: message,
          no_pkk_inaportnet: data.no_pkk_inaportnet,
          timestamp: timestamp,
          storage_type: storageType,
          persistent: storageType.includes('GitHub'),
          use_localstorage: !storageType.includes('GitHub'),
          github_available: !!GITHUB_TOKEN
        }),
      };

    } catch (error) {
      console.error('POST request error:', error);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: error.message,
          github_available: !!GITHUB_TOKEN
        }),
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: 'Method not allowed' }),
  };
};