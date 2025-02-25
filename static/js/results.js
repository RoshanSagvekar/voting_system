document.addEventListener("DOMContentLoaded", async function () {
    const electionInfo = document.getElementById("election-info");
    const winnerSection = document.getElementById("winner-section");
    const candidatesList = document.getElementById("candidates-list");
    const serverMessage = document.getElementById("server-message");
    const urlParams = new URLSearchParams(window.location.search);
    const electionId = urlParams.get("id");

    if (!electionId) {
        serverMessage.innerHTML = `<p class="text-danger">Invalid election.</p>`;
        return;
    }

    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
        window.location.href = "/login/";
        return;
    }

    async function fetchResults() {
        try {
            const response = await fetch(`/api/elections/${electionId}/results/`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${accessToken}` }
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Failed to fetch results.");

            electionInfo.innerText = `Election: ${data.election}`;

            // Winner Announcement
            if (data.winner) {
                winnerSection.innerHTML = `
                    <div class="winner-card text-center p-4">
                        <img src="${data.winner.profile_picture || '/static/images/default-avatar.png'}" class="rounded-circle mb-3" width="120" height="120">
                        <h3 class="text-success fw-bold">${data.winner.name} 🎉</h3>
                        <p><strong>Party:</strong> ${data.winner.party}</p>
                        <p><strong>Votes:</strong> ${data.winner.votes} (${data.winner.vote_percentage}%)</p>
                    </div>
                `;

                startFireworks(); // Trigger fireworks animation 🎆
            } else {
                winnerSection.innerHTML = `<p class="text-muted text-center">No winner declared yet.</p>`;
            }

            // Candidate List
            candidatesList.innerHTML = data.candidates.map(candidate => `
                <div class="col-md-4">
                    <div class="card shadow-sm p-3 text-center h-100">
                        <img src="${candidate.profile_picture || '/static/images/default-avatar.png'}" class="rounded-circle mx-auto" width="80" height="80">
                        <h5 class="mt-2">${candidate.name}</h5>
                        <p class="text-muted">${candidate.party}</p>
                        <p><strong>Votes:</strong> ${candidate.votes} (${candidate.vote_percentage}%)</p>
                    </div>
                </div>
            `).join("");

            // Chart.js for statistics 📊
            renderChart(data.candidates);
        } catch (error) {
            serverMessage.innerHTML = `<p class="text-danger">${error.message}</p>`;
        }
    }

    // Render Bar Chart
    // function renderChart(candidates) {
    //     const ctx = document.getElementById("resultsChart").getContext("2d");
    //     new Chart(ctx, {
    //         type: "bar",
    //         data: {
    //             labels: candidates.map(c => c.name),
    //             datasets: [{
    //                 label: "Votes",
    //                 data: candidates.map(c => c.votes),
    //                 backgroundColor: "rgba(54, 162, 235, 0.7)",
    //                 borderColor: "rgba(54, 162, 235, 1)",
    //                 borderWidth: 1
    //             }]
    //         },
    //         options: {
    //             responsive: true,
    //             scales: {
    //                 y: { beginAtZero: true }
    //             }
    //         }
    //     });
    // }

    function renderChart(candidates) {
        const ctx = document.getElementById("resultsChart").getContext("2d");
    
        if (window.myChart) {
            window.myChart.destroy(); // Destroy previous chart to avoid stacking issues
        }
    
        window.myChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: candidates.map(c => c.name),
                datasets: [{
                    label: "Votes",
                    data: candidates.map(c => c.votes),
                    backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
                    borderColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.5, // Adjust bar width (prevents extra-wide bars)
                    categoryPercentage: 0.6 // Keeps bars aligned and prevents stretching
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Prevents chart from stretching
                animation: { duration: 500, easing: "easeOutQuad" },
                plugins: { legend: { display: false }, tooltip: { enabled: true } },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { weight: "bold" } } },
                    y: {
                        beginAtZero: true,
                        max: Math.max(...candidates.map(c => c.votes)) + 2, // Adds padding at top
                        grid: { color: "rgba(200, 200, 200, 0.3)" },
                        ticks: { stepSize: 1, font: { weight: "bold" } }
                    }
                }
            }
        });
    }
    
    

    // Fireworks Animation 🎆
    function startFireworks() {
        const container = document.getElementById("fireworks-container");
        container.innerHTML = `<div class="fireworks"></div>`;
        setTimeout(() => { container.innerHTML = ""; }, 4000); // Auto-remove after 4s
    }

    fetchResults();
});
