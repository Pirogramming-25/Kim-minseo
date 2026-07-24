document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("sentiment-form");
  const input = document.getElementById("sentiment-input");
  const button = document.getElementById("sentiment-button");
  const loadingElement = document.getElementById(
    "sentiment-loading"
  );
  const errorElement = document.getElementById(
    "sentiment-error"
  );
  const resultSection = document.getElementById(
    "sentiment-result-section"
  );
  const resultElement = document.getElementById(
    "sentiment-result"
  );

  const anonymousHistory = [];

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
        "/sentiment/run/",
        {
          text,
        }
      );

      renderSentimentResult(data.result);
      resultSection.hidden = false;

      if (!window.isAuthenticated) {
        addAnonymousHistory(
          data.input_text,
          data.result
        );
      }
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

  function renderSentimentResult(result) {
    const scoreItems = result.all_scores
      .map(
        (item) => `
          <li>
            <span>${escapeHtml(
              capitalize(item.label)
            )}</span>
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
          <strong>감정:</strong>
          ${escapeHtml(capitalize(result.label))}
        </p>

        <p>
          <strong>신뢰도:</strong>
          ${formatPercent(result.score)}
        </p>
      </div>

      <h3>전체 레이블 점수</h3>

      <ul class="score-list">
        ${scoreItems}
      </ul>
    `;
  }

  function addAnonymousHistory(text, result) {
    anonymousHistory.unshift({
      text,
      label: result.label,
      score: result.score,
    });

    if (anonymousHistory.length > 5) {
      anonymousHistory.pop();
    }

    renderAnonymousHistory();
  }

  function renderAnonymousHistory() {
    const emptyElement = document.getElementById(
      "anonymous-history-empty"
    );
    const listElement = document.getElementById(
      "anonymous-history-list"
    );

    if (!emptyElement || !listElement) {
      return;
    }

    emptyElement.hidden = anonymousHistory.length > 0;

    listElement.innerHTML = anonymousHistory
      .map(
        (history) => `
          <article class="history-item">
            <p>
              <strong>입력:</strong>
              ${escapeHtml(truncateText(history.text, 120))}
            </p>

            <p>
              <strong>감정:</strong>
              ${escapeHtml(capitalize(history.label))}
            </p>

            <p>
              <strong>신뢰도:</strong>
              ${formatPercent(history.score)}
            </p>
          </article>
        `
      )
      .join("");
  }

  function capitalize(value) {
    if (!value) {
      return "";
    }

    return (
      value.charAt(0).toUpperCase()
      + value.slice(1).toLowerCase()
    );
  }

  function truncateText(value, maximumLength) {
    if (value.length <= maximumLength) {
      return value;
    }

    return `${value.slice(0, maximumLength)}...`;
  }
});