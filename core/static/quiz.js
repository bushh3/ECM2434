document.addEventListener("DOMContentLoaded", function() {
    // Hardcoded URL for the questions page
    const questionsUrl = "/questions/";  // Ensure this matches your Django URL pattern

    // Debugging: Log the URL
    console.log("questionsUrl:", questionsUrl);

    // quizpage->questionpage
    document.getElementById("start").addEventListener("click", function() {
        console.log("START button clicked");  // Debugging: Verify the event listener
        console.log("Redirecting to:", questionsUrl);  // Debugging: Log the URL
        window.location.href = questionsUrl;
    });

    // quizpage->navpage
    document.getElementById("back").addEventListener("click", function() {
        console.log("BACK button clicked");  // Debugging: Verify the event listener
        window.history.back();
    });
});