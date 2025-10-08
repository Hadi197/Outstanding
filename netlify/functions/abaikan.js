const fs = require('fs').promises;
const path = require('path');

exports.handler = async (event, context) => {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
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

  // Handle GET request - status check
  if (event.httpMethod === 'GET') {
    try {
      const csvPath = path.join('/tmp', 'abai.csv');
      let totalEntries = 0;
      
      try {
        const data = await fs.readFile(csvPath, 'utf8');
        const lines = data.split('\n').filter(line => line.trim());
        totalEntries = Math.max(0, lines.length - 1); // Exclude header
      } catch (error) {
        // File doesn't exist yet
        totalEntries = 0;
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'running',
          csv_file: csvPath,
          total_entries: totalEntries,
          timestamp: new Date().toISOString(),
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

      const csvPath = path.join('/tmp', 'abai.csv');
      const timestamp = data.timestamp || new Date().toISOString();
      
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
              message: 'Data sudah ada dalam abai.csv',
              no_pkk_inaportnet: data.no_pkk_inaportnet,
              timestamp: timestamp,
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

      // Append to file
      await fs.appendFile(csvPath, csvContent);

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'success',
          message: 'Data berhasil ditambahkan ke abai.csv',
          no_pkk_inaportnet: data.no_pkk_inaportnet,
          timestamp: timestamp,
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