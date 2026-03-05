/* ── Mobile nav ──────────────────────────────────────────────────────────── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', navLinks.classList.contains('open'));
  });
  // Close when a link is clicked
  navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));
}

/* ── Password show/hide ──────────────────────────────────────────────────── */
document.querySelectorAll('.input-wrap__toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    if (!input) return;
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    btn.textContent = isPassword ? 'Hide' : 'Show';
  });
});

/* ── Transaction search (client-side) ────────────────────────────────────── */
function filterTable(query) {
  const rows = document.querySelectorAll('.txn-row-tr');
  const q = query.toLowerCase();
  let visible = 0;
  rows.forEach(row => {
    const match = (row.dataset.desc || '').includes(q);
    row.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  const counter = document.getElementById('txn-count');
  if (counter) counter.textContent = visible;
}

/* ── Transfer review ─────────────────────────────────────────────────────── */
const reviewBtn  = document.getElementById('review-btn');
const submitBtn  = document.getElementById('submit-btn');
const reviewBox  = document.getElementById('transfer-review');

if (reviewBtn) {
  reviewBtn.addEventListener('click', () => {
    const form    = reviewBtn.closest('form');
    const from    = form.querySelector('#from_account');
    const to      = form.querySelector('#to_payee').value.trim();
    const amount  = form.querySelector('#amount').value;
    const txDate  = form.querySelector('#transfer_date').value;

    if (!to || !amount || parseFloat(amount) <= 0) {
      alert('Please fill in all required fields with valid values.');
      return;
    }

    const fromText = from ? from.options[from.selectedIndex].text : '—';
    document.getElementById('rev-from').textContent   = fromText;
    document.getElementById('rev-to').textContent     = to;
    document.getElementById('rev-amount').textContent = `$${parseFloat(amount).toFixed(2)}`;
    document.getElementById('rev-date').textContent   = txDate || 'Today';

    reviewBox.style.display = 'block';
    reviewBtn.style.display = 'none';
    submitBtn.style.display = '';
    reviewBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
}

/* ── Tab navigation (Transfer page) ─────────────────────────────────────── */
document.querySelectorAll('.tab-nav__btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-nav__btn').forEach(b => b.classList.remove('tab-nav__btn--active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('tab-panel--active'));
    btn.classList.add('tab-nav__btn--active');
    const panel = document.getElementById(`tab-${btn.dataset.tab}`);
    if (panel) panel.classList.add('tab-panel--active');
  });
});

/* ── Set today's date as default for transfer date ───────────────────────── */
const dateInput = document.getElementById('transfer_date');
if (dateInput && !dateInput.value) {
  dateInput.value = new Date().toISOString().split('T')[0];
}

/* ── Auto-dismiss flash messages ─────────────────────────────────────────── */
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => {
    flash.style.transition = 'opacity .4s';
    flash.style.opacity = '0';
    setTimeout(() => flash.remove(), 400);
  }, 5000);
});
