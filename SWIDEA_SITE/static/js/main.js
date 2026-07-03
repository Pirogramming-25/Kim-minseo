function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.slice(name.length + 1));
    }
  }
  return "";
}

const csrfToken = getCookie("csrftoken");

async function loadIdeaSearchResults(url, pushState = true) {
  const response = await fetch(url, {
    headers: { "X-Requested-With": "XMLHttpRequest" },
  });
  if (!response.ok) return;

  const html = await response.text();
  const template = document.createElement("template");
  template.innerHTML = html.trim();
  const nextContent = template.content.querySelector("[data-idea-page-content]");
  const currentContent = document.querySelector("[data-idea-page-content]");

  if (nextContent && currentContent) currentContent.replaceWith(nextContent);
  if (pushState) window.history.pushState({}, "", url);
}

document.addEventListener("submit", (event) => {
  const form = event.target.closest("[data-ajax-search]");
  if (!form) return;

  event.preventDefault();
  const params = new URLSearchParams(new FormData(form));
  const url = `${form.action}?${params.toString()}`;
  loadIdeaSearchResults(url);
});

window.addEventListener("popstate", () => {
  if (document.querySelector("[data-ajax-search]")) {
    loadIdeaSearchResults(window.location.href, false);
  }
});

document.addEventListener("click", async (event) => {
  const starButton = event.target.closest("[data-star-url]");
  if (starButton) {
    const response = await fetch(starButton.dataset.starUrl, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
    });
    if (response.redirected) {
      window.location.href = response.url;
      return;
    }
    if (response.status === 403) {
      window.location.href = "/accounts/login/";
      return;
    }
    if (!response.ok) return;

    const data = await response.json();
    starButton.classList.toggle("active", data.starred);
    const scope = starButton.closest(".idea-row, .detail-layout") || document;
    const count = scope.querySelector("[data-star-count]");
    if (count) count.textContent = data.star_count;
    return;
  }

  const interestButton = event.target.closest("[data-interest-url]");
  if (interestButton) {
    const formData = new FormData();
    formData.append("amount", interestButton.dataset.amount);

    const response = await fetch(interestButton.dataset.interestUrl, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    });
    if (!response.ok) return;

    const data = await response.json();
    const scope = interestButton.closest("[data-interest-wrap]");
    const value = scope.querySelector("[data-interest-value]");
    if (value) value.textContent = data.interest;
  }
});

document.addEventListener("change", (event) => {
  const input = event.target;
  if (input.type !== "file" || input.name !== "image") return;

  const preview = input.closest(".field-box")?.querySelector("[data-image-preview]");
  const file = input.files?.[0];
  if (!preview || !file) return;

  const imageUrl = URL.createObjectURL(file);
  const clearInput = input.closest(".field-box")?.querySelector('input[name="clear_image"]');
  const tools = input.closest(".field-box")?.querySelector("[data-image-tools]");
  if (clearInput) clearInput.checked = false;
  if (tools) tools.classList.remove("is-clearing");
  preview.classList.remove("is-empty");
  preview.innerHTML = `<img src="${imageUrl}" alt="선택한 이미지 미리보기">`;
});

document.addEventListener("change", (event) => {
  const input = event.target;
  if (input.name !== "clear_image") return;

  const fieldBox = input.closest(".field-box");
  const preview = fieldBox?.querySelector("[data-image-preview]");
  const tools = fieldBox?.querySelector("[data-image-tools]");
  const fileInput = fieldBox?.querySelector('input[type="file"][name="image"]');
  if (!preview) return;

  tools?.classList.toggle("is-clearing", input.checked);
  if (input.checked) {
    if (fileInput) fileInput.value = "";
    preview.classList.add("is-empty");
    preview.innerHTML = "<span>저장하면 현재 이미지가 삭제됩니다.</span>";
  } else if (preview.dataset.currentSrc) {
    preview.classList.remove("is-empty");
    preview.innerHTML = `<img src="${preview.dataset.currentSrc}" alt="${preview.dataset.currentAlt || "현재 이미지"}">`;
  }
});
