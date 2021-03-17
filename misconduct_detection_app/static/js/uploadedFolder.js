pageName = "Uploaded Folder Files";

function getExtension(filepath) {
    // Return the final extension of a file if any
    let lastDot = filepath.lastIndexOf(".");
    if (lastDot === -1) {
        return "";
    } else {
        return filepath.slice(lastDot + 1);
    }
}

function appendLinksToFile(elementId, extension = "") {
    // Append the links to a file from the folder path list in the given element
    folderPathList.forEach(filePath => {
        if (extension === "" || getExtension(filePath) === extension) {
            // same extension
            $(elementId).append($("<a></a>").attr({
                "href": "/examine/folders/" + filePath.substring(filePath.indexOf("folder") + 8),
                "target": "_blank",
            }).text(filePath.substring(filePath.indexOf("folder") + 8)));
            $(elementId).append("<br>");
        }
    });

}

// Show all the files uploaded
appendLinksToFile("#filesList");

// Show the submissions to be compared
// based on the same extension as the given submission

let filename = fileToComparePathList[0];
appendLinksToFile("#filesToBeComparedList", getExtension(filename));

