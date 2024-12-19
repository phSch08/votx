
function generateRegistrationTokens() {
    const newCodes = +document.getElementById("accessCodeAddCount").value
    fetch("registrationTokens/", {
        method: "POST",
        body: JSON.stringify({
            amount: newCodes
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => { location.reload() }
    )
}

function activateBallot(ballotId) {
    fetch(`ballot/${ballotId}/activate`, {
        method: "POST",
    }).then((res) => { location.reload() }
    )
}

function deactivateBallot(ballotId) {
    fetch(`ballot/${ballotId}/deactivate`, {
        method: "POST",
    }).then((res) => { location.reload() }
    )
}

function focusBallot(ballotId) {
    fetch(`ballot/${ballotId}/focus`, {
        method: "POST",
    })
}

function showBallotResult(ballotId) {
    fetch(`ballot/${ballotId}/result`, {
        method: "POST",
    }).then((res) => { location.reload() }
    )
}

function addVoteOption() {
    const voteOptionList = document.getElementById("vote_option_list")
    const voteOption = document.getElementById("voteOptionTemplate").content.cloneNode(true)
    voteOptionList.appendChild(voteOption)
}

function removeVoteOption() {
    [...document.getElementById("vote_option_list").children].pop().remove()
}

function createBallot() {
    fetch("ballot/", {
        method: "POST",
        body: JSON.stringify({
            title: "Neue Wahl",
            maximumVotes: 1,
            minimumVotes: 1,
            voteStacking: true,
            voteOptions: [],
            active: false
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(async (res) => res.text())
        .then((id) => window.location.replace(`?ballot=${id}`))
}

function updateBallot() {
    fetch("ballot/", {
        method: "POST",
        body: JSON.stringify({
            id: document.getElementsByName("ballot_id")[0].value,
            title: document.getElementsByName("ballot_title")[0].value,
            maximumVotes: document.getElementsByName("ballot_max_votes")[0].value,
            minimumVotes: document.getElementsByName("ballot_min_votes")[0].value,
            voteStacking: document.getElementsByName("ballot_vote_stacking")[0].value == "true",
            voteOptions: [...document.getElementsByName("ballot_vote_option")].map(option => option.value),
            active: false
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => location.reload())
}