const API_BASE = window.ENV_API_URL || 'http://localhost:8000';

const api = {
  getToken: () => localStorage.getItem('tf_token'),
  getUser: () => JSON.parse(localStorage.getItem('tf_user') || 'null'),
  setAuth: (token, user) => {
    localStorage.setItem('tf_token', token);
    localStorage.setItem('tf_user', JSON.stringify(user));
  },
  clearAuth: () => {
    localStorage.removeItem('tf_token');
    localStorage.removeItem('tf_user');
  },
  isLoggedIn: () => !!localStorage.getItem('tf_token'),

  async request(method, path, body = null) {
    const token = this.getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (res.status === 401) { this.clearAuth(); window.location.href = '/index.html'; return; }
    const data = res.status !== 204 ? await res.json() : null;
    if (!res.ok) {
      const msg = data?.detail || 'Something went wrong';
      throw new Error(Array.isArray(msg) ? msg.map(e => e.msg).join(', ') : msg);
    }
    return data;
  },
  get: (path) => api.request('GET', path),
  post: (path, body) => api.request('POST', path, body),
  put: (path, body) => api.request('PUT', path, body),
  delete: (path) => api.request('DELETE', path),
};

function requireAuth() {
  if (!api.isLoggedIn()) window.location.href = '/index.html';
}

// Toast notification
function showToast(message, type = 'success') {
  const existing = document.getElementById('tf-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.id = 'tf-toast';
  const icon = type === 'success'
    ? `<svg class="w-4 h-4 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`
    : `<svg class="w-4 h-4 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`;
  toast.className = 'fixed bottom-6 right-6 z-[9999] flex items-center gap-3 px-4 py-3 bg-gray-900 text-white text-sm rounded-xl shadow-xl border border-gray-700 transition-all duration-300 translate-y-2 opacity-0';
  toast.innerHTML = `${icon}<span>${message}</span>`;
  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });
  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Confirm dialog - replaces browser alert
function showConfirm(message, onConfirm, options = {}) {
  const existing = document.getElementById('tf-confirm');
  if (existing) existing.remove();
  const overlay = document.createElement('div');
  overlay.id = 'tf-confirm';
  overlay.className = 'fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-[9998] p-4';
  overlay.innerHTML = `
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 transform transition-all">
      <div class="flex items-start gap-4 mb-5">
        <div class="w-10 h-10 rounded-full ${options.danger ? 'bg-red-50' : 'bg-gray-100'} flex items-center justify-center flex-shrink-0">
          ${options.danger
            ? `<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`
            : `<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
          }
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-900 mb-1">${options.title || 'Confirm'}</p>
          <p class="text-sm text-gray-500">${message}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button id="tf-confirm-cancel" class="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">${options.cancelText || 'Cancel'}</button>
        <button id="tf-confirm-ok" class="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${options.danger ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-gray-900 hover:bg-gray-800 text-white'}">${options.confirmText || 'Confirm'}</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  document.getElementById('tf-confirm-cancel').onclick = () => overlay.remove();
  document.getElementById('tf-confirm-ok').onclick = () => { overlay.remove(); onConfirm(); };
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function statusBadge(status) {
  const map = { todo: 'bg-gray-100 text-gray-600', in_progress: 'bg-blue-50 text-blue-600', done: 'bg-green-50 text-green-600' };
  const label = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' };
  return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${map[status] || 'bg-gray-100 text-gray-600'}">${label[status] || status}</span>`;
}

function priorityBadge(priority) {
  const map = { low: 'bg-gray-100 text-gray-500', medium: 'bg-amber-50 text-amber-600', high: 'bg-red-50 text-red-500' };
  const icons = { low: '↓', medium: '→', high: '↑' };
  return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${map[priority] || ''}">${icons[priority] || ''} ${priority}</span>`;
}