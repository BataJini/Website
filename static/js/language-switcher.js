document.addEventListener('DOMContentLoaded', function() {
    const languageForm = document.getElementById('language-form');
    
    if (languageForm) {
        // Handle dropdown item clicks
        const dropdownItems = languageForm.querySelectorAll('.dropdown-item');
        
        dropdownItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                
                const formData = new FormData(languageForm);
                formData.set('language', this.value); // Set the selected language
                
                fetch(languageForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Get the current path and strip any language prefix
                        const path = window.location.pathname;
                        const newLang = this.value;
                        
                        // Force reload to the new language URL
                        const newPath = path.replace(/^\/(en|pl)/, '');
                        window.location.href = `/${newLang}${newPath}`;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    }
}); 