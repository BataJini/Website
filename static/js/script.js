// Minimal script with no dependencies
(function() {
    'use strict';
    
    // Safely wait for DOM to be ready
    function whenReady(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }
    
    // Safely handle the navbar
    whenReady(function() {
        try {
            // First ensure the page is not stuck in a broken state
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';
            
            // Only the minimal needed functionality
            const navbar = document.querySelector('.navbar-toggler');
            const menu = document.querySelector('.navbar-collapse');
            
            if (navbar && menu) {
                // Clean up by removing all Bootstrap data attributes
                navbar.removeAttribute('data-bs-toggle');
                navbar.removeAttribute('data-bs-target');
                
                // The simplest possible event handler
                navbar.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Basic toggle with no animations or transitions
                    if (menu.classList.contains('show')) {
                        // Use transition to hide properly
                        menu.style.transform = 'translateY(100%)';
                        menu.style.opacity = '0';
                        
                        // Remove class after transition completes
                        setTimeout(function() {
                            menu.classList.remove('show');
                            navbar.setAttribute('aria-expanded', 'false');
                        }, 300);
                    } else {
                        menu.style.transform = '';
                        menu.style.opacity = '';
                        menu.classList.add('show');
                        navbar.setAttribute('aria-expanded', 'true');
                    }
                    
                    return false;
                });
                
                // Close when clicking outside
                document.addEventListener('click', function(e) {
                    if (!e.target.closest('.navbar-collapse') && 
                        !e.target.closest('.navbar-toggler') && 
                        menu.classList.contains('show')) {
                        // Use same transition as above
                        menu.style.transform = 'translateY(100%)';
                        menu.style.opacity = '0';
                        
                        setTimeout(function() {
                            menu.classList.remove('show');
                        }, 300);
                    }
                });
                
                // Handle window resize to prevent flicker at the breakpoint
                let resizeTimer;
                window.addEventListener('resize', function() {
                    clearTimeout(resizeTimer);
                    // Prevent any animation during resize
                    menu.style.transition = 'none';
                    
                    resizeTimer = setTimeout(function() {
                        // Restore transitions after resize completes
                        menu.style.transition = '';
                    }, 250);
                });
            }
            
            // Handle basic spoller functionality if needed
            const spollerButtons = document.querySelectorAll('[data-spoller] .spollers-faq__button');
            if (spollerButtons.length > 0) {
                spollerButtons.forEach(function(button) {
                    button.addEventListener('click', function() {
                        const item = this.closest('[data-spoller]');
                        if (!item) return;
                        
                        const content = item.querySelector('.spollers-faq__text');
                        if (!content) return;
                        
                        if (item.classList.contains('active')) {
                            item.classList.remove('active');
                            content.style.maxHeight = null;
                        } else {
                            item.classList.add('active');
                            content.style.maxHeight = content.scrollHeight + 'px';
                        }
                    });
                });
            }
            
            // Auto-hide any messages
            const messages = document.querySelectorAll('.message, .alert');
            if (messages.length > 0) {
                setTimeout(function() {
                    messages.forEach(function(message) {
                        message.style.opacity = '0';
                        setTimeout(function() {
                            if (message.parentNode) {
                                message.parentNode.removeChild(message);
                            }
                        }, 300);
                    });
                }, 5000);
            }
        } catch (e) {
            console.error('Error initializing: ', e);
        }
    });
})();
