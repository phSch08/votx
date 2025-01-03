
function generateRegistrationTokens() {
    const newCodes = +document.getElementById("accessCodeAddCount").value
    fetch("registrationTokens/", {
        method: "POST",
        body: JSON.stringify({
            amount: newCodes,
            voteGroups: [...document.getElementsByName("access_code_group_checkbox")].filter(cb => cb.checked).map(cb => cb.value),
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => { location.reload() }
    )
}

function resetRegistrationTokens(){
    const input = document.getElementById("resetTokenInput")
    fetch("registrationToken/reset", {
        method: "POST",
        body: JSON.stringify({
            token: input.value
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => { input.value = ""})
}

function getTokenPDF() {
    const pdfURL = new URL("registrationTokens", window.location.href)
    window.open(pdfURL.href)
}

function getBallotProtocol(ballotId) {
    const pdfURL = new URL(`ballot/${ballotId}/protocol`, window.location.href)
    window.open(pdfURL.href)
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
            voteStacking: false,
            voteOptions: [],
            voteGroups: [],
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
            voteGroups: [...document.getElementsByName("vote_group_checkbox")].filter(cb => cb.checked).map(cb => cb.value),
            active: false
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => location.reload())
}

function createNewVoteGroup() {
    fetch("votegroup/", {
        method: "POST",
        body: JSON.stringify({ title: document.getElementById("newVoteGroupTitleInput").value }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => location.reload())
}

function deleteVoteGroup(id) {
    fetch("votegroup/", {
        method: "DELETE",
        body: JSON.stringify({ id }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((res) => location.reload())
}

function textToBeamer() {
    fetch("beamer/text", {
        method: "POST",
        body: JSON.stringify({ text: document.getElementById("beamer_text").value }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}

function changeDangerMode(checkbox) {
    let params = new URLSearchParams(location.search)
    params.set('danger', checkbox.checked)
    window.location.search = params.toString()
}