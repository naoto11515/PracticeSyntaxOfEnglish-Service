// login button click event handler
const syntaxId = document.getElementById("syntaxId");
const automaticNumbering = document.getElementById("automaticNumbering");
const syntax = document.getElementById("syntax");
const meaning = document.getElementById("meaning");
const registButton = document.getElementById("registButton");

const modal = document.getElementById("modal");
const syntaxIdDisplay = document.getElementById("syntaxId-display");
const syntaxDisplay = document.getElementById("syntax-display");
const meaningDisplay = document.getElementById("meaning-display");
const conditionMessage = document.getElementById("condition-message");

automaticNumbering.addEventListener("change", function(){
  if (this.checked) {
    syntaxId.disabled = true;
  } else {
    syntaxId.disabled = false;
  }
});

registButton.addEventListener("click", async () => {
  const formData = new FormData();
  formData.append("syntaxId", syntaxId.value || "");
  const isChecked = automaticNumbering.checked ? "true" : "false";
  formData.append("automaticNumbering", isChecked);
  formData.append("syntax", syntax.value);
  formData.append("meaning", meaning.value);
  
  const response = await fetch("regist_syntax", {
    method: "POST",
    body: formData
  });

  const result = await response.json();
  
  if (!result.success) {
      alert(result.message);
  } else {
      syntaxIdDisplay.textContent = result.syntaxIdDisplay;
      syntaxDisplay.textContent = result.syntaxDisplay;
      meaningDisplay.textContent = result.meaningDisplay;
      conditionMessage.textContent = result.condition_message;

      modal.style.display = "block";
  }
});
