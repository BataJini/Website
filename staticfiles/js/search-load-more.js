/**
 * Search Results Load More Functionality
 * This script handles the "Load More" button specifically for search results
 */
document.addEventListener('DOMContentLoaded', function() {
    // Function to initialize load more functionality for search results
    function initSearchLoadMore() {
        // Use event delegation to handle clicks on the load more button
        document.addEventListener('click', function(event) {
            // Check if the clicked element is the load more button or one of its children
            const loadMoreBtn = event.target.closest('#loadMoreBtn');
            
            if (loadMoreBtn) {
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
                    
                    // Update the button data and text
                    const currentCount = parseInt(loadMoreBtn.getAttribute('data-current')) + jobsAdded;
                    const totalCount = parseInt(loadMoreBtn.getAttribute('data-total'));
                    loadMoreBtn.setAttribute('data-current', currentCount);
                    
                    const remainingJobs = totalCount - currentCount;
                    const countBadge = loadMoreBtn.querySelector('.badge');
                    
                    if (countBadge) {
                        countBadge.textContent = remainingJobs > 0 ? `${remainingJobs} more` : 'No more jobs';
                    }
                    
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
        });
    }

    // Initialize and observe changes in the DOM
    initSearchLoadMore();

    // Create a MutationObserver to handle dynamic content loading
    const observer = new MutationObserver(function(mutations) {
        // Look for changes that might contain a newly loaded search results
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && 
                mutation.target.id === 'jobListingsContainer') {
                // Re-initialize the load more functionality
                initSearchLoadMore();
            }
        });
    });

    // Start observing the job listings container for changes
    const jobListingsContainer = document.getElementById('jobListingsContainer');
    if (jobListingsContainer) {
        observer.observe(jobListingsContainer, { 
            childList: true,
            subtree: true
        });
    }
}); 