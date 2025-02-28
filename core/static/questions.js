document.addEventListener('DOMContentLoaded', () => {
    const questionNumber = document.getElementById('question-number');
    const questionText = document.getElementById('question-text');
    const optionButtons = document.querySelectorAll('.option');
    const progressBar = document.querySelector('.progress-per');
    const progressIcon = document.getElementById('progress-icon');

    let userAnswers = [];
    let currentQuestionIndex = 0;
    let finished = 0;
    const totalQuestions = 5;//how many questions once a time, can be changed

    // Load the current question
    function loadQuestion() {
        const question = questions[currentQuestionIndex];//random questions No.
        questionNumber.textContent = `Question ${currentQuestionIndex + 1 }`;
        questionText.textContent = question.question_text;

        optionButtons.forEach((button, index) => {
            button.querySelector('span').textContent = question.options[index];
        });
        updateProgress();
    }

    // Check the selected answer
    function checkAnswer(selectedOption, button) {
        const question = questions[currentQuestionIndex];
        userAnswers.push({
            id: question.id,
            answer: selectedOption
        });
        finished++;
        if (selectedOption === question.correct_option) {
            button.classList.add("correct");
            correctSound.play();
        } else {
            button.classList.add("wrong");
            wrongSound.play();
            //will show correct answer if you wrong
            optionButtons.forEach(btn => {
                if (btn.getAttribute("data-option") === question.correct_option) {
                    btn.classList.add("correct");
                }
            });
        }
        // Move to the next question
        setTimeout(() => {
        
            optionButtons.forEach(btn => {
                btn.classList.remove("correct", "wrong");
            });
    
            currentQuestionIndex++;////////////////////////////////////////////////
            if (currentQuestionIndex < totalQuestions) {
                loadQuestion();
            } else {
                updateProgress(endQuiz);
            }
        }, 1000);
    }
    
    // Update the progress bar
    function updateProgress(callback) {
        const progress = (finished / totalQuestions) * 100;
        const animationDuration = "1s";
        progressBar.style.transition = `width ${animationDuration} ease-in-out`;
        progressBar.style.width = `${progress}%`;
        
        progressIcon.style.transition = `left ${animationDuration} ease-in-out`;
        progressIcon.style.left = `${progress}%`;
        
        let grassOverlay = document.getElementById("grass-overlay");
        grassOverlay.style.transition = `width ${animationDuration} ease-in-out`;
        grassOverlay.style.width = `${progress}%`;
        
        progressBar.addEventListener("transitionend", function handleTransition() {
            progressBar.removeEventListener("transitionend", handleTransition);
            if(callback){
                callback();
            }
        });
    }

    // End the quiz (send user's answer to backend to compute score)(need modify)
    window.endQuiz = function() {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/check-answer/';

        //CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'csrfmiddlewaretoken';
        tokenInput.value = csrfToken;
        form.appendChild(tokenInput);

        userAnswers.forEach((item, index) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            // question_1, question_2... 
            input.name = `question_${index + 1}`;
            input.value = item.answer;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    }

    // Add event listeners to option buttons
    optionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedOption = button.getAttribute('data-option');
            checkAnswer(selectedOption, button);
        });
    });

    // Load the first question
    loadQuestion();
});