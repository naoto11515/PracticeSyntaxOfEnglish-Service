// login button click event handler
const username = document.getElementById("username");
const password = document.getElementById("password");
const loginButton = document.getElementById("loginButton");
const registButton = document.getElementById("registButton");
const userNameDisplay = document.getElementById("user-name");
const conditionMessage = document.getElementById("condition-message");

registButton.addEventListener("click", async () => {
  const formData = new FormData();
  formData.append("username", username.value);
  formData.append("password", password.value);

  const response = await fetch("regist_user", {
    method: "POST",
    body: formData
  });

  const result = await response.json();
  
  if (!result.success) {
      alert(result.message);
  } else {
      userNameDisplay.textContent = result.usernamedisplay;
      conditionMessage.textContent = result.condition_message;

      modal.style.display = "block";
  }
});
