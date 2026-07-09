// start button click event handler
const sessionId = document.getElementById("sessionId");
const startId = document.getElementById("startId");
const numberquestions = document.getElementById("numberquestions");
const rowNumber = document.getElementById("rowNumber");
const levelCategory = document.getElementById("levelCategory");
const level = document.getElementById("level");
const japaneseSentence = document.getElementById("japaneseSentence");
const answerInput = document.getElementById("answerInput");
const answerButton = document.getElementById("answerButton");

const modal = document.getElementById("modal");
const resultMessage = document.getElementById("result-message");
const correctAnswer = document.getElementById("correct-answer");
const explanationMessage = document.getElementById("explanation-message");
const nextButton = document.getElementById("next-button");

answerButton.addEventListener("click", async () => {
  
  document.body.setAttribute('inert', 'true');
  
  const formData = new FormData();
  formData.append("sessionId", sessionId.value);
  formData.append("startId", startId.value);
  formData.append("rowNumber", rowNumber.value);
  formData.append("answer", answerInput.value);

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

  document.body.removeAttribute('inert');
});

function goToNext() {
  if (nextButton.dataset.finished === "true") {
    window.location.href = "/result";
  } else {
    window.location.href = "/question";
  }
}