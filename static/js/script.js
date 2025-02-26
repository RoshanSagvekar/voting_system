document.addEventListener("DOMContentLoaded", function () {
    const accessToken = localStorage.getItem("access_token");

    const navHome = document.getElementById("navHome");
    const navRegister = document.getElementById("navRegister");
    const navLogin = document.getElementById("navLogin");
    const navDashboard = document.getElementById("navDashboard");
    const navLogout = document.getElementById("navLogout");

    if (accessToken) {
        navDashboard.classList.remove("d-none");
        navLogout.classList.remove("d-none");
        navHome.classList.add("d-none");
        navRegister.classList.add("d-none");
        navLogin.classList.add("d-none");
    } else {
        navDashboard.classList.add("d-none");
        navLogout.classList.add("d-none");
        navHome.classList.remove("d-none");
        navRegister.classList.remove("d-none");
        navLogin.classList.remove("d-none");
    }

    if (navLogout) {
        navLogout.addEventListener("click", function (e) {
            e.preventDefault();
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login/";
        });
    }

    
});

function showToast(message) {
    const toastElement = new bootstrap.Toast(document.getElementById("toastSuccess"));
    document.getElementById("toastSuccessContent").innerText = message;
    toastElement.show();
}

function showErrorToast(message) {
    const toastElement = new bootstrap.Toast(document.getElementById("toastError"));
    document.getElementById("toastErrorContent").innerText = message;
    toastElement.show();
}

