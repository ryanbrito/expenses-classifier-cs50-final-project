document.addEventListener("DOMContentLoaded", function() {
    /*Hides overlay of the page*/
    document.getElementById("theOverlay").style.display = "none";
    
})

// Loading screen appears when upload button is clicked;
function loadingScreen () {
    document.getElementById("theOverlay").style.display = "inline";
}

function submitCategoryChange () {
    var selectMenusQuantity = document.getElementsByTagName('tr').length - 1;
    alert(selectMenusQuantity)

    var selected = [];

    for (let i = 1; i <= selectMenusQuantity; i++){
        for (var option of document.getElementById(i.toString()).options)
        {
            if (option.selected) {
                selected.push(option.value);
            }
        }
    }
    

    data = {"category" : selected}

    const options = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    fetch("/dashboard/edit", options)
}