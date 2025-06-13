async function updateVisitorCount() {
      const counterElement = document.getElementById("visitor-count");
  
      try {
        const response = await fetch("https://visitor-counter-7fsg6cnsoa-uc.a.run.app");
        const text = await response.text();
        counterElement.textContent = text;
      } catch (error) {
        counterElement.textContent = "Error loading visitor count";
        console.error("Visitor counter error:", error);
      }
    }
  
    // Call it as soon as the page loads
    window.onload = updateVisitorCount;