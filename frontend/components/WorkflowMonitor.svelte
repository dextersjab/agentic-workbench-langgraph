<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';
  
  export let chatId = '';
  
  let isMinimized = true;
  let position = { x: 0, y: 0 };
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };
  let graphState = null;
  let error = null;
  let loading = false;
  let pollInterval = null;
  let graphContainer;
  
  // Initialize position on mount
  onMount(() => {
    position = { 
      x: window.innerWidth - 320, 
      y: window.innerHeight - 420 
    };
    
    // Start polling when component mounts
    startPolling();
    
    return () => {
      stopPolling();
    };
  });
  
  onDestroy(() => {
    stopPolling();
  });
  
  function startPolling() {
    if (!chatId) return;
    
    // Fetch immediately
    fetchGraphState();
    
    // Then poll every 2 seconds
    pollInterval = setInterval(fetchGraphState, 2000);
  }
  
  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }
  
  async function fetchGraphState() {
    if (!chatId) return;
    
    try {
      loading = true;
      error = null;
      
      const response = await fetch(`http://localhost:5001/api/graph-state/${chatId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch graph state: ${response.statusText}`);
      }
      
      const data = await response.json();
      graphState = data;
      
      // Render graph if expanded
      if (!isMinimized && graphContainer) {
        renderGraph();
      }
    } catch (err) {
      console.error('Error fetching graph state:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  function renderGraph() {
    if (!graphContainer || !graphState) return;
    
    // Clear previous graph
    d3.select(graphContainer).selectAll('*').remove();
    
    const width = 280;
    const height = 300;
    const nodeRadius = 20;
    
    // Create SVG
    const svg = d3.select(graphContainer)
      .append('svg')
      .attr('width', width)
      .attr('height', height);
    
    // Simple layout - arrange nodes in a grid
    const nodes = Object.keys(graphState.nodes).map((nodeId, i) => ({
      id: nodeId,
      label: graphState.nodes[nodeId],
      x: 50 + (i % 3) * 80,
      y: 50 + Math.floor(i / 3) * 80,
      visited: graphState.traversal_history.includes(nodeId),
      current: nodeId === graphState.current_node
    }));
    
    // Draw edges
    if (graphState.edges) {
      const edges = [];
      for (const [from, targets] of Object.entries(graphState.edges)) {
        for (const to of targets) {
          const source = nodes.find(n => n.id === from);
          const target = nodes.find(n => n.id === to);
          if (source && target) {
            edges.push({ source, target });
          }
        }
      }
      
      svg.selectAll('line')
        .data(edges)
        .enter()
        .append('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', '#e5e7eb')
        .attr('stroke-width', 2)
        .attr('marker-end', 'url(#arrowhead)');
    }
    
    // Add arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#e5e7eb');
    
    // Draw nodes
    const nodeGroups = svg.selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('transform', d => `translate(${d.x}, ${d.y})`);
    
    nodeGroups.append('circle')
      .attr('r', nodeRadius)
      .attr('fill', d => {
        if (d.current) return '#3b82f6';
        if (d.visited) return '#10b981';
        return '#f3f4f6';
      })
      .attr('stroke', d => {
        if (d.current) return '#2563eb';
        if (d.visited) return '#059669';
        return '#d1d5db';
      })
      .attr('stroke-width', 2)
      .attr('class', d => d.current ? 'current-node' : '');
    
    nodeGroups.append('text')
      .text(d => d.label.substring(0, 8))
      .attr('text-anchor', 'middle')
      .attr('dy', 4)
      .attr('font-size', '10px')
      .attr('fill', d => (d.current || d.visited) ? 'white' : '#374151');
  }
  
  function startDrag(e) {
    isDragging = true;
    dragStart = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
    
    window.addEventListener('mousemove', handleDrag);
    window.addEventListener('mouseup', stopDrag);
  }
  
  function handleDrag(e) {
    if (!isDragging) return;
    
    position = {
      x: Math.max(0, Math.min(window.innerWidth - 300, e.clientX - dragStart.x)),
      y: Math.max(0, Math.min(window.innerHeight - 400, e.clientY - dragStart.y))
    };
  }
  
  function stopDrag() {
    isDragging = false;
    window.removeEventListener('mousemove', handleDrag);
    window.removeEventListener('mouseup', stopDrag);
  }
  
  function toggleMinimize() {
    isMinimized = !isMinimized;
    if (!isMinimized && graphState) {
      // Re-render graph when expanding
      setTimeout(() => renderGraph(), 100);
    }
  }
  
  $: currentNodeLabel = graphState?.current_node ? 
    (graphState.nodes[graphState.current_node] || graphState.current_node) : 
    'No workflow';
</script>

{#if isMinimized}
  <button 
    class="workflow-monitor-minimized" 
    on:click={toggleMinimize}
    title="Workflow Monitor"
  >
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
    {#if graphState?.current_node}
      <span class="node-badge">{currentNodeLabel.substring(0, 8)}</span>
    {/if}
  </button>
{:else}
  <div 
    class="workflow-monitor-panel" 
    style="left: {position.x}px; top: {position.y}px"
  >
    <div 
      class="monitor-header" 
      on:mousedown={startDrag}
    >
      <span class="header-title">Workflow Monitor</span>
      <button class="minimize-btn" on:click={toggleMinimize}>−</button>
    </div>
    <div class="monitor-content">
      {#if loading && !graphState}
        <div class="status-message">Loading workflow...</div>
      {:else if error}
        <div class="error-message">
          <p>Error: {error}</p>
          <button class="retry-btn" on:click={fetchGraphState}>Retry</button>
        </div>
      {:else if !graphState}
        <div class="status-message">No workflow active</div>
      {:else}
        <div class="graph-container" bind:this={graphContainer}></div>
        <div class="graph-info">
          <div class="info-row">
            <span class="info-label">Current:</span>
            <span class="info-value">{currentNodeLabel}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Progress:</span>
            <span class="info-value">
              {graphState.traversal_history.length} / {Object.keys(graphState.nodes).length} nodes
            </span>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
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
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }
  
  .workflow-monitor-minimized:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  }
  
  .node-badge {
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
  }
  
  .workflow-monitor-panel {
    position: fixed;
    width: 300px;
    height: 400px;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    z-index: 1000;
    display: flex;
    flex-direction: column;
  }
  
  .monitor-header {
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
  
  .header-title {
    font-weight: 600;
    color: #374151;
    font-size: 14px;
  }
  
  .minimize-btn {
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
  
  .minimize-btn:hover {
    background: #e5e7eb;
    color: #374151;
  }
  
  .monitor-content {
    flex: 1;
    padding: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .graph-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fafafa;
    border-radius: 4px;
    margin-bottom: 12px;
  }
  
  .graph-info {
    border-top: 1px solid #e5e7eb;
    padding-top: 12px;
  }
  
  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 12px;
  }
  
  .info-label {
    color: #6b7280;
    font-weight: 500;
  }
  
  .info-value {
    color: #374151;
    font-weight: 600;
  }
  
  .status-message, .error-message {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    font-size: 14px;
  }
  
  .error-message {
    color: #ef4444;
  }
  
  .retry-btn {
    margin-top: 12px;
    padding: 6px 16px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .retry-btn:hover {
    background: #2563eb;
  }
  
  :global(.current-node) {
    animation: pulse 2s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
    100% {
      opacity: 1;
    }
  }
</style>