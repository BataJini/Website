document.addEventListener('DOMContentLoaded', function() {
    // Get all footer search links
    const footerSearchLinks = document.querySelectorAll('.footer-search-link');

    footerSearchLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the search tag from the data attribute
            const searchTag = this.getAttribute('data-search-tag');
            
            // Create the search URL - using the home URL which has the search functionality
            const searchUrl = `/?q=${encodeURIComponent(searchTag)}`;
            
            // Redirect to the search page
            window.location.href = searchUrl;
        });
    });
}); 