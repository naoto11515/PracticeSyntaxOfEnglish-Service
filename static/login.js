// [common] login screen element
const loginForm = document.getElementById("loginForm");
const submitButton = document.getElementById("submitButton");

submitButton.addEventListener("click", () => {
  loginForm.classList.add("was-validated");
});

loginForm.addEventListener("submit", async (event) => {
  
  event.preventDefault();

  if (!loginForm.checkValidity()) {
    return; 
  }

  document.body.setAttribute('inert', 'true');
  const formData = new FormData(loginForm);

  try {
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
  } catch (error) {
    alert("通信エラーが発生しました。");
  } finally {
    document.body.removeAttribute('inert');
  }
});
