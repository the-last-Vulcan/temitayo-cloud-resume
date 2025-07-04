document.addEventListener('DOMContentLoaded', function() {
    // Your existing updateVisitorCount function, now inside DOMContentLoaded
    async function updateVisitorCount() {
        const counterElement = document.getElementById("visitor-count");

        try {
            // This is where your API call for incrementing and getting the count would go.
            // Based on your initial description, you likely make a POST to increment,
            // and the response might contain the new count, or you make a subsequent GET.
            // Let's assume for now your current fetch() gets the *current* count after some server-side increment.

            // If your server increments on every GET, this might be enough:
            const response = await fetch("https://visitor-counter-7fsg6cnsoa-uc.a.run.app"); // Your correct Cloud Run URL
            const data = await response.json(); // Parses JSON response

            // Ensure your API returns 'count' property. If it's 'visits', change data.count to data.visits
            counterElement.textContent = "visitor count: " + data.count;
        } catch (error) {
            counterElement.textContent = "Error loading visitor count";
            console.error("Visitor counter error:", error);
        }
    }

    // Call updateVisitorCount as soon as the DOM is ready
    updateVisitorCount();

    // NEW: Scroll to Count Button Logic
    const scrollToCountBtn = document.getElementById('scrollToCountBtn');
    const visitorCountSection = document.getElementById('visitor-count-section'); // This ID must be added to your HTML!

    // Check if the elements exist before adding event listeners
    if (scrollToCountBtn && visitorCountSection) {
        scrollToCountBtn.addEventListener('click', function() {
            visitorCountSection.scrollIntoView({
                behavior: 'smooth', // For a smooth scrolling animation
                block: 'center'     // Aligns the target element to the center of the viewport
            });
        });
    }
});