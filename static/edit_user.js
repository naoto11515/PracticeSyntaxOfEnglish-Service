// login button click event handler
const mode = document.getElementById("mode");
const userName = document.getElementById("userName");
const password = document.getElementById("password");
const loginButton = document.getElementById("loginButton");
const submitButton = document.getElementById("submitButton");
const userNameDisplay = document.getElementById("user-name");
const conditionMessage = document.getElementById("condition-message");

submitButton.addEventListener("click", async () => {

  document.body.setAttribute('inert', 'true');

  const formData = new FormData();

  if (mode.value == "create"){
    post_name = "/create_user"
    formData.append("userName", userName.value);
    formData.append("password", password.value);

  } else if (mode.value == "update") {
    post_name = "/update_user"
    formData.append("userName", userName.value);
    formData.append("password", password.value);

  } else {
    post_name = "/delete_user"
    formData.append("userName", userName.value);
  }

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

  document.body.removeAttribute('inert');
});
