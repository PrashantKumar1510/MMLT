function translateText() {
    const text = document.getElementById("inputText").value;  // Get text from input field
    const targetLang = document.getElementById("targetLang").value;  // Get target language

    fetch("https://mmlt.onrender.com/api/translate/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            text: text,  // User's input
            target_lang: targetLang  // User-selected language
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById("outputText").innerText = data.translated_text;  // Display translation
    })
    .catch(error => console.error("Error:", error));
}

document.addEventListener("DOMContentLoaded", () => {
    const micButton = document.getElementById("mic-button");
    const inputField = document.getElementById("text-input");

    if ("webkitSpeechRecognition" in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US"; // Default language

        micButton.addEventListener("click", () => {
            recognition.start();
            micButton.innerText = "Listening...";
        });

        recognition.onresult = (event) => {
            const speechText = event.results[0][0].transcript;
            inputField.value = speechText;
            micButton.innerText = "🎤";
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event);
            micButton.innerText = "🎤";
        };
    } else {
        alert("Speech recognition not supported in this browser.");
    }
});

fetch("/api/text_to_speech/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "Hello, how are you?", lang: "en" })
})
.then(response => response.blob())
.then(blob => {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
})
.catch(error => console.error("Error:", error));
