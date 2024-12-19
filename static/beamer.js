
document.addEventListener("DOMContentLoaded", function () {
    openWebSocket()
})

function sleep(ms){
    return new Promise(r => setTimeout(r, ms));
} 

function openWebSocket() {
    var loc = window.location, ws_location;
    if (loc.protocol === "https:") {
        ws_location = "wss://";
    } else {
        ws_location = "ws://";
    }
    ws_location += loc.host + loc.pathname + "ws";

    ws = new WebSocket(ws_location);
    ws.onmessage = async function (event) {
        const message = JSON.parse(event.data)
        console.log(message)

        if (message.type == "SETVOTE") {
            document.getElementById("mainContainer").style.opacity = 0
            await sleep(1000)
            setVoteCount(message.data.voteCount)
            setVoteTitle(message.data.voteTitle)
            setVoteOptions(message.data.voteOptions)
            hideStatistics()
            document.getElementById("mainContainer").style.opacity = 1
        }

        if (message.type == "SETVOTECOUNT") {
            setVoteCount(message.data)
        }

        if (message.type == "SETRESULT") {
            
        }

        if (message.type == "BLANK") {
            document.getElementById("mainContainer").style.opacity = 0
        }
    };
}

function setVoteOptions(voteOptions) {
    const optionList = document.getElementById("voteOptions")
    optionList.innerHTML = ''
    for (const voteOption of voteOptions) {
        const li = document.createElement('li');
        li.innerText = voteOption
        optionList.appendChild(li)
    }
}

function setVoteTitle(title) {
    document.getElementById("voteTitle").textContent = title
}

function setVoteCount(count) {
    document.getElementById("voteCount").textContent = count
}

function hideStatistics() {
    document.querySelector(".gridContainer").classList.add("notransition")
    document.querySelector(".gridContainer").classList.add("grid-hidecolumns")
    document.querySelector(".gridContainer").offsetHeight;
    document.querySelector(".gridContainer").classList.remove("notransition")
}