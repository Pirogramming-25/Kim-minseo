document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("summarize-form");
  const input = document.getElementById("summarize-input");
  const button = document.getElementById("summarize-button");

  const loadingElement = document.getElementById(
    "summarize-loading"
  );
  const errorElement = document.getElementById(
    "summarize-error"
  );
  const resultSection = document.getElementById(
    "summarize-result-section"
  );
  const resultElement = document.getElementById(
    "summarize-result"
  );

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    clearMessage(errorElement);
    resultSection.hidden = true;

    const text = input.value.trim();

    if (text.length < 100) {
      showMessage(
        errorElement,
        "요약할 문서는 100자 이상 입력해주세요."
      );
      return;
    }

    if (text.length > 5000) {
      showMessage(
        errorElement,
        "문서는 5,000자 이하로 입력해주세요."
      );
      return;
    }

    setLoadingState({
      button,
      input,
      loadingElement,
      isLoading: true,
    });

    try {
      const data = await postJson(
        "/summarize/run/",
        {
          text,
        }
      );

      renderSummaryResult(data.result);
      resultSection.hidden = false;
    } catch (error) {
      showMessage(
        errorElement,
        error.message
      );
    } finally {
      setLoadingState({
        button,
        input,
        loadingElement,
        isLoading: false,
      });
    }
  });

  function renderSummaryResult(result) {
    resultElement.innerHTML = `
      <div class="summary-metadata">
        <p>
          <strong>원문 길이:</strong>
          ${result.original_length.toLocaleString()}자
        </p>

        <p>
          <strong>요약문 길이:</strong>
          ${result.summary_length.toLocaleString()}자
        </p>

        <p>
          <strong>요약 비율:</strong>
          ${Number(result.summary_ratio).toFixed(2)}%
        </p>
      </div>

      <div class="summary-content">
        <h3>요약 결과</h3>
        <p>${escapeHtml(result.summary)}</p>
      </div>
    `;
  }
});