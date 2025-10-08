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

  console.log('Simple fallback function called:', {
    method: event.httpMethod,
    path: event.path,
    hasBody: !!event.body
  });

  // Handle GET request - return simple status or abai list
  if (event.httpMethod === 'GET') {
    try {
      const queryParams = event.queryStringParameters || {};
      const action = queryParams.action;

      if (action === 'list') {
        // Return empty list as fallback - client will use localStorage
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            abai_list: [],
            total_entries: 0,
            source: 'fallback',
            success: true,
            message: 'Using localStorage fallback'
          })
        };
      }

      // Regular status check
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'running',
          storage_type: 'fallback (localStorage)',
          total_entries: 0,
          timestamp: new Date().toISOString(),
          github_configured: false,
          source: 'fallback',
          message: 'Using client-side localStorage for persistence'
        })
      };

    } catch (error) {
      console.error('Error in GET handler:', error);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: 'GET request failed',
          details: error.message
        })
      };
    }
  }

  // Handle POST request - simple success response
  if (event.httpMethod === 'POST') {
    try {
      console.log('Processing POST request...');

      if (!event.body) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Request body is required'
          })
        };
      }

      let data;
      try {
        data = JSON.parse(event.body);
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Invalid JSON in request body'
          })
        };
      }
      
      if (!data.no_pkk_inaportnet) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ 
            error: 'Missing no_pkk_inaportnet'
          })
        };
      }

      const timestamp = data.timestamp || new Date().toISOString();
      
      console.log('Fallback: Processing abaikan for PKK:', data.no_pkk_inaportnet);
      
      // Return success - client will handle persistence via localStorage
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'success',
          message: 'Data akan disimpan secara lokal (fallback mode)',
          no_pkk_inaportnet: data.no_pkk_inaportnet,
          timestamp: timestamp,
          storage_type: 'localStorage (fallback)',
          persistent: false,  // Indicates localStorage should be used
          duplicate: false,
          fallback_mode: true
        })
      };

    } catch (error) {
      console.error('Error in POST handler:', error);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ 
          error: 'POST request failed',
          details: error.message
        })
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: 'Method not allowed' })
  };
};