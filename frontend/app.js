/* ══════════════════════════════════════════
   KAWAII ATELIER — app.js
   Handles: product data, rendering, cart,
   checkout, helpers, animations
   ══════════════════════════════════════════ */

const API_BASE = 'http://localhost:8000';
let products = [];

async function loadProducts() {
  try {
    const res = await fetch(`${API_BASE}/api/products`);
    products = await res.json();
    products = products.map(p => ({ ...p, price: parseFloat(p.price) }));
    renderProducts();
  } catch (err) {
    console.error('Failed to load products', err);
    toast('⚠️ Could not load products from server');
  }
}

const typeLabel    = {tshirt:'T-Shirt',pin:'Enamel Pin',sticker:'Sticker',artcard:'Art Card'};
const typeTagClass = {tshirt:'tag-tshirt',pin:'tag-pin',sticker:'tag-sticker',artcard:'tag-artcard'};

let cart          = [];
let currentStep   = 1;
let currentFilter = 'all';

/* ─── RENDER PRODUCTS ──────────────────────── */
function renderProducts() {
  const grid     = document.getElementById('productGrid');
  const filtered = currentFilter === 'all'
    ? products
    : products.filter(p => p.type === currentFilter);

  grid.innerHTML = filtered.map(p => `
    <div class="product-card${p.stock === 0 ? ' out-of-stock' : ''}" id="card-${p.id}">
      <div class="card-img">
        <div class="card-img-inner ${p.art}">
          <img
            src="assets/products/${p.image}"
            alt="${p.name}"
            class="card-product-img"
            onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"
          >
          <span class="card-img-fallback" style="display:none">${p.emoji}</span>
        </div>
      </div>
      <div class="card-body">
        <div class="card-code">${p.code}</div>
        <div class="card-name">${p.name}${p.stock === 0 ? ' <span style="font-family:var(--mono);font-size:.65rem;color:var(--rust)">SOLD OUT</span>' : ''}</div>
        <div class="card-desc">${p.desc}</div>
        <div class="card-footer">
          <span class="card-price">₱${p.price.toLocaleString()}</span>
          <span class="card-tag ${typeTagClass[p.type]}">${typeLabel[p.type]}</span>
        </div>
        <div class="card-stock ${p.stock === 0 ? '' : p.stock <= 5 ? 'stock-low' : 'stock-ok'}">
          ${p.stock === 0
            ? '✕ Sold out'
            : p.stock <= 5
              ? `⚡ Only ${p.stock} left`
              : `✦ ${p.stock} in stock`}
        </div>
      </div>
      ${p.stock > 0
        ? `<button class="card-add-btn" onclick="addToCart('${p.id}')">★ Add to Cart</button>`
        : ''}
    </div>
  `).join('');
}

function filterProducts(type, btn) {
  currentFilter = type;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderProducts();
}

/* ─── CART ─────────────────────────────────── */
function addToCart(id) {
  const p        = products.find(x => x.id === id);
  const existing = cart.find(x => x.id === id);
  if (existing) {
    if (existing.qty < p.stock) { existing.qty++; toast(`+1 ${p.emoji} ${p.name}`); }
    else { toast('⚠️ Max stock reached!'); return; }
  } else {
    cart.push({ ...p, qty: 1 });
    toast(`★ Added: ${p.name}`);
  }
  updateCartUI();
  updateCartCount();
}

function removeFromCart(id) {
  cart = cart.filter(x => x.id !== id);
  updateCartUI();
  updateCartCount();
}

function changeQty(id, delta) {
  const item = cart.find(x => x.id === id);
  const p    = products.find(x => x.id === id);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) { removeFromCart(id); return; }
  if (item.qty > p.stock) { item.qty = p.stock; toast('⚠️ Max stock reached!'); }
  updateCartUI();
  updateCartCount();
}

function updateCartCount() {
  const total = cart.reduce((s, i) => s + i.qty, 0);
  document.getElementById('cartCount').textContent = total;
}

