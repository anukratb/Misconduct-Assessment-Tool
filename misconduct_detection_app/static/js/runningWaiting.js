$(document).ready(function () {
    // Set name and other global variables, Django variables for this page
    $("#title").text("Please Wait...");

    // Clear body content
    var $body = $("body");
    $body.empty();
    $body.append("<br>");

    // Create first h1 element and attach it
    $body.append("<h1 style='text-align: center'>Please wait, the detection is in progress.</h1>");
    $body.append("<br>");

    // Create second h1 element and attach it
    $body.append("<h1 style='text-align: center'>This might take some time.</h1>");
    $body.append("<br>");

    // Create the image and attach it
    $body.append("<h1 style='text-align: center'><i class='fa fa-spinner fa-spin' style='font-size:68px'></i></h1>");

    // Redirect
    window.location.replace('/select/running/');
});