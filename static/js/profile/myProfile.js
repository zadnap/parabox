// Handle open and close edit profile modal
const editModal = document.querySelector(".edit-profile-modal");

handleEditProfile = () => {
  editModal.classList.remove("hidden");
};

const closeBtn = document.getElementById("close-edit");
closeBtn.onclick = () => {
  editModal.classList.add("hidden");
};

// Handle submit form
const editProfileForm = document.getElementById("edit_profile_form");
const profilePicture = document.getElementById("profile_picture");
const wallpaperPicture = document.getElementById("wallpaper_picture");

profilePicture.onchange = () => {
  const avatarPreview = document.getElementById("avatar-preview");
  avatarPreview.src = URL.createObjectURL(profilePicture.files[0]);
  avatarPreview.onload = () => {
    URL.revokeObjectURL(profilePicture.src); // Free memory
  };
};
wallpaperPicture.onchange = () => {
  const wallpaperPreview = document.getElementById("wallpaper-preview");
  wallpaperPreview.src = URL.createObjectURL(wallpaperPicture.files[0]);
  wallpaperPreview.onload = () => {
    URL.revokeObjectURL(wallpaperPicture.src); // Free memory
  };
};

editProfileForm.addEventListener("submit", async function (event) {
  event.preventDefault(); // Prevent form submission

  const username = document
    .getElementById("username_edited")
    .value.replace(/\s+/g, " ")
    .trim();
  const firstname = document
    .getElementById("first_name_edited")
    .value.replace(/\s+/g, " ")
    .trim();
  const lastname = document
    .getElementById("last_name_edited")
    .value.replace(/\s+/g, " ")
    .trim();
  const bio = document
    .getElementById("bio_edited")
    .value.replace(/\s+/g, " ")
    .trim();

  const formData = new FormData();
  formData.append("profilePicture", profilePicture.files[0]);
  formData.append("wallpaperPicture", wallpaperPicture.files[0]);
  formData.append("username", username);
  formData.append("firstname", firstname);
  formData.append("lastname", lastname);
  formData.append("bio", bio);

  // Make an AJAX request to validate data
  try {
    const response = await fetch("/edit/profile", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (data.error) {
      document.getElementById("prompt").textContent = data.error;
    } else {
      window.location.href = "/profile/" + username;
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
