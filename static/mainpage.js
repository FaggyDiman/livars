// Modal functions
function showModal(id) {
    document.getElementById(id).style.display = 'block';
}

function hideModal(id) {
    document.getElementById(id).style.display = 'none';
}

async function handleForm(event, url) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    if (result.status === 'ok') {
        location.reload();
    } else {
        alert(result.message || 'Произошла ошибка');
    }
}

document.getElementById('loginForm').onsubmit = (e) => handleForm(e, '/login');
document.getElementById('registerForm').onsubmit = (e) => handleForm(e, '/register');

async function logout() {
    const response = await fetch('/logout', { method: 'POST' });
    if (response.ok) location.reload();
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}

// Map Canvas functions
const canvas = document.getElementById('mapCanvas');
const ctx = canvas.getContext('2d');
const nodeInfo = document.getElementById('nodeInfo');

let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let nodes = [];

// Размеры карты
const MAP_WIDTH = 2000;
const MAP_HEIGHT = 1000;

// Загружаем все ноды с сервера
async function loadNodes() {
    try {
        const response = await fetch('/api/nodes');
        const data = await response.json();
        nodes = data.nodes || [];
        drawMap();
        if (!nodes.length) {
            nodeInfo.textContent = 'Пока нет точек на карте. Кликните на свободное место, чтобы создать свою точку.';
        }
    } catch (error) {
        console.error('Error loading nodes:', error);
    }
}

function showNodeInfo(node) {
    const createdDate = node.created_at ? new Date(node.created_at).toLocaleString('ru-RU') : 'неизвестно';
    nodeInfo.innerHTML = `
        <strong>Точка пользователя:</strong> ${node.creator_username}<br>
        <strong>Размер:</strong> ${node.size}<br>
        <strong>Дата создания:</strong> ${createdDate}<br>
        <strong>Позиция:</strong> ${node.x}, ${node.y}
    `;
}

function clearNodeInfo() {
    nodeInfo.textContent = 'Кликните на точку, чтобы увидеть информацию о ней.';
}

function getClickedNode(clickX, clickY) {
    return nodes.find(node => {
        const dx = clickX - node.x;
        const dy = clickY - node.y;
        const radius = Math.max(node.size / 2, 10);
        return dx * dx + dy * dy <= radius * radius;
    });
}

// Функция для отрисовки карты
function drawMap() {
    // Очищаем canvas
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Сохраняем контекст и применяем смещение
    ctx.save();
    ctx.translate(offsetX, offsetY);
    
    // Рисуем сетку
    drawGrid();
    
    // Рисуем ноды
    drawNodes();
    
    // Восстанавливаем контекст
    ctx.restore();
    
    // Рисуем информацию о смещении
    drawInfo();
}

// Функция для отрисовки сетки
function drawGrid() {
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 0.5;
    
    // Вертикальные линии
    for (let x = 0; x < MAP_WIDTH; x += 100) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, MAP_HEIGHT);
        ctx.stroke();
    }
    
    // Горизонтальные линии
    for (let y = 0; y < MAP_HEIGHT; y += 100) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(MAP_WIDTH, y);
        ctx.stroke();
    }
}

// Функция для отрисовки нод
function drawNodes() {
    nodes.forEach(node => {
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.size / 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = '#000';
        ctx.font = '12px Arial';
        ctx.fillText(node.creator_username, node.x + node.size / 2 + 8, node.y - node.size / 2 - 6);
    });
}

// Функция для отрисовки информации
function drawInfo() {
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.fillText(`Position: (${Math.round(-offsetX)}, ${Math.round(-offsetY)})`, 10, 20);
    ctx.fillText(`Nodes: ${nodes.length}`, 10, 35);
}

// Event listeners для перемещения по карте
canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragStartX = e.clientX - offsetX;
    dragStartY = e.clientY - offsetY;
});

canvas.addEventListener('mousemove', (e) => {
    if (isDragging) {
        offsetX = e.clientX - dragStartX;
        offsetY = e.clientY - dragStartY;
        
        // Ограничиваем смещение
        offsetX = Math.max(-MAP_WIDTH + canvas.width, Math.min(0, offsetX));
        offsetY = Math.max(-MAP_HEIGHT + canvas.height, Math.min(0, offsetY));
        
        drawMap();
    }
});

canvas.addEventListener('mouseup', () => {
    isDragging = false;
});

canvas.addEventListener('mouseleave', () => {
    isDragging = false;
});

// Клик по карте для создания ноды или просмотра информации
canvas.addEventListener('click', async (e) => {
    if (isDragging) return;

    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left - offsetX;
    const clickY = e.clientY - rect.top - offsetY;

    const clickedNode = getClickedNode(clickX, clickY);
    if (clickedNode) {
        showNodeInfo(clickedNode);
        return;
    }

    if (clickX >= 0 && clickX <= MAP_WIDTH && clickY >= 0 && clickY <= MAP_HEIGHT) {
        try {
            const response = await fetch('/api/node/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    x: Math.round(clickX),
                    y: Math.round(clickY),
                    size: 5
                })
            });

            const result = await response.json();
            if (result.status === 'ok') {
                nodes.push(result.node);
                drawMap();
                showNodeInfo(result.node);
            } else {
                alert(result.detail || 'Не удалось создать ноду');
            }
        } catch (error) {
            console.error('Error creating node:', error);
            alert('Ошибка при создании ноды');
        }
    }
});

// Zoom функция (опционально)
canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    // Можно добавить зум если нужно
});

// Загружаем ноды при загрузке страницы
window.addEventListener('load', () => {
    loadNodes();
    
    // Также обновляем размер ноды при каждом заходе
    fetch('/api/node/grow', { method: 'POST' }).catch(err => console.log('No node to grow'));
});