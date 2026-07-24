function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));

  if (!cookieValue) {
    return null;
  }

  return decodeURIComponent(cookieValue.split("=")[1]);
}

async function postJson(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(data),
  });

  let responseData;

  try {
    responseData = await response.json();
  } catch (error) {
    throw new Error("서버 응답을 처리할 수 없습니다.");
  }

  if (!response.ok) {
    throw new Error(
      responseData.error || "요청 처리에 실패했습니다."
    );
  }

  return responseData;
}

function setLoadingState({
  button,
  input,
  loadingElement,
  isLoading,
}) {
  button.disabled = isLoading;
  input.disabled = isLoading;
  loadingElement.hidden = !isLoading;
}

function clearMessage(element) {
  element.textContent = "";
  element.hidden = true;
}

function showMessage(element, message) {
  element.textContent = message;
  element.hidden = false;
}

function formatPercent(score) {
  return `${(score * 100).toFixed(2)}%`;
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}