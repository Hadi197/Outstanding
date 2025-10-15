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
  // Use environment variable only; do NOT hardcode tokens in the repository
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
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

      console.log('🔍 GET request - action:', action, 'queryParams:', queryParams);

      // Handle status check (no action parameter)
      if (!action) {
        try {
          const fileData = await getGitHubFile();
          let totalEntries = 0;
          let source = 'netlify_function';
          if (fileData && fileData.exists && fileData.content) {
            const lines = fileData.content.split('\n').filter(l => l.trim());
            if (lines.length && /no_pkk_inaportnet/i.test(lines[0])) {
              totalEntries = Math.max(0, lines.length - 1);
            } else {
              totalEntries = lines.length;
            }
            source = 'github';
          }

          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              status: 'running',
              total_entries: totalEntries,
              source: source,
              success: true,
              message: 'Netlify function is operational'
            })
          };
        } catch (err) {
          console.error('Status handler: failed to read GitHub file for status:', err && err.message);
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              status: 'running',
              total_entries: 0,
              source: 'netlify_function',
              success: true,
              message: 'Netlify function is operational (could not read GitHub)'
            })
          };
        }
      }

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
          const abaiEntries = []; // structured entries for frontend

          if (fileData.exists && fileData.content) {
            const lines = fileData.content.split('\n').filter(line => line.trim());
            console.log(`📋 Processing ${lines.length} lines from GitHub file...`);

            // Parse header to determine column order (CSV may contain quoted fields)
            const splitCsv = (str) => str.split(/,(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)/);

            let headers = [];
            if (lines.length > 0) {
              headers = splitCsv(lines[0]).map(h => h.replace(/^\"|\"$/g, '').trim());
            }

            for (let i = 1; i < lines.length; i++) {
              const line = lines[i].trim();
              if (!line) continue;

              const cols = splitCsv(line).map(c => c.replace(/^\"|\"$/g, '').trim());

              // Build an object using header names when available, otherwise fall back to known ordering
              const entry = {};
              const mapField = (name, idx) => {
                if (headers && headers.length && headers.includes(name)) {
                  return cols[headers.indexOf(name)] || '';
                }
                return cols[idx] || '';
              };

              // Expected columns: no_pkk_inaportnet, Pelabuhan, Alasan, Keterangan, timestamp
              entry.no_pkk_inaportnet = (mapField('no_pkk_inaportnet', 0) || mapField('NO_PKK_INAPORTNET', 0) || mapField('No_PKK_Inaportnet', 0)).toString();
              entry.Pelabuhan = (mapField('Pelabuhan', 1) || mapField('PELABUHAN', 1) || mapField('name_branch', 1) || '').toString();
              entry.Alasan = (mapField('Alasan', 2) || mapField('Reason', 2) || '').toString();
              entry.Keterangan = (mapField('Keterangan', 3) || mapField('Keterangan ', 3) || mapField('notes', 3) || '').toString();
              entry.timestamp = (mapField('timestamp', 4) || mapField('time', 4) || '').toString();

              // Push both structured and simple variants
              if (entry.no_pkk_inaportnet) {
                abaiEntries.push(entry);
                abaiList.push(entry.no_pkk_inaportnet);
              }
            }

            console.log(`✅ Extracted ${abaiList.length} PKK entries from GitHub (detailed: ${abaiEntries.length})`);
          } else {
            console.log('⚠️ GitHub file does not exist or has no content');
          }

          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              abai_list: abaiList,
              abai_entries: abaiEntries,
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

      if (action === 'clear') {
        // Clear all abai data (overwrite file with header) - ensure we pass existing SHA when updating
        try {
          console.log('🗑️ Clearing all abai data from GitHub...');

          // Create empty file with just header
          const emptyContent = 'no_pkk_inaportnet,Pelabuhan,Alasan,Keterangan,timestamp\n';

          // Get existing file to obtain SHA (if it exists)
          const fileData = await getGitHubFile();
          let result;

          if (fileData && fileData.exists && fileData.sha) {
            // Overwrite existing file by providing its SHA
            result = await updateGitHubFile(emptyContent, fileData.sha);
            console.log('🗑️ Overwrote existing abai.csv with header, commit:', result && result.commit && result.commit.sha);
          } else {
            // File does not exist - create it (no sha)
            result = await updateGitHubFile(emptyContent, null);
            console.log('🗑️ Created new abai.csv with header, commit:', result && result.commit && result.commit.sha);
          }

          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              success: true,
              message: 'All abai data cleared',
              total_entries: 0,
              source: 'github',
              github_commit: result && (result.commit ? result.commit.sha : (result.content ? result.content.sha : null))
            })
          };
        } catch (error) {
          console.error('❌ Error clearing abai data:', error && error.message);
          return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
              success: false,
              error: error && error.message,
              message: 'Failed to clear abai data'
            })
          };
        }
      }

      if (action === 'remove') {
        // Remove specific PKK from abai data
        try {
          const pkkToRemove = queryParams.pkk || queryParams.no_pkk_inaportnet;
          
          if (!pkkToRemove) {
            return {
              statusCode: 400,
              headers,
              body: JSON.stringify({
                success: false,
                error: 'Missing pkk parameter',
                message: 'PKK number is required for removal'
              })
            };
          }

          console.log('🗑️ Removing PKK from abai data:', pkkToRemove);

          // Get current file content from GitHub
          const fileData = await getGitHubFile();
          
          if (!fileData.exists || !fileData.content) {
            return {
              statusCode: 200,
              headers,
              body: JSON.stringify({
                success: true,
                message: 'PKK not found (file does not exist)',
                no_pkk_inaportnet: pkkToRemove,
                source: 'github'
              })
            };
          }

          // Parse CSV and filter out the PKK to remove
          const lines = fileData.content.split('\n').filter(line => line.trim());
          const filteredLines = lines.filter(line => {
            if (!line.trim() || line.toLowerCase().includes('no_pkk_inaportnet')) {
              return true; // Keep header and empty lines
            }
            
            const columns = line.split(',');
            if (columns.length > 0 && columns[0].trim() === pkkToRemove.trim()) {
              console.log('🗑️ Removing line:', line);
              return false; // Remove this line
            }
            
            return true; // Keep other lines
          });

          const newContent = filteredLines.join('\n');
          
          // If no lines were removed, the PKK wasn't found
          if (filteredLines.length === lines.length) {
            return {
              statusCode: 200,
              headers,
              body: JSON.stringify({
                success: true,
                message: 'PKK not found in abai.csv',
                no_pkk_inaportnet: pkkToRemove,
                source: 'github'
              })
            };
          }

          // Update GitHub file
          const result = await updateGitHubFile(newContent, fileData.sha);
          
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
              success: true,
              message: 'PKK berhasil dihapus dari abai.csv',
              no_pkk_inaportnet: pkkToRemove,
              total_entries: Math.max(0, filteredLines.length - 1), // Subtract header
              source: 'github',
              github_commit: result.commit.sha
            })
          };
        } catch (error) {
          console.error('❌ Error removing PKK from abai data:', error && error.message);
          return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
              success: false,
              error: error && error.message,
              message: 'Failed to remove PKK from abai data'
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
        
        // Prepare CSV and handle duplicates by updating existing row if present
        if (!csvContent || csvContent.trim() === '') {
          csvContent = 'no_pkk_inaportnet,Pelabuhan,Alasan,Keterangan,timestamp\n';
        } else if (!csvContent.endsWith('\n')) {
          csvContent += '\n';
        }

        // Extract data fields with fallbacks and escape quotes
        const pelabuhan = (data.pelabuhan || '').toString();
        const alasan = (data.reason || '').toString();
        const keterangan = (data.notes || '').toString();
        const esc = s => s.replace(/"/g, '""');

        // Try to update existing PKK row rather than treating as duplicate
        const lines = csvContent.split('\n');
        let updated = false;

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;
          // keep header as-is
          if (/no_pkk_inaportnet/i.test(line)) continue;

          // crude CSV first-column parse (works with exported format "PKK",...)
          const cols = line.split(',');
          const firstCol = cols[0] ? cols[0].replace(/^\"|\"$/g, '').trim() : '';
          if (firstCol === data.no_pkk_inaportnet) {
            // Build updated CSV row preserving quoting
            const newRow = `"${esc(data.no_pkk_inaportnet)}","${esc(pelabuhan)}","${esc(alasan)}","${esc(keterangan)}",${timestamp}`;
            lines[i] = newRow;
            updated = true;
            break;
          }
        }

        let newContent;
        if (updated) {
          newContent = lines.join('\n');
          console.log('🔁 Updating existing PKK row in abai.csv for', data.no_pkk_inaportnet);
        } else {
          // Append new row
          const newRow = `"${esc(data.no_pkk_inaportnet)}","${esc(pelabuhan)}","${esc(alasan)}","${esc(keterangan)}",${timestamp}`;
          newContent = csvContent + newRow + '\n';
          console.log('➕ Appending new PKK row to abai.csv for', data.no_pkk_inaportnet);
        }

  // Update GitHub file using the modified content (newContent)
  const result = await updateGitHubFile(newContent, fileData.sha);
        
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