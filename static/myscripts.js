document.addEventListener("DOMContentLoaded", function() {
    /*Hides overlay of the page*/
    document.getElementById("theOverlay").style.display = "none";
    
})

// Loading screen appears when upload button is clicked;
function loadingScreen () {
    document.getElementById("theOverlay").style.display = "inline";
}