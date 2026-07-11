// [common] edit_syntax screen element
const editSyntaxForm = document.getElementById("editSyntaxForm");
const submitButton = document.getElementById("submitButton");

// [specific] edit_syntax screen element
const automaticNumbering = document.getElementById("automaticNumbering");
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

submitButton.addEventListener("click", () => {
  editSyntaxForm.classList.add("was-validated");
});

editSyntaxForm.addEventListener("submit", async (event) => {

  event.preventDefault();
  
  if (!editSyntaxForm.checkValidity()) {
    return; 
  }
  
  document.body.setAttribute('inert', 'true');

  const disabledElements = editSyntaxForm.querySelectorAll("[disabled]");
  disabledElements.forEach(el => el.removeAttribute("disabled"));

  const formData = new FormData(editSyntaxForm);

  const isChecked = automaticNumbering.checked ? "true" : "false";
  formData.append("automaticNumbering", isChecked);

  console.log(formData.get("mode"))

  if (formData.get("mode") == "create"){
    post_name = "/create_syntax"
  } else if (formData.get("mode") == "update") {
    post_name = "/update_syntax"
  } else {
    post_name = "/delete_syntax"
  }
  
  try{
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
  } catch(error){
    alert("通信エラーが発生しました。");
  } finally{
    document.body.removeAttribute('inert');
  }
});
