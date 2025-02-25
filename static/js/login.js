document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            // Clear previous errors
            document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));
            document.querySelectorAll(".invalid-feedback").forEach(el => el.innerText = "");
            document.getElementById("server-error").innerText = "";

            let isValid = true;

            const email = document.getElementById("email");
            const password = document.getElementById("password");

            function showError(field, message) {
                field.classList.add("is-invalid");
                field.nextElementSibling.innerText = message;
                isValid = false;
            }

            // Validate inputs
            if (email.value.trim() === "") {
                showError(email, "Please enter your registered email address.");
            } else if (!/^\S+@\S+\.\S+$/.test(email.value.trim())) {
                showError(email, "Please enter a valid email address (e.g., user@example.com).");
            }

            if (password.value.trim() === "") {
                showError(password, "Please enter your password.");
            } else if (password.value.trim().length < 6) {
                showError(password, "Your password must be at least 6 characters long.");
            }

            if (!isValid) return;

            // Create request body
            const requestBody = {
                email: email.value.trim(),
                password: password.value.trim(),
            };

            try {
                const response = await fetch("/api/login/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(requestBody),
                });

                const data = await response.json();
                if (response.ok) {
                    showToast("Login successful! Redirecting to your dashboard...");
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("refresh_token", data.refresh_token);
                    setTimeout(() => {
                        window.location.href = "/dashboard/";
                    }, 2000);
                } else {
                    if (data.errors) {
                        if (data.errors.email) showError(email, "No account found with this email.");
                        if (data.errors.password) showError(password, "Incorrect password. Try again.");
                    } else {
                        document.getElementById("server-error").innerText =
                            data.message || "Login failed. Please check your credentials and try again.";
                    }
                }
            } catch (error) {
                document.getElementById("server-error").innerText =
                    "An unexpected error occurred. Please try again later.";
            }
        });
    }
});
