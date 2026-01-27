
const carta = [
    { nombre: "Café Expresso", precio: 10 },
    { nombre: "Café Clásico", precio: 8 },
    { nombre: "Espresso Martini", precio: 12 },
    { nombre: "Carajillo", precio: 15 },
    { nombre: "Café Calypso", precio: 13 }
];

let currentUser = null;
let loginAttempts = 3;
let cart = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') login();
    });
});

// Login function
function login() {
    const username = document.getElementById('username').value.trim().toLowerCase();
    const password = document.getElementById('password').value.trim();

    fetch("/api/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showError(data.error || "Error de login");
            return;
        }

        currentUser = data.user.username;

        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('menuScreen').style.display = 'block';
        document.getElementById('currentUser').textContent = currentUser;

        loadMenu();
    })
    .catch(err => {
        showError("Error conectando al servidor");
        console.error(err);
    });
}


function showError(message) {
    const errorMsg = document.getElementById('errorMsg');
    errorMsg.textContent = message;
    errorMsg.style.display = 'block';
}

function logout() {
    document.getElementById('menuScreen').style.display = 'none';
    document.getElementById('loginScreen').style.display = 'block';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('password').disabled = false;
    currentUser = null;
    loginAttempts = 3;
    cart = [];
}

// Load menu
function loadMenu() {
    const menuGrid = document.getElementById('menuGrid');
    menuGrid.innerHTML = '';

    carta.forEach((item, index) => {
        const menuItem = document.createElement('div');
        menuItem.className = 'menu-item';
        menuItem.innerHTML = `
            <h3>${item.nombre}</h3>
            <div class="price">S/. ${item.precio.toFixed(2)}</div>
            <div class="quantity-controls">
                <button class="quantity-btn" onclick="changeQuantity(${index}, -1)">−</button>
                <div class="quantity-display" id="qty-${index}">0</div>
                <button class="quantity-btn" onclick="changeQuantity(${index}, 1)">+</button>
            </div>
        `;
        menuGrid.appendChild(menuItem);
    });
}

function changeQuantity(index, delta) {
    const qtyDisplay = document.getElementById(`qty-${index}`);
    let currentQty = parseInt(qtyDisplay.textContent);
    currentQty = Math.max(0, currentQty + delta);
    qtyDisplay.textContent = currentQty;

    updateCart(index, currentQty);
}

function updateCart(index, quantity) {
    const item = carta[index];
    const existingIndex = cart.findIndex(c => c.nombre === item.nombre);

    if (quantity === 0) {
        if (existingIndex !== -1) {
            cart.splice(existingIndex, 1);
        }
    } else {
        if (existingIndex !== -1) {
            cart[existingIndex].cantidad = quantity;
            cart[existingIndex].subtotal = quantity * item.precio;
        } else {
            cart.push({
                nombre: item.nombre,
                precio: item.precio,
                cantidad: quantity,
                subtotal: quantity * item.precio
            });
        }
    }

    renderCart();
}

function renderCart() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');

    if (cart.length === 0) {
        cartItems.innerHTML = '<div class="empty-cart">🛒 Tu carrito está vacío<br>Selecciona productos del menú</div>';
        cartTotal.style.display = 'none';
        return;
    }

    cartItems.innerHTML = '';
    let subtotal = 0;

    cart.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.nombre}</div>
                <div class="cart-item-quantity">${item.cantidad} x S/. ${item.precio.toFixed(2)}</div>
            </div>
            <div class="cart-item-price">S/. ${item.subtotal.toFixed(2)}</div>
        `;
        cartItems.appendChild(cartItem);
        subtotal += item.subtotal;
    });

    const igv = subtotal * 0.18;
    const total = subtotal + igv;

    document.getElementById('subtotal').textContent = `S/. ${subtotal.toFixed(2)}`;
    document.getElementById('igv').textContent = `S/. ${igv.toFixed(2)}`;
    document.getElementById('total').textContent = `S/. ${total.toFixed(2)}`;
    cartTotal.style.display = 'block';
}

function generateTicket() {
    const now = new Date();
    const fecha = now.toLocaleDateString('es-PE');
    const hora = now.toLocaleTimeString('es-PE');

    let subtotal = 0;
    cart.forEach(item => subtotal += item.subtotal);
    
    const igv = subtotal * 0.18;
    const total = subtotal + igv;

    let ticketHTML = `
        <div class="ticket-header">
            <h2>☕ Café Bar 40°</h2>
            <div class="ticket-date">
                Fecha: ${fecha}<br>
                Hora: ${hora}<br>
                Atendido por: ${currentUser}
            </div>
        </div>
        <div class="ticket-items">
    `;

    cart.forEach(item => {
        ticketHTML += `
            <div class="ticket-item">
                <span>${item.cantidad} x ${item.nombre}</span>
                <span>S/. ${item.subtotal.toFixed(2)}</span>
            </div>
        `;
    });

    ticketHTML += `
        </div>
        <div class="ticket-totals">
            <div class="ticket-total-row">
                <span>Subtotal:</span>
                <span>S/. ${subtotal.toFixed(2)}</span>
            </div>
            <div class="ticket-total-row">
                <span>IGV (18%):</span>
                <span>S/. ${igv.toFixed(2)}</span>
            </div>
            <div class="ticket-total-row ticket-final">
                <span>TOTAL A PAGAR:</span>
                <span>S/. ${total.toFixed(2)}</span>
            </div>
        </div>
        <div class="ticket-footer">
            ¡Gracias por su compra!<br>
            Vuelva pronto ☕
        </div>
    `;

    document.getElementById('ticket').innerHTML = ticketHTML;
    document.getElementById('menuScreen').style.display = 'none';
    document.getElementById('ticketScreen').style.display = 'block';
}

function newOrder() {
    cart = [];
    carta.forEach((_, index) => {
        document.getElementById(`qty-${index}`).textContent = '0';
    });
    document.getElementById('ticketScreen').style.display = 'none';
    document.getElementById('menuScreen').style.display = 'block';
    renderCart();
}
