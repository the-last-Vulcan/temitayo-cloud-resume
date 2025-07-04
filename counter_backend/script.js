document.addEventListener('DOMContentLoaded', function() {
    // Fetches and displays visitor count on page load
    async function updateVisitorCount() {
        const counterElement = document.getElementById("visitor-count");

        try {
            // API call to Cloud Run service to get visitor count
            const response = await fetch("https://visitor-counter-7fsg6cnsoa-uc.a.run.app");
            const data = await response.json(); // Parses JSON response

            // Updates the counter text. Assumes API returns 'count' property.
            counterElement.textContent = "visitor count: " + data.count;
        } catch (error) {
            // Displays error if API call fails
            counterElement.textContent = "Error loading visitor count";
            console.error("Visitor counter error:", error);
        }
    }

    // Initialize visitor count when DOM is ready
    updateVisitorCount();

    // Scroll to Visitor Count Button Logic
    const scrollToCountBtn = document.getElementById('scrollToCountBtn');
    const visitorCountSection = document.getElementById('visitor-count-section');

    // Attaches click listener if both button and target section exist
    if (scrollToCountBtn && visitorCountSection) {
        scrollToCountBtn.addEventListener('click', function() {
            // Smoothly scrolls to the visitor count section
            visitorCountSection.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        });
    }
});