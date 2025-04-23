/**
 *  - Job Detail Page Scripts
 * Handles the fixed apply button functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply button handling
    const applyButton = document.getElementById('mobileApplyButton');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (applyButton) {
        console.log('Mobile apply button initialized');
        
        // Add class to body for proper spacing
        document.body.classList.add('has-fixed-apply-btn');
        
        // Set initial visibility
        applyButton.style.display = 'block';
        applyButton.classList.remove('hidden');
        
        // Force visibility after page load
        setTimeout(function() {
            applyButton.style.display = 'block';
            applyButton.classList.remove('hidden');
            
            // Fix for iOS Safari
            if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
                applyButton.style.position = 'fixed';
                applyButton.style.bottom = '0';
                applyButton.style.zIndex = '9999999';
            }
        }, 500);
        
        // Hide button when navbar menu is open
        if (navbarToggler) {
            navbarToggler.addEventListener('click', function() {
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                
                if (!isExpanded) {
                    // Menu is being opened
                    applyButton.classList.add('hidden');
                } else {
                    // Menu is being closed
                    setTimeout(function() {
                        applyButton.classList.remove('hidden');
                    }, 300);
                }
            });
        }
        
        // Also listen for collapse/show events on the navbar
        if (navbarCollapse) {
            navbarCollapse.addEventListener('hidden.bs.collapse', function() {
                applyButton.classList.remove('hidden');
            });
            
            navbarCollapse.addEventListener('shown.bs.collapse', function() {
                applyButton.classList.add('hidden');
            });
        }
        
        // Add scroll handler to ensure button is visible
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const st = window.pageYOffset || document.documentElement.scrollTop;
            
            // Don't handle scroll events if navbar is open
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                return;
            }
            
            // Make button always visible regardless of scroll direction
            applyButton.classList.remove('hidden');
            
            lastScrollTop = st <= 0 ? 0 : st;
        }, { passive: true });
    }
    
    // Check for any modals that might interfere with the apply button
    const modals = document.querySelectorAll('.modal');
    if (modals.length > 0 && applyButton) {
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                applyButton.classList.add('hidden');
            });
            
            modal.addEventListener('hidden.bs.modal', function() {
                if (!navbarCollapse || !navbarCollapse.classList.contains('show')) {
                    applyButton.classList.remove('hidden');
                }
            });
        });
    }
}); 