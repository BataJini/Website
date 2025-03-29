// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = themeToggle.querySelector('.bi-moon-stars');
    const sunIcon = document.createElement('i');
    sunIcon.className = 'bi bi-sun';
    themeToggle.appendChild(sunIcon);

    // Get the current theme from localStorage or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);

    // Update icon visibility based on current theme
    function updateIcons(theme) {
        if (theme === 'dark') {
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'block';
        } else {
            moonIcon.style.display = 'block';
            sunIcon.style.display = 'none';
        }
        
        // For mobile theme toggle, keep the same icon behavior
        const mobileThemeToggle = document.getElementById('mobileThemeToggle');
        if (mobileThemeToggle) {
            const mobileMoonIcon = mobileThemeToggle.querySelector('.bi-moon-stars');
            const mobileSunIcon = mobileThemeToggle.querySelector('.bi-sun');
            
            if (theme === 'dark') {
                mobileMoonIcon.style.display = 'none';
                mobileSunIcon.style.display = 'block';
            } else {
                mobileMoonIcon.style.display = 'block';
                mobileSunIcon.style.display = 'none';
            }
        }
    }

    // Initialize icons
    updateIcons(currentTheme);

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcons(newTheme);
        
        // Ensure mobile menu continues to use dark mode styles regardless of theme
        applyMobileMenuDarkMode();
    });
    
    // Function to apply dark mode styles to mobile menu regardless of current theme
    function applyMobileMenuDarkMode() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse) {
            // Always apply dark mode styles to the mobile menu
            navbarCollapse.style.background = 'linear-gradient(135deg, rgba(5, 15, 30, 0.98) 0%, rgba(10, 25, 45, 0.98) 100%)';
            navbarCollapse.style.color = '#E9ECEF';
            navbarCollapse.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            
            // Ensure links are properly styled
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.style.color = 'rgba(255, 255, 255, 0.85)';
            });
            
            // Ensure auth headers are properly styled
            const authHeaders = navbarCollapse.querySelectorAll('.mobile-auth-header');
            authHeaders.forEach(header => {
                header.style.color = '#9BA1A6';
            });
            
            // Ensure list items are properly styled
            const listItems = navbarCollapse.querySelectorAll('.mobile-auth-list li');
            listItems.forEach(item => {
                item.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                const link = item.querySelector('a');
                if (link) {
                    link.style.background = 'rgba(255, 255, 255, 0.05)';
                    link.style.color = '#E9ECEF';
                }
            });
        }
    }
    
    // Apply mobile menu dark mode on page load
    applyMobileMenuDarkMode();
    
    // Also apply when mobile menu is opened
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            setTimeout(applyMobileMenuDarkMode, 50); // slight delay to ensure menu is visible
        });
    }
}); 