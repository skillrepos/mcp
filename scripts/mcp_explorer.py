#!/usr/bin/env python3
"""
Simple MCP Explorer - Interactive web-based client for exploring MCP servers.

Updated 2026-08-03 for MCP specification revision 2026-07-28.

What changed:
  * No initialize/initialized handshake and no Mcp-Session-Id. Every request is
    self-describing: protocol version, client info and client capabilities all
    travel in params._meta on each call.
  * "Connect" now calls the mandatory server/discover RPC, which returns the
    server's supported protocol versions, capabilities and instructions in one
    round trip.
  * Streamable HTTP now requires the Mcp-Method header on every request, plus
    Mcp-Name on tools/call, resources/read and prompts/get, so gateways can
    route without parsing the JSON body.
  * List and read results carry ttlMs / cacheScope caching hints, which the
    Explorer displays.
  * BACKWARD COMPATIBILITY: if server/discover fails the way a pre-2026 server
    fails (it has no such method and, over HTTP, demands a session id), the
    Explorer falls back to the legacy initialize handshake and carries the
    Mcp-Session-Id header on every later call. The status bar tells you which
    era you landed in.
"""

import asyncio
import aiohttp
from aiohttp import web
import json
from datetime import datetime

# Store the MCP server URL and the protocol version we negotiated.
MCP_SERVER_URL = None
MCP_PROTOCOL_VERSION = "2026-07-28"

# Which era of the spec the connected server speaks.
#   "2026-07-28" - stateless; _meta + Mcp-Method headers on every request
#   "legacy"     - 2025-11-25 or earlier; initialize handshake + Mcp-Session-Id
MCP_ERA = "2026-07-28"
MCP_SESSION_ID = None          # only used in legacy mode
LEGACY_ASK_VERSION = "2025-11-25"   # newest pre-stateless revision we offer

# Identity we advertise on every request (self-reported, not verified).
CLIENT_INFO = {"name": "mcp-explorer", "version": "2.0.0"}

