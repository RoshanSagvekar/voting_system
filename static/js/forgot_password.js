document.addEventListener("DOMContentLoaded", function () {
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");

    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            // Clear previous errors
            document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));
            document.querySelectorAll(".invalid-feedback").forEach(el => el.innerText = "");
            document.getElementById("server-error").innerText = "";

            let isValid = true;
            const email = document.getElementById("email");

            function showError(field, message) {
                field.classList.add("is-invalid");
                field.nextElementSibling.innerText = message;
                isValid = false;
            }

            // Validate input
            if (email.value.trim() === "") {
                showError(email, "Please enter your registered email address.");
            } else if (!/^\S+@\S+\.\S+$/.test(email.value.trim())) {
                showError(email, "Please enter a valid email address (e.g., user@example.com).");
            }

            if (!isValid) return;

            try {
                const response = await fetch("/api/password-reset/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email.value.trim() }),
                });

                const data = await response.json();
                if (response.ok) {
                    showToast("A password reset link has been sent to your email.");
                    setTimeout(() => {
                    }, 2000);
                    forgotPasswordForm.reset();
                } else {
                    document.getElementById("server-error").innerText =
                        data.message || "Error sending reset link. Please try again.";
                }
            } catch (error) {
                document.getElementById("server-error").innerText =
                    "An unexpected error occurred. Please try again later.";
            }
        });
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const resetPasswordForm = document.getElementById("resetPasswordForm");

    if (resetPasswordForm) {
        resetPasswordForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            // Clear previous errors
            document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));
            document.querySelectorAll(".invalid-feedback").forEach(el => el.innerText = "");
            document.getElementById("server-error").innerText = "";

            let isValid = true;
            const password = document.getElementById("password");
            const confirmPassword = document.getElementById("confirm-password");

            function showError(field, message) {
                field.classList.add("is-invalid");
                field.nextElementSibling.innerText = message;
                isValid = false;
            }

            // Validate password fields
            if (password.value.trim() === "") {
                showError(password, "Password is required.");
            } else if (password.value.length < 6) {
                showError(password, "Password must be at least 6 characters.");
            }

            if (confirmPassword.value.trim() === "") {
                showError(confirmPassword, "Please confirm your password.");
            } else if (password.value !== confirmPassword.value) {
                showError(confirmPassword, "Passwords do not match.");
            }

            if (!isValid) return;

            // Get UID and token from the URL
            const urlParts = window.location.pathname.split("/");
            const uidb64 = urlParts[urlParts.length - 2];
            const token = urlParts[urlParts.length - 1];
            console.log(urlParts);
            console.log(uidb64);
            console.log(token);
            try {
                const response = await fetch(`/api/password-reset-confirm/${uidb64}/${token}/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        password: password.value.trim(),
                        confirm_password: confirmPassword.value.trim(),
                    }),
                });

                const data = await response.json();
                if (response.ok) {
                    showToast("Your password has been reset successfully! You can now log in.");
                    setTimeout(() => {
                        window.location.href = "/login/";
                    }, 2000);
                } else {
                    document.getElementById("server-error").innerText =
                        data.message || "Failed to reset password. Please try again.";
                }
            } catch (error) {
                document.getElementById("server-error").innerText =
                    "An unexpected error occurred. Please try again later.";
            }
        });
    }
});
