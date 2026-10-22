(() => {
  'use strict';

  const root = document.documentElement;
  const base = (root.dataset.base || '/').replace(/\/?$/, '/');
  const themeButtons = [...document.querySelectorAll('[data-theme-toggle]')];
  const preference = window.matchMedia('(prefers-color-scheme: dark)');
  let explicitTheme = null;
  try {
    const stored = localStorage.getItem('linux-book-theme');
    if (stored === 'light' || stored === 'dark') explicitTheme = stored;
  } catch (_) { /* Reading remains available when storage is restricted. */ }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    themeButtons.forEach(button => {
      const dark = theme === 'dark';
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? '切换浅色主题' : '切换深色主题');
      button.title = dark ? '切换浅色主题' : '切换深色主题';
    });
  }
  applyTheme(explicitTheme || (preference.matches ? 'dark' : 'light'));
  themeButtons.forEach(button => button.addEventListener('click', () => {
    explicitTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(explicitTheme);
    try { localStorage.setItem('linux-book-theme', explicitTheme); } catch (_) { /* Optional persistence. */ }
  }));
  const preferenceChanged = event => {
    if (!explicitTheme) applyTheme(event.matches ? 'dark' : 'light');
  };
  if (preference.addEventListener) preference.addEventListener('change', preferenceChanged);
  else if (preference.addListener) preference.addListener(preferenceChanged);

  const menuButtons = [...document.querySelectorAll('[data-menu-toggle]')];
  const chapterNav = document.getElementById('chapter-nav');
  function setMenu(open) {
    document.body.classList.toggle('menu-open', Boolean(open && chapterNav));
    menuButtons.forEach(button => button.setAttribute('aria-expanded', String(Boolean(open && chapterNav))));
  }
  menuButtons.forEach(button => button.addEventListener('click', () => {
    setMenu(!document.body.classList.contains('menu-open'));
  }));
  if (chapterNav) chapterNav.addEventListener('click', event => {
    if (event.target.closest('a')) setMenu(false);
  });
  const desktop = window.matchMedia('(min-width: 1100px)');
  if (desktop.addEventListener) desktop.addEventListener('change', event => { if (event.matches) setMenu(false); });
  window.addEventListener('resize', () => { if (desktop.matches) setMenu(false); }, {passive: true});

  const dialog = document.getElementById('search-dialog');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const searchHint = dialog && dialog.querySelector('.search-hint');
  let searchIndex = null;
  let indexPromise = null;
  let searchVersion = 0;
  let debounce;
  let searchOpener = null;

  function hint(text) { if (searchHint) searchHint.textContent = text; }
  function state(text) {
    if (!searchResults) return;
    searchResults.replaceChildren();
    const message = document.createElement('p');
    message.className = 'empty-state';
    message.textContent = text;
    searchResults.append(message);
  }
  function loadIndex() {
    if (searchIndex) return Promise.resolve(searchIndex);
    if (indexPromise) return indexPromise;
    indexPromise = fetch(`${base}search-index.json`, {credentials: 'same-origin'})
      .then(response => {
        if (!response.ok) throw new Error('Search data unavailable');
        return response.json();
      })
      .then(data => {
        if (!Array.isArray(data)) throw new Error('Invalid search data');
        searchIndex = data.filter(item => item && typeof item.title === 'string' &&
          typeof item.url === 'string' && typeof item.text === 'string').map(item => ({
          ...item,
          normalizedTitle: item.title.toLocaleLowerCase(),
          normalizedText: item.text.toLocaleLowerCase()
        }));
        return searchIndex;
      })
      .catch(error => { indexPromise = null; throw error; });
    return indexPromise;
  }
  function appendHighlighted(element, text, terms) {
    const normalized = text.toLocaleLowerCase();
    let cursor = 0;
    while (cursor < text.length) {
      let start = text.length;
      let chosen = '';
      for (const term of terms) {
        const next = normalized.indexOf(term, cursor);
        if (next >= 0 && (next < start || (next === start && term.length > chosen.length))) {
          start = next;
          chosen = term;
        }
      }
      if (!chosen) { element.append(document.createTextNode(text.slice(cursor))); break; }
      element.append(document.createTextNode(text.slice(cursor, start)));
      const mark = document.createElement('mark');
      mark.textContent = text.slice(start, start + chosen.length);
      element.append(mark);
      cursor = start + chosen.length;
    }
  }
  function safeURL(value) {
    try {
      const url = new URL(value, location.href);
      return url.origin === location.origin && url.pathname.startsWith(base) ? url.href : null;
    } catch (_) { return null; }
  }
  async function performSearch() {
    if (!searchInput || !searchResults) return;
    const version = ++searchVersion;
    const query = searchInput.value.trim();
    const terms = [...new Set(query.toLocaleLowerCase().split(/\s+/).filter(Boolean))];
    if (!terms.length) {
      hint('搜索章节名称或正文关键词');
      state('试试 FUSE、页缓存、KVM 或 Android。');
      return;
    }
    hint('正在搜索…');
    try {
      const index = await loadIndex();
      if (version !== searchVersion) return;
      const matches = index.filter(item => terms.every(term =>
        item.normalizedTitle.includes(term) || item.normalizedText.includes(term)))
        .map(item => ({item, score: terms.reduce((score, term) => score +
          (item.normalizedTitle.includes(term) ? 5 : 0) + (item.normalizedTitle === term ? 10 : 0), 0)}))
        .sort((a, b) => b.score - a.score);
      searchResults.replaceChildren();
      hint(matches.length ? `找到 ${matches.length} 项${matches.length > 20 ? '，显示前 20 项' : ''}` : '没有匹配结果');
      if (!matches.length) { state('试试更短的关键词，或按空格组合多个关键词。'); return; }
      for (const {item} of matches.slice(0, 20)) {
        const url = safeURL(item.url);
        if (!url) continue;
        const row = document.createElement('div');
        row.className = 'search-result';
        const link = document.createElement('a');
        link.href = url;
        const heading = document.createElement('strong');
        appendHighlighted(heading, item.title, terms);
        const excerpt = document.createElement('p');
        const first = terms.reduce((found, term) => {
          const at = item.normalizedText.indexOf(term);
          return at >= 0 ? Math.min(found, at) : found;
        }, item.text.length);
        const start = first < item.text.length ? Math.max(0, first - 38) : 0;
        const end = Math.min(item.text.length, start + 150);
        appendHighlighted(excerpt, `${start ? '…' : ''}${item.text.slice(start, end)}${end < item.text.length ? '…' : ''}`, terms);
        link.append(heading, excerpt);
        row.append(link);
        searchResults.append(row);
      }
    } catch (_) {
      if (version !== searchVersion) return;
      hint('搜索数据暂时不可用');
      state('请检查网络，再输入关键词或重新打开搜索以重试。章节目录仍可正常阅读。');
    }
  }
  function openSearch(opener) {
    if (!dialog || !searchInput || !searchResults) return;
    searchOpener = opener || document.activeElement;
    if (typeof dialog.showModal === 'function') {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute('open', '');
      dialog.setAttribute('role', 'dialog');
      dialog.setAttribute('aria-modal', 'true');
    }
    searchInput.focus();
    searchInput.select();
    performSearch();
    // Start loading for the next keystroke. A failed request is retried later.
    if (!searchInput.value.trim()) loadIndex().catch(() => {
      if (dialog.open && !searchInput.value.trim()) {
        hint('搜索数据暂时不可用');
        state('请检查网络，输入关键词或重新打开搜索以重试。');
      }
    });
  }
  function closeSearch() {
    if (!dialog) return;
    ++searchVersion;
    clearTimeout(debounce);
    if (typeof dialog.close === 'function') dialog.close();
    else { dialog.removeAttribute('open'); if (searchOpener && searchOpener.focus) searchOpener.focus(); }
  }
  document.querySelectorAll('[data-search-open]').forEach(button => button.addEventListener('click', () => openSearch(button)));
  document.querySelectorAll('[data-search-close]').forEach(button => button.addEventListener('click', closeSearch));
  if (searchResults) searchResults.setAttribute('aria-live', 'polite');
  if (searchInput) searchInput.addEventListener('input', () => {
    ++searchVersion;
    clearTimeout(debounce);
    debounce = setTimeout(performSearch, 120);
  });
  if (dialog) {
    dialog.addEventListener('close', () => { ++searchVersion; clearTimeout(debounce); });
    dialog.addEventListener('click', event => { if (event.target === dialog) closeSearch(); });
  }

  const article = document.querySelector('.prose');
  const progress = document.getElementById('reading-progress');
  let progressScheduled = false;
  function updateProgress() {
    progressScheduled = false;
    if (!progress || !article) return;
    const rect = article.getBoundingClientRect();
    const header = document.querySelector('.site-header');
    const offset = header ? header.getBoundingClientRect().height : 0;
    const distance = rect.height - Math.max(1, window.innerHeight - offset);
    const percentage = distance > 0 ? Math.max(0, Math.min(1, (offset - rect.top) / distance)) : 1;
    progress.style.width = `${percentage * 100}%`;
    progress.setAttribute('aria-valuenow', String(Math.round(percentage * 100)));
  }
  function scheduleProgress() {
    if (progressScheduled) return;
    progressScheduled = true;
    requestAnimationFrame(updateProgress);
  }
  if (progress) {
    progress.hidden = !article;
    if (article) {
      progress.setAttribute('role', 'progressbar');
      progress.setAttribute('aria-label', '本章阅读进度');
      progress.setAttribute('aria-valuemin', '0');
      progress.setAttribute('aria-valuemax', '100');
      window.addEventListener('scroll', scheduleProgress, {passive: true});
      window.addEventListener('resize', scheduleProgress, {passive: true});
      window.addEventListener('load', scheduleProgress, {once: true});
      article.querySelectorAll('img').forEach(img => img.addEventListener('load', scheduleProgress));
      if (typeof ResizeObserver === 'function') new ResizeObserver(scheduleProgress).observe(article);
      scheduleProgress();
    }
  }

  const imageDialog = document.getElementById('image-dialog');
  const enlargedImage = imageDialog && imageDialog.querySelector('img');
  const imageCaption = imageDialog && imageDialog.querySelector('p');
  let imageOpener = null;
  function closeImage() {
    if (imageDialog && typeof imageDialog.close === 'function') imageDialog.close();
  }
  document.querySelectorAll('.prose img').forEach(img => {
    let link = img.closest('a');
    if (!link) {
      link = document.createElement('a');
      link.href = img.currentSrc || img.src;
      link.className = 'diagram-link';
      img.replaceWith(link);
      link.append(img);
    }
    link.setAttribute('aria-label', `${img.alt || '机制图'}，查看原图`);
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
      if (!imageDialog || !enlargedImage || typeof imageDialog.showModal !== 'function') return;
      event.preventDefault();
      imageOpener = link;
      enlargedImage.src = img.currentSrc || img.src;
      enlargedImage.alt = img.alt;
      if (imageCaption) imageCaption.textContent = img.alt || '原创机制示意图';
      enlargedImage.style.objectFit = 'contain';
      if (!imageDialog.open) imageDialog.showModal();
    });
  });
  document.querySelectorAll('[data-image-close]').forEach(button => button.addEventListener('click', closeImage));
  if (imageDialog) {
    imageDialog.addEventListener('click', event => { if (event.target === imageDialog) closeImage(); });
    imageDialog.addEventListener('close', () => { if (imageOpener) imageOpener.focus(); });
  }

  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (!imageDialog || !imageDialog.open) openSearch();
    }
    if (event.key === 'Escape') {
      setMenu(false);
      if (dialog && dialog.open && typeof dialog.close !== 'function') closeSearch();
    }
  });
})();
