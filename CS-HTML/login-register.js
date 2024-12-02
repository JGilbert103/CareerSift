document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector(".login");
    const registerForm = document.querySelector(".register");
    const loginButton = document.getElementById("show-login");
    const registerButton = document.getElementById("show-register");
    const emailCheckbox = document.getElementById("email-checkbox");
    const emailField = document.getElementById("register-email");
    const emailLabel = document.getElementById("email-label");
    emailField.classList.add("hidden");

    // Function to toggle between Login and Register forms
    const toggleForms = (showLogin) => {
        if (showLogin) {
            loginForm.classList.remove("hidden");
            registerForm.classList.add("hidden");
            loginButton.classList.add("active");
            registerButton.classList.remove("active");
        } else {
            loginForm.classList.add("hidden");
            registerForm.classList.remove("hidden");
            loginButton.classList.remove("active");
            registerButton.classList.add("active");
        }
    };

    // Event listeners for the toggle buttons
    loginButton.addEventListener("click", () => toggleForms(true));
    registerButton.addEventListener("click", () => toggleForms(false));

    // Show/hide the email field based on the checkbox state
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