/**
 * Load More Jobs Functionality
 * This script handles the "Load More" button for job listings
 */

// Function to initialize load more functionality
function initLoadMore() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    if (loadMoreBtn) {
        // Remove existing event listeners to prevent duplicates
        loadMoreBtn.removeEventListener('click', handleLoadMore);
        // Add fresh event listener
        loadMoreBtn.addEventListener('click', handleLoadMore);
    }
}

// Handler function for the load more button click
function handleLoadMore() {
    // Get the hidden job listings container
    const hiddenJobs = document.querySelector('.hidden-job-listings');
    const jobListingsWrapper = document.querySelector('.job-listings-wrapper');
    
    if (hiddenJobs && jobListingsWrapper) {
        // Move the first batch of hidden jobs to the visible container
        const jobsToShow = hiddenJobs.querySelectorAll('.job-listing');
        const batchSize = 25; // Number of jobs to load at once
        let jobsAdded = 0;
        
        // Add additional jobs
        jobsToShow.forEach((job, index) => {
            if (index < batchSize) {
                jobListingsWrapper.appendChild(job);
                jobsAdded++;
            }
        });
        
        // Update the button data
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        const currentCount = parseInt(loadMoreBtn.getAttribute('data-current')) + jobsAdded;
        const totalCount = parseInt(loadMoreBtn.getAttribute('data-total'));
        loadMoreBtn.setAttribute('data-current', currentCount);
        
        const remainingJobs = totalCount - currentCount;
        
        // Hide the button if no more jobs to load
        if (remainingJobs <= 0) {
            loadMoreBtn.parentElement.style.display = 'none';
        }
        
        // Animation for smooth appearance
        const newlyAddedJobs = Array.from(jobListingsWrapper.querySelectorAll('.job-listing')).slice(-jobsAdded);
        newlyAddedJobs.forEach((job, index) => {
            job.style.opacity = '0';
            job.style.transform = 'translateY(20px)';
            setTimeout(() => {
                job.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                job.style.opacity = '1';
                job.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }
}

// Initialize on DOM content loaded (first page load)
document.addEventListener('DOMContentLoaded', initLoadMore);

// Create a MutationObserver to detect when job listings are updated via AJAX
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Check if any added node contains our load more button
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1 && (
                    node.querySelector('#loadMoreBtn') || 
                    node.id === 'loadMoreBtn'
                )) {
                    // Initialize load more functionality
                    initLoadMore();
                }
            });
        }
    });
});

// Start observing after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const jobListingsContainer = document.getElementById('jobListingsContainer');
    if (jobListingsContainer) {
        observer.observe(jobListingsContainer, {
            childList: true,
            subtree: true
        });
    }
}); 