# Methods whose params carry a name/uri that must be mirrored into Mcp-Name.
_NAME_BEARING = {"tools/call": "name", "prompts/get": "name", "resources/read": "uri"}

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
        <div class="section">
            <h2>Resource Templates <span class="badge" id="templates-count">0</span></h2>
            <p style="color:#666; font-size:14px; margin-bottom:10px;">
                Templates are dynamic URIs. Replace the <code>{parameter}</code> with a real value, then read.
            </p>
            <div id="templates-list"></div>
            <div id="template-read-section" style="margin-top:15px; display:none;">
                <label style="font-weight:bold; display:block; margin-bottom:5px;">Read a resource by URI:</label>
                <input type="text" id="template-uri-input" placeholder="e.g. resource://notes/meeting-summary"
                       style="width:70%; padding:8px; border:1px solid #ddd; border-radius:4px; margin-right:10px;">
                <button onclick="readTemplateUri()">Read Resource</button>
                <div id="template-read-result"></div>
            </div>
        </div>
    </div>

    <script>
        let protocolVersion = null;

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
                    // 2026-07-28: no session id. We record the protocol version
                    // that server/discover told us this server speaks.
                    protocolVersion = data.protocolVersion;
                    const info = data.serverInfo || {};
                    const name = info.name ? `${info.name} ${info.version || ''}` : 'server';
                    const eraTag = data.era === 'legacy'
                        ? ' — legacy mode: initialize handshake + Mcp-Session-Id'
                        : ' — stateless';
                    document.getElementById('status-text').textContent =
                        `✅ Connected (${data.protocolVersion}${eraTag})`;
                    document.getElementById('status-text').style.color = '#4caf50';
                    let detail = `Connected to: ${serverUrl} — ${name}`;
                    if (data.supportedVersions && data.supportedVersions.length) {
                        detail += ` · supports: ${data.supportedVersions.join(', ')}`;
                    }
                    if (data.cache && data.cache.ttlMs != null) {
                        detail += ` · discover cache: ttlMs=${data.cache.ttlMs}, scope=${data.cache.cacheScope}`;
                    }
                    document.getElementById('current-server').textContent = detail;

                    // Auto-load all lists
                    await listPrompts();
                    await listTools();
                    await listResources();
                    await listResourceTemplates();
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
                        container.innerHTML = prompts.map(prompt => {
                            const hasArgs = prompt.arguments && prompt.arguments.length > 0;
                            return `
                            <div class="item">
                                <h3>${prompt.name}</h3>
                                ${prompt.description ? `<div class="item-description">${prompt.description}</div>` : ''}
                                ${hasArgs ? `
                                    <div class="item-meta">
                                        Arguments: ${prompt.arguments.map(arg =>
                                            `${arg.name}${arg.required ? '*' : ''} (${arg.description || 'no description'})`
                                        ).join(', ')}
                                    </div>
                                ` : ''}
                                <button onclick="getPrompt('${prompt.name}', ${hasArgs})">Get Prompt</button>
                                <div id="prompt-result-${prompt.name}"></div>
                            </div>
                        `}).join('');
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

        async function getPrompt(promptName, hasArgs) {
            let parsedArgs = {};

            if (hasArgs) {
                const args = prompt('Enter arguments as JSON:', '{}');
                if (args === null) return;
                parsedArgs = JSON.parse(args);
            }

            const resultContainer = document.getElementById(`prompt-result-${promptName}`);
            resultContainer.innerHTML = '<p>Loading prompt...</p>';

            try {
                const response = await fetch('/api/prompts/get', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: promptName, arguments: parsedArgs })
                });
                const data = await response.json();

                if (data.success) {
                    const result = data.result;
                    let displayText = '';

                    if (result.messages && Array.isArray(result.messages)) {
                        displayText = result.messages.map(msg => {
                            let part = '';
                            if (msg.role) part += `[${msg.role}]\\n`;
                            if (msg.content) {
                                if (typeof msg.content === 'string') {
                                    part += msg.content;
                                } else if (msg.content.text) {
                                    part += msg.content.text;
                                } else {
                                    part += JSON.stringify(msg.content, null, 2);
                                }
                            }
                            return part;
                        }).join('\\n\\n');
                    } else {
                        displayText = JSON.stringify(result, null, 2);
                    }

                    resultContainer.innerHTML = `
                        <div class="result">
                            <strong>Prompt result:</strong>
                            <pre>${displayText}</pre>
                        </div>
                    `;
                } else {
                    resultContainer.innerHTML = `<div class="error">${JSON.stringify(data.error, null, 2)}</div>`;
                }
            } catch (error) {
                resultContainer.innerHTML = `<div class="error">Error: ${error}</div>`;
            }
        }

        async function listResourceTemplates() {
            const container = document.getElementById('templates-list');
            container.innerHTML = '<p>Loading...</p>';

            try {
                const response = await fetch('/api/resources/templates/list');
                const data = await response.json();

                if (data.success) {
                    const templates = data.resourceTemplates;
                    document.getElementById('templates-count').textContent = templates.length;

                    if (templates.length === 0) {
                        container.innerHTML = '<p>No resource templates available</p>';
                    } else {
                        document.getElementById('template-read-section').style.display = 'block';
                        container.innerHTML = templates.map(tmpl => `
                            <div class="item" style="border-left-color: #764ba2;">
                                <h3>${tmpl.name || tmpl.uriTemplate}</h3>
                                ${tmpl.description ? `<div class="item-description">${tmpl.description}</div>` : ''}
                                <div class="item-meta">
                                    URI Template: <code>${tmpl.uriTemplate}</code>
                                    ${tmpl.mimeType ? ` | MIME: ${tmpl.mimeType}` : ''}
                                </div>
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

        async function readTemplateUri() {
            const uri = document.getElementById('template-uri-input').value.trim();
            if (!uri) { alert('Enter a URI first'); return; }
            const resultContainer = document.getElementById('template-read-result');
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
                            <strong>Content for <code>${uri}</code>:</strong>
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


def build_request(method, params=None, req_id=1):
    """Build a spec-correct JSON-RPC request for whichever era we negotiated.

    2026-07-28: every request carries its own protocol version and client
    capabilities in _meta - there is no handshake that establishes them once.
    Legacy: the handshake already established them, so params stay bare.
    """
    body_params = dict(params or {})
    if MCP_ERA == "2026-07-28":
        body_params["_meta"] = {
            "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_VERSION,
            "io.modelcontextprotocol/clientInfo": CLIENT_INFO,
            "io.modelcontextprotocol/clientCapabilities": {},
        }
    return {"jsonrpc": "2.0", "id": req_id, "method": method, "params": body_params}


def build_headers(method, params=None):
    """Build the HTTP headers Streamable HTTP requires - era dependent.

    2026-07-28: MCP-Protocol-Version and Mcp-Method are mandatory on every
    request; Mcp-Name on tools/call, resources/read and prompts/get. A server
    MUST reject a request whose headers disagree with its body
    (HeaderMismatchError, JSON-RPC -32020, HTTP 400).

    Legacy (2025-11-25 and earlier): no Mcp-Method/Mcp-Name; instead every
    request after initialize carries the Mcp-Session-Id the server issued.
    """
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
    }
    if MCP_ERA == "2026-07-28":
        headers["Mcp-Method"] = method
        key = _NAME_BEARING.get(method)
        if key and params and params.get(key):
            headers["Mcp-Name"] = str(params[key])
    elif MCP_SESSION_ID:
        headers["Mcp-Session-Id"] = MCP_SESSION_ID
    return headers


def cache_info(result):
    """Pull the SEP-2549 caching hints out of a result, if present."""
    if not isinstance(result, dict):
        return None
    if "ttlMs" not in result and "cacheScope" not in result:
        return None
    return {"ttlMs": result.get("ttlMs"), "cacheScope": result.get("cacheScope")}


async def mcp_call(method, params=None, req_id=1):
    """POST one JSON-RPC request to the MCP endpoint and return the parsed body."""
    params = params or {}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            MCP_SERVER_URL,
            json=build_request(method, params, req_id),
            headers=build_headers(method, params),
        ) as resp:
            return await parse_sse_response(resp)


async def legacy_connect():
    """Fall back to the pre-2026 initialize handshake.

    1. POST initialize (protocolVersion, capabilities, clientInfo in params).
    2. Read the Mcp-Session-Id response header the server issued.
    3. POST notifications/initialized with that header.
    Every later request must carry the same Mcp-Session-Id header.
    """
    global MCP_ERA, MCP_PROTOCOL_VERSION, MCP_SESSION_ID

    init_body = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": LEGACY_ASK_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        },
    }
    headers = {"Accept": "application/json, text/event-stream",
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(MCP_SERVER_URL, json=init_body,
                                headers=headers) as resp:
            session_id = resp.headers.get("mcp-session-id")
            body = await parse_sse_response(resp)
        if "result" not in body:
            raise RuntimeError(f"legacy initialize failed: {body}")
        r = body["result"]

        # Adopt whatever the handshake negotiated, and pin the session id.
        MCP_ERA = "legacy"
        MCP_PROTOCOL_VERSION = r.get("protocolVersion", LEGACY_ASK_VERSION)
        MCP_SESSION_ID = session_id

        # The old spec requires this notification before normal traffic.
        note = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        note_headers = dict(headers)
        if MCP_SESSION_ID:
            note_headers["Mcp-Session-Id"] = MCP_SESSION_ID
        note_headers["MCP-Protocol-Version"] = MCP_PROTOCOL_VERSION
        async with session.post(MCP_SERVER_URL, json=note,
                                headers=note_headers):
            pass
    return r


def looks_pre_2026(result):
    """Does this server/discover response look like a pre-2026 server?

    A legacy Streamable HTTP server rejects the sessionless POST outright
    (e.g. -32600 'Missing session ID') or reports the method as unknown
    (-32601). Either way it never answers -32022, which is what a MODERN
    server says when it merely lacks our version - that case should not
    trigger a legacy fallback.
    """
    err = result.get('error') if isinstance(result, dict) else None
    return bool(err) and err.get('code') in (-32600, -32601)


async def connect_handler(request):
    """Connect to the MCP server via the mandatory server/discover RPC.

    In 2026-07-28 there is no initialize handshake and no session to establish.
    server/discover is simply a normal request that reports what the server
    supports; calling it is optional for a client, but implementing it is
    mandatory for a server.

    If the server turns out to be pre-2026, fall through to legacy_connect().
    """
    global MCP_SERVER_URL, MCP_PROTOCOL_VERSION, MCP_ERA, MCP_SESSION_ID

    try:
        data = await request.json()
        new_server_url = data.get('serverUrl')
        if new_server_url:
            MCP_SERVER_URL = new_server_url

        # Reset to the modern era for every new connection attempt.
        MCP_ERA = "2026-07-28"
        MCP_PROTOCOL_VERSION = "2026-07-28"
        MCP_SESSION_ID = None

        result = await mcp_call("server/discover", {}, req_id=1)

        if looks_pre_2026(result):
            r = await legacy_connect()
            return web.json_response({
                'success': True,
                'era': 'legacy',
                'protocolVersion': MCP_PROTOCOL_VERSION,
                'supportedVersions': [MCP_PROTOCOL_VERSION],
                'capabilities': r.get('capabilities', {}),
                'instructions': r.get('instructions'),
                'serverInfo': r.get('serverInfo', {}),
                'cache': None,
            })

        if 'result' in result:
            r = result['result']
            supported = r.get('supportedVersions', [])
            # Pin ourselves to a version the server actually supports.
            if supported and MCP_PROTOCOL_VERSION not in supported:
                MCP_PROTOCOL_VERSION = supported[0]

            server_info = (r.get('_meta') or {}).get(
                'io.modelcontextprotocol/serverInfo', {})

            return web.json_response({
                'success': True,
                'era': '2026-07-28',
                'protocolVersion': MCP_PROTOCOL_VERSION,
                'supportedVersions': supported,
                'capabilities': r.get('capabilities', {}),
                'instructions': r.get('instructions'),
                'serverInfo': server_info,
                'cache': cache_info(r),
            })

        # A modern server that does not speak our version answers with
        # UnsupportedProtocolVersionError (-32022) and lists what it does speak.
        err = result.get('error', {})
        if err.get('code') == -32022:
            supported = (err.get('data') or {}).get('supported', [])
            return web.json_response({
                'success': False,
                'error': f"Server does not support {MCP_PROTOCOL_VERSION}. "
                         f"It supports: {', '.join(supported) or 'unknown'}"
            })

        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})


async def list_prompts_handler(request):
    """prompts/list - see build_headers() for the headers 2026-07-28 requires."""
    try:
        result = await mcp_call("prompts/list", {}, req_id=2)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'prompts': result['result'].get('prompts', []),
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def list_tools_handler(request):
    """tools/list - see build_headers() for the headers 2026-07-28 requires."""
    try:
        result = await mcp_call("tools/list", {}, req_id=3)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'tools': result['result'].get('tools', []),
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def list_resources_handler(request):
    """resources/list - see build_headers() for the headers 2026-07-28 requires."""
    try:
        result = await mcp_call("resources/list", {}, req_id=4)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'resources': result['result'].get('resources', []),
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def list_resource_templates_handler(request):
    """resources/templates/list - see build_headers() for the headers 2026-07-28 requires."""
    try:
        result = await mcp_call("resources/templates/list", {}, req_id=8)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'resourceTemplates': result['result'].get('resourceTemplates', []),
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def call_tool_handler(request):
    """tools/call - see build_headers() for the headers 2026-07-28 requires."""
    try:
        data = await request.json()
        params = {"name": data.get('name'), "arguments": data.get('arguments', {})}
        result = await mcp_call("tools/call", params, req_id=5)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'result': result['result'],
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def get_prompt_handler(request):
    """prompts/get - see build_headers() for the headers 2026-07-28 requires."""
    try:
        data = await request.json()
        params = {"name": data.get('name'), "arguments": data.get('arguments', {})}
        result = await mcp_call("prompts/get", params, req_id=6)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'result': result['result'],
                'cache': cache_info(result['result']),
            })
        return web.json_response({'success': False, 'error': str(result)})

    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)})

async def read_resource_handler(request):
    """resources/read - see build_headers() for the headers 2026-07-28 requires."""
    try:
        data = await request.json()
        params = {"uri": data.get('uri')}
        result = await mcp_call("resources/read", params, req_id=7)

        if 'result' in result:
            return web.json_response({
                'success': True,
                'result': result['result'],
                'cache': cache_info(result['result']),
            })
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
    app.router.add_get('/api/resources/templates/list', list_resource_templates_handler)
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

    print(f"MCP Explorer starting on http://localhost:{port}")
    print(f"Default MCP server: {server_url}")
    print(f"Open http://localhost:{port} in your browser")
    print(f"You can connect to different servers through the UI")

    web.run_app(app, host='0.0.0.0', port=port)
