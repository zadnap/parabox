// Load more posts once the user scroll to the bottom of the page
const renderMedia = (media, postId) => {
  const slider = document.createElement("ul");
  slider.classList.add("slider");

  media.forEach((file, index) => {
    const mediaItem = document.createElement("li");
    mediaItem.classList.add("item");
    mediaItem.setAttribute("onclick", `slide(0,${postId},${index})`);
    mediaItem.innerHTML = `<img 
        src="data:image/jpeg;base64,${file}" 
        alt="An image for the post"
        onerror="this.src='../static/images/avatar_placeholder.jpg';"
    >`;
    slider.appendChild(mediaItem);
  });
  return slider.innerHTML;
};
const renderComments = (comments) => {
  const commentSection = document.createElement("div");
  commentSection.classList.add("comments");
  comments.forEach((cmt) => {
    const userComment = document.createElement("div");
    userComment.classList.add("user-comment");
    userComment.innerHTML = `<a href="/profile/${cmt.username}">
        <img 
            class="avatar"
            src="data:image/jpeg;base64,${cmt.profile_picture}" 
            alt="${cmt.first_name} ${cmt.last_name}"
            onerror="this.src='../../static/images/avatar_placeholder.jpg';"
        >
    </a>
    <div class="info">
        <a href="/profile/${cmt.username}" class="poppins-medium name">${cmt.first_name} ${cmt.last_name}</a>
        <p class="text">${cmt.content}</p>
        <span class="time">${cmt.created_at}</span>
    </div>`;

    commentSection.appendChild(userComment);
  });

  return commentSection.innerHTML;
};

const renderPost = (post, username) => {
  const newPost = document.createElement("article");
  newPost.classList.add("post");
  newPost.setAttribute("id", post.id);
  newPost.innerHTML = `<div class="head">
    <div class="info">
        <a href="/profile/${post.username}">
            <img 
                class="avatar"
                src="data:image/jpeg;base64,${post.profile_picture}" 
                alt="${post.first_name} ${post.last_name}"
                onerror="this.src='../static/images/avatar_placeholder.jpg';"
            >
        </a>
        <div class="names">
            <a href="/profile/${post.username}" class="poppins-semibold">${
    post.first_name
  } ${post.last_name}</a>
            <p class="poppins-medium">${post.created_at}</p>
        </div>
    </div>
    ${
      username == post.username
        ? `
        <div class="handles">
          <div class="dropdown">
            <button class="handle-post" onclick="openHandlePost(${post.id})}">
              <i class="fa-solid fa-ellipsis-vertical"></i>
            </button>
            <div class="dropdown-content">
              <button onclick="deletePost(${post.id})">Delete post</button>
            </div>
          </div>
        </div>`
        : ""
    }
  </div>
  <div class="content">
    ${post.caption ? `<p class="caption">${post.caption}</p>` : ""}
    ${
      post.media_count != 0
        ? `
        <div class="pictures">
          <button class="prev" onclick="slide(-1, ${post.id})">
            <i class="fa-solid fa-angle-left"></i>
          </button>
          <ul class="slider">
            ${renderMedia(post.media_blobs, post.id)}
          </ul>
          <button class="next" onclick="slide(1, ${post.id})">
            <i class="fa-solid fa-angle-right"></i>
          </button>
        </div>
      `
        : ""
    }
  </div>
  <div class="interactions">
    <button class="poppins-medium like ${
      post.is_liked ? "liked" : ""
    }" onclick="handleLikePost(${post.id})">
        <i class="fa-regular fa-heart"></i><i class="fa-solid fa-heart"></i><span>${
          post.likes.length
        }</span>
    </button>
    <button class="poppins-medium comment" onclick="openCommentSection(${
      post.id
    })">
        <i class="fa-regular fa-comment"></i><span>${
          post.comments.length
        }</span>
    </button>
  </div>
  <div class="comment-section hidden">
    ${renderComments(post.comments)}
    <div class="cmt-box">
        <textarea class="comment-textarea" rows="1" placeholder="Say something less than 2000 characters" maxlength="2000" oninput="editComment(${
          post.id
        })"></textarea>
        <div class="prompt"></div>
        <div class="handles">
            <div class="word-count">0/2000</div>
            <button disabled class="cmt-btn" onclick="sendComment(${
              post.id
            })">Send</button>
        </div>
    </div>
  </div>`;

  return newPost;
};

const handleScrollWindow = () => {
  if (window.innerHeight + window.scrollY >= document.body.scrollHeight) {
    fetchMorePosts();
  }
};

// Get a reference to the posts container
const postsContainer = document.querySelector(".news");

// When it render the first 5 posts, that is page 1
let currentPage = 2;

const fetchMorePosts = async () => {
  try {
    const response = await fetch(`/generate_post?page=${currentPage}`);
    const data = await response.json();

    if (data.posts.length == 0) {
      const prompt = document.createElement("div");
      prompt.classList.add("out-of-content");
      prompt.textContent = "You have viewed all the content!";
      postsContainer.appendChild(prompt);
      window.removeEventListener("scroll", handleScrollWindow);
    } else {
      data.posts.forEach((post) => {
        postsContainer.appendChild(renderPost(post, data.username));
      });
    }
    currentPage++;
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

// Detect when the user scrolls to the bottom
window.addEventListener("scroll", handleScrollWindow);

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
