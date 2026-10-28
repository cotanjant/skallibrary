// Sezai Karakoç Anadolu Lisesi Kütüphanesi - İstemci İşlevleri

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobil Menü Açma/Kapatma (Klavye Escape ve Dışarı Tıklama Desteği)
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    function closeMobileMenu() {
        if (!navToggle || !navMenu) return;
        navMenu.classList.remove('nav-open');
        navToggle.setAttribute('aria-expanded', 'false');
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', String(!isExpanded));
            navMenu.classList.toggle('nav-open');
        });

        document.addEventListener('click', (event) => {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                closeMobileMenu();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && navMenu.classList.contains('nav-open')) {
                closeMobileMenu();
                navToggle.focus();
            }
        });
    }

    // 2. Canlı Kitap Arama, Durum Filtreleme ve Sıralama (/search/ ve /books/)
    const catalogForm = document.getElementById('catalogFilterForm');
    const bookSearch = document.getElementById('bookSearch');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const statusInput = document.getElementById('statusInput');
    const filterChips = Array.from(document.querySelectorAll('.filter-chip[data-status]'));
    const bookSort = document.getElementById('bookSort');
    const booksGrid = document.getElementById('booksGrid');
    const bookCountElem = document.getElementById('booksCount');
    const noResultsMsg = document.getElementById('noSearchResults');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');

    if (!booksGrid) {
        return;
    }

    const bookCards = Array.from(booksGrid.querySelectorAll('.book-card'));
    const totalBooks = bookCards.length;
    const initialParams = new URLSearchParams(window.location.search);
    const hadInitialServerFilter = Boolean(initialParams.get('q') || initialParams.get('status'));

    function toTrLower(value) {
        return (value || '').toString().trim().toLocaleLowerCase('tr-TR');
    }

    function getActiveStatus() {
        const activeChip = filterChips.find((chip) => chip.classList.contains('is-active'));
        if (activeChip) {
            return activeChip.getAttribute('data-status') || 'all';
        }
        const rawStatus = statusInput ? statusInput.value.trim() : '';
        return rawStatus || 'all';
    }

    function setActiveStatus(statusValue) {
        const normalized = statusValue === 'available' || statusValue === 'borrowed' ? statusValue : 'all';
        if (statusInput) {
            statusInput.value = normalized === 'all' ? '' : normalized;
        }
        filterChips.forEach((chip) => {
            const isMatch = (chip.getAttribute('data-status') || 'all') === normalized;
            chip.classList.toggle('is-active', isMatch);
            chip.setAttribute('aria-selected', isMatch ? 'true' : 'false');
        });
    }

    function updateClearButtonVisibility() {
        if (!clearSearchBtn || !bookSearch) return;
        if (bookSearch.value.trim().length > 0) {
            clearSearchBtn.removeAttribute('hidden');
        } else {
            clearSearchBtn.setAttribute('hidden', '');
        }
    }

    function syncUrlState(query, status, sort) {
        if (!window.history || typeof window.history.replaceState !== 'function') {
            return;
        }
        const params = new URLSearchParams();
        if (query) {
            params.set('q', query);
        }
        if (status && status !== 'all') {
            params.set('status', status);
        }
        if (sort && sort !== 'name') {
            params.set('sort', sort);
        }
        const queryString = params.toString();
        const newUrl = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
        window.history.replaceState(null, '', newUrl);
    }

    function sortCards(cards, sortKey) {
        return cards.slice().sort((a, b) => {
            const nameA = a.getAttribute('data-name') || '';
            const nameB = b.getAttribute('data-name') || '';
            const authorA = a.getAttribute('data-author') || '';
            const authorB = b.getAttribute('data-author') || '';
            const statusA = a.getAttribute('data-status') || 'borrowed';
            const statusB = b.getAttribute('data-status') || 'borrowed';
            const dueA = a.getAttribute('data-due') || '9999-12-31';
            const dueB = b.getAttribute('data-due') || '9999-12-31';

            if (sortKey === 'author') {
                const cmpAuthor = authorA.localeCompare(authorB, 'tr', { sensitivity: 'base' });
                if (cmpAuthor !== 0) return cmpAuthor;
                return nameA.localeCompare(nameB, 'tr', { sensitivity: 'base' });
            }

            if (sortKey === 'availability') {
                const rankA = statusA === 'available' ? 0 : 1;
                const rankB = statusB === 'available' ? 0 : 1;
                if (rankA !== rankB) return rankA - rankB;
                return nameA.localeCompare(nameB, 'tr', { sensitivity: 'base' });
            }

            if (sortKey === 'due_date') {
                if (dueA !== dueB) return dueA.localeCompare(dueB);
                return nameA.localeCompare(nameB, 'tr', { sensitivity: 'base' });
            }

            return nameA.localeCompare(nameB, 'tr', { sensitivity: 'base' });
        });
    }

    function applyCatalogFilters() {
        const rawQuery = bookSearch ? bookSearch.value.trim() : '';
        const query = toTrLower(rawQuery);
        const activeStatus = getActiveStatus();
        const activeSort = bookSort ? bookSort.value : 'name';

        updateClearButtonVisibility();

        if (totalBooks === 0) {
            syncUrlState(rawQuery, activeStatus, activeSort);
            return;
        }

        const sortedCards = sortCards(bookCards, activeSort);
        let visibleCount = 0;

        sortedCards.forEach((card) => {
            booksGrid.appendChild(card);

            const name = toTrLower(card.getAttribute('data-name'));
            const author = toTrLower(card.getAttribute('data-author'));
            const cardStatus = card.getAttribute('data-status') || 'available';

            const matchesQuery = query === '' || name.includes(query) || author.includes(query);
            const matchesStatus = activeStatus === 'all' || cardStatus === activeStatus;

            if (matchesQuery && matchesStatus) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (noResultsMsg) {
            booksGrid.appendChild(noResultsMsg);
            noResultsMsg.style.display = visibleCount === 0 ? 'flex' : 'none';
        }

        if (bookCountElem) {
            if (query === '' && activeStatus === 'all') {
                bookCountElem.textContent = `${totalBooks} kitap`;
            } else {
                bookCountElem.textContent = `${visibleCount} / ${totalBooks} kitap`;
            }
        }

        syncUrlState(rawQuery, activeStatus, activeSort);
    }

    if (bookSearch) {
        bookSearch.addEventListener('input', () => {
            applyCatalogFilters();
        });
    }

    if (clearSearchBtn && bookSearch) {
        clearSearchBtn.addEventListener('click', () => {
            bookSearch.value = '';
            if (hadInitialServerFilter) {
                if (catalogForm) {
                    catalogForm.submit();
                    return;
                }
            }
            applyCatalogFilters();
            bookSearch.focus();
        });
    }

    filterChips.forEach((chip) => {
        chip.addEventListener('click', () => {
            const targetStatus = chip.getAttribute('data-status') || 'all';
            setActiveStatus(targetStatus);
            if (hadInitialServerFilter && catalogForm) {
                catalogForm.submit();
                return;
            }
            applyCatalogFilters();
        });
    });

    if (bookSort) {
        bookSort.addEventListener('change', () => {
            if (hadInitialServerFilter && catalogForm) {
                catalogForm.submit();
                return;
            }
            applyCatalogFilters();
        });
    }

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', (event) => {
            if (!hadInitialServerFilter && totalBooks > 0) {
                event.preventDefault();
                if (bookSearch) bookSearch.value = '';
                if (bookSort) bookSort.value = 'name';
                setActiveStatus('all');
                applyCatalogFilters();
                if (bookSearch) bookSearch.focus();
            }
        });
    }

    updateClearButtonVisibility();
    if (totalBooks > 0 && !hadInitialServerFilter) {
        applyCatalogFilters();
    }
});
