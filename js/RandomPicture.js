var iconImg;
var pictures = ["haystacks", "legrandcanal", "starrynight", "sunrise", "sunsetativory", "thecliff", "womanwithaparasol", ];
var descriptions = ["Monet 1890", "Monet 1908", "Van Gogh 1889", "Monet 1872", "Guillaumin 1873", "Monet 1885", "Monet 1875", ];
var stopButton = document.getElementById('stop');

function pickImage() {
    var index = Math.floor(Math.random() * 7);
    iconImg.setAttribute("src", "../photos/" + pictures[index] + ".png");
    iconImg.setAttribute("alt", descriptions[index]);
}

function start() {
    iconImg = document.getElementById("large");
    id = setInterval(function() { pickImage(); }, 2000);
}

function stop() {
    clearInterval(id);
}
stopButton.onclick = function() {
    stop();
    clearInterval(id);
}
window.addEventListener("load", start, false);