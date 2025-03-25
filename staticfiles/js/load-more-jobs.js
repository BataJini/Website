/**
 * Load More Jobs Functionality
 * Handles the AJAX loading of additional job listings when the "Load More" button is clicked
 */
document.addEventListener('DOMContentLoaded', function() {
    // Variables for infinite scrolling
    let currentPage = 1;
    let isLoading = false;
    let hasMoreJobs = false;
    
    // Get DOM elements
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const jobListingsContainer = document.getElementById('jobListingsContainer');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    
    // Check if these elements exist (we're on the job listings page)
    if (loadMoreBtn && loadingSpinner && jobListingsContainer) {
        // Get initial has more jobs value from data attribute
        hasMoreJobs = loadMoreBtn.dataset.hasMore === 'true';
        
        // Function to load more jobs
        function loadMoreJobs() {
            if (isLoading || !hasMoreJobs) return;
            
            isLoading = true;
            currentPage++;
            
            // Show loading spinner
            loadMoreBtn.classList.add('d-none');
            loadingSpinner.classList.remove('d-none');
            
            // Get current search parameters
            const searchParams = new URLSearchParams(window.location.search);
            const query = searchParams.get('q') || '';
            const location = searchParams.get('location') || '';
            const remote = searchParams.get('remote') || 'false';
            const fulltime = searchParams.get('fulltime') || 'false';
            const parttime = searchParams.get('parttime') || 'false';
            
            // Build request parameters
            const requestParams = new URLSearchParams();
            requestParams.append('page', currentPage);
            requestParams.append('q', query);
            requestParams.append('location', location);
            requestParams.append('remote', remote);
            requestParams.append('fulltime', fulltime);
            requestParams.append('parttime', parttime);
            
            // Make AJAX request
            fetch(`/ajax/load-more-jobs/?${requestParams.toString()}`)
                .then(response => response.json())
                .then(data => {
                    // Append new jobs to the container
                    jobListingsContainer.insertAdjacentHTML('beforeend', data.html);
                    
                    // Update state
                    hasMoreJobs = data.has_more;
                    isLoading = false;
                    
                    // Hide loading spinner
                    loadingSpinner.classList.add('d-none');
                    
                    // Show or hide load more button
                    if (hasMoreJobs) {
                        loadMoreBtn.classList.remove('d-none');
                    } else {
                        loadMoreContainer.classList.add('d-none');
                    }
                })
                .catch(error => {
                    console.error('Error loading more jobs:', error);
                    isLoading = false;
                    loadingSpinner.classList.add('d-none');
                    loadMoreBtn.classList.remove('d-none');
                });
        }
        
        // Add event listener to the load more button
        loadMoreBtn.addEventListener('click', loadMoreJobs);
    }
}); 