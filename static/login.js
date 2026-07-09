// login button click event handler
const username = document.getElementById("username");
const password = document.getElementById("password");
const loginButton = document.getElementById("loginButton");

loginButton.addEventListener("click", async () => {
  const formData = new FormData();
  formData.append("username", username.value);
  formData.append("password", password.value);

  const response = await fetch("/login", {
    method: "POST",
    body: formData
  });
  const result = await response.json();

  if (!result.success) {
      alert(result.message);
  } else {
      window.location.href = result.next;
  }
});
