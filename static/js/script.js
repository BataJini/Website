(function() {
    // Defensive wrapper to prevent global scope pollution
    'use strict';

    // Utility function to safely add event listeners
    function safeAddEventListener(selectors, event, handler) {
        if (typeof selectors === 'string') {
            selectors = [selectors];
        }
        
        selectors.forEach(function(selector) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(function(element) {
                element.addEventListener(event, handler);
            });
        });
    }

    // DOM ready function
    function domReady(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }

    domReady(() => {
        // Mobile menu toggle functionality
        const toggleMenu = function() {
            document.body.classList.toggle('menu-open');
            document.documentElement.classList.toggle('menu-open');
        };

        // Menu toggle event handlers
        safeAddEventListener([
            ".icon-menu",
            "#mobileMenuToggle",
            ".navbar-toggler"
        ], "click", function(event) {
            event.preventDefault();
            toggleMenu();
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (document.body.classList.contains('menu-open') && 
                !e.target.closest('.menu__body') && 
                !e.target.closest('.navbar-toggler') && 
                !e.target.closest('.icon-menu') &&
                !e.target.closest('#mobileMenuToggle')) {
                toggleMenu();
            }
        });
        
        // Handle mobile dropdown menus
        safeAddEventListener('.navbar-collapse .dropdown-toggle', 'click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                e.stopPropagation();
                
                const parent = this.closest('.dropdown');
                const menu = parent.querySelector('.dropdown-menu');
                
                // Toggle the clicked dropdown
                if (menu.classList.contains('show')) {
                    menu.classList.remove('show');
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    // Close other open dropdowns
                    document.querySelectorAll('.navbar-collapse .dropdown-menu.show').forEach(function(openMenu) {
                        openMenu.classList.remove('show');
                        openMenu.previousElementSibling.setAttribute('aria-expanded', 'false');
                    });
                    
                    // Open this dropdown
                    menu.classList.add('show');
                    this.setAttribute('aria-expanded', 'true');
                }
            }
        });
        
        // Handle clicks on dropdown items
        safeAddEventListener('.navbar-collapse .dropdown-item', 'click', function(e) {
            if (window.innerWidth <= 768) {
                const menu = this.closest('.dropdown-menu');
                if (menu) {
                    menu.classList.remove('show');
                    const toggle = menu.previousElementSibling;
                    if (toggle) {
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                }
            }
        });
        
        // Close dropdowns when clicking outside in mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && !e.target.closest('.dropdown')) {
                document.querySelectorAll('.navbar-collapse .dropdown-menu.show').forEach(function(menu) {
                    menu.classList.remove('show');
                    const toggle = menu.previousElementSibling;
                    if (toggle) {
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        });

        // Spoller buttons with additional error checking
        try {
            const spollerButtons = document.querySelectorAll("[data-spoller] .spollers-faq__button");
            spollerButtons.forEach((button) => {
                button.addEventListener("click", function () {
                    try {
                        const currentItem = button.closest("[data-spoller]");
                        const content = currentItem.querySelector(".spollers-faq__text");

                        const parent = currentItem.parentNode;
                        const isOneSpoller = parent.hasAttribute("data-one-spoller");

                        if (isOneSpoller) {
                            const allItems = parent.querySelectorAll("[data-spoller]");
                            allItems.forEach((item) => {
                                if (item !== currentItem) {
                                    const otherContent = item.querySelector(".spollers-faq__text");
                                    item.classList.remove("active");
                                    otherContent.style.maxHeight = null;
                                }
                            });
                        }

                        if (currentItem.classList.contains("active")) {
                            currentItem.classList.remove("active");
                            content.style.maxHeight = null;
                        } else {
                            currentItem.classList.add("active");
                            content.style.maxHeight = content.scrollHeight + "px";
                        }
                    } catch (error) {
                        console.error("Spoller button error:", error);
                    }
                });
            });
        } catch (error) {
            console.error("Spoller initialization error:", error);
        }

        // Auto-hide messages
        try {
            const messages = document.querySelectorAll('.message, .alert');
            if (messages.length > 0) {
                setTimeout(function() {
                    messages.forEach(message => {
                        message.style.opacity = '0';
                        setTimeout(() => {
                            if (message.parentNode) {
                                message.parentNode.removeChild(message);
                            }
                        }, 300);
                    });
                }, 5000);
            }
        } catch (error) {
            console.error("Message auto-hide error:", error);
        }

        // Form input validation
        try {
            const formInputs = document.querySelectorAll('.form-group input, .form-control');
            formInputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.value.trim() !== '') {
                        this.classList.add('has-value');
                    } else {
                        this.classList.remove('has-value');
                    }
                });
            });
        } catch (error) {
            console.error("Form input validation error:", error);
        }

        // Job search form
        try {
            const searchForm = document.querySelector('.search-form');
            if (searchForm) {
                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();

                    // Safely get form values
                    const getInputValue = (selector) => {
                        const input = this.querySelector(selector);
                        return input ? input.value : '';
                    };
                    const getCheckboxValue = (selector) => {
                        const checkbox = this.querySelector(selector);
                        return checkbox ? checkbox.checked : false;
                    };

                    const keyword = getInputValue('input[name="q"]');
                    const location = getInputValue('input[name="location"]');
                    const isRemote = getCheckboxValue('input[name="remote"]');
                    const isFullTime = getCheckboxValue('input[name="fulltime"]');
                    const isPartTime = getCheckboxValue('input[name="parttime"]');

                    const params = new URLSearchParams();
                    if (keyword) params.append('q', keyword);
                    if (location) params.append('location', location);
                    if (isRemote) params.append('remote', '1');
                    if (isFullTime) params.append('fulltime', '1');
                    if (isPartTime) params.append('parttime', '1');

                    window.location.href = `/jobs?${params.toString()}`;
                });
            }
        } catch (error) {
            console.error("Job search form error:", error);
        }

        // Smooth scroll for anchor links
        try {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const targetSelector = this.getAttribute('href');
                    const target = document.querySelector(targetSelector);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            });
        } catch (error) {
            console.error("Smooth scroll error:", error);
        }

        // Animate on scroll
        try {
            const animateOnScroll = function() {
                const elements = document.querySelectorAll('.animate-on-scroll');
                elements.forEach(element => {
                    const elementPosition = element.getBoundingClientRect().top;
                    const windowHeight = window.innerHeight;
                    if (elementPosition < windowHeight - 100) {
                        element.classList.add('animated');
                    }
                });
            };

            window.addEventListener('scroll', animateOnScroll);
            animateOnScroll(); // Run once on page load
        } catch (error) {
            console.error("Animate on scroll error:", error);
        }
    });
})();
