const registerForm = document.querySelector("#login-form");

registerForm.addEventListener("submit", async function (event) {
  event.preventDefault(); // Prevent form submission

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const isRemember = document.getElementById("remember_me").checked;

  // Make an AJAX request to validate username and password
  try {
    const response = await fetch("/login", {
      method: "POST",
      body: new URLSearchParams({
        username,
        password,
        isRemember,
      }),
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const data = await response.json();

    if (data.error) {
      document.getElementById("prompt").textContent = data.error;
    } else {
      window.location.href = "/";
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
