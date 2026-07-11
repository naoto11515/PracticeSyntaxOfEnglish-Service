// [common] edit_User screen element
const editUserForm = document.getElementById("editUserForm");
const submitButton = document.getElementById("submitButton");

// [specific] edit_User screen element
const userNameDisplay = document.getElementById("user-name");
const conditionMessage = document.getElementById("condition-message");

submitButton.addEventListener("click", () => {
  editUserForm.classList.add("was-validated");
});

editUserForm.addEventListener("submit", async (event) => {

  event.preventDefault();
  
  if (!editUserForm.checkValidity()) {
    return; 
  }
  
  document.body.setAttribute('inert', 'true');
  const formData = new FormData(editUserForm);

  if (formData.get("mode") == "create"){
    post_name = "/create_user"

  } else if (formData.get("mode") == "update") {
    post_name = "/update_user"

  } else {
    post_name = "/delete_user"
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
        userNameDisplay.textContent = result.userNamedisplay;
        conditionMessage.textContent = result.condition_message;

        modal.style.display = "block";
    }
  } catch(error){
    alert("通信エラーが発生しました。");
  } finally{
    document.body.removeAttribute('inert');
  }
});
