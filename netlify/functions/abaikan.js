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

  // GitHub configuration with your token
  const GITHUB_TOKEN = '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';
  const GITHUB_OWNER = 'Hadi197';
  const GITHUB_REPO = 'Outstanding';
  const FILE_PATH = 'abai.csv';

  // Helper function to get file content from GitHub
  async function getGitHubFile() {
    try {
      const response = await fetch(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${FILE_PATH}`,
        {
          headers: {
            'Authorization': `token ${GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Outstanding-Dashboard'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        const content = Buffer.from(data.content, 'base64').toString('utf-8');
        return { content, sha: data.sha, exists: true };
      } else if (response.status === 404) {
        return { content: '', sha: null, exists: false };
      } else {
        console.error('GitHub API error:', response.status, await response.text());
        throw new Error(`GitHub API error: ${response.status}`);
      }
    } catch (error) {
      console.error('Error fetching from GitHub:', error);
      throw error;
    }
  }

  // Helper function to update file in GitHub
  async function updateGitHubFile(content, sha = null) {
    try {
      const body = {
        message: `Update abai.csv - ${new Date().toISOString()}`,
        content: Buffer.from(content).toString('base64'),
        branch: 'main'
      };

      if (sha) {
        body.sha = sha;
      }

      const response = await fetch(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${FILE_PATH}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `token ${GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'Outstanding-Dashboard'
          },
          body: JSON.stringify(body)
        }
      );

      if (response.ok) {
        return await response.json();
      } else {
        console.error('GitHub update error:', response.status, await response.text());
        throw new Error(`Failed to update GitHub file: ${response.status}`);
      }
    } catch (error) {
      console.error('Error updating GitHub:', error);
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
          const fileData = await getGitHubFile();
          const abaiList = [];

          if (fileData.exists && fileData.content) {
            const lines = fileData.content.split('\n').filter(line => line.trim());
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
          console.error('Error getting abai list:', error);
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              abai_list: [],
              total_entries: 0,
              source: 'error',
              success: false,
              error: error.message
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
      const data = JSON.parse(event.body);
      
      if (!data.no_pkk_inaportnet) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ error: 'Missing no_pkk_inaportnet' })
        };
      }

      const timestamp = data.timestamp || new Date().toISOString();
      
      try {
        // Get current file content from GitHub
        const fileData = await getGitHubFile();
        let csvContent = fileData.content || '';
        
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