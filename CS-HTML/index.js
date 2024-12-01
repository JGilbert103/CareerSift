document.addEventListener("DOMContentLoaded", () => {
    const slider = document.getElementById("sal");
    const amtDisplay = document.getElementById("amt");
    amtDisplay.textContent = "$0";
    slider.addEventListener("input", () => {
        amtDisplay.textContent = `$${slider.value}`;
    });
});