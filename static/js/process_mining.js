let allFlowDots = [];
let animationFrame;

async function loadDropdowns() {
  const states = await fetch('/available-states').then(res => res.json());
  const users = await fetch('/available-users').then(res => res.json());
  states.forEach(state => {
    const opt = document.createElement("option");
    opt.value = opt.text = state;
    document.getElementById('state').appendChild(opt);
  });
  users.forEach(user => {
    const opt = document.createElement("option");
    opt.value = opt.text = user;
    document.getElementById('user').appendChild(opt);
  });
}

function clearDots() {
  if (animationFrame) cancelAnimationFrame(animationFrame);
  allFlowDots.forEach(obj => obj.dot.remove());
  allFlowDots = [];
}

function animateAllFlows(cy) {
  clearDots();
  const flowColors = ['#f39c12', '#27ae60', '#3498db', '#9b59b6', '#e74c3c'];
  cy.edges().forEach(edge => {
    const source = edge.source().position();
    const target = edge.target().position();
    const color = flowColors[Math.floor(Math.random() * flowColors.length)];
    const dot = cy.add({
      group: 'nodes',
      position: { x: source.x, y: source.y },
      data: { id: `dot-${edge.id()}-${Math.random()}` },
      style: { 'background-color': color },
      classes: 'flow-dot'
    });
    allFlowDots.push({ dot, source, target, progress: Math.random() });
  });
  function animate() {
    allFlowDots.forEach(obj => {
      const { dot, source, target } = obj;
      obj.progress += 0.002;
      if (obj.progress > 1) obj.progress = 0;
      dot.position({ x: source.x + (target.x - source.x) * obj.progress, y: source.y + (target.y - source.y) * obj.progress });
    });
    animationFrame = requestAnimationFrame(animate);
  }
  animate();
}

function animateNeighborhoodFlows(cy, neighborhood) {
  clearDots();
  const flowColors = ['#f39c12', '#27ae60', '#3498db', '#9b59b6', '#e74c3c'];
  const edges = neighborhood.filter(ele => ele.isEdge());
  edges.forEach(edge => {
    const source = edge.source().position();
    const target = edge.target().position();
    const color = flowColors[Math.floor(Math.random() * flowColors.length)];
    const dot = cy.add({
      group: 'nodes',
      position: { x: source.x, y: source.y },
      data: { id: `dot-${edge.id()}-${Math.random()}` },
      style: { 'background-color': color },
      classes: 'flow-dot'
    });
    allFlowDots.push({ dot, source, target, progress: Math.random() });
  });
  function animate() {
    allFlowDots.forEach(obj => {
      const { dot, source, target } = obj;
      obj.progress += 0.002;
      if (obj.progress > 1) obj.progress = 0;
      dot.position({ x: source.x + (target.x - source.x) * obj.progress, y: source.y + (target.y - source.y) * obj.progress });
    });
    animationFrame = requestAnimationFrame(animate);
  }
  animate();
}

function renderGraph(elements) {
  const cy = cytoscape({
    container: document.getElementById('cy'),
    elements: elements,
    layout: {
      name: 'cose-bilkent',
      animate: 'end',
      animationDuration: 1000,
      fit: true,
      padding: 50,
      nodeDimensionsIncludeLabels: true,
      nodeRepulsion: 1000000,
      idealEdgeLength: 400,
      edgeElasticity: 0.1,
      nestingFactor: 1.2,
      gravity: 0.9,
      numIter: 3000
    },
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'background-color': 'data(color)',
          'color': '#fff',
          'shape': 'rectangle',
          'text-wrap': 'wrap',
          'text-max-width': 80,
          'font-size': 8,
          'text-valign': 'center',
          'text-halign': 'center',
          'padding': '4px',
          'width': 'label',
          'height': 'label',
          'border-width': 1,
          'border-color': '#333'
        }
      },
      {
        selector: 'edge',
        style: {
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'width': 1,
          'line-color': '#bbb',
          'target-arrow-color': '#bbb',
          'label': 'data(label)',
          'font-size': 7,
          'text-background-color': '#fff',
          'text-background-opacity': 1,
          'text-background-padding': '2px'
        }
      },
      {
        selector: '.flow-dot',
        style: {
          'width': 6,
          'height': 6,
          'shape': 'ellipse',
          'z-index-compare': 'manual',
          'z-index': 2,
          'opacity': 0.6
        }
      },
      {
        selector: 'node.faded, edge.faded',
        style: {
          'opacity': 0.1,
          'text-opacity': 0.1
        }
      }
    ]
  });

  animateAllFlows(cy);

  cy.on('tap', 'node', function(evt) {
    const node = evt.target;
    const neighborhood = node.closedNeighborhood();
    cy.elements().addClass('faded');
    neighborhood.removeClass('faded');
    animateNeighborhoodFlows(cy, neighborhood);
    cy.animate({ fit: { eles: neighborhood, padding: 80 }, duration: 500 });
  });

  cy.on('tap', function(evt) {
    if (evt.target === cy) {
      cy.elements().removeClass('faded');
      clearDots();
      animateAllFlows(cy);
    }
  });
}

async function loadGraph() {
  const state = document.getElementById('state').value;
  const user = document.getElementById('user').value;
  const freq = document.getElementById('freq').value;
  const params = new URLSearchParams();
  if (state) params.append("state", state);
  if (user) params.append("user", user);
  if (freq) params.append("minFreq", freq);
  const response = await fetch(`/vsm-data?${params.toString()}`);
  const elements = await response.json();
  renderGraph(elements);
}

document.getElementById('state').addEventListener('change', loadGraph);
document.getElementById('user').addEventListener('change', loadGraph);
document.getElementById('freq').addEventListener('change', loadGraph);

loadDropdowns().then(loadGraph);
