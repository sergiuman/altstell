/**
 * Interactive Force-Directed Constellation Graph Explorer for AltStell.
 * Visualizes Books (17), Developmental Values (25+), 11yo Dilemmas, and Short-Video Episodes (24+)
 * with interactive hover/click inspection and Value-Path playlist launching.
 */
window.AltStellConstellation = (function () {
  let canvas, ctx;
  let nodes = [];
  let edges = [];
  let selectedNode = null;
  let hoveredNode = null;
  let animFrame = null;
  let width = 800, height = 600;
  let dragNode = null;
  let onSelectCallback = null;

  const TYPE_COLORS = {
    book: '#fbbf24',
    value: '#38bdf8',
    episode: '#a855f7',
    dilemma: '#10b981'
  };

  const TYPE_RADIUS = {
    book: 11,
    value: 9,
    episode: 6.5,
    dilemma: 5.5
  };

  function init(canvasEl, graphData, onSelect) {
    canvas = canvasEl;
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    onSelectCallback = onSelect;

    resize();
    window.addEventListener('resize', resize);

    const rawNodes = (graphData && graphData.nodes) ? graphData.nodes : [];
    const rawEdges = (graphData && graphData.edges) ? graphData.edges : [];

    // Position nodes in concentric orbital rings by semantic type for instant clarity
    const byType = { value: [], book: [], episode: [], dilemma: [] };
    rawNodes.forEach(n => {
      if (byType[n.type]) byType[n.type].push(n);
      else byType.value.push(n);
    });

    nodes = [];
    const cx = width / 2;
    const cy = height / 2;
    const minDim = Math.min(width, height);

    function placeRing(arr, radiusFactor, jitter) {
      arr.forEach((n, idx) => {
        const angle = (idx / Math.max(1, arr.length)) * Math.PI * 2;
        const r = minDim * radiusFactor + ((idx % 2 === 0 ? 1 : -1) * jitter);
        nodes.push({
          ...n,
          x: cx + Math.cos(angle) * r,
          y: cy + Math.sin(angle) * r,
          vx: 0,
          vy: 0,
          radius: TYPE_RADIUS[n.type] || 7,
          color: n.accent_color || n.color || TYPE_COLORS[n.type] || '#6366f1'
        });
      });
    }

    placeRing(byType.value, 0.19, 18);
    placeRing(byType.book, 0.33, 14);
    placeRing(byType.episode, 0.44, 16);
    placeRing(byType.dilemma.slice(0, 10), 0.10, 8);

    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    edges = rawEdges
      .filter(e => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map(e => ({
        ...e,
        srcNode: nodeMap.get(e.source),
        dstNode: nodeMap.get(e.target)
      }));

    bindEvents();
    if (nodes.length > 0 && !selectedNode) {
      selectNode(nodes.find(n => n.type === 'value') || nodes[0]);
    }
    startLoop();
  }

  function resize() {
    if (!canvas || !canvas.parentElement) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    width = Math.max(320, rect.width || 800);
    height = Math.max(300, rect.height || 600);
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function bindEvents() {
    canvas.onmousemove = (e) => {
      const pos = getPos(e);
      if (dragNode) {
        dragNode.x = pos.x;
        dragNode.y = pos.y;
        return;
      }
      hoveredNode = findNodeAt(pos.x, pos.y);
      canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
    };

    canvas.onmousedown = (e) => {
      const pos = getPos(e);
      const hit = findNodeAt(pos.x, pos.y);
      if (hit) {
        dragNode = hit;
        selectNode(hit);
      }
    };

    window.addEventListener('mouseup', () => { dragNode = null; });

    canvas.ontouchstart = (e) => {
      if (!e.touches.length) return;
      const pos = getPos(e.touches[0]);
      const hit = findNodeAt(pos.x, pos.y);
      if (hit) selectNode(hit);
    };
  }

  function getPos( evt ) {
    const rect = canvas.getBoundingClientRect();
    return { x: evt.clientX - rect.left, y: evt.clientY - rect.top };
  }

  function findNodeAt(x, y) {
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      const dx = n.x - x;
      const dy = n.y - y;
      if (Math.hypot(dx, dy) <= n.radius + 7) return n;
    }
    return null;
  }

  function selectNode(node) {
    selectedNode = node;
    if (onSelectCallback && node) {
      const neighbors = [];
      edges.forEach(e => {
        if (e.srcNode.id === node.id) neighbors.push({ node: e.dstNode, relation: e.relation });
        else if (e.dstNode.id === node.id) neighbors.push({ node: e.srcNode, relation: e.relation });
      });
      onSelectCallback(node, neighbors);
    }
  }

  function focusNodeById(id) {
    const found = nodes.find(n => n.id === id);
    if (found) selectNode(found);
  }

  function stepPhysics() {
    const cx = width / 2;
    const cy = height / 2;
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      if (a === dragNode) continue;
      // Gentle repulsion so labels stay legible
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let d2 = dx * dx + dy * dy + 0.1;
        if (d2 < 2400) {
          const f = 18 / d2;
          a.vx += dx * f;
          a.vy += dy * f;
          if (b !== dragNode) {
            b.vx -= dx * f;
            b.vy -= dy * f;
          }
        }
      }
      // Gentle pull toward viewport bounds
      a.vx += (cx - a.x) * 0.0004;
      a.vy += (cy - a.y) * 0.0004;
      a.vx *= 0.82;
      a.vy *= 0.82;
      a.x = Math.max(28, Math.min(width - 28, a.x + a.vx));
      a.y = Math.max(28, Math.min(height - 28, a.y + a.vy));
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    const activeSet = new Set();
    if (selectedNode) {
      activeSet.add(selectedNode.id);
      edges.forEach(e => {
        if (e.srcNode.id === selectedNode.id) activeSet.add(e.dstNode.id);
        if (e.dstNode.id === selectedNode.id) activeSet.add(e.srcNode.id);
      });
    }

    // Draw edges
    edges.forEach(e => {
      const isHighlighted = selectedNode && (e.srcNode.id === selectedNode.id || e.dstNode.id === selectedNode.id);
      ctx.beginPath();
      ctx.moveTo(e.srcNode.x, e.srcNode.y);
      ctx.lineTo(e.dstNode.x, e.dstNode.y);
      if (isHighlighted) {
        ctx.strokeStyle = e.relation === 'SYNERGIZES_WITH' ? 'rgba(251, 191, 36, 0.85)' : 'rgba(56, 189, 248, 0.78)';
        ctx.lineWidth = 2.0;
      } else {
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.11)';
        ctx.lineWidth = 0.8;
      }
      ctx.stroke();
    });

    // Draw nodes
    const lang = window.AltStellLang || 'en';
    nodes.forEach(n => {
      const isSelected = selectedNode && selectedNode.id === n.id;
      const isHovered = hoveredNode && hoveredNode.id === n.id;
      const isNeighbor = activeSet.has(n.id);
      const alpha = (!selectedNode || isNeighbor) ? 1.0 : 0.28;

      ctx.save();
      ctx.globalAlpha = alpha;

      if (isSelected || isHovered) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 7, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(56, 189, 248, 0.25)';
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = TYPE_COLORS[n.type] || n.color;
      ctx.fill();
      ctx.lineWidth = isSelected ? 2.5 : 1;
      ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255,255,255,0.4)';
      ctx.stroke();

      if (n.type === 'book' || n.type === 'value' || isSelected || isHovered) {
        const lbl = (lang === 'ro' ? (n.label_ro || n.title_ro) : (n.label_en || n.title_en)) || n.id;
        const shortLbl = lbl.length > 22 ? lbl.slice(0, 20) + '…' : lbl;
        ctx.font = (isSelected ? '700 11.5px' : '600 10px') + ' system-ui, sans-serif';
        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.fillText(shortLbl, n.x, n.y - n.radius - 5);
      }
      ctx.restore();
    });
  }

  function startLoop() {
    if (animFrame) cancelAnimationFrame(animFrame);
    function tick() {
      stepPhysics();
      draw();
      animFrame = requestAnimationFrame(tick);
    }
    tick();
  }

  return { init, resize, focusNodeById };
})();
