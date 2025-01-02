
document.addEventListener("DOMContentLoaded", function () {
    openWebSocket()
})

function sleep(ms) {
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
            if (document.getElementById("voteTitle").textContent != message.data.voteTitle) {
                document.getElementById("mainContainer").style.opacity = 0
                await sleep(1000)
                setVoteTitle(message.data.voteTitle)
                setVoteOptions(message.data.voteOptions)
                document.getElementById("mainContainer").style.opacity = 1
            }
            setVoteCount(message.data.voteCount)
            setStatistics(message.data.voteOptions)
            showStatistics()

        }

        if (message.type == "BLANK") {
            document.getElementById("mainContainer").style.opacity = 0
        }
    };
}

function setVoteOptions(voteOptions) {
    document.getElementById("voteOptionsElement").hidden = false
    const optionList = document.getElementById("voteOptions")
    const optionGraph = document.getElementById("voteOptionsGraph")
    optionList.innerHTML = ''
    for (const voteOption of voteOptions) {
        const li = document.createElement('li');
        li.innerText = voteOption.title
        optionList.appendChild(li)
    }
}

function setStatistics(voteOptions) {
    const optionGraph = document.getElementById("voteOptionsGraph")
    optionGraph.innerHTML = ''

    for (const voteOption of voteOptions) {
        const g_li_k = document.createElement('li')
        g_li_k.innerText = voteOption.title
        g_li_k.classList.add("name")
        optionGraph.appendChild(g_li_k)

        const g_li_v = document.createElement('li')
        const value_span = document.createElement("span")
        value_span.innerText = voteOption.votes
        g_li_v.appendChild(value_span)
        g_li_v.classList.add("value")
        g_li_v.style = "grid-column-end: span " + (voteOption.votes +1)
        optionGraph.appendChild(g_li_v)
    }
}

function setVoteTitle(title) {
    document.getElementById("voteTitle").textContent = title
}

function setVoteCount(count) {
    document.getElementById("voteCountElement").hidden = false
    document.getElementById("voteCount").textContent = count
}

function hideStatistics() {
    document.querySelector(".gridContainer").classList.add("notransition")
    document.querySelector(".gridContainer").classList.add("grid-hidecolumns")
    document.querySelector(".gridContainer").offsetHeight;
    document.querySelector(".gridContainer").classList.remove("notransition")
}

function showStatistics() {
    //document.querySelector(".gridContainer").classList.add("notransition")
    document.querySelector(".gridContainer").classList.remove("grid-hidecolumns")
    document.querySelector(".gridContainer").offsetHeight;
    //document.querySelector(".gridContainer").classList.remove("notransition")
}