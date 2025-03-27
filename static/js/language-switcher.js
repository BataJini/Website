document.addEventListener('DOMContentLoaded', function() {
    const languageSwitcher = document.getElementById('languageSwitcher');
    const currentFlag = document.getElementById('currentFlag');
    
    // Define available languages and their flags
    const languages = {
        'en': {
            flag: '/static/img/gb-flag.svg',
            name: 'English'
        },
        'pl': {
            flag: '/static/img/pl-flag.svg',
            name: 'Polski'
        }
    };

    // Get current language from localStorage or default to 'en'
    let currentLang = localStorage.getItem('language') || 'en';

    // Update flag based on current language
    function updateFlag(lang) {
        if (languages[lang]) {
            currentFlag.src = languages[lang].flag;
            currentFlag.alt = `${languages[lang].name} flag`;
        }
    }

    // Initialize flag
    updateFlag(currentLang);

    // Toggle language when button is clicked
    languageSwitcher.addEventListener('click', function() {
        // Toggle between 'en' and 'pl'
        currentLang = currentLang === 'en' ? 'pl' : 'en';
        
        // Update localStorage
        localStorage.setItem('language', currentLang);
        
        // Update flag
        updateFlag(currentLang);

        // Reload the page to apply the new language
        window.location.reload();
    });
}); 