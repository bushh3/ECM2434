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


    // fetch questions
    async function fetchQuestions() {
        try {
            const response = await fetch('/api/questions/');
            questions = await response.text();  
            totalQuestions = questions.length;
            loadQuestion();
        } catch (error) {
            questionText.textContent = "Failed to load the question. Please refresh the page and try again.";
        }
    }

    function loadQuestion() {
        if (currentQuestionIndex >= totalQuestions) {
            return;
        }

        let question = questions[currentQuestionIndex];
        questionText.textContent = question.text;
        questionNumber.textContent = `Question ${currentQuestionIndex + 1}`;

        options.forEach((button, index) => {
            const optionKey = ["A", "B", "C", "D"][index];
            button.innerHTML = `${optionKey}. ${question.options[optionKey]}`;
            button.classList.remove("correct", "wrong");
            button.disabled = false;
            button.onclick = () => checkAnswer(button, optionKey);
        });
    }

    async function checkAnswer(button, selectedOption) {
        options.forEach(btn => btn.disabled = true);

        try {
            //  FormData 
            const formData = new FormData();
            formData.append('option', selectedOption);
            
            const response = await fetch('/api/check-answer/', {
                method: 'POST',
                body: formData
            });

            const result = await response.text(); 
            
            if (result === 'correct') {
                button.classList.add("correct");
                correctSound.play();
            } else {
                button.classList.add("wrong");
                wrongSound.play();
                const correctAnswer = result.split('-')[1];  
                const correctButton = document.querySelector(`[data-option="${correctAnswer}"]`);
                if (correctButton) {
                    correctButton.classList.add("correct");
                }
            }

            updateProgress(() => {
                if (currentQuestionIndex + 1 < totalQuestions) {
                    setTimeout(() => {
                        currentQuestionIndex++;
                        loadQuestion();
                    }, 300);
                } else {
                    setTimeout(() => {
                        window.location.href = "/quiz/result/";
                    }, 600);
                }
            });

        } catch (error) {
            console.error('Failed to submit the answer:', error);
        }
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

    fetchQuestions();
});

//TEST
    // const questions = [
    //     { text: "What is the center of the solar system?", options: { A: "Earth", B: "Mars", C: "Sun", D: "Jupiter" }, correctAnswer: "C" },
    //     { text: "What is the chemical formula of water?", options: { A: "H2O", B: "CO2", C: "O2", D: "H2" }, correctAnswer: "A" },
    //     { text: "What is the highest mountain in the world?", options: { A: "K2", B: "Mount Everest", C: "Kangchenjunga", D: "Annapurna" }, correctAnswer: "B" },
    //     { text: "Who is one of the founders of Apple Inc.?", options: { A: "Bill Gates", B: "Steve Jobs", C: "Mark Zuckerberg", D: "Larry Page" }, correctAnswer: "B" },
    //     { text: "What are the first two decimal places of π (pi)?", options: { A: "3.12", B: "3.15", C: "3.14", D: "3.16" }, correctAnswer: "C" }
    // ];