
let voteCards = []
let vcCounter = 0
var ws
var message
let ballots = {}


document.addEventListener("DOMContentLoaded", function() {
    voteCards = document.getElementsByClassName("voteCard")
    openWebSocket()
})

function openWebSocket() {
    ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = function (event) {
        const message = JSON.parse(event.data)
        console.log(message)

        if (message.type == "BALLOTS") {
            updateBallots(message.data)
        }

        if (message.type == "AUTHENTICATED") {
            sendMessage(`{"type": "GETBALLOTS", "data": "${accessCode}"}`)
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

    ws.onopen = () => sendMessage(`{"type": "AUTHENTICATE", "data": "${accessCode}"}`)
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
      }, 400);
    
}

function sendMessage(content) {
    console.log(content)
    ws.send(content)
}

function vote(content) {
    const modal = document.getElementById("voteDialog")
    const { documentElement: html } = document;

    html.classList.add("modal-is-open", "modal-is-opening");
    setTimeout(() => {
        html.classList.remove("modal-is-opening");
      }, 400);
    modal.showModal()

    sendMessage(JSON.stringify({
        type: 'VOTE', 
        data: {
            accessCode,
            ballotId: +content.querySelector(".formVoteId").value,
            votes: [+content.querySelector(".voteOptions input[type=radio]:checked").value]
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
                ballot.alreadyVoted ? "Gewählt" : "Wahl ausstehend")
            
            ballots[ballot.id] = ballotItem.children[0].id
            ballotList.appendChild(ballotItem)
        }

        ballotCard = document.getElementById(ballots[ballot.id])
        if (ballot.alreadyVoted != ballotCard.classList.contains("voteCardSuccess")) {
            ballotCard.classList.toggle("voteCardSuccess")
            ballotCard.querySelector(".voteState").textContent = ballot.alreadyVoted ? "Gewählt" : "Wahl ausstehend"
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

    for (let i = 0; i < voteOptions.length; i++) {
        const voteOption = document.createElement("label")
        const input = document.createElement("input")
        input.type = "radio"
        input.name = "vc" + vcCounter
        input.value = voteOptions[i].optionId
        voteOption.appendChild(input)
        voteOption.appendChild(document.createTextNode(voteOptions[i].optionTitle))

        clone.querySelector(".voteOptions").appendChild(voteOption)
    }
    return clone
}