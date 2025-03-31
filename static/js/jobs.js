document.addEventListener('DOMContentLoaded', function() {
    // Double Range Slider functionality
    const minRange = document.getElementById('minSalaryRange');
    const maxRange = document.getElementById('maxSalaryRange');
    const minInput = document.getElementById('minSalaryInput');
    const maxInput = document.getElementById('maxSalaryInput');
    const track = document.querySelector('.slider-track');
    const minHandle = document.getElementById('minSalaryHandle');
    const maxHandle = document.getElementById('maxSalaryHandle');
    const minTooltip = document.getElementById('minSalaryTooltip');
    const maxTooltip = document.getElementById('maxSalaryTooltip');
    
    // Track whether handles are being dragged
    let minHandleActive = false;
    let maxHandleActive = false;

    // Format number with thousand separators
    function formatNumber(num) {
        return new Intl.NumberFormat('pl-PL').format(num);
    }

    // Update slider visuals based on range values
    function updateSlider() {
        if (!minRange || !maxRange || !track || !minHandle || !maxHandle) return;

        const min = parseInt(minRange.min);
        const max = parseInt(minRange.max);
        const range = max - min;
        
        const minVal = parseInt(minRange.value);
        const maxVal = parseInt(maxRange.value);
        
        // Calculate percentages for positioning
        const minPercent = ((minVal - min) / range) * 100;
        const maxPercent = ((maxVal - min) / range) * 100;
        
        // Position handles
        minHandle.style.left = `${minPercent}%`;
        maxHandle.style.left = `${maxPercent}%`;
        
        // Position tooltips and update their content
        minTooltip.style.left = `${minPercent}%`;
        maxTooltip.style.left = `${maxPercent}%`;
        minTooltip.textContent = `${formatNumber(minVal)} PLN`;
        maxTooltip.textContent = `${formatNumber(maxVal)} PLN`;
        
        // Update track highlighting
        track.style.background = `linear-gradient(to right, 
            var(--bs-border-color) ${minPercent}%, 
            var(--primary-color) ${minPercent}%, 
            var(--primary-color) ${maxPercent}%, 
            var(--bs-border-color) ${maxPercent}%)`;
        
        // Only update input fields if they don't have focus
        // This prevents overriding user input while they're typing
        if (minInput && document.activeElement !== minInput) {
            minInput.value = minVal;
        }
        if (maxInput && document.activeElement !== maxInput) {
            maxInput.value = maxVal;
        }
    }

    // Parse number removing thousand separators
    function parseFormattedNumber(str) {
        if (typeof str !== 'string') return parseInt(str) || 0;
        return parseInt(str.replace(/\s/g, '').replace(/\./g, '').replace(/,/g, '')) || 0;
    }

    // Set up range input event listeners
    if (minRange) {
        minRange.addEventListener('input', function() {
            const minVal = parseInt(this.value);
            const maxVal = parseInt(maxRange.value);
            
            // Prevent min from exceeding max
            if (minVal > maxVal) {
                this.value = maxVal;
            }
            
            // Force update the input field with the current slider value
            if (minInput) {
                minInput.value = parseInt(this.value);
            }
            
            updateSlider();
        });
    }

    if (maxRange) {
        maxRange.addEventListener('input', function() {
            const minVal = parseInt(minRange.value);
            const maxVal = parseInt(this.value);
            
            // Prevent max from being less than min
            if (maxVal < minVal) {
                this.value = minVal;
            }
            
            // Force update the input field with the current slider value
            if (maxInput) {
                maxInput.value = parseInt(this.value);
            }
            
            updateSlider();
        });
    }
    
    // Set up handle drag events
    if (minHandle) {
        // Show tooltip on mouseover
        minHandle.addEventListener('mouseover', function() {
            minTooltip.style.opacity = '1';
        });
        
        minHandle.addEventListener('mouseout', function() {
            if (!minHandleActive) {
                minTooltip.style.opacity = '0';
            }
        });
        
        // Handle mouse/touch events for dragging
        minHandle.addEventListener('mousedown', function(e) {
            e.preventDefault();
            minHandleActive = true;
            minHandle.classList.add('active');
            minTooltip.style.opacity = '1';
            document.addEventListener('mousemove', handleMinDrag);
            document.addEventListener('mouseup', stopMinDrag);
        });
        
        minHandle.addEventListener('touchstart', function(e) {
            minHandleActive = true;
            minHandle.classList.add('active');
            minTooltip.style.opacity = '1';
            document.addEventListener('touchmove', handleMinDrag);
            document.addEventListener('touchend', stopMinDrag);
        });
    }
    
    if (maxHandle) {
        // Show tooltip on mouseover
        maxHandle.addEventListener('mouseover', function() {
            maxTooltip.style.opacity = '1';
        });
        
        maxHandle.addEventListener('mouseout', function() {
            if (!maxHandleActive) {
                maxTooltip.style.opacity = '0';
            }
        });
        
        // Handle mouse/touch events for dragging
        maxHandle.addEventListener('mousedown', function(e) {
            e.preventDefault();
            maxHandleActive = true;
            maxHandle.classList.add('active');
            maxTooltip.style.opacity = '1';
            document.addEventListener('mousemove', handleMaxDrag);
            document.addEventListener('mouseup', stopMaxDrag);
        });
        
        maxHandle.addEventListener('touchstart', function(e) {
            maxHandleActive = true;
            maxHandle.classList.add('active');
            maxTooltip.style.opacity = '1';
            document.addEventListener('touchmove', handleMaxDrag);
            document.addEventListener('touchend', stopMaxDrag);
        });
    }
    
    // Handle drag functions
    function handleMinDrag(e) {
        if (!minHandleActive) return;
        
        const sliderRect = track.getBoundingClientRect();
        let clientX = e.clientX;
        
        // Handle touch events
        if (e.touches && e.touches[0]) {
            clientX = e.touches[0].clientX;
        }
        
        // Calculate position as percentage
        let position = (clientX - sliderRect.left) / sliderRect.width;
        position = Math.max(0, Math.min(position, 1));
        
        // Calculate value based on position
        const min = parseInt(minRange.min);
        const max = parseInt(minRange.max);
        const step = parseInt(minRange.step) || 1;
        const range = max - min;
        
        // Calculate value and round to nearest step
        let value = min + (position * range);
        value = Math.round(value / step) * step;
        
        // Get current max value
        const maxVal = parseInt(maxRange.value);
        
        // Check if min handle is pushing the max handle
        if (value >= maxVal) {
            // Push the max handle along with the min handle
            const newMaxVal = Math.min(value, max);
            maxRange.value = newMaxVal;
            maxHandle.style.left = `${((newMaxVal - min) / range) * 100}%`;
            maxTooltip.style.left = `${((newMaxVal - min) / range) * 100}%`;
            maxTooltip.textContent = `${formatNumber(newMaxVal)} PLN`;
            maxTooltip.style.opacity = '1';
            
            // Add visual indicators for pushing
            minHandle.classList.add('pushing');
            maxHandle.classList.add('active', 'pushed');
            
            // Force update max input field
            if (maxInput) {
                maxInput.value = newMaxVal;
            }
        } else {
            // If not pushing, remove indicator classes
            minHandle.classList.remove('pushing');
            maxHandle.classList.remove('active', 'pushed');
        }
        
        // Update min range input
        minRange.value = value;
        
        // Force update min input field
        if (minInput) {
            minInput.value = value;
        }
        
        updateSlider();
        
        // Ensure tooltip stays visible during drag
        minTooltip.style.opacity = '1';
    }
    
    function handleMaxDrag(e) {
        if (!maxHandleActive) return;
        
        const sliderRect = track.getBoundingClientRect();
        let clientX = e.clientX;
        
        // Handle touch events
        if (e.touches && e.touches[0]) {
            clientX = e.touches[0].clientX;
        }
        
        // Calculate position as percentage
        let position = (clientX - sliderRect.left) / sliderRect.width;
        position = Math.max(0, Math.min(position, 1));
        
        // Calculate value based on position
        const min = parseInt(maxRange.min);
        const max = parseInt(maxRange.max);
        const step = parseInt(maxRange.step) || 1;
        const range = max - min;
        
        // Calculate value and round to nearest step
        let value = min + (position * range);
        value = Math.round(value / step) * step;
        
        // Get current min value
        const minVal = parseInt(minRange.value);
        
        // Check if max handle is pushing the min handle
        if (value <= minVal) {
            // Push the min handle along with the max handle
            const newMinVal = Math.max(value, min);
            minRange.value = newMinVal;
            minHandle.style.left = `${((newMinVal - min) / range) * 100}%`;
            minTooltip.style.left = `${((newMinVal - min) / range) * 100}%`;
            minTooltip.textContent = `${formatNumber(newMinVal)} PLN`;
            minTooltip.style.opacity = '1';
            
            // Add visual indicators for pushing
            maxHandle.classList.add('pushing');
            minHandle.classList.add('active', 'pushed');
            
            // Force update min input field
            if (minInput) {
                minInput.value = newMinVal;
            }
        } else {
            // If not pushing, remove indicator classes
            maxHandle.classList.remove('pushing');
            minHandle.classList.remove('active', 'pushed');
        }
        
        // Update max range input
        maxRange.value = value;
        
        // Force update max input field
        if (maxInput) {
            maxInput.value = value;
        }
        
        updateSlider();
        
        // Ensure tooltip stays visible during drag
        maxTooltip.style.opacity = '1';
    }
    
    function stopMinDrag() {
        minHandleActive = false;
        minHandle.classList.remove('active', 'pushing');
        minTooltip.style.opacity = '0';
        document.removeEventListener('mousemove', handleMinDrag);
        document.removeEventListener('mouseup', stopMinDrag);
        document.removeEventListener('touchmove', handleMinDrag);
        document.removeEventListener('touchend', stopMinDrag);
        
        // Remove pushed state from max handle when drag stops
        maxHandle.classList.remove('pushed');
    }
    
    function stopMaxDrag() {
        maxHandleActive = false;
        maxHandle.classList.remove('active', 'pushing');
        maxTooltip.style.opacity = '0';
        document.removeEventListener('mousemove', handleMaxDrag);
        document.removeEventListener('mouseup', stopMaxDrag);
        document.removeEventListener('touchmove', handleMaxDrag);
        document.removeEventListener('touchend', stopMaxDrag);
        
        // Remove pushed state from min handle when drag stops
        minHandle.classList.remove('pushed');
    }

    // Update input fields
    if (minInput) {
        minInput.addEventListener('input', function() {
            const input = this.value.trim();
            // Allow empty input while typing
            if (input === '') return;
            
            const minVal = parseFormattedNumber(input);
            // Only proceed if it's a valid number
            if (!isNaN(minVal)) {
                // Enforce minimum limit of 0
                if (minVal < 0) {
                    this.value = "0";
                    return;
                }
                
                // Constrain to min and max range values
                const constrainedVal = Math.max(parseInt(minRange.min), Math.min(minVal, parseInt(minRange.max)));
                
                const maxVal = parseInt(maxRange.value);
                
                // Ensure min doesn't exceed max
                minRange.value = Math.min(constrainedVal, maxVal);
                
                // Now update the slider immediately
                updateSlider();
            }
        });
        
        // Keep this for consistency/backwards compatibility
        minInput.addEventListener('change', function() {
            const minVal = parseFormattedNumber(this.value);
            const maxVal = parseInt(maxRange.value);
            
            if (!isNaN(minVal)) {
                // Enforce minimum limit of 0
                if (minVal < 0) {
                    this.value = "0";
                    const constrainedVal = 0;
                    minRange.value = constrainedVal;
                    updateSlider();
                    return;
                }
                
                // Constrain to min and max range values
                const constrainedVal = Math.max(parseInt(minRange.min), Math.min(minVal, parseInt(minRange.max)));
                
                // Ensure min doesn't exceed max
                minRange.value = Math.min(constrainedVal, maxVal);
                
                // Now update the slider
                updateSlider();
            }
        });
        
        // Format inputs on focus out
        minInput.addEventListener('blur', function() {
            const input = this.value.trim();
            // If empty, use the current slider value
            if (input === '') {
                this.value = minRange.value;
                return;
            }
            
            const val = parseFormattedNumber(input);
            if (!isNaN(val)) {
                // Enforce minimum limit of 0
                if (val < 0) {
                    this.value = "0";
                    minRange.value = 0;
                    updateSlider();
                    return;
                }
                
                const maxVal = parseInt(maxRange.value);
                const constrainedVal = Math.max(parseInt(minRange.min), Math.min(val, parseInt(minRange.max)));
                minRange.value = Math.min(constrainedVal, maxVal);
                updateSlider();
            }
        });
    }

    if (maxInput) {
        maxInput.addEventListener('input', function() {
            const input = this.value.trim();
            // Allow empty input while typing
            if (input === '') return;
            
            const maxVal = parseFormattedNumber(input);
            // Only proceed if it's a valid number
            if (!isNaN(maxVal)) {
                // Enforce maximum limit
                const maxLimit = parseInt(maxRange.max);
                if (maxVal > maxLimit) {
                    this.value = maxLimit.toString();
                    return;
                }
                
                // Constrain to min and max range values
                const constrainedVal = Math.max(parseInt(maxRange.min), Math.min(maxVal, maxLimit));
                
                const minVal = parseInt(minRange.value);
                
                // Ensure max isn't less than min
                maxRange.value = Math.max(constrainedVal, minVal);
                
                // Now update the slider immediately
                updateSlider();
            }
        });
        
        // Keep this for consistency/backwards compatibility
        maxInput.addEventListener('change', function() {
            const minVal = parseInt(minRange.value);
            const maxVal = parseFormattedNumber(this.value);
            
            if (!isNaN(maxVal)) {
                // Enforce maximum limit
                const maxLimit = parseInt(maxRange.max);
                if (maxVal > maxLimit) {
                    this.value = maxLimit.toString();
                    maxRange.value = maxLimit;
                    updateSlider();
                    return;
                }
                
                // Constrain to min and max range values
                const constrainedVal = Math.max(parseInt(maxRange.min), Math.min(maxVal, maxLimit));
                
                // Ensure max isn't less than min
                maxRange.value = Math.max(constrainedVal, minVal);
                
                // Now update the slider
                updateSlider();
            }
        });
        
        // Format inputs on focus out
        maxInput.addEventListener('blur', function() {
            const input = this.value.trim();
            // If empty, use the current slider value
            if (input === '') {
                this.value = maxRange.value;
                return;
            }
            
            const val = parseFormattedNumber(input);
            if (!isNaN(val)) {
                // Enforce maximum limit
                const maxLimit = parseInt(maxRange.max);
                if (val > maxLimit) {
                    this.value = maxLimit.toString();
                    maxRange.value = maxLimit;
                    updateSlider();
                    return;
                }
                
                const minVal = parseInt(minRange.value);
                const constrainedVal = Math.max(parseInt(maxRange.min), Math.min(val, maxLimit));
                maxRange.value = Math.max(constrainedVal, minVal);
                updateSlider();
            }
        });
    }

    // Initialize slider
    if (track) {
        updateSlider();
    }

    // Clear filters
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            // Reset salary range
            if (minRange && maxRange) {
                // Use smooth animation for resetting
                const duration = 300;
                const startMin = parseInt(minRange.value);
                const startMax = parseInt(maxRange.value);
                const endMin = parseInt(minRange.min);
                const endMax = parseInt(maxRange.max);
                
                const startTime = performance.now();
                
                function animate(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    
                    // Easing function for smooth animation
                    const easeProgress = 1 - Math.pow(1 - progress, 3);
                    
                    minRange.value = Math.round(startMin + (endMin - startMin) * easeProgress);
                    maxRange.value = Math.round(startMax + (endMax - startMax) * easeProgress);
                    
                    updateSlider();
                    
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    }
                }
                
                requestAnimationFrame(animate);
            }
            
            // Reset all checkboxes for experience, workplace, employment, and work type
            document.querySelectorAll('.filter-experience, .filter-workplace, .filter-employment, .filter-work-type').forEach(checkbox => {
                checkbox.checked = false;
            });

            // Reset location
            const locationInput = document.getElementById('locationInput');
            if (locationInput) locationInput.value = '';
            
            const remoteCheck = document.getElementById('remoteCheck');
            if (remoteCheck) remoteCheck.checked = false;
        });
    }

    // Handle Apply Filters button click
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            // Get search tags container
            const searchTags = document.querySelector('.search-tags');
            if (!searchTags) return;

            // Clear existing search tags
            searchTags.innerHTML = '';
            
            // Get selected filters
            // 1. Location
            const locationInput = document.getElementById('locationInput');
            if (locationInput && locationInput.value.trim()) {
                const locationTag = createSearchTag(locationInput.value.trim(), 'bi-geo-alt');
                searchTags.appendChild(locationTag);
            }
            
            // 2. Experience Levels
            document.querySelectorAll('.filter-experience:checked').forEach(checkbox => {
                const experienceTag = createSearchTag(checkbox.value, 'bi-bar-chart');
                searchTags.appendChild(experienceTag);
            });
            
            // 3. Workplace
            document.querySelectorAll('.filter-workplace:checked').forEach(checkbox => {
                const workplaceTag = createSearchTag(checkbox.value, 'bi-building');
                searchTags.appendChild(workplaceTag);
            });
            
            // 4. Employment Type
            document.querySelectorAll('.filter-employment:checked').forEach(checkbox => {
                const employmentTag = createSearchTag(checkbox.value, 'bi-file-earmark-text');
                searchTags.appendChild(employmentTag);
            });
            
            // 5. Work Type
            document.querySelectorAll('.filter-work-type:checked').forEach(checkbox => {
                const workTypeTag = createSearchTag(checkbox.value, 'bi-clock');
                searchTags.appendChild(workTypeTag);
            });
            
            // 6. Remote checkbox
            const remoteCheck = document.getElementById('remoteCheck');
            if (remoteCheck && remoteCheck.checked) {
                const remoteTag = createSearchTag('Remote', 'bi-house');
                searchTags.appendChild(remoteTag);
            }
            
            // 7. Salary Range
            let minSalary, maxSalary, minDefault, maxDefault;
            
            // Try with minSalaryRange/maxSalaryRange first (from index.html)
            const minSalaryRangeEl = document.getElementById('minSalaryRange');
            const maxSalaryRangeEl = document.getElementById('maxSalaryRange');
            
            // Fall back to minSalary/maxSalary (from job_list.html) if the above don't exist
            const minSalaryEl = document.getElementById('minSalary');
            const maxSalaryEl = document.getElementById('maxSalary');
            
            if (minSalaryRangeEl && maxSalaryRangeEl) {
                minSalary = parseInt(minSalaryRangeEl.value);
                maxSalary = parseInt(maxSalaryRangeEl.value);
                minDefault = parseInt(minSalaryRangeEl.min);
                maxDefault = parseInt(maxSalaryRangeEl.max);
            } else if (minSalaryEl && maxSalaryEl) {
                minSalary = parseInt(minSalaryEl.value);
                maxSalary = parseInt(maxSalaryEl.value);
                minDefault = parseInt(minSalaryEl.min);
                maxDefault = parseInt(maxSalaryEl.max);
            } else {
                // If neither set of elements exists, use defaults
                minSalary = 0;
                maxSalary = 200000;
                minDefault = 0;
                maxDefault = 200000;
            }
            
            if (minSalary > minDefault || maxSalary < maxDefault) {
                const salaryTag = createSearchTag(
                    `${new Intl.NumberFormat('pl-PL').format(minSalary)} - ${new Intl.NumberFormat('pl-PL').format(maxSalary)} PLN`,
                    'bi-currency-dollar',
                    'salary-filter',
                    { minSalary: minSalary, maxSalary: maxSalary }
                );
                searchTags.appendChild(salaryTag);
            }
            
            // Update the hidden search input with all tags
            updateSearchInput();
            
            // Close the modal
            const filtersModal = document.getElementById('jobFiltersModal');
            if (filtersModal) {
                // Use the Bootstrap modal method to hide the modal
                const bsModal = bootstrap.Modal.getInstance(filtersModal);
                if (bsModal) {
                    bsModal.hide();
                }
                
                // As a fallback, also remove the modal backdrop manually
                setTimeout(() => {
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                        backdrop.remove();
                    });
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }, 300);
            }
            
            // Perform AJAX search
            performAjaxSearch();
        });
    }

    // Get URL parameters to check if we're coming back from a search
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');

    // Get the hero tags container
    const heroTagsContainer = document.getElementById('heroTags');
    if (!heroTagsContainer) return;

    // Define all possible tags
    const allTags = [
        'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'TypeScript', 'Angular',
        'Vue.js', 'Java', 'C#', 'PHP', 'Ruby', 'Go', 'Swift', 'Kotlin', 'Rust',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'DevOps', 'Machine Learning',
        'Data Science', 'Artificial Intelligence', 'Blockchain', 'IoT', 'Mobile Development',
        'Frontend', 'Backend', 'Full Stack', 'UI/UX', 'QA', 'Testing', 'Security',
        'Database', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis',
        'GraphQL', 'REST API', 'Microservices', 'CI/CD', 'Git', 'Linux', 'Agile'
    ];

    // Function to get icon class based on tag
    function getIconClass(tag) {
        if (tag === 'Python' || tag === 'JavaScript' || tag === 'TypeScript' || tag === 'Java' || tag === 'C#' || tag === 'PHP' || tag === 'Ruby' || tag === 'Go' || tag === 'Swift' || tag === 'Kotlin' || tag === 'Rust') {
            return 'bi-code-slash';
        } else if (tag === 'React' || tag === 'Angular' || tag === 'Vue.js' || tag === 'Frontend') {
            return 'bi-layout-text-window';
        } else if (tag === 'Django' || tag === 'Node.js' || tag === 'Backend') {
            return 'bi-server';
        } else if (tag === 'AWS' || tag === 'Azure' || tag === 'GCP' || tag === 'Cloud') {
            return 'bi-cloud';
        } else if (tag === 'Docker' || tag === 'Kubernetes' || tag === 'DevOps' || tag === 'CI/CD') {
            return 'bi-gear';
        } else if (tag === 'Machine Learning' || tag === 'Data Science' || tag === 'Artificial Intelligence') {
            return 'bi-graph-up';
        } else if (tag === 'Database' || tag === 'SQL' || tag === 'NoSQL' || tag === 'MongoDB' || tag === 'PostgreSQL' || tag === 'MySQL' || tag === 'Redis') {
            return 'bi-database';
        } else if (tag === 'Mobile Development') {
            return 'bi-phone';
        } else if (tag === 'UI/UX') {
            return 'bi-palette';
        } else if (tag === 'QA' || tag === 'Testing') {
            return 'bi-bug';
        } else if (tag === 'Security') {
            return 'bi-shield';
        } else if (tag === 'GraphQL' || tag === 'REST API') {
            return 'bi-hdd-network';
        } else if (tag === 'Microservices') {
            return 'bi-diagram-3';
        } else if (tag === 'Git') {
            return 'bi-git';
        } else if (tag === 'Linux') {
            return 'bi-terminal';
        } else if (tag === 'Agile') {
            return 'bi-kanban';
        }
        return 'bi-code-slash'; // Default
    }

    // Function to create a search tag element
    function createSearchTag(text, iconClass = 'bi-tag', dataAttribute = '', dataValue = {}) {
        const searchTags = document.getElementById('searchTags');
        if (!searchTags) return;
        
        // Create tag element
        const tag = document.createElement('div');
        tag.className = 'search-tag';
        
        // Add icon
        const icon = document.createElement('i');
        // Ensure the icon has both 'bi' and the specific icon class
        icon.className = `bi ${iconClass.startsWith('bi-') ? iconClass : 'bi-' + iconClass} me-2`;
        icon.style.opacity = '0.7';
        
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        
        tag.appendChild(icon);
        tag.appendChild(textSpan);
        
        // Add data attributes
        if (dataAttribute) {
            tag.setAttribute(`data-${dataAttribute}`, JSON.stringify(dataValue));
        }
        
        // Add touch-friendly styles for mobile
        if (window.innerWidth <= 768) {
            tag.style.minHeight = '28px';
            tag.style.display = 'inline-flex';
            tag.style.padding = '0.25rem 0.75rem';
            tag.style.margin = '0 0.15rem';
            tag.style.touchAction = 'manipulation';
        }
        
        // Add click event to remove tag
        tag.addEventListener('click', function(e) {
            // Prevent clicks from propagating (especially important on mobile)
            e.stopPropagation();
            
            // Find and deactivate corresponding category button if it exists
            document.querySelectorAll('.btn-category').forEach(btn => {
                const btnText = btn.querySelector('i').nextSibling.textContent.trim();
                if (btnText === text) {
                    btn.classList.remove('active');
                    const btnIcon = btn.querySelector('i');
                    if (btnIcon) {
                        btnIcon.style.opacity = '0.7';
                    }
                }
            });

            // Find and deactivate corresponding hero tag if it exists
            document.querySelectorAll('.hero-tag').forEach(heroTag => {
                if (heroTag.textContent.trim() === text) {
                    heroTag.classList.remove('active');
                    const iconElement = heroTag.querySelector('i');
                    if (iconElement) {
                        iconElement.style.opacity = '0.7';
                    }
                }
            });

            // Remove the tag
            this.remove();
            updateSearchInput();
            
            // Manually trigger a sync between all search tags and category buttons
            syncCategoryButtonsWithTags();
            
            // Use AJAX to update results
            performAjaxSearch();
        });
        
        // Add better mobile touch handling
        tag.addEventListener('touchstart', function(e) {
            // Change appearance briefly to indicate the tag is being touched
            this.style.opacity = '0.7';
            this.style.transform = 'scale(0.95)';
        });
        
        tag.addEventListener('touchend', function(e) {
            // Reset appearance
            this.style.opacity = '';
            this.style.transform = '';
        });
        
        // Add the tag to the container
        searchTags.appendChild(tag);
        
        // Scroll the search tags container to show the newly added tag
        setTimeout(() => {
            searchTags.scrollLeft = searchTags.scrollWidth;
        }, 10);
        
        // Update hidden input
        updateSearchInput();
        
        return tag;
    }

    // Function to update search input value based on tags
    function updateSearchInput() {
        if (!hiddenSearchInput || !searchTagsContainer) return;
        
        const tags = searchTagsContainer.querySelectorAll('.search-tag span');
        const searchText = Array.from(tags)
            .map(tag => `"${tag.textContent.trim()}"`)
            .join(' ');
        
        hiddenSearchInput.value = searchText;
        
        // Update visible input placeholder
        if (visibleSearchInput) {
            if (tags.length > 0) {
                visibleSearchInput.value = '';
                visibleSearchInput.placeholder = '';
            } else {
                // Get the total jobs from the data attribute
                const totalJobs = visibleSearchInput.getAttribute('data-total-jobs');
                if (totalJobs) {
                    visibleSearchInput.placeholder = `${totalJobs} offers`;
                    // Ensure placeholder is aligned left on mobile
                    if (window.innerWidth <= 768) {
                        visibleSearchInput.style.textAlign = 'left';
                        visibleSearchInput.style.paddingLeft = '0.5rem';
                    }
                }
            }
        }
    }

    // Function to synchronize category buttons with search tags
    function syncCategoryButtonsWithTags() {
        const searchTags = document.getElementById('searchTags');
        if (!searchTags) return;
        
        // Get all current tag texts
        const currentTagTexts = Array.from(searchTags.querySelectorAll('.search-tag span'))
            .map(span => span.textContent.trim());
        
        // Update category buttons based on tag presence
        document.querySelectorAll('.btn-category').forEach(btn => {
            const btnText = btn.querySelector('i').nextSibling.textContent.trim();
            const isTagPresent = currentTagTexts.includes(btnText);
            
            // Set button state based on tag presence
            if (isTagPresent && !btn.classList.contains('active')) {
                btn.classList.add('active');
                const btnIcon = btn.querySelector('i');
                if (btnIcon) {
                    btnIcon.style.opacity = '1';
                }
            } else if (!isTagPresent && btn.classList.contains('active')) {
                btn.classList.remove('active');
                const btnIcon = btn.querySelector('i');
                if (btnIcon) {
                    btnIcon.style.opacity = '0.7';
                }
            }
        });
    }

    // Function to create a tag element
    function createTagElement(tag, isActive = false) {
        const tagElement = document.createElement('button');
        tagElement.className = 'hero-tag';
        if (isActive) {
            tagElement.classList.add('active');
        }

        // Add appropriate icon
        const iconClass = getIconClass(tag);
        const icon = document.createElement('i');
        icon.className = `bi ${iconClass} me-2`;
        icon.style.opacity = '0.7';

        // Append icon and text
        tagElement.appendChild(icon);
        tagElement.appendChild(document.createTextNode(tag));

        // Add click event
        tagElement.addEventListener('click', function(e) {
            // Prevent immediate form submission
            e.preventDefault();

            // Toggle active class
            this.classList.toggle('active');

            // Make icon fully opaque when active
            const iconElement = this.querySelector('i');
            if (this.classList.contains('active')) {
                iconElement.style.opacity = '1';
                
                // Add tag to search input
                const searchTags = document.querySelector('.search-tags');
                if (searchTags) {
                    // Check if tag already exists
                    const existingTags = Array.from(searchTags.querySelectorAll('.search-tag span'))
                        .map(span => span.textContent);
                    
                    if (!existingTags.includes(tag)) {
                        const searchTag = createSearchTag(tag, iconClass);
                        searchTags.appendChild(searchTag);
                        updateSearchInput();
                        
                        // Use AJAX to update results
                        performAjaxSearch();
                    }
                }
            } else {
                iconElement.style.opacity = '0.7';
                
                // Remove tag from search input
                const searchTags = document.querySelector('.search-tags');
                if (searchTags) {
                    const tags = searchTags.querySelectorAll('.search-tag');
                    tags.forEach(tagElement => {
                        if (tagElement.querySelector('span').textContent === tag) {
                            tagElement.remove();
                            updateSearchInput();
                            
                            // Use AJAX to update results
                            performAjaxSearch();
                        }
                    });
                }
            }

            // Store selected tags in session storage
            updateSelectedTags();
        });

        return tagElement;
    }

    // Function to update selected tags in session storage
    function updateSelectedTags() {
        const selectedTags = [];
        document.querySelectorAll('.hero-tag').forEach(tag => {
            const tagText = tag.textContent.trim();
            const isActive = tag.classList.contains('active');
            selectedTags.push({ text: tagText, active: isActive });
        });
        sessionStorage.setItem('selectedHeroTags', JSON.stringify(selectedTags));
    }

    // Check if we have previously selected tags in session storage
    let selectedTags = [];
    try {
        const storedTags = sessionStorage.getItem('selectedHeroTags');
        if (storedTags) {
            selectedTags = JSON.parse(storedTags);
        }
    } catch (e) {
        console.error('Error parsing stored tags:', e);
    }

    // Clear the container
    heroTagsContainer.innerHTML = '';

    // If we have previously selected tags, use those
    if (selectedTags.length > 0) {
        // Add the stored tags
        selectedTags.forEach(tagInfo => {
            // Check if this tag is in the search query
            const isInQuery = searchQuery && searchQuery.split(' ').some(term =>
                term.toLowerCase() === tagInfo.text.toLowerCase()
            );
            const tagElement = createTagElement(tagInfo.text, tagInfo.active || isInQuery);
            heroTagsContainer.appendChild(tagElement);
        });
    } else {
        // If we don't have selected tags, generate random ones
        // Shuffle array and take first 5 elements
        const shuffledTags = [...allTags].sort(() => 0.5 - Math.random()).slice(0, 5);

        // Create and append tag elements
        shuffledTags.forEach(tag => {
            // Check if this tag is in the search query
            const isInQuery = searchQuery && searchQuery.split(' ').some(term =>
                term.toLowerCase() === tag.toLowerCase()
            );
            const tagElement = createTagElement(tag, isInQuery);
            heroTagsContainer.appendChild(tagElement);
        });
    }

    // Update selected tags in storage
    updateSelectedTags();

    // AJAX Search Functionality
    const searchForm = document.querySelector("form.search-form");
    const searchTagsContainer = document.getElementById('searchTags');
    const visibleSearchInput = document.getElementById('visibleSearchInput');
    const hiddenSearchInput = document.getElementById('hiddenSearchInput');
    const jobListingsContainer = document.getElementById('jobListingsContainer');
    const categoryButtons = document.querySelectorAll('.btn-category');
    
    // Update visible search input with current query value
    if (visibleSearchInput && hiddenSearchInput) {
        visibleSearchInput.value = hiddenSearchInput.value;
    }
    
    // Handle input changes
    if (visibleSearchInput && hiddenSearchInput) {
        visibleSearchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                
                // If there's text in the visible input, create a tag for it
                if (this.value.trim()) {
                    if (searchTagsContainer) {
                        const tag = createSearchTag(this.value.trim());
                        searchTagsContainer.appendChild(tag);
                        this.value = '';
                        updateSearchInput();
                        performAjaxSearch();
                    }
                }
            }
        });
        
        // Clear placeholder when focused
        visibleSearchInput.addEventListener('focus', function() {
            this.placeholder = '';
        });

        // Restore placeholder when blurred and no tags
        visibleSearchInput.addEventListener('blur', function() {
            const tags = document.querySelectorAll('.search-tag');
            if (tags.length === 0 && !this.value) {
                // Get the total jobs from the data attribute
                const totalJobs = this.getAttribute('data-total-jobs');
                if (totalJobs) {
                    this.placeholder = `${totalJobs} offers`;
                    // Ensure placeholder is aligned left on mobile
                    if (window.innerWidth <= 768) {
                        this.style.textAlign = 'left';
                        this.style.paddingLeft = '0.5rem';
                    }
                }
            }
        });
    }
    
    // Handle form submission with AJAX
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performAjaxSearch();
        });
    }
    
    // Initial sync to ensure category buttons match any existing search tags
    syncCategoryButtonsWithTags();
    
    // Handle category button clicks
    categoryButtons.forEach(button => {
        // Remove any existing event listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get the text and icon class
            const text = this.querySelector('i').nextSibling.textContent.trim();
            const iconClass = this.querySelector('i').className.split(' ')[1];
            
            // Toggle active state
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            // Update icon opacity
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.opacity = isActive ? '1' : '0.7';
            }
            
            if (isActive) {
                // Add tag to search input
                if (searchTagsContainer) {
                    const existingTags = Array.from(searchTagsContainer.querySelectorAll('.search-tag span'))
                        .map(span => span.textContent.trim());
                    
                    if (!existingTags.includes(text)) {
                        const searchTag = createSearchTag(text, iconClass);
                        searchTagsContainer.appendChild(searchTag);
                        
                        if (visibleSearchInput) {
                            visibleSearchInput.placeholder = '';
                        }
                        
                        updateSearchInput();
                        performAjaxSearch();
                    }
                }
            } else {
                // Remove tag from search input
                if (searchTagsContainer) {
                    const tags = searchTagsContainer.querySelectorAll('.search-tag');
                    tags.forEach(tagElement => {
                        const tagText = tagElement.querySelector('span').textContent.trim();
                        if (tagText === text) {
                            tagElement.remove();
                            updateSearchInput();
                            performAjaxSearch();
                        }
                    });
                    
                    if (visibleSearchInput && searchTagsContainer.children.length === 0) {
                        // Get the total jobs from the data attribute
                        const totalJobs = visibleSearchInput.getAttribute('data-total-jobs');
                        if (totalJobs) {
                            visibleSearchInput.placeholder = `${totalJobs} offers`;
                            // Ensure placeholder is aligned left on mobile
                            if (window.innerWidth <= 768) {
                                visibleSearchInput.style.textAlign = 'left';
                                visibleSearchInput.style.paddingLeft = '0.5rem';
                            }
                        }
                    }
                    
                    // Hide clear button
                    updateClearButtonVisibility();
                    
                    // Perform search to update results
                    if (typeof performAjaxSearch === 'function') {
                        performAjaxSearch();
                    } else {
                        // If AJAX search is not available, submit the form
                        document.querySelector('form.search-form').submit();
                    }
                }
            }
        });

        // Set initial state based on URL parameters
        if (searchQuery) {
            const terms = searchQuery.match(/"[^"]+"|[^\s"]+/g) || [];
            terms.forEach(term => {
                term = term.replace(/^"(.*)"$/, '$1');
                const buttonText = newButton.querySelector('i').nextSibling.textContent.trim();
                if (buttonText === term) {
                    newButton.classList.add('active');
                    const icon = newButton.querySelector('i');
                    if (icon) {
                        icon.style.opacity = '1';
                    }
                }
            });
        }
    });

    // Initialize search tags from URL parameters
    if (searchQuery && searchTagsContainer) {
        // Clear existing tags first
        searchTagsContainer.innerHTML = '';
        
        const matches = searchQuery.match(/"[^"]+"|[^\s"]+/g) || [];
        matches.forEach(term => {
            if (term) {
                term = term.replace(/^"(.*)"$/, '$1');
                let iconClass = 'bi-tag';
                
                // Try to find a matching hero tag to get its icon
                document.querySelectorAll('.hero-tag').forEach(heroTag => {
                    if (heroTag.textContent.trim() === term) {
                        const icon = heroTag.querySelector('i');
                        if (icon) {
                            iconClass = icon.className.replace('me-2', '');
                        }
                    }
                });
                
                // Also check category buttons
                document.querySelectorAll('.btn-category').forEach(categoryBtn => {
                    if (categoryBtn.textContent.trim() === term) {
                        const icon = categoryBtn.querySelector('i');
                        if (icon) {
                            iconClass = icon.className.replace('me-2', '');
                        }
                    }
                });
                
                const tag = createSearchTag(term, iconClass);
                searchTagsContainer.appendChild(tag);
            }
        });
        
        // Clear the visible input if there are tags
        if (visibleSearchInput && matches.length > 0) {
            visibleSearchInput.value = '';
            visibleSearchInput.placeholder = '';
        }
        
        updateSearchInput();
    }
    
    // Function to perform AJAX search
    function performAjaxSearch() {
        if (!jobListingsContainer) return;
        
        // Show loading state with skeleton loaders
        const skeletonHTML = `
            <div class="skeleton-loader fade-in">
                <div class="job-listing skeleton">
                    <div class="job-listing-logo skeleton-circle"></div>
                    <div class="job-listing-info">
                        <div class="job-listing-details">
                            <div class="job-listing-left">
                                <div class="skeleton-title"></div>
                                <div class="skeleton-meta">
                                    <div class="skeleton-text"></div>
                                    <div class="skeleton-text"></div>
                                    <div class="skeleton-text"></div>
                                </div>
                            </div>
                            <div class="job-listing-right">
                                <div class="skeleton-salary"></div>
                                <div class="skeleton-tags">
                                    <span class="skeleton-badge"></span>
                                    <span class="skeleton-badge"></span>
                                    <span class="skeleton-badge"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert multiple skeleton loaders
        let skeletonLoaders = '';
        for (let i = 0; i < 5; i++) {
            skeletonLoaders += skeletonHTML;
        }
        
        jobListingsContainer.innerHTML = skeletonLoaders;
        
        // Get form data
        const searchQuery = hiddenSearchInput.value;
        const locationInput = document.getElementById('locationInput');
        const remoteCheckbox = document.getElementById('remoteCheck');
        const fulltimeCheckbox = document.querySelector('input[name="fulltime"]');
        const parttimeCheckbox = document.querySelector('input[name="parttime"]');
        
        // Get salary range values
        let minSalary, maxSalary, minDefault, maxDefault;
        
        // Try with minSalaryRange/maxSalaryRange first (from index.html)
        const minSalaryRangeEl = document.getElementById('minSalaryRange');
        const maxSalaryRangeEl = document.getElementById('maxSalaryRange');
        
        // Fall back to minSalary/maxSalary (from job_list.html) if the above don't exist
        const minSalaryEl = document.getElementById('minSalary');
        const maxSalaryEl = document.getElementById('maxSalary');
        
        if (minSalaryRangeEl && maxSalaryRangeEl) {
            minSalary = parseInt(minSalaryRangeEl.value);
            maxSalary = parseInt(maxSalaryRangeEl.value);
            minDefault = parseInt(minSalaryRangeEl.min);
            maxDefault = parseInt(maxSalaryRangeEl.max);
        } else if (minSalaryEl && maxSalaryEl) {
            minSalary = parseInt(minSalaryEl.value);
            maxSalary = parseInt(maxSalaryEl.value);
            minDefault = parseInt(minSalaryEl.min);
            maxDefault = parseInt(maxSalaryEl.max);
        } else {
            // If neither set of elements exists, use defaults
            minSalary = 0;
            maxSalary = 200000;
            minDefault = 0;
            maxDefault = 200000;
        }
        
        // Build query parameters
        let params = new URLSearchParams();
        if (searchQuery) params.append('q', searchQuery);
        if (locationInput && locationInput.value) params.append('location', locationInput.value);
        if (remoteCheckbox && remoteCheckbox.checked) params.append('remote', 'true');
        if (fulltimeCheckbox && fulltimeCheckbox.checked) params.append('fulltime', 'true');
        if (parttimeCheckbox && parttimeCheckbox.checked) params.append('parttime', 'true');
        
        // Add salary range parameters if they're different from defaults
        if (minSalary > minDefault) params.append('min_salary', minSalary);
        if (maxSalary < maxDefault) params.append('max_salary', maxSalary);
        
        // Add a minimum delay to ensure the animation is visible (at least 500ms)
        const fetchStart = Date.now();
        const minDelay = 500; // milliseconds
        
        // Send AJAX request
        fetch('/ajax/search-jobs/?' + params.toString())
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Calculate how much time has passed
                const fetchTime = Date.now() - fetchStart;
                const remainingDelay = Math.max(0, minDelay - fetchTime);
                
                // Apply remaining delay if needed for smooth animation
                setTimeout(() => {
                    // Create a temporary div to hold the new content
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = data.html;
                    
                    // Add fade-out class to current content
                    jobListingsContainer.classList.add('fade-out');
                    
                    // After fade out, update content and fade in
                    setTimeout(() => {
                        jobListingsContainer.innerHTML = data.html;
                        jobListingsContainer.classList.remove('fade-out');
                        jobListingsContainer.classList.add('fade-in');
                        
                        // Remove the fade-in class after animation completes
                        setTimeout(() => {
                            jobListingsContainer.classList.remove('fade-in');
                        }, 300);
                        
                        // Update URL with search parameters (for browser history)
                        const url = new URL(window.location);
                        if (searchQuery) {
                            url.searchParams.set('q', searchQuery);
                        } else {
                            url.searchParams.delete('q');
                        }
                        
                        window.history.pushState({}, '', url);
                        
                        // Initialize load more functionality for search results
                        if (typeof initLoadMore === 'function') {
                            initLoadMore();
                        }
                    }, 200); // Short fade-out duration
                }, remainingDelay);
            })
            .catch(error => {
                console.error('Error during search:', error);
                jobListingsContainer.innerHTML = '<div class="alert alert-danger">An error occurred during search. Please try again.</div>';
            });
    }

    // Handle search button click
    const searchButton = document.querySelector('.search-button');
    if (searchButton) {
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            performAjaxSearch();
        });
    }

    // Make sure category buttons and search tags are synchronized on page load
    setTimeout(function() {
        syncCategoryButtonsWithTags();
    }, 100);

    // Initial check for category buttons
    updateClearButtonVisibility();
    
    // Ensure placeholder is aligned left on mobile for initial load
    if (visibleSearchInput && window.innerWidth <= 768) {
        visibleSearchInput.style.textAlign = 'left';
        visibleSearchInput.style.paddingLeft = '0.5rem';
    }
    
    // Handle window resize for placeholder alignment
    window.addEventListener('resize', function() {
        if (visibleSearchInput) {
            if (window.innerWidth <= 768) {
                visibleSearchInput.style.textAlign = 'left';
                visibleSearchInput.style.paddingLeft = '0.5rem';
            } else {
                visibleSearchInput.style.textAlign = '';
                visibleSearchInput.style.paddingLeft = '';
            }
        }
    });
});

// Reset hero tags on page refresh
window.addEventListener('pageshow', function(event) {
    // Check if the page is being loaded from cache (refresh)
    if (event.persisted || (window.performance && window.performance.navigation.type === 1)) {
        // Clear session storage for hero tags
        sessionStorage.removeItem('selectedHeroTags');
    }
});

// Process skills placeholders
document.addEventListener('DOMContentLoaded', function() {
    const skillsPlaceholders = document.querySelectorAll('.skills-placeholder');
    
    skillsPlaceholders.forEach(function(placeholder) {
        try {
            const skillsData = placeholder.getAttribute('data-skills');
            if (skillsData) {
                const skills = JSON.parse(skillsData);
                const tagsContainer = placeholder.parentElement;
                
                if (Array.isArray(skills) && skills.length > 0) {
                    // Remove the placeholder
                    placeholder.remove();
                    
                    // Add skill badges
                    skills.forEach(function(skill) {
                        const badge = document.createElement('span');
                        badge.className = 'badge';
                        badge.textContent = skill;
                        tagsContainer.appendChild(badge);
                    });
                }
            }
        } catch (e) {
            console.error('Error processing skills:', e);
        }
    });
});
