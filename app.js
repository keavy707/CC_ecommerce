/* ══════════════════════════════════════════
   KAWAII ATELIER — app.js
   Handles: product data, rendering, cart,
   checkout, helpers, animations
   ══════════════════════════════════════════ */

/* ─── PRODUCT DATA ───────────────────────────
   NOTE: When connecting to a database, replace
   this array with an API fetch call.
   Example:
     const products = await fetch('/api/products').then(r => r.json());
   Each product object shape must match this schema.
──────────────────────────────────────────── */
const products = [
  // T-SHIRTS
  {id:'ts-001',code:'MO-001',name:'Impression Sunrise Tee',type:'tshirt',price:1290,stock:15,art:'art-sunrise',emoji:'🌅',desc:'Screen-printed on 220gsm cotton'},
  {id:'ts-002',code:'MO-002',name:'Water Lilies Tee',type:'tshirt',price:1290,stock:10,art:'art-waterlily',emoji:'💧',desc:'Heavyweight jersey, unisex cut'},
  {id:'ts-003',code:'DE-001',name:'Ballet Tee',type:'tshirt',price:1390,stock:8,art:'art-ballet',emoji:'🎀',desc:'Organic cotton, oversized fit'},
  {id:'ts-004',code:'RE-001',name:'Regatta Tee',type:'tshirt',price:1290,stock:0,art:'art-boating',emoji:'⛵',desc:'Premium ring-spun cotton'},
  // ENAMEL PINS
  {id:'pn-001',code:'MO-003',name:'Waterlily Pin',type:'pin',price:550,stock:30,art:'art-waterlily',emoji:'💧',desc:'Hard enamel, gold plating'},
  {id:'pn-002',code:'MO-004',name:'Sunrise Pin',type:'pin',price:550,stock:22,art:'art-sunrise',emoji:'🌅',desc:'1.5" cloisonné enamel'},
  {id:'pn-003',code:'DE-002',name:'Ballet Pin',type:'pin',price:500,stock:18,art:'art-ballet',emoji:'🎀',desc:'Soft enamel, rubber clasp'},
  {id:'pn-004',code:'PI-001',name:'Parasol Pin',type:'pin',price:500,stock:14,art:'art-parasol',emoji:'☂️',desc:'Hard enamel, silver plating'},
  // STICKERS
  {id:'st-001',code:'MO-005',name:'Garden Sticker Pack',type:'sticker',price:290,stock:50,art:'art-garden',emoji:'🌷',desc:'Holo vinyl, 4-pack'},
  {id:'st-002',code:'CA-001',name:'Cathedral Sticker',type:'sticker',price:290,stock:40,art:'art-rouen',emoji:'⛪',desc:'Matte archival vinyl'},
  {id:'st-003',code:'PI-002',name:'Boulevard Sticker',type:'sticker',price:250,stock:60,art:'art-boulevard',emoji:'🌃',desc:'Clear vinyl, waterproof'},
  {id:'st-004',code:'MO-006',name:'Bridge Sticker Pack',type:'sticker',price:290,stock:0,art:'art-bridge',emoji:'🌉',desc:'Foil-finish vinyl pack'},
  // ART CARDS
  {id:'ac-001',code:'DE-003',name:'Ballet Art Card',type:'artcard',price:750,stock:20,art:'art-ballet',emoji:'🩰',desc:'Letterpress on cotton rag'},
  {id:'ac-002',code:'MO-007',name:'Haystacks Art Card',type:'artcard',price:750,stock:15,art:'art-haystacks',emoji:'🌾',desc:'Giclée, numbered edition'},
  {id:'ac-003',code:'RE-002',name:'Parasol Art Card',type:'artcard',price:700,stock:10,art:'art-parasol',emoji:'☂️',desc:'Silkscreen, 5-colour print'},
  {id:'ac-004',code:'IR-001',name:'Iris Art Card',type:'artcard',price:700,stock:7,art:'art-iris',emoji:'🌸',desc:'Risograph, hand-signed'},
];

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
      <div class="card-img ${p.art}">
        <div class="card-img-inner">
          <span>${p.emoji}</span>
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

  // Remove old items
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
      <div class="cart-item-thumb ${item.art}">${item.emoji}</div>
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

function placeOrder() {
  /* ──────────────────────────────────────────
     DATABASE HOOK POINT
     Replace this block with an API call:

     const orderPayload = {
       items: cart,
       customer: {
         name:     fname.value + ' ' + lname.value,
         email:    email.value,
         address:  addr1.value,
         city:     city.value,
         province: province.value,
       },
       paymentMethod: paymethod.value,
       total: cart.reduce((s,i) => s+(i.price*i.qty), 0) + 120
     };
     const res = await fetch('/api/orders', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(orderPayload)
     });
     const order = await res.json();
     document.getElementById('orderNum').textContent = `Order #${order.id}`;
  ────────────────────────────────────────── */

  // Basic field validation
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

  // Show success
  document.getElementById('checkoutForm').style.display = 'none';
  const sv = document.getElementById('successView');
  sv.classList.add('show');
  const orderNum = 'KA' + Date.now().toString().slice(-6);
  document.getElementById('orderNum').textContent = `Order #${orderNum}`;
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
renderProducts();
