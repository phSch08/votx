
let voteCards = []
let vcCounter = 0
var ws
var message
let ballots = {}


document.addEventListener("DOMContentLoaded", function () {
    voteCards = document.getElementsByClassName("voteCard")
    updateBallots(initialBallots)
    openWebSocket()
})

function openWebSocket(reconnect = false) {
    let socketProtocol = "wss://"
    if (window.location.protocol === 'http:') {
        socketProtocol = "ws://"
    }
    ws = new WebSocket(new URL("vote/ws", socketProtocol + window.location.host))
    ws.onmessage = function (event) {
        const message = JSON.parse(event.data)
        console.log(message)

        if (message.type == "BALLOTS") {
            updateBallots(message.data)
        }
    };

    ws.onopen = function () {
        if (reconnect) {
            console.log("Websocket reestablished...")
            ws.send(`{"type": "GETBALLOTS"}`)
        } 
    }

    ws.onclose = function (event) {
        console.log("Websocket closed, trying to reconnect in 20 seconds.")
        console.log(event.reason)
        setTimeout(function () {
            openWebSocket(true)
        }, 20000);
    }

    ws.onerror = function (err) {
        console.error('Websocket error: ', err.message, 'Closing socket');
        ws.close();
    };

}

function closeModal() {
    const modal = document.getElementById("voteDialog")
    const { documentElement: html } = document;

    html.classList.add("modal-is-closing");
    setTimeout(() => {
        html.classList.remove("modal-is-closing", "modal-is-open");
        modal.close()
        document.getElementById("voteInProgress").hidden = false
        document.getElementById("voteSuccessfull").hidden = true
        document.getElementById("voteFailed").hidden = true
        document.getElementById("voteSecret").type = "password"
    }, 400);

}

function vote(content) {
    const custom_id = window.crypto.randomUUID().split("-").at(-1).toUpperCase()
    const modal = document.getElementById("voteDialog")
    const { documentElement: html } = document;

    document.getElementById("voteSecret").value = custom_id
    html.classList.add("modal-is-open", "modal-is-opening");
    setTimeout(() => {
        html.classList.remove("modal-is-opening");
    }, 400);
    modal.showModal()

    fetch("submit/", {
        method: "POST",
        body: JSON.stringify({
            ballot_id: +content.querySelector(".formVoteId").value,
            votes: [...content.querySelectorAll(
                ".voteOptions input[type=radio]:checked,\
                .voteOptions input[type=checkbox]:checked"
            )].map(el => +el.value),
            custom_id
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(async (res) => res.json())
        .then((res) => {
            if (res.ballots) {
                updateBallots(res.ballots)
            }

            if (res.success) {
                document.getElementById("voteInProgress").hidden = true
                document.getElementById("voteSuccessfull").hidden = false
                document.getElementById("voteFailed").hidden = true
            } else {
                document.getElementById("voteInProgress").hidden = true
                document.getElementById("voteSuccessfull").hidden = true
                document.getElementById("voteFailed").hidden = false
            }
        })
}

function toggleCard(voteCardId) {
    let voteCard = document.getElementById(voteCardId)

    for (const child of voteCard.childNodes) {
        if (child.tagName == "DIV" && child.classList.contains("voteCardContent")) {
            child.classList.toggle("hiddenContent")
        }
    }
}

function updateBallots(ballotUpdate) {
    const ballotList = document.getElementById("voteList")
    for (const ballot of ballotUpdate) {
        if (!(ballot.id in ballots)) {
            const ballotItem = getVoteCard(
                ballot.id,
                ballot.title,
                ballot.vote_options,
                ballot.minimum_votes,
                ballot.maximum_votes,
                ballot.vote_stacking,
                ballot.voted ? "Gewählt" : "Wahl ausstehend")

            ballots[ballot.id] = ballotItem.children[0].id
            ballotList.appendChild(ballotItem)
        }

        const ballotCard = document.getElementById(ballots[ballot.id])
        if (ballot.voted != ballotCard.classList.contains("voteCardSuccess")) {
            ballotCard.classList.toggle("voteCardSuccess")
            ballotCard.querySelector(".voteState").textContent = ballot.voted ? "Gewählt" : "Wahl ausstehend"
        }
    }

    for (const ballotId of Object.keys(ballots)) {
        if (!ballotUpdate.find(ballot => ballot.id == ballotId)) {
            document.getElementById(ballots[ballotId]).remove()
            delete ballots[ballotId]
        }
    }
}

function getVoteCard(voteId, voteTitle, voteOptions, minVotes, maxVotes, accumulation, state) {
    const template = document.getElementById("voteCardTemplate")
    const clone = template.content.cloneNode(true);
    clone.getElementById("voteCardTemplateDiv").id = "vc" + ++vcCounter
    clone.querySelector(".voteCardTitle").textContent = voteTitle
    clone.querySelector(".voteCount").textContent = (minVotes == maxVotes) ? `${maxVotes}` : `${minVotes} - ${maxVotes}`
    clone.querySelector(".voteAccumulation").textContent = accumulation ? "Ja" : "Nein"
    clone.querySelector(".voteState").textContent = state
    clone.querySelector(".formVoteId").value = voteId

    for (const option of voteOptions.sort((a, b) => { return a.option_index - b.option_index })) {
        const voteOption = document.createElement("label")
        const input = document.createElement("input")
        if (maxVotes == 1) {
            input.type = "radio"
        } else {
            input.type = "checkbox"
        }

        input.name = "vc" + vcCounter
        input.value = option.option_id
        voteOption.appendChild(input)
        voteOption.appendChild(document.createTextNode(option.option_title))

        clone.querySelector(".voteOptions").appendChild(voteOption)
    }
    return clone
}

function toggleVoteSecretVisibility() {
    secret = document.getElementById("voteSecret")
    if (secret.type === "password") {
        secret.type = "text"
    } else {
        secret.type = "password"
    }
}