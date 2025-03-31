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
    });
}); 