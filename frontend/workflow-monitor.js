// Workflow Monitor - Injected Script for OpenWebUI
(function() {
  'use strict';

  // Configuration
  const API_BASE = 'http://localhost:8000';

  // State
  let isMinimized = true;
  let position = { x: window.innerWidth - 320, y: window.innerHeight - 420 };
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };
  let eventSource = null;
  let currentChatId = null;
  let graphState = null;

  // Create styles
  const style = document.createElement('style');
  style.textContent = `
    .workflow-monitor-minimized {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #3b82f6;
      color: white;
      border: none;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
      cursor: pointer;
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    
    .workflow-monitor-minimized:hover {
      transform: scale(1.05);
      box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .workflow-monitor-minimized svg {
      width: 24px;
      height: 24px;
    }
    
    .workflow-monitor-badge {
      position: absolute;
      top: -5px;
      right: -5px;
      background: #10b981;
      color: white;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 10px;
      font-weight: 600;
      white-space: nowrap;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      max-width: 80px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .workflow-monitor-panel {
      position: fixed;
      width: 300px;
      height: 400px;
      background: rgba(255, 255, 255, 0.98);
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      z-index: 10000;
      display: flex;
      flex-direction: column;
    }
    
    .workflow-monitor-header {
      padding: 12px 16px;
      background: #f9fafb;
      border-radius: 8px 8px 0 0;
      cursor: move;
      user-select: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #e5e7eb;
    }
    
    .workflow-monitor-title {
      font-weight: 600;
      color: #374151;
      font-size: 14px;
    }
    
    .workflow-monitor-minimize {
      background: none;
      border: none;
      font-size: 20px;
      line-height: 1;
      color: #6b7280;
      cursor: pointer;
      padding: 0 4px;
      border-radius: 4px;
      transition: all 0.2s ease;
    }
    
    .workflow-monitor-minimize:hover {
      background: #e5e7eb;
      color: #374151;
    }
    
    .workflow-monitor-content {
      flex: 1;
      padding: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    
    .workflow-monitor-graph {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fafafa;
      border-radius: 4px;
      margin-bottom: 12px;
    }
    
    .workflow-monitor-info {
      border-top: 1px solid #e5e7eb;
      padding-top: 12px;
    }
    
    .workflow-monitor-info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-size: 12px;
    }
    
    .workflow-monitor-info-label {
      color: #6b7280;
      font-weight: 500;
    }
    
    .workflow-monitor-info-value {
      color: #374151;
      font-weight: 600;
    }
    
    .workflow-monitor-status {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #6b7280;
      font-size: 14px;
    }
    
    .workflow-monitor-error {
      color: #ef4444;
    }
    
    @keyframes workflow-pulse {
      0% { opacity: 1; }
      50% { opacity: 0.6; }
      100% { opacity: 1; }
    }
    
    .workflow-current-node {
      animation: workflow-pulse 2s ease-in-out infinite;
    }
  `;
  document.head.appendChild(style);

  // Helper functions
  function getChatIdFromURL() {
    const match = window.location.pathname.match(/\/c\/([^\/]+)/);
    return match ? match[1] : null;
  }

  function connectSSE() {
    if (!currentChatId) return;
    
    // Close existing connection
    if (eventSource) {
      eventSource.close();
    }
    
    try {
      const sseUrl = `${API_BASE}/v1/graph-state/stream/chat-${currentChatId}`;
      console.log('Connecting to SSE:', sseUrl);
      
      eventSource = new EventSource(sseUrl);
      
      eventSource.onopen = function(event) {
        console.log('SSE connection opened for chat:', currentChatId);
      };
      
      eventSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);
          
          if (data.status === 'heartbeat') {
            // Just a heartbeat, keep connection alive
            return;
          }
          
          if (data.status === 'waiting') {
            // No workflow state yet
            graphState = null;
            renderGraph();
            updateBadge();
            return;
          }
          
          if (data.status === 'error') {
            console.error('SSE error:', data.message);
            return;
          }
          
          // Regular graph state update
          graphState = data;
          renderGraph();
          updateBadge();
          
        } catch (err) {
          console.error('Error parsing SSE data:', err);
        }
      };
      
      eventSource.onerror = function(event) {
        console.error('SSE connection error:', event);
        
        // Attempt to reconnect after delay
        setTimeout(() => {
          if (currentChatId && (!eventSource || eventSource.readyState === EventSource.CLOSED)) {
            console.log('Attempting to reconnect SSE...');
            connectSSE();
          }
        }, 5000);
      };
      
    } catch (err) {
      console.error('Error setting up SSE connection:', err);
    }
  }
  
  function disconnectSSE() {
    if (eventSource) {
      console.log('Disconnecting SSE for chat:', currentChatId);
      eventSource.close();
      eventSource = null;
    }
  }

  function renderGraph() {
    const graphContainer = document.querySelector('.workflow-monitor-graph');
    if (!graphContainer || !graphState) return;
    
    // Clear previous content
    graphContainer.innerHTML = '';
    
    // Create simple SVG visualization
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '260');
    svg.setAttribute('height', '260');
    
    // Get nodes from graph_structure
    const nodes = graphState.graph_structure ? graphState.graph_structure.nodes : [];
    const edges = graphState.graph_structure ? graphState.graph_structure.edges : [];
    
    if (nodes.length === 0) {
      // Show "no data" message
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', '130');
      text.setAttribute('y', '130');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '14');
      text.setAttribute('fill', '#6b7280');
      text.textContent = 'No graph data';
      svg.appendChild(text);
      graphContainer.appendChild(svg);
      return;
    }
    
    // Simple layout - arrange nodes in a grid
    const nodePositions = {};
    const radius = 20;
    const padding = 40;
    const cols = Math.ceil(Math.sqrt(nodes.length));
    
    nodes.forEach((nodeId, i) => {
      const row = Math.floor(i / cols);
      const col = i % cols;
      nodePositions[nodeId] = {
        x: padding + col * (180 / cols),
        y: padding + row * (180 / cols)
      };
    });
    
    // Draw edges
    edges.forEach(edge => {
      const from = edge.from;
      const to = edge.to;
      if (nodePositions[from] && nodePositions[to]) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', nodePositions[from].x);
        line.setAttribute('y1', nodePositions[from].y);
        line.setAttribute('x2', nodePositions[to].x);
        line.setAttribute('y2', nodePositions[to].y);
        line.setAttribute('stroke', '#e5e7eb');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        svg.appendChild(line);
      }
    });
    
    // Add arrow marker definition
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '7');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('orient', 'auto');
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
    polygon.setAttribute('fill', '#e5e7eb');
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    
    // Draw nodes
    nodes.forEach(nodeId => {
      const pos = nodePositions[nodeId];
      const isVisited = graphState.traversal_history && graphState.traversal_history.includes(nodeId);
      const isCurrent = nodeId === graphState.current_node;
      
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', pos.x);
      circle.setAttribute('cy', pos.y);
      circle.setAttribute('r', radius);
      circle.setAttribute('fill', isCurrent ? '#3b82f6' : (isVisited ? '#10b981' : '#f3f4f6'));
      circle.setAttribute('stroke', isCurrent ? '#2563eb' : (isVisited ? '#059669' : '#d1d5db'));
      circle.setAttribute('stroke-width', '2');
      if (isCurrent) {
        circle.classList.add('workflow-current-node');
      }
      
      // Node label (abbreviated)
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', pos.x);
      text.setAttribute('y', pos.y + 3);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '8');
      text.setAttribute('font-weight', '600');
      text.setAttribute('fill', (isCurrent || isVisited) ? 'white' : '#374151');
      
      // Create abbreviated node name
      const words = nodeId.split('_');
      const abbrev = words.length > 1 ? words.map(w => w[0].toUpperCase()).join('') : nodeId.substring(0, 3).toUpperCase();
      text.textContent = abbrev;
      
      // Add title for full name on hover
      const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      title.textContent = nodeId.replace(/_/g, ' ');
      g.appendChild(title);
      
      g.appendChild(circle);
      g.appendChild(text);
      svg.appendChild(g);
    });
    
    graphContainer.appendChild(svg);
    
    // Update info
    updateInfo();
  }

  function updateInfo() {
    const currentLabel = document.querySelector('.workflow-monitor-current');
    const progressLabel = document.querySelector('.workflow-monitor-progress');
    
    if (currentLabel && graphState) {
      currentLabel.textContent = graphState.current_node || 'None';
    }
    
    if (progressLabel && graphState && graphState.graph_structure) {
      const total = graphState.graph_structure.nodes ? graphState.graph_structure.nodes.length : 0;
      const visited = graphState.traversal_history ? graphState.traversal_history.length : 0;
      progressLabel.textContent = `${visited} / ${total} nodes`;
    }
  }

  function updateBadge() {
    const badge = document.querySelector('.workflow-monitor-badge');
    if (badge && graphState && graphState.current_node) {
      const currentNode = graphState.current_node;
      // Create abbreviated version for badge
      const words = currentNode.split('_');
      const abbrev = words.length > 1 ? words.map(w => w[0].toUpperCase()).join('') : currentNode.substring(0, 4).toUpperCase();
      badge.textContent = abbrev;
      badge.style.display = 'block';
    } else if (badge) {
      badge.style.display = 'none';
    }
  }

  function createMinimizedButton() {
    const button = document.createElement('button');
    button.className = 'workflow-monitor-minimized';
    button.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"/>
        <circle cx="12" cy="4" r="2"/>
        <circle cx="12" cy="20" r="2"/>
        <circle cx="4" cy="12" r="2"/>
        <circle cx="20" cy="12" r="2"/>
        <line x1="12" y1="6" x2="12" y2="9"/>
        <line x1="12" y1="15" x2="12" y2="18"/>
        <line x1="6" y1="12" x2="9" y2="12"/>
        <line x1="15" y1="12" x2="18" y2="12"/>
      </svg>
      <span class="workflow-monitor-badge" style="display: none;"></span>
    `;
    button.onclick = () => {
      isMinimized = false;
      button.remove();
      createPanel();
    };
    document.body.appendChild(button);
  }

  function createPanel() {
    const panel = document.createElement('div');
    panel.className = 'workflow-monitor-panel';
    panel.style.left = position.x + 'px';
    panel.style.top = position.y + 'px';
    
    panel.innerHTML = `
      <div class="workflow-monitor-header">
        <span class="workflow-monitor-title">Workflow Monitor</span>
        <button class="workflow-monitor-minimize">−</button>
      </div>
      <div class="workflow-monitor-content">
        <div class="workflow-monitor-graph">
          <div class="workflow-monitor-status">
            ${graphState ? '' : 'No workflow active'}
          </div>
        </div>
        <div class="workflow-monitor-info">
          <div class="workflow-monitor-info-row">
            <span class="workflow-monitor-info-label">Current:</span>
            <span class="workflow-monitor-info-value workflow-monitor-current">None</span>
          </div>
          <div class="workflow-monitor-info-row">
            <span class="workflow-monitor-info-label">Progress:</span>
            <span class="workflow-monitor-info-value workflow-monitor-progress">0 / 0 nodes</span>
          </div>
        </div>
      </div>
    `;
    
    // Add event handlers
    const header = panel.querySelector('.workflow-monitor-header');
    const minimizeBtn = panel.querySelector('.workflow-monitor-minimize');
    
    header.addEventListener('mousedown', startDrag);
    minimizeBtn.addEventListener('click', () => {
      isMinimized = true;
      position.x = parseInt(panel.style.left);
      position.y = parseInt(panel.style.top);
      panel.remove();
      createMinimizedButton();
    });
    
    document.body.appendChild(panel);
    
    if (graphState) {
      renderGraph();
    }
  }

  function startDrag(e) {
    if (e.target.tagName === 'BUTTON') return;
    
    const panel = document.querySelector('.workflow-monitor-panel');
    isDragging = true;
    dragStart = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
    
    function handleDrag(e) {
      if (!isDragging) return;
      
      position = {
        x: Math.max(0, Math.min(window.innerWidth - 300, e.clientX - dragStart.x)),
        y: Math.max(0, Math.min(window.innerHeight - 400, e.clientY - dragStart.y))
      };
      
      panel.style.left = position.x + 'px';
      panel.style.top = position.y + 'px';
    }
    
    function stopDrag() {
      isDragging = false;
      window.removeEventListener('mousemove', handleDrag);
      window.removeEventListener('mouseup', stopDrag);
    }
    
    window.addEventListener('mousemove', handleDrag);
    window.addEventListener('mouseup', stopDrag);
  }

  function startMonitoring() {
    connectSSE();
  }

  function stopMonitoring() {
    disconnectSSE();
  }

  // Initialize
  function init() {
    // Check if we're on a chat page
    currentChatId = getChatIdFromURL();
    
    if (!currentChatId) {
      return;
    }
    
    // Create minimized button
    createMinimizedButton();
    
    // Start monitoring
    startMonitoring();
    
    // Watch for URL changes
    let lastChatId = currentChatId;
    setInterval(() => {
      const newChatId = getChatIdFromURL();
      if (newChatId !== lastChatId) {
        lastChatId = newChatId;
        currentChatId = newChatId;
        if (newChatId) {
          startMonitoring();
        } else {
          stopMonitoring();
        }
      }
    }, 1000);
  }

  // Wait for page to load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();