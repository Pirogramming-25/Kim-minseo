function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return document.querySelector("meta[name='csrf-token']")?.content || "";
}

function postForm(url, formData = new FormData()) {
    return fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
    });
}

document.querySelectorAll(".like-button").forEach((button) => {
    button.dataset.baseLikeCount = button.dataset.likeCount || "0";

    button.addEventListener("click", async () => {
        const meta = button.closest(".post-card").querySelector(".like-text");
        const url = button.dataset.likeUrl;
        if (!url) return;

        const response = await postForm(url);
        if (!response.ok) return;

        const data = await response.json();
        button.classList.toggle("is-liked", data.liked);
        button.dataset.likeCount = String(data.like_count);
        meta.textContent = data.like_text;
    });
});

document.querySelectorAll(".save-button").forEach((button) => {
    button.addEventListener("click", async () => {
        const url = button.dataset.saveUrl;
        if (!url) return;

        const response = await postForm(url);
        if (!response.ok) return;

        const data = await response.json();
        button.classList.toggle("is-saved", data.saved);
    });
});

document.querySelectorAll("[data-auto-submit] select").forEach((select) => {
    select.addEventListener("change", () => {
        select.form.requestSubmit();
    });
});

document.querySelectorAll("[data-auto-upload]").forEach((input) => {
    input.addEventListener("change", () => {
        if (input.files?.length) input.form.requestSubmit();
    });
});

document.addEventListener("change", (event) => {
    const input = event.target.closest("[data-image-input]");
    if (!input) return;

    const file = input.files?.[0];
    const preview = input.closest("form")?.querySelector("[data-upload-preview]");
    if (!file || !preview) return;

    const imageUrl = URL.createObjectURL(file);
    const fileCount = input.files.length;
    const label = fileCount > 1 ? `사진 ${fileCount}장 미리보기` : "사진 미리보기";
    preview.innerHTML = `<img src="${imageUrl}" alt="선택한 사진 미리보기"><span>${label}</span>`;
    preview.classList.add("has-preview-image");
});

document.querySelectorAll(".suggestion-row button, .follow-button").forEach((button) => {
    button.addEventListener("click", async () => {
        const url = button.dataset.followUrl;
        if (!url) return;

        const response = await postForm(url);
        if (!response.ok) return;

        const data = await response.json();
        button.classList.toggle("is-following", data.following);
        button.textContent = data.following ? "팔로잉" : "팔로우";

        const followers = document.querySelector("[data-profile-followers]");
        if (followers && typeof data.followers !== "undefined") {
            followers.textContent = data.followers.toLocaleString();
        }
    });
});

document.querySelectorAll("[data-comment-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const input = form.querySelector("input[name='content']");
        const content = input?.value.trim();
        if (!content) return;

        const response = await postForm(form.dataset.actionUrl, new FormData(form));
        if (!response.ok) return;

        const data = await response.json();
        input.value = "";

        if (form.classList.contains("comment-form")) {
            const meta = form.closest(".post-card").querySelector(".post-meta");
            const row = document.createElement("div");
            row.className = "comment-row";
            row.dataset.commentId = data.comment.id;
            row.dataset.editUrl = data.comment.edit_url;
            row.dataset.deleteUrl = data.comment.delete_url;
            row.innerHTML = `<p><strong>${data.comment.author}</strong> ${data.comment.content}</p>`;
            meta.querySelector("time").before(row);

            const allComments = meta.querySelector(".all-comments");
            if (allComments) allComments.textContent = `댓글 ${data.comment_count}개 모두 보기`;
        } else {
            const parentRow = form.closest(".comment-row");
            const replies = parentRow.querySelector(".comment-replies");
            const row = document.createElement("div");
            row.className = "comment-row";
            row.dataset.commentId = data.comment.id;
            row.dataset.editUrl = data.comment.edit_url;
            row.dataset.deleteUrl = data.comment.delete_url;
            row.innerHTML = `<p><strong>${data.comment.author}</strong> ${data.comment.content}</p>
                <div class="comment-tools">
                    <button type="button">수정</button>
                    <button type="button">삭제</button>
                </div>`;
            replies?.append(row);
            form.reset();
            parentRow.classList.remove("is-replying");
        }
    });
});

document.querySelectorAll("[data-show-comments]").forEach((button) => {
    button.addEventListener("click", () => {
        const meta = button.closest(".post-meta");
        const hiddenComments = meta?.querySelector(".hidden-comments");
        if (!hiddenComments) return;

        const isHidden = hiddenComments.hidden;
        hiddenComments.hidden = !isHidden;
        button.textContent = isHidden ? "댓글 숨기기" : button.dataset.originalText;
    });
    button.dataset.originalText = button.textContent;
});

document.addEventListener("click", async (event) => {
    const button = event.target.closest(".comment-tools button");
    if (!button) return;

    const row = button.closest(".comment-row");
    const label = button.textContent.trim();

    if (label === "답글") {
        row.classList.toggle("is-replying");
    }

    if (label === "수정") {
        const text = row.querySelector("p");
        const current = text.textContent.replace(/^\S+\s/, "").trim();
        const next = window.prompt("댓글을 수정하세요.", current);
        if (!next) return;

        const formData = new FormData();
        formData.append("content", next);
        const response = await postForm(row.dataset.editUrl, formData);
        if (!response.ok) return;

        const data = await response.json();
        text.innerHTML = `<strong>${data.comment.author}</strong> ${data.comment.content}`;
    }

    if (label === "삭제") {
        const response = await postForm(row.dataset.deleteUrl);
        if (!response.ok) return;
        row.remove();
    }
});

