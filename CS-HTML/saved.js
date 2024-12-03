document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll(".card #choice");
    const compareBtn = document.querySelector(".compareBtn");

    const updateButtonState = () => {
        
        const checkedCount = Array.from(checkboxes).filter(checkbox => checkbox.checked).length;
        if (checkedCount === 2) {
            compareBtn.classList.remove("no");
            compareBtn.setAttribute("href", "compare.html");
            compareBtn.style.cursor = "pointer";
            compareBtn.style.pointerEvents = "auto"; // Enable the button.
        } else {
            compareBtn.classList.add("no");
            compareBtn.style.cursor = "not-allowed";
            compareBtn.setAttribute("href", "");
            compareBtn.style.pointerEvents = "none"; // Disable the button.
        }
    };

    // Initialize button state
    updateButtonState();

    // Add event listeners to checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateButtonState);
    });
});