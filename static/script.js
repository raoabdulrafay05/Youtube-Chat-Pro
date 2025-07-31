document.addEventListener("DOMContentLoaded", () => {
  const urlInput = document.querySelector(".input-url");
  const questionInput = document.querySelector(".input-question");
  const resultBox = document.querySelector(".result-box");
  const loadingWrapper = document.querySelector(".loading-wrapper");
  const progressWrapper = document.querySelector(".progress-wrapper");
  const progressFill = document.querySelector(".progress-fill");
  const progressPercent = document.querySelector(".progress-percent");

  function simulateProgress(duration = 4000) {
    let percent = 0;
    progressWrapper.style.display = "block";
    progressFill.style.width = "0%";
    progressPercent.textContent = "0%";

    const interval = setInterval(() => {
      percent += Math.random() * 10;
      if (percent >= 100) {
        percent = 100;
        clearInterval(interval);
      }
      progressFill.style.width = percent + "%";
      progressPercent.textContent = Math.floor(percent) + "%";
    }, duration / 30);
  }

  async function postToAPI(endpoint, payload) {
    try {
      const response = await fetch(`/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Fetch error:", error);
      return { error: "This video is not available in english caption" };
    }
  }

  async function handleAction(endpoint, payload, resultKey, emptyMessage) {
    loadingWrapper.style.display = "block";
    progressWrapper.style.display = "block";
    resultBox.value = "";
    simulateProgress();

    const res = await postToAPI(endpoint, payload);

    loadingWrapper.style.display = "none";
    progressWrapper.style.display = "none";
    resultBox.value = res[resultKey] || res.error || emptyMessage;
  }

  document.querySelector(".btn-summary").addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) return (resultBox.value = "Please enter a YouTube URL.");
    await handleAction("summary", { url }, "summary", "No summary available.");
  });

  document.querySelector(".btn-notes").addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) return (resultBox.value = "Please enter a YouTube URL.");
    await handleAction("notes", { url }, "notes", "No notes available.");
  });

  document
    .querySelector(".btn-question")
    .addEventListener("click", async () => {
      const url = urlInput.value.trim();
      if (!url) return (resultBox.value = "Please enter a YouTube URL.");
      await handleAction(
        "questions",
        { url },
        "questions",
        "No questions generated."
      );
    });

  document.querySelector(".btn-answer").addEventListener("click", async () => {
    const url = urlInput.value.trim();
    const question = questionInput.value.trim();
    if (!url || !question) {
      return (resultBox.value = "Please enter both a URL and a question.");
    }
    await handleAction(
      "answer",
      { url, question },
      "answer_to_question",
      "No answer generated."
    );
  });
});
