function renderNavbar(activePage) {
  const user = api.getUser();
  const isAdmin = user?.role === 'admin';
  const nav = `
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-6">
      <div class="flex items-center justify-between h-14">
        <div class="flex items-center gap-8">
          <a href="/dashboard.html" class="flex items-center gap-2 flex-shrink-0">
            <div class="w-7 h-7 bg-gray-900 rounded-lg flex items-center justify-center">
              <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
            </div>
            <span class="text-sm font-semibold text-gray-900 tracking-tight">TeamFlow</span>
          </a>
          <div class="hidden md:flex items-center gap-1">
            <a href="/dashboard.html" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${activePage === 'dashboard' ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
              Dashboard
            </a>
            <a href="/projects.html" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${activePage === 'projects' ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
              Projects
            </a>
          </div>
        </div>
        <div class="flex items-center gap-3">
          ${isAdmin ? `<span class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-900 text-white">Admin</span>` : ''}
          <div class="relative group">
            <button class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
              <div class="w-7 h-7 bg-gray-900 rounded-full flex items-center justify-center">
                <span class="text-white text-xs font-semibold">${user?.name?.[0]?.toUpperCase() || 'U'}</span>
              </div>
              <span class="hidden sm:block text-sm font-medium text-gray-700">${user?.name || ''}</span>
              <svg class="w-3.5 h-3.5 text-gray-400 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div class="absolute right-0 top-full mt-1 w-44 bg-white border border-gray-200 rounded-xl shadow-lg py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50">
              <div class="px-3 py-2 border-b border-gray-100">
                <p class="text-xs font-medium text-gray-900 truncate">${user?.name || ''}</p>
                <p class="text-xs text-gray-400 truncate">${user?.email || ''}</p>
              </div>
              <button onclick="handleLogout()" class="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>`;
  document.getElementById('navbar').innerHTML = nav;
}

function handleLogout() {
  showConfirm('You will be signed out of TeamFlow.', () => {
    api.clearAuth();
    window.location.href = '/index.html';
  }, { title: 'Sign out?', confirmText: 'Sign out' });
}