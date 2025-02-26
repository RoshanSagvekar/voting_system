document.addEventListener("DOMContentLoaded", async function () {
    const electionsContainer = document.getElementById("elections-container");
    const completedElectionsDiv = document.getElementById("completed-elections");

    // Get stored auth token
    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
        window.location.href = "/login/"; // Redirect if not authenticated
        return;
    }

    async function fetchElections() {
        try {
            const response = await fetch("/api/elections/", {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
            });

            if (response.status === 401) {
                // Unauthorized: Redirect user to login page
                localStorage.removeItem("access_token");
                window.location.href = "/login/";
            }

            let data = await response.json();

            if (response.ok) {
                const upcomingElections = data.upcoming_elections;
                const ongoingElections = data.ongoing_elections;
                const completedElections = data.completed_elections;

                renderElections([...upcomingElections, ...ongoingElections], electionsContainer);
                renderElections(completedElections, completedElectionsDiv, "completed");

                addVoteButtonListeners();
            } else if (response.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login/";
            } else {
                showErrorMessage();
            }
        } catch (error) {
            console.log(error);
            showErrorMessage();
        }
    }

    function showErrorMessage() {
        electionsContainer.innerHTML = `<p class='text-danger text-center'>Failed to load elections. Please try again.</p>`;
        completedElectionsDiv.innerHTML = `<p class='text-danger text-center'>Failed to load elections. Please try again.</p>`;
    }

    function renderElections(elections, container, type = "ongoing") {
        if (elections.length === 0) {
            container.innerHTML = `<p class='text-center text-muted'>No ${type === "ongoing" ? "ongoing or upcoming" : "completed"} elections at the moment.</p>`;
            return;
        }
    
        const currentDate = new Date();
    
        container.innerHTML = elections.map(election => {
            const startDate = new Date(election.start_date);
            const endDate = new Date(election.end_date);
            const hasStarted = currentDate >= startDate;
            const hasEnded = currentDate >= endDate;
    
            let buttonText = "Vote Now";
            let buttonClass = "btn-primary";
            let disabled = "";
            let message = "";
            let countdownHTML = "";
    
            if (!hasStarted) {
                buttonText = "Upcoming";
                buttonClass = "btn-secondary";
                disabled = "disabled";
                countdownHTML = `<p id="countdown-${election.id}" class="text-warning fw-bold"></p>`;
                message = `<small class="text-muted">Starts on: ${startDate.toLocaleDateString()}</small>`;
            } else if (hasEnded || election.has_voted) {
                buttonText = "View Results";
                buttonClass = "btn-success";
            }
    
            return `
                <div class="col-md-4 mb-3">
                    <div class="card shadow-sm h-100">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${election.name}</h5>
                            <p class="card-text">${hasEnded ? "Ended on" : "Ends on"}: ${endDate.toLocaleDateString()}</p>
                            ${message}
                            ${countdownHTML}
                            <button class="btn ${buttonClass} vote-btn mt-auto"
                                data-election-id="${election.id}" 
                                data-has-voted="${election.has_voted}"
                                data-election-end="${election.end_date}"
                                data-election-start="${election.start_date}"
                                ${disabled}>
                                ${buttonText}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    
        startCountdownTimers(elections);
    }
    

    function startCountdownTimers(elections) {
        elections.forEach(election => {
            const countdownElement = document.getElementById(`countdown-${election.id}`);
            if (!countdownElement) return;

            const startDate = new Date(election.start_date);
            const interval = setInterval(() => {
                const now = new Date();
                const timeDifference = startDate - now;

                if (timeDifference <= 0) {
                    clearInterval(interval);
                    countdownElement.innerHTML = `<span class="text-success">Election has started!</span>`;
                    enableVoteButton(election.id);
                    return;
                }

                const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

                countdownElement.innerHTML = `Starts in: ${days}d ${hours}h ${minutes}m ${seconds}s`;

                if (timeDifference <= 3600000) {
                    countdownElement.classList.add("blink-text");
                }
            }, 1000);
        });
    }

    function enableVoteButton(electionId) {
        const button = document.querySelector(`.vote-btn[data-election-id='${electionId}']`);
        if (button) {
            button.textContent = "Vote Now";
            button.classList.remove("btn-secondary");
            button.classList.add("btn-primary", "flash-button");
            button.removeAttribute("disabled");
        }
    }

    function addVoteButtonListeners() {
        document.querySelectorAll(".vote-btn").forEach(button => {
            button.addEventListener("click", function () {
                const electionId = this.getAttribute("data-election-id");
                const hasVoted = this.getAttribute("data-has-voted") === "true";
                const electionEndDate = new Date(this.getAttribute("data-election-end"));
                const currentDate = new Date();

                if (hasVoted || currentDate >= electionEndDate) {
                    window.location.href = `/results/?id=${electionId}`;
                } else {
                    window.location.href = `/vote/?id=${electionId}`;
                }
            });
        });
    }

    fetchElections();
});
