document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("combo-form");
  const input = document.getElementById("combo-input");
  const button = document.getElementById("combo-button");
  const regenerateButton = document.getElementById(
    "regenerate-button"
  );

  const loadingElement = document.getElementById(
    "combo-loading"
  );
  const errorElement = document.getElementById(
    "combo-error"
  );
  const resultSection = document.getElementById(
    "combo-result-section"
  );
  const resultElement = document.getElementById(
    "combo-result"
  );

  let lastInputText = "";

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await runCombo(false);
  });

  regenerateButton.addEventListener("click", async () => {
    await runCombo(true);
  });

  async function runCombo(regenerate) {
    clearMessage(errorElement);

    const text = regenerate
      ? lastInputText
      : input.value.trim();

    if (text.length < 200) {
      showMessage(
        errorElement,
        "고객 피드백은 200자 이상 입력해주세요."
      );
      return;
    }

    if (text.length > 5000) {
      showMessage(
        errorElement,
        "고객 피드백은 5,000자 이하로 입력해주세요."
      );
      return;
    }

    button.disabled = true;
    input.disabled = true;
    regenerateButton.disabled = true;
    loadingElement.hidden = false;

    try {
      const data = await postJson(
        "/combo/run/",
        {
          text,
          regenerate,
        }
      );

      lastInputText = data.input_text;
      input.value = data.input_text;

      renderComboResult(data.result);
      resultSection.hidden = false;
      regenerateButton.hidden = false;
    } catch (error) {
      showMessage(
        errorElement,
        error.message
      );
    } finally {
      button.disabled = false;
      input.disabled = false;
      regenerateButton.disabled = false;
      loadingElement.hidden = true;
    }
  }

  function renderComboResult(result) {
    const toxicityScores = result.toxicity.all_scores
      .map(
        (item) => `
          <li>
            <span>${escapeHtml(item.label)}</span>
            <strong>${formatPercent(item.score)}</strong>
          </li>
        `
      )
      .join("");

    resultElement.innerHTML = `
      <div class="report-block">
        <h3>1. 입력 원문</h3>
        <p>${escapeHtml(result.original_text)}</p>
      </div>

      <div class="report-block">
        <h3>2. 요약문</h3>
        <p>${escapeHtml(result.summary)}</p>
      </div>

      <div class="report-block">
        <h3>3. 감정 분석</h3>
        <p>
          <strong>Label:</strong>
          ${escapeHtml(result.sentiment.label)}
        </p>
        <p>
          <strong>Score:</strong>
          ${formatPercent(result.sentiment.score)}
        </p>
      </div>

      <div class="report-block">
        <h3>4. 유해 표현 분석</h3>
        <p>
          <strong>Highest Risk:</strong>
          ${escapeHtml(result.toxicity.highest_label)}
        </p>
        <p>
          <strong>Score:</strong>
          ${formatPercent(result.toxicity.highest_score)}
        </p>

        <ul class="score-list">
          ${toxicityScores}
        </ul>
      </div>

      <div class="report-block judgment-block">
        <h3>5. 종합 판정</h3>
        <p>${escapeHtml(result.judgment)}</p>
      </div>
    `;
  }
});