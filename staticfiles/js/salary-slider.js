// Dedicated script for the salary range slider
document.addEventListener('DOMContentLoaded', function() {
    console.log('Salary slider script loaded');
    
    // Basic slider initialization
    const minRange = document.getElementById('minSalaryRange');
    const maxRange = document.getElementById('maxSalaryRange');
    const minInput = document.getElementById('minSalaryInput');
    const maxInput = document.getElementById('maxSalaryInput');
    const track = document.querySelector('.slider-track');
    const minHandle = document.getElementById('minSalaryHandle');
    const maxHandle = document.getElementById('maxSalaryHandle');
    const minTooltip = document.getElementById('minSalaryTooltip');
    const maxTooltip = document.getElementById('maxSalaryTooltip');
    
    // Debug element existence
    console.log('Slider elements:', {
        minRange: !!minRange,
        maxRange: !!maxRange,
        track: !!track,
        minHandle: !!minHandle,
        maxHandle: !!maxHandle,
        minTooltip: !!minTooltip,
        maxTooltip: !!maxTooltip
    });
    
    if (minRange && maxRange && track && minHandle && maxHandle && minTooltip && maxTooltip) {
        console.log('All slider elements found, initializing...');
        
        // Format number with thousand separators
        function formatNumber(num) {
            return new Intl.NumberFormat('pl-PL').format(num);
        }
        
        // Update slider visuals based on range values
        function updateSlider() {
            const min = parseInt(minRange.min);
            const max = parseInt(minRange.max);
            const range = max - min;
            
            const minVal = parseInt(minRange.value);
            const maxVal = parseInt(maxRange.value);
            
            console.log('Updating slider with values:', minVal, maxVal);
            
            // Calculate percentages for positioning
            const minPercent = ((minVal - min) / range) * 100;
            const maxPercent = ((maxVal - min) / range) * 100;
            
            // Position handles
            minHandle.style.left = `${minPercent}%`;
            maxHandle.style.left = `${maxPercent}%`;
            
            // Position tooltips and update their content - DISABLED
            // minTooltip.style.left = `${minPercent}%`;
            // maxTooltip.style.left = `${maxPercent}%`;
            // minTooltip.textContent = `${formatNumber(minVal)} PLN`;
            // maxTooltip.textContent = `${formatNumber(maxVal)} PLN`;
            
            // Update track highlighting
            track.style.background = `linear-gradient(to right, 
                var(--bs-border-color, #e9ecef) ${minPercent}%, 
                #0d6efd ${minPercent}%, 
                #0d6efd ${maxPercent}%, 
                var(--bs-border-color, #e9ecef) ${maxPercent}%)`;
            
            // Only update input fields if they don't have focus (to prevent overwriting user input)
            if (minInput && document.activeElement !== minInput) {
                minInput.value = minVal;
            }
            if (maxInput && document.activeElement !== maxInput) {
                maxInput.value = maxVal;
            }
        }
        
        // Set up event listeners
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
        
        // Also update when number inputs change
        if (minInput) {
            // Update the slider in real-time as the user types
            minInput.addEventListener('input', function() {
                let value = parseInt(this.value);
                
                // Only update if it's a valid number
                if (!isNaN(value)) {
                    // Enforce minimum limit of 0
                    if (value < 0) {
                        value = 0;
                        this.value = value;
                    }
                    
                    // Ensure value is within allowed range
                    value = Math.max(0, Math.min(value, parseInt(minRange.max)));
                    
                    const maxVal = parseInt(maxRange.value);
                    
                    // Update the slider, ensuring min doesn't exceed max
                    minRange.value = Math.min(value, maxVal);
                    
                    // Update the slider visuals
                    updateSlider();
                }
            });
            
            // Keep the update on blur for safety (in case JS errors occur)
            minInput.addEventListener('blur', function() {
                let value = parseInt(this.value);
                if (isNaN(value)) value = 0;
                
                // Enforce minimum limit of 0
                if (value < 0) {
                    value = 0;
                    this.value = value;
                }
                
                // Ensure value is within allowed range
                value = Math.max(0, Math.min(value, parseInt(minRange.max)));
                
                const maxVal = parseInt(maxRange.value);
                
                // Update the slider, ensuring min doesn't exceed max
                minRange.value = Math.min(value, maxVal);
                updateSlider();
            });
        }
        
        if (maxInput) {
            // Update the slider in real-time as the user types
            maxInput.addEventListener('input', function() {
                let value = parseInt(this.value);
                
                // Only update if it's a valid number
                if (!isNaN(value)) {
                    // Enforce maximum limit
                    const maxLimit = parseInt(maxRange.max);
                    if (value > maxLimit) {
                        value = maxLimit;
                        this.value = value;
                    }
                    
                    // Ensure value is within allowed range
                    value = Math.max(0, Math.min(value, maxLimit));
                    
                    const minVal = parseInt(minRange.value);
                    
                    // Update the slider, ensuring max isn't less than min
                    maxRange.value = Math.max(value, minVal);
                    
                    // Update the slider visuals
                    updateSlider();
                }
            });
            
            // Keep the update on blur for safety (in case JS errors occur)
            maxInput.addEventListener('blur', function() {
                let value = parseInt(this.value);
                if (isNaN(value)) value = parseInt(maxRange.max);
                
                // Enforce maximum limit
                const maxLimit = parseInt(maxRange.max);
                if (value > maxLimit) {
                    value = maxLimit;
                    this.value = value;
                }
                
                // Ensure value is within allowed range
                value = Math.max(0, Math.min(value, maxLimit));
                
                const minVal = parseInt(minRange.value);
                
                // Update the slider, ensuring max isn't less than min
                maxRange.value = Math.max(value, minVal);
                updateSlider();
            });
        }
        
        // Initialize slider on load
        try {
            updateSlider();
            console.log('Slider initialized successfully');
        } catch (e) {
            console.error('Error initializing slider:', e);
        }
    } else {
        console.warn('Some slider elements not found:', {
            minRange: !!minRange,
            maxRange: !!maxRange,
            track: !!track,
            minHandle: !!minHandle,
            maxHandle: !!maxHandle
        });
    }
}); 