const storyModal = document.querySelector("[data-story-modal]");
const storyProgress = document.querySelector("[data-story-progress]");
const storyPhoto = document.querySelector("[data-story-photo]");
const storyProfileLink = document.querySelector("[data-story-profile-link]");
const storyPhotoDot = document.querySelector(".story-photo-dot");
const storyTitle = document.querySelector("[data-story-title]");
const storyCaption = document.querySelector("[data-story-caption]");
const storyButtons = Array.from(document.querySelectorAll("[data-story-open]"));
const storyPrevButton = document.querySelector("[data-story-prev]");
const storyNextButton = document.querySelector("[data-story-next]");
let activeStoryIndex = 0;
let activeStoryImageIndex = 0;
let storyTimer = null;
const storyDuration = 5000;

function storyImages(story) {
    try {
        const images = JSON.parse(story.dataset.storyImages || "[]");
        if (Array.isArray(images) && images.length > 0) return images;
    } catch (error) {
        return [];
    }
    return [{ url: story.dataset.storyImage || "", color: story.style.getPropertyValue("--avatar-color") || "#9fd3ca" }];
}

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function isFirstStoryFrame() {
    return activeStoryIndex === 0 && activeStoryImageIndex === 0;
}

function isLastStoryFrame() {
    const images = storyImages(storyButtons[activeStoryIndex]);
    return activeStoryIndex === storyButtons.length - 1 && activeStoryImageIndex === images.length - 1;
}

function updateStoryNavigation() {
    if (storyPrevButton) storyPrevButton.disabled = isFirstStoryFrame();
    if (storyNextButton) storyNextButton.disabled = isLastStoryFrame();
}

function scheduleNextStory() {
    window.clearTimeout(storyTimer);
    if (isLastStoryFrame()) return;
    storyTimer = window.setTimeout(() => {
        renderNextStoryImage();
        scheduleNextStory();
    }, storyDuration);
}

function renderStory(index, imageIndex = 0) {
    if (!storyModal || storyButtons.length === 0) return;

    activeStoryIndex = clamp(index, 0, storyButtons.length - 1);
    const story = storyButtons[activeStoryIndex];
    const images = storyImages(story);
    activeStoryImageIndex = clamp(imageIndex, 0, images.length - 1);
    const image = images[activeStoryImageIndex] || {};
    const color = image.color || story.style.getPropertyValue("--avatar-color") || "#9fd3ca";
    const imageUrl = image.url || "";

    storyPhoto.style.setProperty("--story-photo-color", color);
    if (storyPhotoDot) {
        storyPhotoDot.style.backgroundImage = story.dataset.storyAvatarUrl ? `url("${story.dataset.storyAvatarUrl}")` : "";
    }
    storyPhoto.style.backgroundImage = imageUrl
        ? `linear-gradient(to bottom, rgb(0 0 0 / 0.35), transparent 28%, rgb(0 0 0 / 0.18)), url("${imageUrl}")`
        : "";
    storyPhoto.classList.toggle("has-image", Boolean(imageUrl));
    storyTitle.textContent = story.dataset.storyName || "스토리";
    if (storyProfileLink) {
        storyProfileLink.href = story.dataset.storyProfileUrl || "#";
    }
    storyCaption.textContent = `${activeStoryImageIndex + 1} / ${images.length}`;

    storyProgress.style.transition = "none";
    storyProgress.style.width = "0";
    window.setTimeout(() => {
        storyProgress.style.transition = `width ${storyDuration}ms linear`;
        storyProgress.style.width = "100%";
    }, 30);
    updateStoryNavigation();
}

function renderNextStoryImage() {
    const images = storyImages(storyButtons[activeStoryIndex]);
    if (activeStoryImageIndex + 1 < images.length) {
        renderStory(activeStoryIndex, activeStoryImageIndex + 1);
        return;
    }
    if (activeStoryIndex + 1 >= storyButtons.length) return;
    renderStory(activeStoryIndex + 1, 0);
}

function renderPreviousStoryImage() {
    if (activeStoryImageIndex > 0) {
        renderStory(activeStoryIndex, activeStoryImageIndex - 1);
        return;
    }
    if (activeStoryIndex === 0) return;
    const previousStoryIndex = activeStoryIndex - 1;
    const previousImages = storyImages(storyButtons[previousStoryIndex]);
    renderStory(previousStoryIndex, previousImages.length - 1);
}

function openStory(index) {
    if (!storyModal) return;

    storyModal.hidden = false;
    renderStory(index);
    scheduleNextStory();
}

function closeStory() {
    if (!storyModal) return;

    storyModal.hidden = true;
    window.clearTimeout(storyTimer);
}

storyButtons.forEach((button, index) => {
    button.addEventListener("click", () => openStory(index));
});

document.querySelectorAll("[data-story-close]").forEach((button) => {
    button.addEventListener("click", closeStory);
});

storyPrevButton?.addEventListener("click", () => {
    if (storyPrevButton.disabled) return;
    renderPreviousStoryImage();
    scheduleNextStory();
});
storyNextButton?.addEventListener("click", () => {
    if (storyNextButton.disabled) return;
    renderNextStoryImage();
    scheduleNextStory();
});