function updateCartUI() {
  const container = document.getElementById('cartItems');
  const empty     = document.getElementById('cartEmpty');
  const totalEl   = document.getElementById('cartTotal');
  const total     = cart.reduce((s, i) => s + (i.price * i.qty), 0);

  totalEl.textContent = `₱${total.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  document.querySelectorAll('.cart-item').forEach(el => el.remove());

  if (cart.length === 0) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  const frag = document.createDocumentFragment();
  cart.forEach(item => {
    const div       = document.createElement('div');
    div.className   = 'cart-item';
    div.id          = `ci-${item.id}`;
    div.innerHTML   = `
      <div class="cart-item-thumb ${item.art}">
        <img
          src="assets/products/${item.image}"
          alt="${item.name}"
          class="cart-thumb-img"
          onerror="this.style.display='none';this.nextElementSibling.style.display='block'"
        >
        <span class="cart-thumb-fallback" style="display:none">${item.emoji}</span>
      </div>
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-meta">${typeLabel[item.type]} · ${item.code}</div>
        <div class="cart-item-price">₱${(item.price * item.qty).toLocaleString('en-PH', { minimumFractionDigits: 2 })}</div>
        <div class="qty-ctrl">
          <button class="qty-btn" onclick="changeQty('${item.id}', -1)">−</button>
          <span class="qty-num">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty('${item.id}', 1)">+</button>
          <small style="font-family:var(--mono);font-size:.6rem;color:var(--warm);margin-left:.4rem">/${item.stock} avail</small>
        </div>
        <button class="cart-item-remove" onclick="removeFromCart('${item.id}')">✕ remove</button>
      </div>
    `;
    frag.appendChild(div);
  });
  container.insertBefore(frag, empty);
}

function toggleCart() {
  document.getElementById('cartOverlay').classList.toggle('open');
  document.getElementById('cartDrawer').classList.toggle('open');
}

/* ─── CHECKOUT ──────────────────────────────── */
function openCheckout() {
  if (cart.length === 0) { toast('🛒 Add items first!'); return; }
  toggleCart();
  setTimeout(() => {
    document.getElementById('checkoutModal').classList.add('open');
    goStep(1);
  }, 300);
}

function closeCheckout() {
  document.getElementById('checkoutModal').classList.remove('open');
}

function goStep(n) {
  currentStep = n;
  document.querySelectorAll('.form-section').forEach((s, i) => {
    s.classList.toggle('active', i + 1 === n);
  });
  document.querySelectorAll('.step-tab').forEach((t, i) => {
    t.classList.remove('active', 'done');
    if (i + 1 === n)      t.classList.add('active');
    else if (i + 1 < n)   t.classList.add('done');
  });
  if (n === 3) buildReview();
}

function buildReview() {
  const sub = cart.reduce((s, i) => s + (i.price * i.qty), 0);
  const ship = 120;
  document.getElementById('reviewSubtotal').textContent = `₱${sub.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`;
  document.getElementById('reviewTotal').textContent    = `₱${(sub + ship).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`;
  document.getElementById('reviewItems').innerHTML      = cart.map(i => `
    <div class="order-row">
      <span>${i.emoji} ${i.name} × ${i.qty}</span>
      <span style="font-family:var(--mono)">₱${(i.price * i.qty).toLocaleString('en-PH', { minimumFractionDigits: 2 })}</span>
    </div>
  `).join('');

  const addr = [
    document.getElementById('fname')?.value,
    document.getElementById('lname')?.value + ',',
    document.getElementById('addr1')?.value + ',',
    document.getElementById('city')?.value + ',',
    document.getElementById('province')?.value
  ].filter(x => x && x !== ',').join(' ');
  document.getElementById('reviewAddress').textContent = addr || 'No address entered';
}

/* ─── PHONE VALIDATION ──────────────────────── */
function validatePhone(phone) {
  // Philippine mobile: starts with 09, exactly 11 digits, numbers only
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length !== 11) return { ok: false, msg: 'Phone must be exactly 11 digits' };
  if (!cleaned.startsWith('09')) return { ok: false, msg: 'Phone must start with 09 (Philippine mobile)' };
  return { ok: true, cleaned: cleaned };
}

function formatPhoneInput(el) {
  let v = el.value.replace(/\D/g, '').slice(0, 11);
  el.value = v;
}

/* ─── PLACE ORDER ──────────────────────────── */
async function placeOrder() {
  const required = ['fname', 'lname', 'email'];
  let ok = true;
  required.forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.value.trim()) {
      el.style.borderColor = 'var(--pink)';
      ok = false;
    } else if (el) {
      el.style.borderColor = '';
    }
  });
  if (!ok) { toast('⚠️ Please fill all required fields'); return; }

  // Phone validation
  const phoneEl = document.getElementById('phone');
  const phoneVal = phoneEl?.value?.trim() || '';
  if (phoneVal) {
    const phoneCheck = validatePhone(phoneVal);
    if (!phoneCheck.ok) {
      phoneEl.style.borderColor = 'var(--pink)';
      toast('⚠️ ' + phoneCheck.msg);
      return;
    }
    phoneEl.style.borderColor = '';
    phoneEl.value = phoneCheck.cleaned;
  }

  // Address validation - must be in Philippines
  const city = document.getElementById('city')?.value?.trim() || '';
  const province = document.getElementById('province')?.value?.trim() || '';
  if (!city && !province) {
    toast('⚠️ Please enter your city and province');
    return;
  }

  const orderPayload = {
    items: cart.map(i => ({ product_id: i.id, quantity: i.qty, unit_price: i.price })),
    customer_name: document.getElementById('fname').value + ' ' + document.getElementById('lname').value,
    customer_email: document.getElementById('email').value,
    customer_phone: document.getElementById('phone').value,
    shipping_address: [
      document.getElementById('addr1').value,
      document.getElementById('city').value,
      document.getElementById('province').value,
      'Philippines'
    ].filter(Boolean).join(', '),
    payment_method: document.getElementById('paymethod').value,
    total_amount: cart.reduce((s, i) => s + (i.price * i.qty), 0) + 120
  };

  try {
    const res = await fetch(`${API_BASE}/api/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderPayload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Order failed');

    document.getElementById('checkoutForm').style.display = 'none';
    document.getElementById('successView').classList.add('show');
    document.getElementById('orderNum').textContent = `Order #${data.id}`;
    toast('🎉 Order confirmed!');
  } catch (err) {
    toast('⚠️ ' + err.message);
  }
}

function resetOrder() {
  cart = [];
  updateCartUI();
  updateCartCount();
  document.getElementById('checkoutForm').style.display = 'block';
  document.getElementById('successView').classList.remove('show');
  goStep(1);
}

/* ─── INPUT FORMATTERS ──────────────────────── */
function formatCard(el) {
  let v = el.value.replace(/\D/g, '').slice(0, 16);
  el.value = v.replace(/(.{4})/g, '$1 ').trim();
}
function formatExpiry(el) {
  let v = el.value.replace(/\D/g, '').slice(0, 4);
  if (v.length >= 2) v = v.slice(0, 2) + ' / ' + v.slice(2);
  el.value = v;
}

/* ─── TOAST ─────────────────────────────────── */
function toast(msg) {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className   = 'toast';
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), 2700);
}

/* ─── INIT ──────────────────────────────────── */
loadProducts();
