// Set name and other global variables, Django variables for this page
pageName = "Upload";

let uploadFileFinish = false;
let uploadFolderFinish = false;

function setFileDetectionPackage() {
    $.ajax({
        url: '/select/autoDetect/',
        type: "GET",
        dataType: "json",
        success: function (autoDetectResults) {
            let autoDetectionLibSelection = autoDetectResults[0][0];
            let autoDetectionLanguage = autoDetectResults[1];
            if (autoDetectResults === "FILE_TYPE_NOT_SUPPORTED") {
                $("#languageSelectionModal").modal("show");
                autoDetectionLibSelection = "JPlag";
                autoDetectionLanguage = "text";
            }

            let programmingConfigs = new FormData();
            programmingConfigs.append("csrfmiddlewaretoken", document.getElementsByName('csrfmiddlewaretoken')[0].value);
            programmingConfigs.append("detectionLibSelection", autoDetectionLibSelection);
            programmingConfigs.append("detectionLanguage", autoDetectionLanguage);
            if(detectionThreshold){
                // Previous value
                programmingConfigs.append("detectionThreshold", detectionThreshold);
            }else{
                // Default value
                programmingConfigs.append("detectionThreshold", 80);
            }

            $.ajax({
                url: "/configs/savingConfigs/",
                type: 'POST',
                cache: false,
                data: programmingConfigs,
                processData: false,
                contentType: false,
                dataType: "json",
                beforeSend: function () {
                    uploading = true;
                },
                success: function (data) {
                    uploading = false;
                }
            });
            let $detectionLibSelection = $("#detectionLibSelection");
            $detectionLibSelection.empty();
            let button = createButtonWithIcon("settings", autoDetectionLibSelection + " : " + autoDetectionLanguage, false);
            button.addClass("text-primary"); // Add the link colour to match the other buttons
            $detectionLibSelection.append(button);
        }
    });
}

$("#changeDetectionLib").on("click", function () {
    $("#languageSelectionModal").modal("hide");
    $("#programmingLanguageChoosingModal").modal("show");
});

// Update the bottom bar from the context processor
// (Xin implemented the bottom bar to be updated using the context processor and used to not update until selecting next)
function updateBottomBar() {
    $.ajax({
        url: "/upload/updateContext/",
        type: 'GET',
        cache: false,
        success: function (data) {
            //console.log(data);
            let context = data;
            fileToComparePathList = context["fileToComparePathList"];
            resultsPathList = context["resultsPathList"];
            folderPathList = context["folderPathList"];
            segmentsPathList = context["segmentsPathList"];
            detectionLibList = context["detectionLibList"];
            configsList = context["configsList"];

            loadUploadedComparingFile();
            loadUploadedFolder();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.warn("Error updating bottom bar");
        }
    });
}

function modifyDOMAfterUploadingFile() {
    uploadFileFinish = true;
    openNextButton();
    $("#uploadFileLabel").text("Reupload");
    updateBottomBar();
}

function modifyDOMAfterUploadingFolder() {
    uploadFolderFinish = true;
    openNextButton();
    $("#uploadFolderLabel").text("Reupload");
    updateBottomBar();
}

var isFileIncluded;

function checkFileIncluded() {
    // Check if the uploaded file is included in the uploaded folder
    $.ajax({
        url: "checkIncluded/",
        type: 'GET',
        cache: false,
        success: function (data) {
            isFileIncluded = data;
            updateSubmissionsCount();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.warn("Error checking if file included in folder");
        }
    });
}

function updateSubmissionsCount() {
    if (isFileIncluded === "Yes") {
        $("#fileIncludedCheck").html("(Uploaded file <i>included</i> in the folder)")
    } else if (isFileIncluded === "No") {
        $("#fileIncludedCheck").html("(Uploaded file <i>not included</i> in the folder)")
    }
}

function fileUploaded() {
    modifyDOMAfterUploadingFile();
    $("#uploadFileCheck").empty();
    $("#uploadFileCheck").append("<i class='material-icons'>check</i> File uploaded.");
    checkFileIncluded();
}

function folderUploaded() {
    modifyDOMAfterUploadingFolder();
    $("#uploadFolderCheck").empty();
    $("#uploadFolderCheck").append("<i class='material-icons'>check</i> Folder uploaded. <i>" + numberOfSubmissions + " submissions</i>");
    checkFileIncluded();
}

function uploadFile() {
    let singleFile = new FormData($('#uploadFileForm')[0]);
    $("#uploadFileCheck").html("<i class='fa fa-spinner fa-spin'></i> Please wait while uploading...");

    $.ajax({
        url: "uploadFile/",
        type: 'POST',
        cache: false,
        data: singleFile,
        processData: false,
        contentType: false,
        beforeSend: function(){
            uploading = true;
        },
        success: function (data) {
            uploading = false;
            setFileDetectionPackage();
            fileUploaded();

        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.warn("Error sending the file");
            alert("Error: file not uploaded");
            //alert(xhr.status);
            //alert(thrownError);
            $("#uploadFileCheck").html('<i class="material-icons">block</i>There was an error while uploading the file');
        }
    });

}

function uploadFolder() {
    let folderFile = new FormData();
    $("#fileIncludedCheck").empty();
    $("#uploadFolderCheck").html("<i class='fa fa-spinner fa-spin'></i> Please wait while uploading...");

    for (let value of $('#uploadFolderInput')[0].files) {
        folderFile.append("file", value, value.webkitRelativePath);
    }
    folderFile.append("csrfmiddlewaretoken", document.getElementsByName('csrfmiddlewaretoken')[0].value);

    $.ajax({
        url: "uploadFolder/",
        type: 'POST',
        cache: false,
        data: folderFile,
        processData: false,
        contentType: false,
        dataType:"json",
        beforeSend: function(){
            uploading = true;
        },
        success : function(data) {
            uploading = false;
            numberOfSubmissions = data;
            folderUploaded();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.warn("Error sending the file");
            alert("Error: folder not uploaded");
            $("#uploadFolderCheck").html('<i class="material-icons">block</i>There was an error while uploading the folder');
        }
    });

}

function openNextButton() {
    if (uploadFileFinish && uploadFolderFinish && numberOfSubmissions > 0) {
        document.getElementById("nextButton").removeAttribute("disabled");
    } else {
        // Disable the next button
        document.getElementById("nextButton").setAttribute("disabled", "");
    }
}

$("#uploadFileForm").change(function (){
    uploadFile();
 });

$("#uploadFolderForm").change(function (){
    uploadFolder();
});

$(document).ready(function () {
    if (fileToComparePathList != "NOFOLDEREXISTS") {
        modifyDOMAfterUploadingFile();
        fileUploaded();
    }

    if (folderPathList[0] != "NOFOLDEREXISTS") {
        modifyDOMAfterUploadingFolder();
        folderUploaded();
    }
    openNextButton();
    console.log('document.ready()')
});
