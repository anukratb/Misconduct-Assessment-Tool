$(document).ready(function() {
    $("#layoutHeader").text(pageName);
    $("#title").text(pageName + " • " + toolName);
    $("#layoutToolName").html(toolName.italics());
});
