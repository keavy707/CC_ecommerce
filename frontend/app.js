/* ══════════════════════════════════════════
   KAWAII ATELIER — app.js
   
   Grid is hardcoded in index.html.
   This file handles: filter, cart, checkout.

   PRODUCTS ARRAY
   - Used only for cart lookups (price, stock,
     name, image, etc.)
   - image path = assets/<filename>
   - When connecting to a DB, replace this
     array with: const products = await
     fetch('/api/products').then(r=>r.json())
     and call initCart() after.
══════════════════════════════════════════ */

const API_BASE = 'http://localhost:8000';

const products = [
  // T-SHIRTS
  { id:'ts-001', code:'MO-001', name:'Impression Sunrise Tee', type:'tshirt', price:1290, stock:15, art:'art-sunrise',   emoji:'🌅', image:'ts-sunrise.jpg',   desc:'Screen-printed on 220gsm cotton' },
  { id:'ts-002', code:'MO-002', name:'Water Lilies Tee',        type:'tshirt', price:1290, stock:10, art:'art-waterlily', emoji:'💧', image:'ts-waterlily.jpg', desc:'Heavyweight jersey, unisex cut' },
  { id:'ts-003', code:'DE-001', name:'Ballet Tee',               type:'tshirt', price:1390, stock:8,  art:'art-ballet',   emoji:'🎀', image:'ts-ballet.jpg',   desc:'Organic cotton, oversized fit' },
  { id:'ts-004', code:'RE-001', name:'Regatta Tee',              type:'tshirt', price:1290, stock:0,  art:'art-boating',  emoji:'⛵', image:'ts-regatta.jpg',  desc:'Premium ring-spun cotton' },
  // ENAMEL PINS
  { id:'pn-001', code:'MO-003', name:'Waterlily Pin',            type:'pin',    price:550,  stock:30, art:'art-waterlily', emoji:'💧', image:'pn-waterlily.jpg', desc:'Hard enamel, gold plating' },
  { id:'pn-002', code:'MO-004', name:'Sunrise Pin',              type:'pin',    price:550,  stock:22, art:'art-sunrise',   emoji:'🌅', image:'pn-sunrise.jpg',   desc:"1.5\" cloisonné enamel" },
  { id:'pn-003', code:'DE-002', name:'Ballet Pin',               type:'pin',    price:500,  stock:18, art:'art-ballet',    emoji:'🎀', image:'pn-ballet.jpg',    desc:'Soft enamel, rubber clasp' },
  { id:'pn-004', code:'PI-001', name:'Parasol Pin',              type:'pin',    price:500,  stock:14, art:'art-parasol',   emoji:'☂️', image:'pn-parasol.jpg',   desc:'Hard enamel, silver plating' },
  // STICKERS
  { id:'st-001', code:'MO-005', name:'Garden Sticker Pack',      type:'sticker', price:290, stock:50, art:'art-garden',    emoji:'🌷', image:'st-garden.jpg',    desc:'Holo vinyl, 4-pack' },
  { id:'st-002', code:'CA-001', name:'Cathedral Sticker',        type:'sticker', price:290, stock:40, art:'art-rouen',     emoji:'⛪', image:'st-cathedral.jpg', desc:'Matte archival vinyl' },
  { id:'st-003', code:'PI-002', name:'Boulevard Sticker',        type:'sticker', price:250, stock:60, art:'art-boulevard', emoji:'🌃', image:'st-boulevard.jpg', desc:'Clear vinyl, waterproof' },
  { id:'st-004', code:'MO-006', name:'Bridge Sticker Pack',      type:'sticker', price:290, stock:0,  art:'art-bridge',    emoji:'🌉', image:'st-bridge.jpg',    desc:'Foil-finish vinyl pack' },
  // ART CARDS
  { id:'ac-001', code:'DE-003', name:'Ballet Art Card',          type:'artcard', price:750, stock:20, art:'art-ballet',    emoji:'🩰', image:'ac-ballet.jpg',    desc:'Letterpress on cotton rag' },
  { id:'ac-002', code:'MO-007', name:'Haystacks Art Card',       type:'artcard', price:750, stock:15, art:'art-haystacks', emoji:'🌾', image:'ac-haystacks.jpg', desc:'Giclée, numbered edition' },
  { id:'ac-003', code:'RE-002', name:'Parasol Art Card',         type:'artcard', price:700, stock:10, art:'art-parasol',   emoji:'☂️', image:'ac-parasol.jpg',   desc:'Silkscreen, 5-colour print' },
  { id:'ac-004', code:'IR-001', name:'Iris Art Card',            type:'artcard', price:700, stock:7,  art:'art-iris',      emoji:'🌸', image:'ac-iris.jpg',       desc:'Risograph, hand-signed' },
];

const typeLabel = { tshirt:'T-Shirt', pin:'Enamel Pin', sticker:'Sticker', artcard:'Art Card' };

let cart        = [];
let currentStep = 1;

/* ─── FILTER ─────────────────────────────────
   Grid is hardcoded HTML. Filter shows/hides
   cards by their data-type attribute.
   No innerHTML overwrite — DOM stays intact.
──────────────────────────────────────────── */
function filterProducts(type, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.querySelectorAll('.product-grid .product-card').forEach(card => {
    const match = type === 'all' || card.dataset.type === type;
    card.style.display = match ? '' : 'none';
  });
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
  document.getElementById('cartCount').textContent = cart.reduce((s, i) => s + i.qty, 0);
}

