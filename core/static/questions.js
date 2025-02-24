document.addEventListener('DOMContentLoaded', () => {
    const questionNumber = document.getElementById('question-number');
    const questionText = document.getElementById('question-text');
    const optionButtons = document.querySelectorAll('.option');
    const progressBar = document.querySelector('.progress-per');
    const progressIcon = document.getElementById('progress-icon');

    let currentQuestionIndex = 0;
    let score = 0;
    const totalQuestions = questions.length;

    // Load the current question
    function loadQuestion() {
        const question = questions[currentQuestionIndex];
        questionNumber.textContent = `Question ${currentQuestionIndex + 1}`;
        questionText.textContent = question.question_text;

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

    // Update the progress bar
    function updateProgress() {
        const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
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

    // End the quiz
    function endQuiz() {
        window.location.href = '/quiz-results/';
    }

    // Add event listeners to option buttons
    optionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedOption = button.getAttribute('data-option');
            checkAnswer(selectedOption);
        });
    });

    // Load the first question
    loadQuestion();
});