document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));
            document.querySelectorAll(".invalid-feedback").forEach(el => el.innerText = "");
            document.getElementById("server-error").innerText = "";

            let isValid = true;

            const formFields = {
                first_name: document.getElementById("first_name"),
                last_name: document.getElementById("last_name"),
                username: document.getElementById("username"),
                email: document.getElementById("email"),
                password: document.getElementById("password"),
                confirm_password: document.getElementById("confirm_password"),
                date_of_birth: document.getElementById("date_of_birth"),
                phone_number: document.getElementById("phone_number"),
                aadhar_number: document.getElementById("aadhar_number"),
                profile_picture: document.getElementById("profile_picture")
            };

            function showError(field, message) {
                field.classList.add("is-invalid");
                field.nextElementSibling.innerText = message;
                isValid = false;
            }

            // Validate inputs (frontend validation)
            if (formFields.first_name.value.trim() === "") showError(formFields.first_name, "First name is required.");
            if (formFields.last_name.value.trim() === "") showError(formFields.last_name, "Last name is required.");
            if (formFields.username.value.trim() === "") showError(formFields.username, "Username is required.");
            if (formFields.email.value.trim() === "") showError(formFields.email, "Email is required.");
            if (formFields.date_of_birth.value.trim() === "") showError(formFields.date_of_birth, "Date of birth is required.");
            if (formFields.aadhar_number.value.trim() === "") showError(formFields.aadhar_number, "Aadhaar number is required.");
            if (formFields.password.value.trim().length < 6) showError(formFields.password, "Password must be at least 6 characters.");
            if (formFields.confirm_password.value.trim() !== formFields.password.value.trim()) showError(formFields.confirm_password, "Passwords do not match.");

            // Age validation (must be 18+)
            const dob = new Date(formFields.date_of_birth.value);
            const today = new Date();
            const age = today.getFullYear() - dob.getFullYear();
            if (age < 18) showError(formFields.date_of_birth, "You must be at least 18 years old to register.");

            // Stop form submission if frontend validation fails
            if (!isValid) return;

            // Create FormData object for API request
            const formData = new FormData();
            Object.keys(formFields).forEach(key => {
                if (formFields[key].type === "file" && formFields[key].files[0]) {
                    formData.append(key, formFields[key].files[0]);
                } else {
                    formData.append(key, formFields[key].value.trim());
                }
            });

            try {
                const response = await fetch("/api/register/", { method: "POST", body: formData });
                const data = await response.json();
                if (response.ok) {
                    showToast("Registration successful! Please check your email.");
                    setTimeout(() => {
                        window.location.href = "/login/";
                    }, 2000);
                } else {
                    Object.keys(data.errors || {}).forEach(key => showError(formFields[key], data.errors[key][0]));
                }
            } catch (error) {
                document.getElementById("server-error").innerText = "An error occurred. Please try again.";
            }
        });
    }
});
