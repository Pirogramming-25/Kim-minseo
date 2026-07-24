document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("moderate-form");
  const input = document.getElementById("moderate-input");
  const button = document.getElementById("moderate-button");

  const loadingElement = document.getElementById(
    "moderate-loading"
  );
  const errorElement = document.getElementById(
    "moderate-error"
  );
  const resultSection = document.getElementById(
    "moderate-result-section"
  );
  const resultElement = document.getElementById(
    "moderate-result"
  );

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    clearMessage(errorElement);
    resultSection.hidden = true;

    const text = input.value.trim();

    if (!text) {
      showMessage(
        errorElement,
        "분석할 문장을 입력해주세요."
      );
      return;
    }

    if (text.length > 1000) {
      showMessage(
        errorElement,
        "문장은 1,000자 이하로 입력해주세요."
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
        "/moderate/run/",
        {
          text,
        }
      );

      renderModerationResult(data.result);
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

  function renderModerationResult(result) {
    const scoreItems = result.all_scores
      .map(
        (item) => `
          <li>
            <span>
              ${escapeHtml(item.label)}
            </span>
            <strong>
              ${formatPercent(item.score)}
            </strong>
          </li>
        `
      )
      .join("");

    resultElement.innerHTML = `
      <div class="primary-result">
        <p>
          <strong>최고 위험 레이블:</strong>
          ${escapeHtml(result.highest_label)}
        </p>

        <p>
          <strong>위험 점수:</strong>
          ${formatPercent(result.highest_score)}
        </p>
      </div>

      <h3>전체 레이블 점수</h3>

      <ul class="score-list">
        ${scoreItems}
      </ul>
    `;
  }
});