document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('people-search-input');
    const searchClear = document.getElementById('people-search-clear');
    const categoryButtons = document.getElementById('people-cat-buttons');
    const peopleContainers = document.querySelectorAll('.my-row-zebra');
    
    let activeCategory = 'all';

    // Highlight matching text
    function highlightText(element, searchTerm) {
        if (!searchTerm) return;
        
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        textNodes.forEach(textNode => {
            const parent = textNode.parentNode;
            if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') return;
            
            const text = textNode.textContent;
            let regex;
            
            // Smart case matching for highlighting
            if (searchTerm !== searchTerm.toLowerCase()) {
                // Case sensitive
                regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'g');
            } else {
                // Case insensitive
                regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            }
            
            if (regex.test(text)) {
                const highlightedText = text.replace(regex, '<mark class="search-highlight" style="padding:0; margin:0; background-color:yellow; color:black;">$1</mark>');
                const span = document.createElement('span');
                span.innerHTML = highlightedText;
                parent.replaceChild(span, textNode);
            }
        });
    }

    // Remove highlighting
    function removeHighlighting() {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
    }

    // Add data attributes to people rows for easier searching
    function initializePeopleData() {
        peopleContainers.forEach(container => {
            const rows = container.querySelectorAll('.row');
            rows.forEach(row => {
                // Extract person information
                const nameLink = row.querySelector('a.nonupper-h5');
                if (!nameLink) return;
                
                // Extract UVA ID from the link href
                const href = nameLink.getAttribute('href');
                const uvaIdMatch = href?.match(/\/people\/([^\/]+)\//);
                const uvaId = uvaIdMatch ? uvaIdMatch[1] : '';
                
                const fullName = nameLink.textContent.trim();
                const position = row.querySelector('div i')?.parentElement?.textContent?.trim() || '';
                const specialty = row.querySelector('div[style*="font-size:0.9em"]')?.textContent?.trim() || '';
                const office = row.querySelector('.fa-building')?.nextSibling?.textContent?.trim() || '';
                const email = row.querySelector('a[href^="mailto:"]')?.textContent?.trim() || '';
                const phone = row.querySelector('a[href^="tel:"]')?.textContent?.trim() || '';
                const officeHours = row.querySelector('.fa-clock')?.parentElement?.textContent?.replace('Office hours:', '').trim() || '';
                const researchTags = Array.from(row.querySelectorAll('.btn-secondary')).map(btn => btn.textContent.trim()).join(' ');
                
                // Determine category based on section header
                let category = 'other';
                let currentElement = container.previousElementSibling;
                while (currentElement) {
                    if (currentElement.tagName === 'H2') {
                        const headerText = currentElement.textContent.toLowerCase();
                        if (headerText.includes('faculty') && !headerText.includes('emeritus')) {
                            category = 'faculty';
                        } else if (headerText.includes('postdoc')) {
                            category = 'postdoc';
                        } else if (headerText.includes('lecturer')) {
                            category = 'lecturer';
                        } else if (headerText.includes('emeritus')) {
                            category = 'emeritus';
                        } else if (headerText.includes('graduate student')) {
                            category = 'gradstudent';
                        } else if (headerText.includes('staff')) {
                            category = 'staff';
                        }
                        break;
                    }
                    currentElement = currentElement.previousElementSibling;
                }
                
                // Store data in attributes - include ALL fields especially UVA ID
                row.dataset.personName = fullName.toLowerCase();
                row.dataset.personCategory = category;
                row.dataset.searchData = `${uvaId} ${fullName} ${position} ${specialty} ${office} ${email} ${phone} ${officeHours} ${researchTags}`.toLowerCase();
            });
        });
    }

    // Filter function
    function filterPeople() {
        const searchTerm = searchInput.value.toLowerCase();
        const originalSearchTerm = searchInput.value;
        let visibleCount = 0;

        // Remove previous highlighting
        removeHighlighting();

        // Track which sections have visible items
        const sectionVisibility = {};

        peopleContainers.forEach(container => {
            const rows = container.querySelectorAll('.row');
            let sectionHasVisibleItems = false;
            
            rows.forEach(row => {
                if (!row.dataset.personName) return; // Skip rows without person data
                
                const category = row.dataset.personCategory || 'other';
                
                let matchesSearch = false;
                if (searchTerm === '') {
                    matchesSearch = true;
                } else {
                    const searchData = row.dataset.searchData;
                    
                    // Smart case matching
                    if (originalSearchTerm !== originalSearchTerm.toLowerCase()) {
                        // Contains uppercase letters - case sensitive search
                        matchesSearch = row.textContent.includes(originalSearchTerm);
                    } else {
                        // All lowercase - case insensitive search
                        matchesSearch = searchData.includes(searchTerm);
                    }
                }
                
                const matchesCategory = activeCategory === 'all' || category === activeCategory;
                
                if (matchesSearch && matchesCategory) {
                    row.style.display = '';
                    visibleCount++;
                    sectionHasVisibleItems = true;
                    
                    // Highlight matching text in visible items
                    if (searchTerm !== '') {
                        highlightText(row, originalSearchTerm);
                    }
                } else {
                    row.style.display = 'none';
                }
            });

            // Hide/show section header based on visibility
            const sectionHeader = container.previousElementSibling;
            if (sectionHeader && sectionHeader.tagName === 'H2') {
                if (sectionHasVisibleItems) {
                    sectionHeader.style.display = '';
                } else {
                    sectionHeader.style.display = 'none';
                }
            }
        });

        // Update no results message if needed
        updateNoResultsMessage(visibleCount);
    }

    // Update no results message
    function updateNoResultsMessage(count) {
        let noResultsMsg = document.getElementById('no-results-message');
        
        if (count === 0 && searchInput.value !== '') {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.id = 'no-results-message';
                noResultsMsg.className = 'alert alert-info mt-4';
                noResultsMsg.textContent = 'No people found. Try adjusting your search or filters.';
                
                // Insert after search area
                const searchGroup = document.getElementById('people-search-group');
                if (searchGroup && searchGroup.parentElement) {
                    searchGroup.parentElement.appendChild(noResultsMsg);
                }
            }
        } else if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }

    // Clear search
    function clearSearch() {
        searchInput.value = '';
        activeCategory = 'all';
        updateCategoryButtons();
        removeHighlighting();
        filterPeople();
        searchInput.focus();
    }

    // Update category button states
    function updateCategoryButtons() {
        const buttons = categoryButtons?.querySelectorAll('.category-btn') || [];
        buttons.forEach(btn => {
            if (btn.dataset.category === activeCategory) {
                btn.classList.add('active');
                btn.style.backgroundColor = '#002F6C';
                btn.style.borderColor = '#002F6C';
                btn.style.color = 'white';
            } else {
                btn.classList.remove('active');
                btn.style.backgroundColor = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }
        });
    }


    // Event listeners
    if (searchInput) {
        searchInput.addEventListener('input', filterPeople);
        searchInput.focus();
    }

    if (searchClear) {
        searchClear.addEventListener('click', clearSearch);
    }


    // ESC key to clear
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchInput) {
            clearSearch();
        }
    });

    // Category button clicks
    if (categoryButtons) {
        categoryButtons.addEventListener('click', function(e) {
            if (e.target.classList.contains('category-btn')) {
                activeCategory = e.target.dataset.category;
                updateCategoryButtons();
                filterPeople();
            }
        });
    }

    // Initialize categories from data
    function initializeCategories() {
        if (!categoryButtons) return;
        
        const categories = new Set(['all']);
        
        peopleContainers.forEach(container => {
            const rows = container.querySelectorAll('.row');
            rows.forEach(row => {
                const category = row.dataset.personCategory;
                if (category) categories.add(category);
            });
        });

        // Clear existing buttons
        categoryButtons.innerHTML = '';
        
        // Create category buttons with proper labels
        const categoryLabels = {
            'all': 'All',
            'faculty': 'Faculty',
            'postdoc': 'Postdocs',
            'lecturer': 'Lecturers',
            'emeritus': 'Emeritus',
            'gradstudent': 'Grad Students',
            'staff': 'Staff'
        };
        
        categories.forEach(category => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-secondary category-btn' + (category === 'all' ? ' active' : '');
            btn.dataset.category = category;
            btn.textContent = categoryLabels[category] || category.charAt(0).toUpperCase() + category.slice(1);
            btn.style.fontSize = '0.9em';
            btn.style.marginRight = '0.5em';
            btn.style.marginBottom = '0.5em';
            
            categoryButtons.appendChild(btn);
        });
    }

    // Initialize
    initializePeopleData();
    initializeCategories();
    filterPeople();
});