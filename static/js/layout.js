// Handle profile dropdown menu
const closeOtherDropdowns = (currentDropdown) => {
  const dropdowns = document.querySelectorAll(".dropdown-content");
  for (dropdown of dropdowns) {
    if (dropdown !== currentDropdown) {
      dropdown.classList.remove("show");
    }
  }
};

const profileBtn = document.querySelector("#profile");
const dropdownProfile = document.querySelector("#profile-dropdown");

profileBtn.onclick = () => {
  closeOtherDropdowns(dropdownProfile);
  dropdownProfile.classList.toggle("show");
};

// Handle scrolling post image into view
const slide = (goto, id, index) => {
  let currentIndex = 0;
  const post = document.getElementById(id);
  const slider = post.querySelector(".slider");
  const sliderItems = slider.querySelectorAll(".item");

  sliderItems.forEach((li, index) => {
    if (li.classList.contains("focused")) {
      currentIndex = index;
    }
  });

  if (goto == 1) {
    if (currentIndex < sliderItems.length - 1) {
      currentIndex++;
    } else {
      currentIndex = 0;
    }
  } else if (goto == -1) {
    if (currentIndex > 0) {
      currentIndex--;
    } else {
      currentIndex = sliderItems.length - 1;
    }
  } else if (goto == 0) {
    currentIndex = index;
  }
  console.log(sliderItems[currentIndex]);

  sliderItems[currentIndex].scrollIntoView({
    block: "center",
    inline: "center",
  });

  sliderItems.forEach((li) => {
    li.classList.remove("focused");
  });
  sliderItems[currentIndex].classList.add("focused");
};

// Handle like posts
const handleLikePost = async (id) => {
  const post = document.getElementById(id);
  const likeBtn = post.querySelector(".like");
  const likeCount = likeBtn.querySelector("span");

  const formData = new FormData();
  formData.append("id", id);

  // Make an AJAX request
  try {
    const response = await fetch("/post/like", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (data.message) {
      likeBtn.classList.toggle("liked");
      likeCount.innerText = data.like_count;
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

// Handle comments
const openCommentSection = (id) => {
  const post = document.getElementById(id);
  const commentSection = post.querySelector(".comment-section");
  const commentTextarea = post.querySelector(".comment-textarea");

  commentSection.classList.toggle("hidden");
  commentTextarea.focus();
};

const editComment = (id) => {
  const post = document.getElementById(id);
  const commentTextarea = post.querySelector(".comment-textarea");
  const wordCount = post.querySelector(".word-count");
  const sendBtn = post.querySelector(".cmt-btn");

  // Count world and expand textarea
  const heightLimit = 250;
  commentTextarea.style.height = "";
  commentTextarea.style.height =
    Math.min(commentTextarea.scrollHeight, heightLimit) + "px";
  wordCount.textContent = commentTextarea.value.length + "/2000";

  if (commentTextarea.value.length == 0) {
    sendBtn.disabled = true;
  } else {
    sendBtn.disabled = false;
  }
};

const sendComment = async (id) => {
  const post = document.getElementById(id);
  const commentTextarea = post.querySelector(".comment-textarea");
  const prompt = post.querySelector(".prompt");
  const cmtBtn = post.querySelector(".comment");
  const cmtCount = cmtBtn.querySelector("span");
  const wordCount = post.querySelector(".word-count");

  const formData = new FormData();

  formData.append("id", id);
  formData.append("comment", commentTextarea.value);

  // Make an AJAX request
  try {
    const response = await fetch("/post/comment", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (data.message) {
      cmtCount.textContent = data.cmt_count;
      commentTextarea.style.height = "30px";
      wordCount.textContent = "0/2000";

      const comments = post.querySelector(".comments");

      const userComment = document.createElement("div");
      userComment.className = "user-comment";
      userComment.innerHTML = `<a href="/profile/${data.username}">
          <img class="avatar" src="data:image/jpeg;base64,${data.profile_picture}" alt="${data.display_name}" onerror="this.src='../../static/images/avatar_placeholder.jpg';">
        </a>
        <div class="info">
          <a href="/profile/${data.username}" class="poppins-medium name">${data.display_name}</a>
          <p class="text">${commentTextarea.value}</p>
          <span class="time">Just now</span>
        </div>
      `;
      comments.appendChild(userComment);

      commentTextarea.value = "";
      comments.scrollTop = comments.scrollHeight;
    } else {
      prompt.textContent = data.error;
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

// Edit and delete post
const openHandlePost = async (id) => {
  const post = document.getElementById(id);
  const dropdownContent = post.querySelector(".dropdown-content");

  dropdownContent.classList.toggle("show");
};
const deletePost = async (id) => {
  const formData = new FormData();
  formData.append("id", id);

  try {
    const response = await fetch("/post/delete", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (data.message) {
      document.getElementById(id).remove();
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

// Handle mark posts
const markPost = async (id) => {
  const post = document.getElementById(id);
  const markBtn = post.querySelector(".mark");

  const formData = new FormData();
  formData.append("id", id);

  try {
    const response = await fetch("/post/mark", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (data.message) {
      markBtn.classList.toggle("marked");
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
