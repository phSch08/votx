
let voteCards = []
let vcCounter = 0
var ws
var message
let ballots = {}


document.addEventListener("DOMContentLoaded", function () {
    voteCards = document.getElementsByClassName("voteCard")
    openWebSocket()
})

function openWebSocket() {
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

        if (message.type == "AUTHENTICATED") {
            sendMessage(`{"type": "GETBALLOTS"}`)
        }

        if (message.type == "VOTERESULT") {
            if (message.data.success) {
                document.getElementById("voteInProgress").hidden = true
                document.getElementById("voteSuccessfull").hidden = false
                document.getElementById("voteFailed").hidden = true
            } else {
                document.getElementById("voteInProgress").hidden = true
                document.getElementById("voteSuccessfull").hidden = true
                document.getElementById("voteFailed").hidden = false
            }
        }
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

function sendMessage(content) {
    console.log(content)
    ws.send(content)
}

function vote(content) {
    const customId = window.crypto.randomUUID().split("-").at(-1).toUpperCase()
    const modal = document.getElementById("voteDialog")
    const { documentElement: html } = document;

    document.getElementById("voteSecret").value = customId
    html.classList.add("modal-is-open", "modal-is-opening");
    setTimeout(() => {
        html.classList.remove("modal-is-opening");
    }, 400);
    modal.showModal()

    sendMessage(JSON.stringify({
        type: 'VOTE',
        data: {
            ballotId: +content.querySelector(".formVoteId").value,
            votes: [...document.querySelectorAll(
                ".voteOptions input[type=radio]:checked,\
                .voteOptions input[type=checkbox]:checked"
            )].map(el => +el.value),
            customId
        }
    }))
}

function toggleCard(voteCardId) {
    let voteCard = document.getElementById(voteCardId)

    for (const child of voteCard.childNodes) {
        if (child.tagName == "DIV" && child.classList.contains("voteCardContent")) {
            child.classList.toggle("hiddenContent")
        }
    }
}

function fetchBallotToken(ballotId) {
    return "TOKEN"
}

function updateBallots(ballotUpdate) {
    const ballotList = document.getElementById("voteList")
    for (const ballot of ballotUpdate) {
        if (!(ballot.id in ballots)) {
            const ballotItem = getVoteCard(
                ballot.id,
                ballot.title,
                ballot.voteOptions,
                ballot.minimumVotes,
                ballot.maximumVotes,
                ballot.voteStacking,
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

    for (const option of voteOptions.sort((a, b) => { return a.optionIndex - b.optionIndex })) {
        const voteOption = document.createElement("label")
        const input = document.createElement("input")
        if (maxVotes == 1) {
            input.type = "radio"
        } else {
            input.type = "checkbox"
        }
            
        input.name = "vc" + vcCounter
        input.value = option.optionId
        voteOption.appendChild(input)
        voteOption.appendChild(document.createTextNode(option.optionTitle))

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