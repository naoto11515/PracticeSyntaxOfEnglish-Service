// login button click event handler
const mode = document.getElementById("mode");
const syntaxId = document.getElementById("syntaxId");
const automaticNumbering = document.getElementById("automaticNumbering");
const syntax = document.getElementById("syntax");
const meaning = document.getElementById("meaning");
const submitButton = document.getElementById("submitButton");

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

submitButton.addEventListener("click", async () => {

  document.body.setAttribute('inert', 'true');

  const formData = new FormData();
  formData.append("syntaxId", syntaxId.value || "");
  const isChecked = automaticNumbering.checked ? "true" : "false";
  formData.append("automaticNumbering", isChecked);
  formData.append("syntax", syntax.value);
  formData.append("meaning", meaning.value);

  if (mode.value == "create"){
    post_name = "/create_syntax"
  } else if (mode.value == "update") {
    post_name = "/update_syntax"
  } else {
    post_name = "/delete_syntax"
  }
  
  const response = await fetch(post_name, {
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

  document.body.removeAttribute('inert');
});
