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

  // Helper function to get file from GitHub
  async function getFileFromGitHub() {
    try {
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

      if (response.ok) {
        const data = await response.json();
        const content = Buffer.from(data.content, 'base64').toString('utf-8');
        return { content, sha: data.sha, exists: true };
      } else if (response.status === 404) {
        return { content: '', sha: null, exists: false };
      } else {
        throw new Error(`GitHub API error: ${response.status}`);
      }
    } catch (error) {
      console.error('Error fetching from GitHub:', error);
      return { content: '', sha: null, exists: false };
    }
  }

  // Helper function to update file in GitHub
  async function updateFileInGitHub(content, sha = null) {
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

      return response.ok;
    } catch (error) {
      console.error('Error updating GitHub:', error);
      return false;
    }
  }

  // Handle GET request - status check and get abai data
  if (event.httpMethod === 'GET') {
    try {
      // Check if requesting abai data list
      const url = new URL(event.rawUrl || `https://example.com${event.path}`);
      const action = url.searchParams.get('action');

      if (action === 'list') {
        // Return list of abai data for frontend filtering
        if (!GITHUB_TOKEN) {
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              abai_list: [],
              source: 'no-github-token'
            })
          };
        }

        const fileData = await getFileFromGitHub();
        const abaiList = [];

        if (fileData.exists && fileData.content) {
          const lines = fileData.content.split('\n').filter(line => line.trim());
          for (let i = 1; i < lines.length; i++) { // Skip header
            const columns = lines[i].split(',');
            if (columns.length > 0 && columns[0].trim()) {
              abaiList.push(columns[0].trim());
            }
          }
        }

        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            abai_list: abaiList,
            total_entries: abaiList.length,
            source: 'github'
          })
        };
      }

      // Regular status check
      let totalEntries = 0;
      let source = 'local';

      if (GITHUB_TOKEN) {
        const fileData = await getFileFromGitHub();
        if (fileData.exists) {
          const lines = fileData.content.split('\n').filter(line => line.trim());
          totalEntries = Math.max(0, lines.length - 1);
          source = 'github';
        }
      } else {
        // Fallback to local storage for development
        const csvPath = path.join('/tmp', 'abai.csv');
        try {
          const data = await fs.readFile(csvPath, 'utf8');
          const lines = data.split('\n').filter(line => line.trim());
          totalEntries = Math.max(0, lines.length - 1);
        } catch (error) {
          totalEntries = 0;
        }
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'running',
          storage_type: GITHUB_TOKEN ? 'persistent (GitHub)' : 'temporary (local)',
          total_entries: totalEntries,
          timestamp: new Date().toISOString(),
          github_configured: !!GITHUB_TOKEN,
          source: source
        }),
      };
    } catch (error) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: error.message }),
      };
    }
  }

  // Handle POST request - abaikan data
  if (event.httpMethod === 'POST') {
    try {
      const data = JSON.parse(event.body);
      
      if (!data.no_pkk_inaportnet) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ error: 'Missing no_pkk_inaportnet' }),
        };
      }

      const timestamp = data.timestamp || new Date().toISOString();
      let success = false;
      let storageType = 'local';

      // Try GitHub first if token available
      if (GITHUB_TOKEN) {
        try {
          const fileData = await getFileFromGitHub();
          let csvContent = fileData.content;
          
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
                storage_type: 'persistent (GitHub)'
              }),
            };
          }

          // Prepare CSV content
          if (!fileData.exists || !csvContent) {
            csvContent = 'no_pkk_inaportnet,timestamp,status\n';
          }
          csvContent += `${data.no_pkk_inaportnet},${timestamp},diabaikan\n`;

          // Update GitHub
          success = await updateFileInGitHub(csvContent, fileData.sha);
          storageType = 'persistent (GitHub)';
        } catch (error) {
          console.error('GitHub update failed, falling back to local:', error);
          success = false;
        }
      }

      // Fallback to local storage
      if (!success) {
        const csvPath = path.join('/tmp', 'abai.csv');
        
        // Check if file exists
        let fileExists = false;
        try {
          await fs.access(csvPath);
          fileExists = true;
        } catch (error) {
          fileExists = false;
        }

        // Check for duplicates if file exists
        if (fileExists) {
          const existingData = await fs.readFile(csvPath, 'utf8');
          if (existingData.includes(data.no_pkk_inaportnet)) {
            return {
              statusCode: 200,
              headers,
              body: JSON.stringify({
                status: 'success',
                message: 'Data sudah ada dalam abai.csv (local)',
                no_pkk_inaportnet: data.no_pkk_inaportnet,
                timestamp: timestamp,
                storage_type: 'temporary (local)'
              }),
            };
          }
        }

        // Prepare CSV content
        let csvContent = '';
        if (!fileExists) {
          csvContent = 'no_pkk_inaportnet,timestamp,status\n';
        }
        csvContent += `${data.no_pkk_inaportnet},${timestamp},diabaikan\n`;

        // Append to local file
        await fs.appendFile(csvPath, csvContent);
        success = true;
        storageType = 'temporary (local)';
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'success',
          message: `Data berhasil ditambahkan ke abai.csv (${storageType})`,
          no_pkk_inaportnet: data.no_pkk_inaportnet,
          timestamp: timestamp,
          storage_type: storageType,
          persistent: storageType.includes('GitHub')
        }),
      };

    } catch (error) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: error.message }),
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: 'Method not allowed' }),
  };
};