// Enhanced version dengan GitHub integration untuk data persistence
const fs = require('fs').promises;
const path = require('path');

// Environment variables untuk GitHub integration (opsional)
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO || 'Hadi197/Outstanding';

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // GET - Status check
  if (event.httpMethod === 'GET') {
    try {
      // Try to read from local temp first
      let totalEntries = 0;
      const csvPath = path.join('/tmp', 'abai.csv');
      
      try {
        const data = await fs.readFile(csvPath, 'utf8');
        const lines = data.split('\n').filter(line => line.trim());
        totalEntries = Math.max(0, lines.length - 1);
      } catch (error) {
        totalEntries = 0;
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'running',
          environment: 'netlify',
          csv_file: csvPath,
          total_entries: totalEntries,
          timestamp: new Date().toISOString(),
          github_integration: !!GITHUB_TOKEN,
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

  // POST - Abaikan data or Keterangan
  if (event.httpMethod === 'POST') {
    try {
      const data = JSON.parse(event.body);
      console.log('📨 POST request received:', JSON.stringify(data));
      
      // Handle keterangan GET action - read from GitHub
      if (data.action === 'get_keterangan') {
        console.log('🔀 Routing to handleGetKeterangan');
        return await handleGetKeterangan(headers);
      }
      
      // Handle keterangan SAVE action - must return immediately
      if (data.action === 'save_keterangan') {
        console.log('🔀 Routing to handleSaveKeterangan');
        return await handleSaveKeterangan(data, headers);
      }
      
      // Handle abaikan (original logic) - only if not keterangan
      console.log('🔀 Routing to abaikan handler');
      if (!data.no_pkk_inaportnet) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Missing no_pkk_inaportnet',
            debug: 'Required field not provided'
          }),
        };
      }

      const csvPath = path.join('/tmp', 'abai.csv');
      const timestamp = data.timestamp || new Date().toISOString();
      
      // Read existing data
      let existingData = '';
      let fileExists = false;
      
      try {
        existingData = await fs.readFile(csvPath, 'utf8');
        fileExists = true;
      } catch (error) {
        fileExists = false;
      }

      // Check for duplicates
      if (fileExists && existingData.includes(data.no_pkk_inaportnet)) {
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            status: 'success',
            message: 'Data sudah ada dalam abai.csv',
            no_pkk_inaportnet: data.no_pkk_inaportnet,
            timestamp: timestamp,
            duplicate: true,
          }),
        };
      }

      // Prepare new entry
      let csvContent = existingData;
      if (!fileExists) {
        csvContent = 'no_pkk_inaportnet,timestamp,status\n';
      }
      csvContent += `${data.no_pkk_inaportnet},${timestamp},diabaikan\n`;

      // Write to temp file
      await fs.writeFile(csvPath, csvContent);

      // Optional: Commit to GitHub (if token available)
      let githubSyncStatus = 'disabled';
      if (GITHUB_TOKEN) {
        try {
          await syncToGitHub(csvContent);
          githubSyncStatus = 'success';
        } catch (error) {
          console.error('GitHub sync failed:', error);
          githubSyncStatus = 'failed';
        }
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'success',
          message: 'Data berhasil ditambahkan ke abai.csv',
          no_pkk_inaportnet: data.no_pkk_inaportnet,
          timestamp: timestamp,
          github_sync: githubSyncStatus,
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

// Handler to GET keterangan directly from GitHub (bypass static file cache)
async function handleGetKeterangan(headers) {
  try {
    console.log('📖 handleGetKeterangan: Reading from GitHub...');
    
    if (!GITHUB_TOKEN) {
      // Fallback to local /tmp if no GitHub token
      const csvPath = path.join('/tmp', 'keterangan.csv');
      try {
        const csvContent = await fs.readFile(csvPath, 'utf8');
        const lines = csvContent.split('\n');
        const keteranganData = {};
        
        for (let i = 1; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;
          const match = line.match(/^"([^"]*)","([^"]*)","([^"]*)"$/);
          if (match) {
            const key = match[2] || match[1];
            keteranganData[key] = match[3];
          }
        }
        
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(keteranganData),
        };
      } catch (error) {
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({}), // Empty object if file doesn't exist
        };
      }
    }
    
    // Read directly from GitHub
    const { Octokit } = require('@octokit/rest');
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    
    try {
      const { data } = await octokit.rest.repos.getContent({
        owner: GITHUB_REPO.split('/')[0],
        repo: GITHUB_REPO.split('/')[1],
        path: 'keterangan.csv',
      });
      
      // Decode base64 content
      const csvContent = Buffer.from(data.content, 'base64').toString('utf8');
      const lines = csvContent.split('\n');
      const keteranganData = {};
      
      // Parse CSV (3 columns: PKK, no_pkk_inaportnet, keterangan)
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const match = line.match(/^"([^"]*)","([^"]*)","([^"]*)"$/);
        if (match) {
          const key = match[2] || match[1]; // Use pkk_inaportnet if exists, else PKK
          keteranganData[key] = match[3];
        }
      }
      
      console.log(`✅ Loaded ${Object.keys(keteranganData).length} keterangan from GitHub`);
      
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(keteranganData),
      };
      
    } catch (error) {
      if (error.status === 404) {
        // File doesn't exist yet
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({}),
        };
      }
      throw error;
    }
    
  } catch (error) {
    console.error('❌ Error in handleGetKeterangan:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: error.message,
        stack: error.stack 
      }),
    };
  }
}

