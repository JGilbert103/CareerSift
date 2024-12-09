/*
ABOUT
Author: Adam Kerns
For: ITSC 3155, Software Engineering, Fall 2024
Project: Final Project - Group 9, "CareerSift"
*/

document.addEventListener("DOMContentLoaded", () => {
    const emailCheckbox = document.getElementById("email-checkbox");
    const emailField = document.getElementById("register-email");
    const emailLabel = document.getElementById("email-label");
    emailField.classList.add("hidden");
    emailLabel.classList.add("hidden")

    emailCheckbox.addEventListener("change", () => {
        if (emailCheckbox.checked) {
            emailField.classList.remove("hidden");
            emailLabel.classList.remove("hidden");
        } else {
            emailField.classList.add("hidden");
            emailLabel.classList.add("hidden");
        }
    });
});