const ARROW_POSITION_MAPPING = {
    "neutral": {
        "none": 46.25
    },
    "left": {
        "minimal": 57.18,
        "moderate": 68.11,
        "strong": 79.04,
        "extreme": 89.97,
    },
    "right": {
        "minimal": 35.29,
        "moderate": 24.36,
        "strong": 13.43,
        "extreme": 2.5,
    }
};

chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
    // Get the current tab
    let tab = tabs[0];

    // Send the request
    let response = await fetch("https://ivyhacks-skew.wl.r.appspot.com/process", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            id: `${window.location.host}_${document.title.split(" ").join("-")}`,
            text: "",
            url: tab.url
        })
    });
    let json = await response.json();

    // Set the bias
    document.getElementById("bias").innerText = json.bias;

    // Set the extent position
    let position = ARROW_POSITION_MAPPING[json.bias][json.extent];
    document.getElementById("arrow").style.left = `${position}%`;
})
