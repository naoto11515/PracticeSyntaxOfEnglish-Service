// [common] question screen element
const questionForm = document.getElementById("questionForm");
const submitButton = document.getElementById("submitButton");

// [specific] question screen element
const modal = document.getElementById("modal");
const resultMessage = document.getElementById("result-message");
const correctAnswer = document.getElementById("correct-answer");
const explanationMessage = document.getElementById("explanation-message");
const nextButton = document.getElementById("next-button");
const hint = document.getElementById("hint");

submitButton.addEventListener("click", () => {
  questionForm.classList.add("was-validated");
});

questionForm.addEventListener("submit", async (event) => {

  event.preventDefault();
  
  if (!questionForm.checkValidity()) {
    return; 
  }
  
  document.body.setAttribute('inert', 'true');
  const formData = new FormData(questionForm);

  try{
    const response = await fetch("/answer", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    nextButton.dataset.finished = result.finished;

    if (result.finished) {
      nextButton.textContent = "結果を見る";
    } else {
      nextButton.textContent = "次へ進む";
    }
    // Display the result message
    resultMessage.textContent = result.result;
    correctAnswer.textContent = result.correct_answer;
    explanationMessage.textContent = result.explanation;

    // Show the modal
    modal.style.display = "block";
  } catch(error){
    alert("通信エラーが発生しました。");
  } finally{
    document.body.removeAttribute('inert');
  }
});

function goToNext() {
  if (nextButton.dataset.finished === "true") {
    window.location.href = "/result";
  } else {
    window.location.href = "/question";
  }
}

function toggeleText() {
  hint.classList.toggle("is-visible");
}