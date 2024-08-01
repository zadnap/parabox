// Handle open and close posting modal
const createBtn = document.querySelector("#create-post");
const createModal = document.querySelector(".create-modal");
const closeBtn = document.querySelector("#close");
const postForm = document.querySelector("#post");
const wordCount = document.querySelector("#word-count");

createBtn.onclick = () => {
  createModal.classList.remove("hidden");
  wordCount.innerHTML = postEdit.value.length + "/2500";
};
closeBtn.onclick = () => {
  createModal.classList.add("hidden");
};

// Handle typing text
const postEdit = document.getElementById("post_edit");

wordCount.innerHTML = postEdit.value.length + "/2500";

const countWord = () => {
  wordCount.innerHTML = postEdit.value.length + "/2500";
};

// Handle expand post creating textarea
const heightLimit = 250;

postEdit.addEventListener("input", () => {
  postEdit.style.height = ""; // Reset the height
  postEdit.style.height = Math.min(postEdit.scrollHeight, heightLimit) + "px";
  countWord();
});

// Handle adding hashtag
const addHashtagBtn = document.getElementById("add_hashtag");

addHashtagBtn.addEventListener("click", () => {
  if (postEdit.value.length == 0) {
    postEdit.value += "#";
  } else if (postEdit.value.length < 2499) {
    postEdit.value += "\n#";
  }
  postEdit.style.height = ""; // Reset the height
  postEdit.style.height = Math.min(postEdit.scrollHeight, heightLimit) + "px";
  postEdit.focus();
  countWord();
});

// Handle showing images for posts
const postingForm = document.getElementById("posting");
const imageInput = document.getElementById("post_image");
const postingPrompt = document.querySelector(".posting-prompt");
const images = [];

const renderImage = () => {
  const imageContainer = document.querySelector(".images");

  imageContainer.innerHTML = images.map((image, index) => {
    return `<div class="image">
      <img src="${URL.createObjectURL(image)}" alt="">
      <button type="button" onclick="handleRemoveImage(${index})"><i class="fa-solid fa-xmark"></i></button>
  </div>`;
  });
};

imageInput.onchange = () => {
  if (images.length + imageInput.files.length > 10) {
    postingPrompt.innerHTML = "You can only upload 10 or less pictures!";
  } else {
    images.push(...imageInput.files);
    renderImage();
  }
};

const handleRemoveImage = (index) => {
  images.splice(index, 1);
  renderImage();
};

postingForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData();
  formData.append("caption", postEdit.value);
  for (image of images) {
    formData.append("image", image);
  }

  // Make an AJAX request to validate data
  try {
    const response = await fetch("/posting", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (data.error) {
      postingPrompt.textContent = data.error;
    } else {
      window.location.href = "/";
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
