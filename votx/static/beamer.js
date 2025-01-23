
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

    ws.onclose = function (event) {
        console.log("Websocket closed, trying to reconnect in 10 seconds.")
        console.log(event.reason)
        setTimeout(function () {
            openWebSocket()
        }, 10000);
    }

    ws.onerror = function (err) {
        console.error('Websocket error: ', err.message, 'Closing socket');
        ws.close();
    };

    ws.onmessage = async function (event) {
        const message = JSON.parse(event.data)
        console.log(message)

        if (message.type == "SETVOTE") {
            document.getElementById("mainContainer").style.opacity = 0
            await sleep(1000)
            setVoteCount(message.data.vote_count)
            setVoteTitle(message.data.vote_title, false)
            setVoteOptions(message.data.vote_options)
            hideStatistics()
            document.getElementById("mainContainer").style.opacity = 1
        }

        if (message.type == "SETVOTECOUNT") {
            setVoteCount(message.data)
        }

        if (message.type == "SETRESULT") {
            if (document.getElementById("voteTitle").textContent != message.data.vote_title) {
                document.getElementById("mainContainer").style.opacity = 0
                await sleep(1000)
                setVoteTitle(message.data.vote_title, false)
                setVoteCount(message.data.vote_count)
                setVoteOptions(message.data.vote_options)
                document.getElementById("mainContainer").style.opacity = 1
            }
            setVoteCount(message.data.vote_count)
            setStatistics(message.data.vote_options)
            showStatistics()

        }

        if (message.type == "SETTEXT") {
            await setText(message.data)
        }
    };
}


async function setText(text) {
    if (text.toLowerCase() == "votx") {
        if (!document.getElementById("voteTitle").hidden) {
            document.getElementById("mainContainer").style.opacity = 0
            await sleep(1000)
            document.getElementById("voteTitle").hidden = true
            document.getElementById("voteOptionsElement").hidden = true
            document.getElementById("mainContainer").style.opacity = 1
            document.getElementById("voteCountElement").hidden = true
            document.getElementById("voteTitle").value = text
            document.getElementById("votxLogo").hidden = false
        }
        hideStatistics()
    } else {
        document.getElementById("mainContainer").style.opacity = 0
        await sleep(1000)
        await setVoteTitle(text, false)
        hideStatistics()
        document.getElementById("voteOptionsElement").hidden = true
        document.getElementById("mainContainer").style.opacity = 1
        document.getElementById("voteCountElement").hidden = true
    }
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

async function setVoteTitle(title, animate = true) {
    const element = document.getElementById("voteTitle")
    element.textContent = title
    if (element.hidden) {
        if (animate){
            document.getElementById("mainContainer").style.opacity = 0
            await sleep(1000)
        }
        
        element.hidden = false
        document.getElementById("votxLogo").hidden = true

        if (animate) {
            document.getElementById("mainContainer").style.opacity = 1
        }
    }

}

function setVoteCount(count) {
    if (!document.getElementById("voteOptionsElement").hidden){
        document.getElementById("voteCountElement").hidden = false
    }
    document.getElementById("voteCount").textContent = count
}

function hideStatistics() {
    document.querySelector(".gridContainer").classList.add("notransition")
    document.querySelector(".gridContainer").classList.add("grid-hidecolumns")
    document.querySelector(".gridContainer").offsetHeight;
    document.querySelector(".gridContainer").classList.remove("notransition")
}

function showStatistics() {
    document.querySelector(".gridContainer").classList.remove("grid-hidecolumns")
    document.querySelector(".gridContainer").offsetHeight;
}