const registerForm = document.querySelector("#register-form");

registerForm.addEventListener("submit", async function (event) {
  event.preventDefault(); // Prevent form submission

  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const confirmation = document.getElementById("confirmation").value;

  // Make an AJAX request to validate data
  try {
    const response = await fetch("/register", {
      method: "POST",
      body: new URLSearchParams({
        firstName,
        lastName,
        username,
        password,
        confirmation,
      }),
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    const data = await response.json();

    if (data.error) {
      document.getElementById("prompt").textContent = data.error;
    } else {
      window.location.href = "/login";
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
