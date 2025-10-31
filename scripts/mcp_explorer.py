#!/usr/bin/env python3
"""
Simple MCP Explorer - Interactive web-based client for exploring MCP servers
"""

import asyncio
import aiohttp
from aiohttp import web
import json
from datetime import datetime

# Store the MCP server URL and session ID
MCP_SERVER_URL = None
MCP_SESSION_ID = None

async def index_handler(request):
    """Serve the main HTML page"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Explorer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .item {
            background: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .item h3 {
            margin: 0 0 10px 0;
            color: #667eea;
        }
        .item-description {
            color: #666;
            margin: 5px 0;
        }
        .item-meta {
            font-size: 12px;
            color: #999;
            margin-top: 10px;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
        }
        .tool-form {
            margin-top: 10px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        .tool-form input, .tool-form textarea {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .tool-form label {
            font-weight: bold;
            color: #333;
            display: block;
            margin-top: 10px;
        }
        .result {
            margin-top: 10px;
            padding: 10px;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            border-radius: 5px;
        }
        .error {
            margin-top: 10px;
            padding: 10px;
            background: #ffebee;
            border-left: 4px solid #f44336;
            border-radius: 5px;
        }
        .loading {
            display: inline-block;
            margin-left: 10px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 10px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 5px;
            cursor: pointer;
            color: #667eea;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 MCP Explorer</h1>
        <p>Interactive explorer for MCP servers</p>
        <div id="connection-status">
            <span id="status-text">Not connected</span>
        </div>
    </div>

    <div class="section">
        <h2>Connection</h2>
        <div style="margin-bottom: 15px;">
            <label for="server-url" style="font-weight: bold; display: block; margin-bottom: 5px;">MCP Server URL:</label>
            <input type="text" id="server-url" placeholder="http://localhost:8000/mcp"
                   style="width: 70%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-right: 10px;">
            <button onclick="connect()">Connect</button>
        </div>
        <div id="current-server" style="color: #666; font-size: 14px; margin-top: 10px;"></div>
        <span id="connect-loading" class="loading" style="display:none;">Connecting...</span>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('prompts')">Prompts</div>
        <div class="tab" onclick="switchTab('tools')">Tools</div>
        <div class="tab" onclick="switchTab('resources')">Resources</div>
    </div>

    <div id="prompts" class="tab-content active">
        <div class="section">
            <h2>Prompts <span class="badge" id="prompts-count">0</span></h2>
            <div id="prompts-list"></div>
        </div>
    </div>

    <div id="tools" class="tab-content">
        <div class="section">
            <h2>Tools <span class="badge" id="tools-count">0</span></h2>
            <div id="tools-list"></div>
        </div>
    </div>

    <div id="resources" class="tab-content">
        <div class="section">
            <h2>Resources <span class="badge" id="resources-count">0</span></h2>
            <div id="resources-list"></div>
        </div>
    </div>

    <script>
        let sessionId = null;

        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        async function connect() {
            const loading = document.getElementById('connect-loading');
            const serverUrlInput = document.getElementById('server-url');
            const serverUrl = serverUrlInput.value.trim();

            if (!serverUrl) {
                alert('Please enter a server URL');
                return;
            }

            loading.style.display = 'inline';

            try {
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ serverUrl: serverUrl })
                });
                const data = await response.json();

                if (data.success) {
                    sessionId = data.sessionId;
                    document.getElementById('status-text').textContent = '✅ Connected';
                    document.getElementById('status-text').style.color = '#4caf50';
                    document.getElementById('current-server').textContent = `Connected to: ${serverUrl}`;

                    // Auto-load all lists
                    await listPrompts();
                    await listTools();
                    await listResources();
                } else {
                    alert('Failed to connect: ' + data.error);
                    document.getElementById('status-text').textContent = '❌ Connection failed';
                    document.getElementById('status-text').style.color = '#f44336';
                }
            } catch (error) {
                alert('Error connecting: ' + error);
                document.getElementById('status-text').textContent = '❌ Connection failed';
                document.getElementById('status-text').style.color = '#f44336';
            } finally {
                loading.style.display = 'none';
            }
        }

        async function listPrompts() {
            const container = document.getElementById('prompts-list');
            container.innerHTML = '<p>Loading...</p>';

            try {
                const response = await fetch('/api/prompts/list');
                const data = await response.json();

                if (data.success) {
                    const prompts = data.prompts;
                    document.getElementById('prompts-count').textContent = prompts.length;

                    if (prompts.length === 0) {
                        container.innerHTML = '<p>No prompts available</p>';
                    } else {
                        container.innerHTML = prompts.map(prompt => `
                            <div class="item">
                                <h3>${prompt.name}</h3>
                                ${prompt.description ? `<div class="item-description">${prompt.description}</div>` : ''}
                                ${prompt.arguments ? `
                                    <div class="item-meta">
                                        Arguments: ${prompt.arguments.map(arg =>
                                            `${arg.name}${arg.required ? '*' : ''} (${arg.description || 'no description'})`
                                        ).join(', ')}
                                    </div>
                                ` : ''}
                                <button onclick="getPrompt('${prompt.name}')">Get Prompt</button>
                            </div>
                        `).join('');
                    }
                } else {
                    container.innerHTML = `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        async function listTools() {
            const container = document.getElementById('tools-list');
            container.innerHTML = '<p>Loading...</p>';

            try {
                const response = await fetch('/api/tools/list');
                const data = await response.json();

                if (data.success) {
                    const tools = data.tools;
                    document.getElementById('tools-count').textContent = tools.length;

                    if (tools.length === 0) {
                        container.innerHTML = '<p>No tools available</p>';
                    } else {
                        container.innerHTML = tools.map((tool, index) => {
                            const schema = tool.inputSchema || {};
                            const properties = schema.properties || {};
                            const required = schema.required || [];

                            // Store tool data globally
                            window[`toolData_${index}`] = { properties, required };

                            return `
                                <div class="item">
                                    <h3>${tool.name}</h3>
                                    ${tool.description ? `<div class="item-description">${tool.description}</div>` : ''}
                                    ${Object.keys(properties).length > 0 ? `
                                        <div class="item-meta">
                                            Parameters: ${Object.entries(properties).map(([name, prop]) =>
                                                `${name}${required.includes(name) ? '*' : ''} (${prop.type || 'any'}${prop.description ? ': ' + prop.description : ''})`
                                            ).join(', ')}
                                        </div>
                                    ` : ''}
                                    <button onclick="showToolForm('${tool.name}', ${index})">
                                        Call Tool
                                    </button>
                                    <div id="tool-form-${tool.name}"></div>
                                    <div id="tool-result-${tool.name}"></div>
                                </div>
                            `;
                        }).join('');
                    }
                } else {
                    container.innerHTML = `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        async function listResources() {
            const container = document.getElementById('resources-list');
            container.innerHTML = '<p>Loading...</p>';

            try {
                const response = await fetch('/api/resources/list');
                const data = await response.json();

                if (data.success) {
                    const resources = data.resources;
                    document.getElementById('resources-count').textContent = resources.length;

                    if (resources.length === 0) {
                        container.innerHTML = '<p>No resources available</p>';
                    } else {
                        container.innerHTML = resources.map(resource => `
                            <div class="item">
                                <h3>${resource.name}</h3>
                                ${resource.description ? `<div class="item-description">${resource.description}</div>` : ''}
                                <div class="item-meta">
                                    URI: <code>${resource.uri}</code>
                                    ${resource.mimeType ? ` | MIME: ${resource.mimeType}` : ''}
                                </div>
                                <button onclick="readResource('${resource.uri}')">Read Resource</button>
                                <div id="resource-result-${btoa(resource.uri)}"></div>
                            </div>
                        `).join('');
                    }
                } else {
                    container.innerHTML = `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                container.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        function showToolForm(toolName, dataIndex) {
            const formContainer = document.getElementById(`tool-form-${toolName}`);

            if (formContainer.innerHTML) {
                // Toggle off
                formContainer.innerHTML = '';
                return;
            }

            const toolData = window[`toolData_${dataIndex}`];
            if (!toolData) {
                formContainer.innerHTML = '<div class="error">Tool data not found</div>';
                return;
            }

            const properties = toolData.properties;
            const required = toolData.required;

            const fields = Object.entries(properties).map(([name, prop]) => {
                const isRequired = required.includes(name);
                const fieldType = prop.type === 'number' || prop.type === 'integer' ? 'number' :
                                 prop.type === 'boolean' ? 'checkbox' : 'text';

                if (prop.type === 'object' || prop.type === 'array') {
                    return `
                        <label>${name}${isRequired ? '*' : ''} (${prop.type}):</label>
                        <textarea id="param-${toolName}-${name}" placeholder='${prop.description || 'Enter JSON'}'></textarea>
                    `;
                } else {
                    return `
                        <label>${name}${isRequired ? '*' : ''} (${prop.type || 'string'}):</label>
                        <input type="${fieldType}" id="param-${toolName}-${name}" placeholder="${prop.description || ''}" />
                    `;
                }
            }).join('');

            // Store param names globally
            window[`toolParams_${toolName}`] = Object.keys(properties);

            formContainer.innerHTML = `
                <div class="tool-form">
                    ${fields}
                    <button onclick="callTool('${toolName}')">Execute</button>
                    <button onclick="document.getElementById('tool-form-${toolName}').innerHTML = ''">Cancel</button>
                </div>
            `;
        }

        async function callTool(toolName) {
            const resultContainer = document.getElementById(`tool-result-${toolName}`);
            resultContainer.innerHTML = '<p>Calling tool...</p>';

            // Get param names from global storage
            const paramNames = window[`toolParams_${toolName}`] || [];

            // Collect parameters
            const params = {};
            paramNames.forEach(name => {
                const input = document.getElementById(`param-${toolName}-${name}`);
                if (input) {
                    let value = input.type === 'checkbox' ? input.checked : input.value;

                    // Try to parse as JSON for objects/arrays
                    if (input.tagName === 'TEXTAREA' && value) {
                        try {
                            value = JSON.parse(value);
                        } catch (e) {
                            // Keep as string if not valid JSON
                        }
                    }

                    if (value !== '' && value !== false) {
                        params[name] = value;
                    }
                }
            });

            try {
                const response = await fetch('/api/tools/call', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: toolName, arguments: params })
                });
                const data = await response.json();

                if (data.success) {
                    resultContainer.innerHTML = `
                        <div class="result">
                            <strong>Result:</strong>
                            <pre>${JSON.stringify(data.result, null, 2)}</pre>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                resultContainer.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        async function getPrompt(promptName) {
            const args = prompt('Enter arguments as JSON (or leave empty):', '{}');
            if (args === null) return;

            try {
                const response = await fetch('/api/prompts/get', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: promptName, arguments: JSON.parse(args) })
                });
                const data = await response.json();

                if (data.success) {
                    // Show the result in a more readable format
                    const result = data.result;
                    let displayText = '';

                    if (result.messages && Array.isArray(result.messages)) {
                        displayText = result.messages.map(msg => {
                            if (msg.role) displayText += `[${msg.role}]\\n`;
                            if (msg.content) {
                                if (typeof msg.content === 'string') {
                                    displayText += msg.content;
                                } else if (msg.content.text) {
                                    displayText += msg.content.text;
                                } else {
                                    displayText += JSON.stringify(msg.content, null, 2);
                                }
                            }
                            return displayText;
                        }).join('\\n\\n');
                    } else {
                        displayText = JSON.stringify(result, null, 2);
                    }

                    alert('Prompt result:\\n\\n' + displayText);
                } else {
                    alert('Error: ' + JSON.stringify(data.error, null, 2));
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }

        async function readResource(uri) {
            const resultContainer = document.getElementById(`resource-result-${btoa(uri)}`);
            resultContainer.innerHTML = '<p>Reading resource...</p>';

            try {
                const response = await fetch('/api/resources/read', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ uri: uri })
                });
                const data = await response.json();

                if (data.success) {
                    resultContainer.innerHTML = `
                        <div class="result">
                            <strong>Content:</strong>
                            <pre>${JSON.stringify(data.result, null, 2)}</pre>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `<div class="error">${data.error}</div>`;
                }
            } catch (error) {
                resultContainer.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        // Set default server URL from backend and auto-connect
        window.onload = async () => {
            try {
                const response = await fetch('/api/server-url');
                const data = await response.json();
                if (data.serverUrl) {
                    document.getElementById('server-url').value = data.serverUrl;
                    connect();
                }
            } catch (error) {
                console.error('Failed to get default server URL:', error);
            }
        };
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')


async def parse_sse_response(response):
    """Parse Server-Sent Events response"""
    text = await response.text()

    # SSE format: data: {json}\n\n
    for line in text.split('\n'):
        if line.startswith('data: '):
            json_str = line[6:]  # Remove 'data: ' prefix
            return json.loads(json_str)

    # If not SSE format, try to parse as plain JSON
    return json.loads(text)


def get_headers_with_session():
    """Get headers with session ID if needed"""
    headers = {
        'Accept': 'text/event-stream, application/json',
        'Content-Type': 'application/json'
    }

    if MCP_SESSION_ID:
        headers['MCP-Session-ID'] = MCP_SESSION_ID

    return headers


async def connect_handler(request):
    """Connect to the MCP server"""
    global MCP_SESSION_ID, MCP_SERVER_URL

    try:
        import uuid

        # Get server URL from request body if provided
        data = await request.json()
        new_server_url = data.get('serverUrl')

        if new_server_url:
            # Update the global server URL
            MCP_SERVER_URL = new_server_url
            # Reset session ID for new server
            MCP_SESSION_ID = None

        # Initialize connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-explorer",
                    "version": "1.0.0"
                }
            }
        }

        # MCP server requires both content types to be accepted
        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(MCP_SERVER_URL, json=init_request, headers=headers) as resp:
                # Extract session ID from response headers
                session_id = resp.headers.get('mcp-session-id') or resp.headers.get('MCP-Session-ID')
                if session_id:
                    MCP_SESSION_ID = session_id

                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({'success': True, 'sessionId': MCP_SESSION_ID or 'active'})
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def list_prompts_handler(request):
    """List available prompts"""
    try:
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/list"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'prompts': result['result'].get('prompts', [])
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def list_tools_handler(request):
    """List available tools"""
    try:
        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        # Add session ID if available
        if MCP_SESSION_ID:
            headers['MCP-Session-ID'] = MCP_SESSION_ID

        async with aiohttp.ClientSession() as session:
            rpc_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            }

            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'tools': result['result'].get('tools', [])
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def list_resources_handler(request):
    """List available resources"""
    try:
        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        # Add session ID if available
        if MCP_SESSION_ID:
            headers['MCP-Session-ID'] = MCP_SESSION_ID

        async with aiohttp.ClientSession() as session:
            rpc_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/list"
            }

            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'resources': result['result'].get('resources', [])
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def call_tool_handler(request):
    """Call a tool"""
    try:
        data = await request.json()
        tool_name = data.get('name')
        arguments = data.get('arguments', {})

        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        # Add session ID if available
        if MCP_SESSION_ID:
            headers['MCP-Session-ID'] = MCP_SESSION_ID

        async with aiohttp.ClientSession() as session:
            rpc_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'result': result['result']
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def get_prompt_handler(request):
    """Get a prompt"""
    try:
        data = await request.json()
        prompt_name = data.get('name')
        arguments = data.get('arguments', {})

        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        # Add session ID if available
        if MCP_SESSION_ID:
            headers['MCP-Session-ID'] = MCP_SESSION_ID

        async with aiohttp.ClientSession() as session:
            rpc_request = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "prompts/get",
                "params": {
                    "name": prompt_name,
                    "arguments": arguments
                }
            }

            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'result': result['result']
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def read_resource_handler(request):
    """Read a resource"""
    try:
        data = await request.json()
        uri = data.get('uri')

        headers = {
            'Accept': 'text/event-stream, application/json',
            'Content-Type': 'application/json'
        }

        # Add session ID if available
        if MCP_SESSION_ID:
            headers['MCP-Session-ID'] = MCP_SESSION_ID

        async with aiohttp.ClientSession() as session:
            rpc_request = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "resources/read",
                "params": {
                    "uri": uri
                }
            }

            async with session.post(MCP_SERVER_URL, json=rpc_request, headers=get_headers_with_session()) as resp:
                result = await parse_sse_response(resp)

                if 'result' in result:
                    return web.json_response({
                        'success': True,
                        'result': result['result']
                    })
                else:
                    return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def get_server_url_handler(request):
    """Get the current MCP server URL"""
    return web.json_response({'serverUrl': MCP_SERVER_URL})


def create_app(server_url):
    """Create the web application"""
    global MCP_SERVER_URL
    MCP_SERVER_URL = server_url

    app = web.Application()

    # Routes
    app.router.add_get('/', index_handler)
    app.router.add_get('/api/server-url', get_server_url_handler)
    app.router.add_post('/api/connect', connect_handler)
    app.router.add_get('/api/prompts/list', list_prompts_handler)
    app.router.add_get('/api/tools/list', list_tools_handler)
    app.router.add_get('/api/resources/list', list_resources_handler)
    app.router.add_post('/api/tools/call', call_tool_handler)
    app.router.add_post('/api/prompts/get', get_prompt_handler)
    app.router.add_post('/api/resources/read', read_resource_handler)

    return app


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 mcp_explorer.py <MCP_SERVER_URL> [PORT]")
        print("Example: python3 mcp_explorer.py http://localhost:8000/mcp 5000")
        sys.exit(1)

    server_url = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    app = create_app(server_url)

    print(f"🚀 MCP Explorer starting on http://localhost:{port}")
    print(f"📡 Default MCP server: {server_url}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    print(f"💡 You can connect to different servers through the UI")

    web.run_app(app, host='0.0.0.0', port=port)







