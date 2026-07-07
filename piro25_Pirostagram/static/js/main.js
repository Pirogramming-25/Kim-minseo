document.querySelectorAll(".like-button").forEach((button) => {
    button.dataset.baseLikeCount = button.dataset.likeCount || "0";

    button.addEventListener("click", () => {
        const meta = button.closest(".post-card").querySelector(".like-text");
        const base = Number(button.dataset.baseLikeCount || 0);
        const next = button.classList.toggle("is-liked") ? base + 1 : base;

        button.dataset.likeCount = String(next);
        meta.textContent = `좋아요 ${next.toLocaleString()}개`;
    });
});

document.querySelectorAll(".save-button").forEach((button) => {
    button.addEventListener("click", () => {
        button.classList.toggle("is-saved");
    });
});

document.querySelectorAll(".post-delete-button").forEach((button) => {
    button.addEventListener("click", () => {
        button.closest(".post-card").style.display = "none";
    });
});

document.querySelectorAll("[data-auto-submit] select").forEach((select) => {
    select.addEventListener("change", () => {
        select.form.requestSubmit();
    });
});

document.querySelectorAll(".suggestion-row button, .follow-button").forEach((button) => {
    button.addEventListener("click", () => {
        const following = button.classList.toggle("is-following");
        button.textContent = following ? "팔로잉" : "팔로우";
    });
});

document.querySelectorAll(".comment-tools button").forEach((button) => {
    button.addEventListener("click", () => {
        const row = button.closest(".comment-row");

        if (button.textContent.trim() === "답글") {
            row.classList.toggle("is-replying");
        }

        if (button.textContent.trim() === "수정") {
            const text = row.querySelector("p");
            text.contentEditable = text.contentEditable !== "true";
            text.focus();
        }

        if (button.textContent.trim() === "삭제") {
            row.style.display = "none";
        }
    });
});

const storyModal = document.querySelector("[data-story-modal]");
const storyProgress = document.querySelector("[data-story-progress]");
const storyPhoto = document.querySelector("[data-story-photo]");
const storyTitle = document.querySelector("[data-story-title]");
const storyCaption = document.querySelector("[data-story-caption]");
const storyButtons = Array.from(document.querySelectorAll("[data-story-open]"));
let activeStoryIndex = 0;
let storyTimer = null;
let progressTimer = null;

function renderStory(index) {
    if (!storyModal || storyButtons.length === 0) return;

    activeStoryIndex = (index + storyButtons.length) % storyButtons.length;
    const story = storyButtons[activeStoryIndex];
    const color = story.style.getPropertyValue("--avatar-color") || "#9fd3ca";

    storyPhoto.style.setProperty("--story-photo-color", color);
    storyTitle.textContent = story.dataset.storyName || "스토리";
    storyCaption.textContent = `${activeStoryIndex + 1} / ${storyButtons.length}`;

    storyProgress.style.transition = "none";
    storyProgress.style.width = "0";
    window.setTimeout(() => {
        storyProgress.style.transition = "width 3s linear";
        storyProgress.style.width = "100%";
    }, 30);
}

function openStory(index) {
    if (!storyModal) return;

    storyModal.hidden = false;
    renderStory(index);
    window.clearInterval(storyTimer);
    window.clearInterval(progressTimer);
    storyTimer = window.setInterval(() => renderStory(activeStoryIndex + 1), 3000);
}

function closeStory() {
    if (!storyModal) return;

    storyModal.hidden = true;
    window.clearInterval(storyTimer);
    window.clearInterval(progressTimer);
}

storyButtons.forEach((button, index) => {
    button.addEventListener("click", () => openStory(index));
});

document.querySelectorAll("[data-story-close]").forEach((button) => {
    button.addEventListener("click", closeStory);
});

document.querySelector("[data-story-prev]")?.addEventListener("click", () => renderStory(activeStoryIndex - 1));
document.querySelector("[data-story-next]")?.addEventListener("click", () => renderStory(activeStoryIndex + 1));