function updateCartUI() {
  const container = document.getElementById('cartItems');
  const empty     = document.getElementById('cartEmpty');
  const totalEl   = document.getElementById('cartTotal');
  const total     = cart.reduce((s, i) => s + (i.price * i.qty), 0);

  totalEl.textContent = `₱${total.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.querySelectorAll('.cart-item').forEach(el => el.remove());

  if (cart.length === 0) { empty.style.display = 'flex'; return; }
  empty.style.display = 'none';

  const frag = document.createDocumentFragment();
  cart.forEach(item => {
    const div     = document.createElement('div');
    div.className = 'cart-item';
    div.id        = `ci-${item.id}`;
    div.innerHTML = `
      <div class="cart-item-thumb ${item.art}">
        <img
          src="assets/${item.image}"
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
  document.querySelectorAll('.form-section').forEach((s, i) => s.classList.toggle('active', i + 1 === n));
  document.querySelectorAll('.step-tab').forEach((t, i) => {
    t.classList.remove('active', 'done');
    if (i + 1 === n)    t.classList.add('active');
    else if (i + 1 < n) t.classList.add('done');
  });
  if (n === 2) updateCODAmount();
  if (n === 3) buildConfirm();
}

function updateCODAmount() {
  const sub  = cart.reduce((s, i) => s + (i.price * i.qty), 0);
  const el   = document.getElementById('codAmount');
  if (el) el.textContent = (sub + 120).toLocaleString('en-PH', { minimumFractionDigits: 2 });
}

function buildConfirm() {
  const sub  = cart.reduce((s, i) => s + (i.price * i.qty), 0);
  const ship = 120;

  document.getElementById('confirmSubtotal').textContent = `₱${sub.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`;
  document.getElementById('confirmTotal').textContent    = `₱${(sub + ship).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`;
  document.getElementById('confirmItems').innerHTML      = cart.map(i => `
    <div class="confirm-row">
      <span>${i.emoji} ${i.name} × ${i.qty}</span>
      <span style="font-family:var(--mono)">₱${(i.price * i.qty).toLocaleString('en-PH', { minimumFractionDigits: 2 })}</span>
    </div>
  `).join('');

  const addr = [
    document.getElementById('fname')?.value,
    document.getElementById('lname')?.value,
    document.getElementById('addr1')?.value,
    document.getElementById('city')?.value,
    document.getElementById('province')?.value,
    'Philippines'
  ].filter(Boolean).join(', ');
  document.getElementById('confirmAddress').textContent = addr || 'No address entered';
}

/* ─── PHONE VALIDATION ──────────────────────── */
function validatePhone(phone) {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length !== 11)          return { ok:false, msg:'Phone must be exactly 11 digits' };
  if (!cleaned.startsWith('09'))      return { ok:false, msg:'Phone must start with 09 (Philippine mobile)' };
  return { ok:true, cleaned };
}
function formatPhoneInput(el) {
  el.value = el.value.replace(/\D/g, '').slice(0, 11);
}

/* ─── PLACE ORDER ────────────────────────────
   DB HOOK: swap the simulated block below
   with the real fetch('/api/orders/') call
   that is commented out beneath it.
──────────────────────────────────────────── */
async function placeOrder() {
  // Required field check
  const required = ['fname', 'lname', 'email'];
  let ok = true;
  required.forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.value.trim()) { el.style.borderColor = 'var(--pink)'; ok = false; }
    else if (el) el.style.borderColor = '';
  });
  if (!ok) { toast('⚠️ Please fill all required fields'); return; }

  // Phone check
  const phoneEl  = document.getElementById('phone');
  const phoneVal = phoneEl?.value?.trim() || '';
  if (phoneVal) {
    const check = validatePhone(phoneVal);
    if (!check.ok) { phoneEl.style.borderColor = 'var(--pink)'; toast('⚠️ ' + check.msg); return; }
    phoneEl.style.borderColor = '';
    phoneEl.value = check.cleaned;
  }

  // Address check
  const city     = document.getElementById('city')?.value?.trim()     || '';
  const province = document.getElementById('province')?.value?.trim() || '';
  if (!city && !province) { toast('⚠️ Please enter your city and province'); return; }

  const orderPayload = {
    items: cart.map(i => ({ product_id: i.id, quantity: i.qty, unit_price: i.price })),
    customer_name:    document.getElementById('fname').value + ' ' + document.getElementById('lname').value,
    customer_email:   document.getElementById('email').value,
    customer_phone:   document.getElementById('phone').value,
    shipping_address: [
      document.getElementById('addr1').value,
      city, province, 'Philippines'
    ].filter(Boolean).join(', '),
    payment_method: document.getElementById('paymethod').value,
    total_amount:   cart.reduce((s, i) => s + (i.price * i.qty), 0) + 120
  };

  /* ── SIMULATED SUCCESS (remove when DB is live) ── */
  const simulatedOrderId = 'KA' + Date.now().toString().slice(-6);
  showOrderSuccess(simulatedOrderId);

  /* ── REAL API CALL (uncomment when DB is ready) ──
  try {
    const res  = await fetch(`${API_BASE}/api/orders/`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(orderPayload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Order failed');
    showOrderSuccess(data.id);
  } catch (err) {
    toast('⚠️ ' + err.message);
  }
  ─────────────────────────────────────────────── */
}

function showOrderSuccess(orderId) {
  document.getElementById('checkoutForm').style.display = 'none';
  document.getElementById('successView').classList.add('show');
  document.getElementById('orderNum').textContent = `Order #${orderId}`;
  toast('🎉 Order confirmed!');
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
// Grid is already in the HTML — nothing to render.
// Cart count starts at 0. Ready.