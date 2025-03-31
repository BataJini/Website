document.addEventListener('DOMContentLoaded', function() {
    const locationInput = document.getElementById('locationInput');
    const hiddenLocationInput = document.getElementById('hiddenLocationInput');
    const autocompleteWrapper = document.createElement('div');
    autocompleteWrapper.className = 'city-autocomplete-wrapper';
    locationInput.parentNode.insertBefore(autocompleteWrapper, locationInput);

    // Create input wrapper for tags and input
    const inputWrapper = document.createElement('div');
    inputWrapper.className = 'input-tags-wrapper';
    autocompleteWrapper.appendChild(inputWrapper);

    // Create tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'tags-container';
    inputWrapper.appendChild(tagsContainer);

    // Move input to the wrapper
    inputWrapper.appendChild(locationInput);

    let resultsDiv = null;
    let selectedIndex = -1;
    let allCities = [];
    let selectedCities = new Set();

    // Initialize selected cities from hidden input
    if (hiddenLocationInput && hiddenLocationInput.value) {
        const initialCities = hiddenLocationInput.value.split(',').map(city => city.trim());
        initialCities.forEach(city => {
            if (city) {
                addSelectedCity(city);
            }
        });
    }

    // Handle clear filters
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            selectedCities.clear();
            tagsContainer.innerHTML = '';
            locationInput.value = '';
            hiddenLocationInput.value = '';
            updateInputPlaceholder();
            adjustInputWidth();
            
            // Clear other filter inputs
            document.querySelectorAll('.btn-check').forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Reset salary range if it exists
            const minSalaryInput = document.getElementById('minSalaryInput');
            const maxSalaryInput = document.getElementById('maxSalaryInput');
            if (minSalaryInput && maxSalaryInput) {
                minSalaryInput.value = '';
                maxSalaryInput.value = '';
            }
        });
    }

    // Handle form submission
    const filtersForm = document.getElementById('filtersForm');
    if (filtersForm) {
        filtersForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // Get existing search tags
            const searchTagsContainer = document.getElementById('searchTags');
            const existingTags = Array.from(searchTagsContainer.children).map(tag => tag.textContent);
            
            // Add new city tags to search
            selectedCities.forEach(city => {
                if (!existingTags.includes(city)) {
                    const tag = document.createElement('span');
                    tag.className = 'search-tag';
                    tag.textContent = city;
                    
                    // Add remove functionality
                    tag.addEventListener('click', function() {
                        tag.remove();
                        // Trigger search with updated tags
                        performSearch();
                    });
                    
                    searchTagsContainer.appendChild(tag);
                }
            });

            // Update hidden search input with all tags
            const hiddenSearchInput = document.getElementById('hiddenSearchInput');
            const allTags = Array.from(searchTagsContainer.children).map(tag => tag.textContent);
            hiddenSearchInput.value = allTags.join(' ');

            // Perform AJAX search
            performSearch();

            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('jobFiltersModal'));
            modal.hide();
        });
    }

    // Function to perform AJAX search
    function performSearch() {
        const searchTags = Array.from(document.getElementById('searchTags').children).map(tag => tag.textContent);
        const query = searchTags.join(' ');
        
        // Update URL without page reload
        const url = new URL(window.location.href);
        url.searchParams.set('q', query);
        window.history.pushState({}, '', url);

        // Perform AJAX search with correct URL
        fetch(`/search-jobs/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('jobListingsContainer').innerHTML = data.html;
                
                // Update job count if it exists
                const jobCountElement = document.getElementById('jobCount');
                if (jobCountElement && data.count !== undefined) {
                    jobCountElement.textContent = `${data.count} offers`;
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to update hidden input value
    function updateHiddenInput() {
        hiddenLocationInput.value = Array.from(selectedCities).join(', ');
    }

    // Handle apply filters button click
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            // Update the main search with selected cities
            updateHiddenInput();
        });
    }

    // Fetch all cities when the page loads
    async function fetchAllCities() {
        try {
            const response = await fetch('/search-cities/?q=');
            allCities = await response.json();
        } catch (error) {
            console.error('Error fetching cities:', error);
        }
    }

    // Initial fetch of all cities
    fetchAllCities();

    function addSelectedCity(cityName) {
        if (!selectedCities.has(cityName)) {
            selectedCities.add(cityName);
            const cityTag = document.createElement('div');
            cityTag.className = 'selected-city-tag';
            cityTag.textContent = cityName;
            
            cityTag.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedCities.delete(cityName);
                cityTag.remove();
                updateInputPlaceholder();
                adjustInputWidth();
                hiddenLocationInput.value = Array.from(selectedCities).join(', ');
                locationInput.focus();
                showCities(locationInput.value.trim());
            });

            tagsContainer.appendChild(cityTag);
            locationInput.value = '';
            updateInputPlaceholder();
            adjustInputWidth();
            hiddenLocationInput.value = Array.from(selectedCities).join(', ');
        }
    }

    function adjustInputWidth() {
        const wrapper = locationInput.parentElement;
        const tags = tagsContainer.getElementsByClassName('selected-city-tag');
        const totalTagsWidth = Array.from(tags).reduce((width, tag) => width + tag.offsetWidth + 8, 0);
        const minWidth = 100; // Minimum width for the input
        const wrapperWidth = wrapper.offsetWidth;
        const availableWidth = Math.max(minWidth, wrapperWidth - totalTagsWidth - 20);
        locationInput.style.width = `${availableWidth}px`;
    }

    function updateInputPlaceholder() {
        if (selectedCities.size > 0) {
            locationInput.placeholder = 'Add another city...';
        } else {
            locationInput.placeholder = 'Start typing a city name...';
        }
    }

    // Show all cities or filtered cities
    function showCities(query = '') {
        if (resultsDiv) {
            resultsDiv.remove();
        }

        resultsDiv = document.createElement('div');
        resultsDiv.className = 'city-autocomplete-results';
        
        // Prevent any clicks within results from bubbling
        resultsDiv.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        // Filter cities based on query and exclude already selected cities
        const filteredCities = allCities.filter(city => {
            const matchesQuery = !query || city.name.toLowerCase().includes(query.toLowerCase());
            const notSelected = !selectedCities.has(city.name);
            return matchesQuery && notSelected;
        });

        filteredCities.forEach((city, index) => {
            const div = document.createElement('div');
            div.className = 'city-autocomplete-item';
            div.textContent = city.name;
            
            div.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                addSelectedCity(city.name);
                // Keep focus on input and show updated city list
                locationInput.focus();
                showCities(locationInput.value.trim());
            });

            div.addEventListener('mouseenter', () => {
                selectedIndex = index;
                updateSelectedItem();
            });

            resultsDiv.appendChild(div);
        });

        if (filteredCities.length > 0) {
            autocompleteWrapper.appendChild(resultsDiv);
        }
    }

    // Show dropdown when input is focused
    locationInput.addEventListener('focus', () => {
        showCities(locationInput.value.trim());
    });

    // Filter cities when typing - immediate update
    locationInput.addEventListener('input', function() {
        const query = this.value.trim();
        showCities(query);
        adjustInputWidth();
    });

    // Handle keyboard navigation and backspace
    locationInput.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && !this.value) {
            // If input is empty and backspace is pressed, remove the last tag
            const tags = tagsContainer.getElementsByClassName('selected-city-tag');
            if (tags.length > 0) {
                const lastTag = tags[tags.length - 1];
                const cityName = lastTag.textContent;
                selectedCities.delete(cityName);
                lastTag.remove();
                updateInputPlaceholder();
                adjustInputWidth();
                // Keep focus and show updated city list
                showCities(locationInput.value.trim());
                return;
            }
        }

        if (!resultsDiv) return;

        const items = resultsDiv.querySelectorAll('.city-autocomplete-item');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelectedItem();
                scrollSelectedIntoView();
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelectedItem();
                scrollSelectedIntoView();
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && selectedIndex < items.length) {
                    const selectedCity = items[selectedIndex].textContent;
                    addSelectedCity(selectedCity);
                    // Reset selection index after selection
                    selectedIndex = -1;
                    showCities(locationInput.value.trim());
                }
                break;
            case 'Escape':
                resultsDiv.remove();
                resultsDiv = null;
                break;
        }
    });

    // Close autocomplete only when clicking outside the wrapper
    document.addEventListener('click', function(e) {
        // Don't close if clicking inside the wrapper or results
        if (autocompleteWrapper.contains(e.target) || (resultsDiv && resultsDiv.contains(e.target))) {
            return;
        }
        // Only close if clicking outside
        if (resultsDiv) {
            resultsDiv.remove();
            resultsDiv = null;
        }
    });

    // Ensure input wrapper click focuses input and shows results
    inputWrapper.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        locationInput.focus();
        showCities(locationInput.value.trim());
    });

    function updateSelectedItem() {
        const items = resultsDiv.querySelectorAll('.city-autocomplete-item');
        items.forEach((item, index) => {
            item.classList.toggle('active', index === selectedIndex);
        });
    }

    function scrollSelectedIntoView() {
        const activeItem = resultsDiv.querySelector('.city-autocomplete-item.active');
        if (activeItem) {
            activeItem.scrollIntoView({
                block: 'nearest',
                behavior: 'smooth'
            });
        }
    }

    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initial input width adjustment
    adjustInputWidth();

    // Handle window resize
    window.addEventListener('resize', adjustInputWidth);
}); 