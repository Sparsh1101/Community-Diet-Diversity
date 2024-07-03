let opacity = 0
let intervalID = 0
const temp = () => {
    setInterval(hide, 200)
}
const hide = () => {
    let message = document.getElementById("message")
    opacity =
        Number(window.getComputedStyle(message).getPropertyValue("opacity"))

    if (opacity > 0) {
        opacity = opacity - 0.1;
        message.style.opacity = opacity
    }
    else {
        clearInterval(intervalID)
    }
}
const display = () => {
    let message = document.getElementById("message")
    message.style.display = "none"
}
const fadeout = () => {
    let height = window.innerHeight - 60
    document.getElementById("content").style.minHeight = height.toString() + "px"
    setTimeout(temp, 20000)
    setTimeout(display, 22000)
}
window.onload = fadeout