async function updateVisitorCount() {
    const counterElement = document.getElementById("visitor-count");

    try {
        const response = await fetch("https://visitor-counter-7fsg6cnsoa-uc.a.run.app"); // Ensure this is your correct Cloud Run URL
        const data = await response.json(); // Parses JSON response
        counterElement.textContent = "visitor count: " + data.count; // Accesses the 'count' property and adds text
    } catch (error) {
        counterElement.textContent = "Error loading visitor count";
        console.error("Visitor counter error:", error);
    }
}

// Call it as soon as the page loads
window.onload = updateVisitorCount;