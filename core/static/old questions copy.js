document.addEventListener("DOMContentLoaded", async function() {
    const questionText = document.getElementById("question-text");
    const questionNumber = document.getElementById("question-number");
    const options = document.querySelectorAll(".option");
    const progressBar = document.querySelector(".progress-per");
    const progressIcon = document.getElementById("progress-icon"); 
    
    let currentQuestionIndex = 0;
    let questions = [];
    let totalQuestions = 0;

    // preload sounds effects
    const correctSound = new Audio("/static/sounds/correct.mp3");
    const wrongSound = new Audio("/static/sounds/wrong.mp3");


    function loadQuestion() {
        const question = questions[currentQuestionIndex];
        questionNumberElement.textContent = `Question ${currentQuestionIndex + 1}`;
        questionTextElement.textContent = question.question_text;

        optionButtons.forEach((button, index) => {
            button.querySelector('span').textContent = question.options[index];
        });

        updateProgress();
    }

    // Check the selected answer
    function checkAnswer(selectedOption) {
        const question = questions[currentQuestionIndex];
        if (selectedOption === question.correct_option) {
            score++;
            alert('Correct!');
        } else {
            alert(`Wrong! The correct answer is ${question.correct_option}.`);
        }

        // Move to the next question
        currentQuestionIndex++;
        if (currentQuestionIndex < totalQuestions) {
            loadQuestion();
        } else {
            endQuiz();
        }
    }
    
    // End the quiz
    function endQuiz() {
        alert(`Quiz over! Your score is ${score}/${totalQuestions}.`);
        // Optionally, reset the quiz or redirect to a results page
    }
    
    function updateProgress(callback) {
        let progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
        const animationDuration = "1s";
        
        progressBar.style.transition = `width ${animationDuration} ease-in-out`;
        progressBar.style.width = `${progress}%`;
        
        progressIcon.style.transition = `left ${animationDuration} ease-in-out`;
        progressIcon.style.left = `${progress}%`;
        
        let grassOverlay = document.getElementById("grass-overlay");
        grassOverlay.style.transition = `width ${animationDuration} ease-in-out`;
        grassOverlay.style.width = `${(currentQuestionIndex + 1) * 20}%`;
    
        progressBar.addEventListener("transitionend", function handleTransition() {
            progressBar.removeEventListener("transitionend", handleTransition);
            callback();
        });
    }

    loadQuestion();
});

//TEST
    // const questions = [
    //     { text: "What is the center of the solar system?", options: { A: "Earth", B: "Mars", C: "Sun", D: "Jupiter" }, correctAnswer: "C" },
    //     { text: "What is the chemical formula of water?", options: { A: "H2O", B: "CO2", C: "O2", D: "H2" }, correctAnswer: "A" },
    //     { text: "What is the highest mountain in the world?", options: { A: "K2", B: "Mount Everest", C: "Kangchenjunga", D: "Annapurna" }, correctAnswer: "B" },
    //     { text: "Who is one of the founders of Apple Inc.?", options: { A: "Bill Gates", B: "Steve Jobs", C: "Mark Zuckerberg", D: "Larry Page" }, correctAnswer: "B" },
    //     { text: "What are the first two decimal places of π (pi)?", options: { A: "3.12", B: "3.15", C: "3.14", D: "3.16" }, correctAnswer: "C" }
    // ];