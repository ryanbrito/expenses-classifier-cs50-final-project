document.addEventListener("DOMContentLoaded", function() {
    inform = document.getElementById("inform")
    if (inform != null){
        closeinform = sessionStorage.getItem("closeInform")
        if (closeinform){
            inform.style.display = "none";
        }
    }

    /*Hides overlay of the page*/
    document.getElementById("theOverlay").style.display = "none";
    
})




// Loading screen appears when upload button is clicked;
function loadingScreen () {
    document.getElementById("theOverlay").style.display = "inline";
}

// Submits all category changes requests the user wants:
function submitCategoryChange () {
    var selectMenusQuantity = document.getElementsByTagName('tr').length - 1;

    // Holds all the users required category changes
    var changes = [];

    // Iterates over each expense select menu, to get the changes in each one:
    for (let i = 1; i <= selectMenusQuantity; i++){
        var currentSelect = document.getElementById((i.toString()));
        for (var option of currentSelect.options)
        {
            var oldCategory = currentSelect.getAttribute("data-oldCategory");
            var newCategory = option.value;
            if (option.selected && newCategory != oldCategory) {
                var expenseId = currentSelect.id;

                changes.push(
                    {
                        "expenseId" : expenseId,
                        "oldCategory" : oldCategory,
                        "newCategory" : newCategory
                    }
                );

            }
        }
    }

    titleDash = document.getElementById("titleDash")
    tableName = titleDash.getAttribute("data-tableName")

    var data = {"Changes" : [tableName, changes]}

    const options = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    fetch("/dashboard/edit", options)
    location.reload()
}

function submitCategoryEdit(){
    var categoryEdit = document.getElementById("inputName").getAttribute("data-Oldcategory");
    var newCategoryName = document.getElementById("newCategoryName").value;
    var newKeywords = document.getElementById("textarea").value;

    var data = [
        {"categoryEdit": categoryEdit},
        {"newCategoryName" : newCategoryName},
        {"newKeywords" : newKeywords}
    ]

    const options = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    fetch("/categoryEdition", options)

    setTimeout(function(){
        location.replace("/categories")
    }, 10)
}


function deleteKeyword(keyword){
    var oldCategory = document.getElementById("inputName").getAttribute("data-Oldcategory");
    var data = [{"deleteKeyword" : keyword}, {"oldCategory":oldCategory}]
    const options = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    fetch("/categoryEdition", options)

    setTimeout(function(){
        location.reload()
    }, 1)
   
}


function closeInform(){
    sessionStorage.setItem("closeInform", "closed")
    document.getElementById("inform").style.display = "none";
}

function keywordAlert(){
    alert("A keyword with the same name as the category can't be deleted.")
}