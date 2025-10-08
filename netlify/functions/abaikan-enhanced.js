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

  // POST - Abaikan data
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