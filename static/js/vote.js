document.addEventListener("DOMContentLoaded", async function () {
    const electionInfo = document.getElementById("election-info");
    const candidatesList = document.getElementById("candidates-list");
    const voteForm = document.getElementById("voteForm");
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

    // Fetch election details and candidates
    async function fetchElectionDetails() {
        try {
            const response = await fetch(`/api/elections/${electionId}/candidates/`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${accessToken}` }
            });

            if (response.status === 401) {
                // Unauthorized: Redirect user to login page
                localStorage.removeItem("access_token");
                window.location.href = "/login/";
            }
    
            let data = await response.json();
            if (!response.ok) throw new Error(data.message || "Failed to fetch candidates.");
    
            electionInfo.innerText = `Election: ${data.election_name}`;
    
            // Handle empty candidates array
            if (!data.candidates || data.candidates.length === 0) {
                candidatesList.innerHTML = `
                    <div class="alert alert-warning text-center w-100">
                        <strong>No candidates available for this election.</strong><br>
                        Candidates may not have been added or registered yet.
                    </div>
                `;
                const submit_vote = document.getElementById("submit-vote");
                if (submit_vote) submit_vote.style.display = "none"; // Hide Vote button
                return;
            }
    
            candidatesList.innerHTML = data.candidates.map(candidate => {
                const candidateName = candidate.name || "Unknown Candidate";
                const partyName = candidate.party || "Independent";
                const profilePicture = candidate.profile_picture || "/static/images/default-avatar.jpg";
    
                return `
                    <div class="col-md-4">
                        <div class="card shadow-lg p-3 mb-4 text-center h-100">
                            <img src="${profilePicture}" class="card-img-top rounded-circle mx-auto border border-dark" alt="${candidateName}" style="width: 100px; height: 100px; object-fit: cover;">
                            <div class="card-body">
                                <h5 class="card-title">${candidateName}</h5>
                                <p class="card-text"><strong>${partyName}</strong></p>
                                <input type="radio" name="candidate" value="${candidate.id}" id="candidate-${candidate.id}">
                                <label class="btn btn-outline-primary w-100 mt-2" for="candidate-${candidate.id}">Select</label>
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
        } catch (error) {
            serverMessage.innerHTML = `<p class="text-danger">${error.message}</p>`;
        }
    }
    

    fetchElectionDetails();
});


// Submit Vote
document.addEventListener("DOMContentLoaded", async function () {
    const voteForm = document.getElementById("voteForm");
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

    voteForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const selectedCandidate = document.querySelector("input[name='candidate']:checked");

        if (!selectedCandidate) {
            showErrorToast('Please select a candidate')
            return;
        }

        try {
            const response = await fetch(`/api/elections/${electionId}/vote/`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ candidate_id: selectedCandidate.value })
            });

            if (response.status === 401) {
                // Unauthorized: Redirect user to login page
                localStorage.removeItem("access_token");
                window.location.href = "/login/";
            }
            const data = await response.json();

            if (response.ok) {
                // Show success message
                showToast(data.message)
                setTimeout(() => window.location.href = "/dashboard/", 2000);
            } else {
                // Handle errors properly
                if (data.error) {
                    serverMessage.innerHTML = `<p class="text-danger">${data.error}</p>`;
                } else {
                    serverMessage.innerHTML = `<p class="text-danger">An unknown error occurred. Please try again.</p>`;
                }
            }
        } catch (error) {
            serverMessage.innerHTML = `<p class="text-danger">A network error occurred. Please check your connection and try again.</p>`;
        }
    });
});