// Handle save keterangan
async function handleSaveKeterangan(data, headers) {
  try {
    console.log('📝 handleSaveKeterangan called with:', JSON.stringify(data));
    
    if (!data.pkk && !data.pkk_inaportnet) {
      console.error('❌ Missing PKK or pkk_inaportnet in data:', data);
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Missing PKK or pkk_inaportnet', received: data }),
      };
    }

    const csvPath = path.join('/tmp', 'keterangan.csv');
    const keterangan = data.keterangan || '';
    const pkk = data.pkk || '';
    const pkkInaportnet = data.pkk_inaportnet || '';
    
    console.log(`💾 Saving keterangan - PKK: ${pkk}, PKK_Inaportnet: ${pkkInaportnet}, keterangan: "${keterangan}"`);
    
    // Read existing keterangan (now with 3 columns)
    let existingData = {};
    try {
      const csvContent = await fs.readFile(csvPath, 'utf8');
      const lines = csvContent.split('\n');
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const match = line.match(/^"([^"]*)","([^"]*)","([^"]*)"$/);
        if (match) {
          const key = match[2] || match[1]; // Use pkk_inaportnet if exists, else PKK
          existingData[key] = {
            pkk: match[1],
            pkk_inaportnet: match[2],
            keterangan: match[3]
          };
        }
      }
    } catch (error) {
      // File doesn't exist yet
    }

    // Determine the key to use
    const key = pkkInaportnet || pkk;

    // Update or delete
    if (keterangan.trim()) {
      existingData[key] = {
        pkk: pkk,
        pkk_inaportnet: pkkInaportnet,
        keterangan: keterangan.trim()
      };
    } else {
      delete existingData[key];
    }

    // Write back to CSV with 3 columns
    let csvContent = 'PKK,no_pkk_inaportnet,keterangan\n';
    for (const [k, v] of Object.entries(existingData).sort()) {
      csvContent += `"${v.pkk}","${v.pkk_inaportnet}","${v.keterangan}"\n`;
    }

    await fs.writeFile(csvPath, csvContent);

    // Optional: Sync to GitHub
    let githubSyncStatus = 'disabled';
    if (GITHUB_TOKEN) {
      try {
        await syncKeteranganToGitHub(csvContent);
        githubSyncStatus = 'success';
      } catch (error) {
        console.error('GitHub sync failed:', error);
        githubSyncStatus = 'failed';
      }
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Keterangan saved successfully',
        pkk: pkk,
        pkk_inaportnet: pkkInaportnet,
        keterangan: keterangan,
        github_sync: githubSyncStatus,
      }),
    };

  } catch (error) {
    console.error('❌ Error in handleSaveKeterangan:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: error.message,
        stack: error.stack,
        data: data 
      }),
    };
  }
}

// Optional GitHub sync function
async function syncToGitHub(csvContent) {
  if (!GITHUB_TOKEN) return;
  
  const { Octokit } = require('@octokit/rest');
  const octokit = new Octokit({ auth: GITHUB_TOKEN });

  // Get current file SHA (if exists)
  let sha = null;
  try {
    const { data } = await octokit.rest.repos.getContent({
      owner: GITHUB_REPO.split('/')[0],
      repo: GITHUB_REPO.split('/')[1],
      path: 'abai.csv',
    });
    sha = data.sha;
  } catch (error) {
    // File doesn't exist yet
  }

  // Update or create file
  await octokit.rest.repos.createOrUpdateFileContents({
    owner: GITHUB_REPO.split('/')[0],
    repo: GITHUB_REPO.split('/')[1],
    path: 'abai.csv',
    message: `Update abai.csv - ${new Date().toISOString()}`,
    content: Buffer.from(csvContent).toString('base64'),
    sha: sha,
  });
}

// Sync keterangan to GitHub
async function syncKeteranganToGitHub(csvContent) {
  if (!GITHUB_TOKEN) return;
  
  const { Octokit } = require('@octokit/rest');
  const octokit = new Octokit({ auth: GITHUB_TOKEN });

  // Get current file SHA (if exists)
  let sha = null;
  try {
    const { data } = await octokit.rest.repos.getContent({
      owner: GITHUB_REPO.split('/')[0],
      repo: GITHUB_REPO.split('/')[1],
      path: 'keterangan.csv',
    });
    sha = data.sha;
  } catch (error) {
    // File doesn't exist yet
  }

  // Update or create file
  await octokit.rest.repos.createOrUpdateFileContents({
    owner: GITHUB_REPO.split('/')[0],
    repo: GITHUB_REPO.split('/')[1],
    path: 'keterangan.csv',
    message: `Update keterangan.csv - ${new Date().toISOString()}`,
    content: Buffer.from(csvContent).toString('base64'),
    sha: sha,
  });
}