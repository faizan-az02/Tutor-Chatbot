(function () {
  const messagesEl = document.getElementById("messages");
  const typingEl = document.getElementById("typing");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("send-btn");

  function hideTyping() {
    if (typingEl) {
      typingEl.hidden = true;
      typingEl.style.display = "none";
    }
  }

  function showTyping() {
    if (!typingEl) return;
    typingEl.hidden = false;
    typingEl.style.display = "";
    messagesEl.appendChild(typingEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  const chatWelcome = document.getElementById("chat-welcome");

  function addMessage(content, role, options) {
    hideTyping();
    if (chatWelcome) chatWelcome.classList.add("hidden");
    const div = document.createElement("div");
    div.className = "message " + role;
    if (options && options.error) div.classList.add("error");

    const inner = document.createElement("div");
    inner.className = "message-content";
    inner.textContent = content;
    div.appendChild(inner);

    if (options && options.youtubeLinks && options.youtubeLinks.length) {
      const linksDiv = document.createElement("div");
      linksDiv.className = "youtube-links";
      const ul = document.createElement("ul");
      options.youtubeLinks.forEach(function (link) {
        if (!link.href) return;
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = link.href;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = link.title || link.href;
        li.appendChild(a);
        ul.appendChild(li);
      });
      linksDiv.appendChild(ul);
      div.appendChild(linksDiv);
    }

    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setLoading(loading) {
    sendBtn.disabled = loading;
    if (loading) showTyping();
  }

  function fetchGreeting() {
    setLoading(true);
    fetch("/api/greeting")
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load greeting");
        return res.json();
      })
      .then(function (data) {
        addMessage(data.greeting || "What would you like to learn today?", "bot");
      })
      .catch(function (err) {
        addMessage("Could not load greeting. " + err.message, "bot", { error: true });
      })
      .finally(function () {
        setLoading(false);
      });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const query = (input.value || "").trim();
    if (!query) return;

    addMessage(query, "user");
    input.value = "";
    input.style.height = "auto";

    setLoading(true);
    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) {
            var msg = (data && (data.answer || data.error)) || "Request failed";
            throw new Error(msg);
          }
          return data;
        });
      })
      .then(function (data) {
        addMessage(data.answer || "No response.", "bot", {
          youtubeLinks: data.youtube_links || null,
        });
      })
      .catch(function (err) {
        addMessage("Something went wrong. " + (err.message || "Request failed"), "bot", { error: true });
      })
      .finally(function () {
        setLoading(false);
      });
  });

  // Auto-resize textarea
  input.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 160) + "px";
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event("submit"));
    }
  });

  fetchGreeting();

  // Ingest PDFs modal
  const ingestModal = document.getElementById("ingest-modal");
  const addPdfsBtn = document.getElementById("add-pdfs-btn");
  const ingestModalClose = document.getElementById("ingest-modal-close");
  const ingestModalCancel = document.getElementById("ingest-modal-cancel");
  const ingestModalBackdrop = document.getElementById("ingest-modal-backdrop");
  const ingestFileInput = document.getElementById("ingest-file-input");
  const ingestFileList = document.getElementById("ingest-file-list");
  const ingestProgress = document.getElementById("ingest-progress");
  const ingestProgressLog = document.getElementById("ingest-progress-log");
  const ingestBtn = document.getElementById("ingest-btn");

  function openIngestModal() {
    if (ingestModal) ingestModal.hidden = false;
    if (ingestFileList) ingestFileList.textContent = "";
    if (ingestProgressLog) ingestProgressLog.textContent = "";
    if (ingestProgress) ingestProgress.hidden = true;
    if (ingestFileInput) ingestFileInput.value = "";
    if (ingestBtn) ingestBtn.disabled = true;
  }

  function closeIngestModal() {
    if (ingestModal) ingestModal.hidden = true;
  }

  function appendProgress(text) {
    if (!ingestProgressLog) return;
    ingestProgressLog.textContent += (ingestProgressLog.textContent ? "\n" : "") + text;
    ingestProgressLog.scrollTop = ingestProgressLog.scrollHeight;
  }

  function setIngestButtonEnabled(enabled) {
    if (ingestBtn) ingestBtn.disabled = !enabled;
  }

  if (addPdfsBtn) addPdfsBtn.addEventListener("click", openIngestModal);
  if (ingestModalClose) ingestModalClose.addEventListener("click", closeIngestModal);
  if (ingestModalCancel) ingestModalCancel.addEventListener("click", closeIngestModal);
  if (ingestModalBackdrop) ingestModalBackdrop.addEventListener("click", closeIngestModal);

  if (ingestFileInput) {
    ingestFileInput.addEventListener("change", function () {
      var files = this.files;
      if (!ingestFileList) return;
      ingestFileList.textContent = "";
      if (files && files.length > 0) {
        for (var i = 0; i < files.length; i++) {
          var li = document.createElement("div");
          li.textContent = files[i].name;
          ingestFileList.appendChild(li);
        }
        setIngestButtonEnabled(true);
      } else {
        setIngestButtonEnabled(false);
      }
    });
  }

  if (ingestBtn) {
    ingestBtn.addEventListener("click", function () {
      var files = ingestFileInput && ingestFileInput.files;
      if (!files || files.length === 0) return;

      ingestBtn.disabled = true;
      ingestProgress.hidden = false;
      ingestProgressLog.textContent = "";
      var pagesBarWrap = document.getElementById("ingest-pages-bar-wrap");
      var pagesBarFill = document.getElementById("ingest-pages-bar-fill");
      var pagesBarText = document.getElementById("ingest-pages-bar-text");
      if (pagesBarWrap) pagesBarWrap.hidden = true;
      if (pagesBarFill) pagesBarFill.style.width = "0%";
      if (pagesBarText) pagesBarText.textContent = "0 pages";

      appendProgress("Uploading " + files.length + " file(s)...");

      var formData = new FormData();
      for (var i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      fetch("/api/upload-pdfs", {
        method: "POST",
        body: formData,
      })
        .then(function (res) {
          return res.json().then(function (data) {
            if (!res.ok) throw new Error(data.error || "Upload failed");
            return data;
          });
        })
        .then(function (data) {
          appendProgress("Uploaded: " + (data.saved && data.saved.length ? data.saved.join(", ") : "—"));
          appendProgress("Running database ingestion...");
          return fetch("/api/ingest-stream");
        })
        .then(function (response) {
          if (!response.ok) throw new Error("Ingest failed");
          var reader = response.body.getReader();
          var decoder = new TextDecoder();
          var buffer = "";

          function read() {
            return reader.read().then(function (result) {
              if (result.done) return;
              buffer += decoder.decode(result.value, { stream: true });
              var events = buffer.split("\n\n");
              buffer = events.pop() || "";
              for (var i = 0; i < events.length; i++) {
                var dataLine = events[i].split("\n").filter(function (l) { return l.startsWith("data: "); })[0];
                if (dataLine) {
                  try {
                    var payload = JSON.parse(dataLine.slice(6));
                    if (payload.progress_pages !== undefined) {
                      var wrap = document.getElementById("ingest-pages-bar-wrap");
                      var fill = document.getElementById("ingest-pages-bar-fill");
                      var text = document.getElementById("ingest-pages-bar-text");
                      if (wrap) wrap.hidden = false;
                      var current = payload.progress_pages;
                      var total = payload.total_pages;
                      var pct = total && total > 0
                        ? Math.min(100, Math.round((current / total) * 100))
                        : Math.min(90, current * 3);
                      if (fill) fill.style.width = pct + "%";
                      if (text) text.textContent = total ? current + " / " + total + " pages" : current + " pages";
                    }
                    if (payload.line) appendProgress(payload.line);
                  } catch (e) {}
                }
              }
              return read();
            });
          }
          return read();
        })
        .then(function () {
          appendProgress("Done.");
          if (ingestFileInput) ingestFileInput.value = "";
          if (ingestFileList) ingestFileList.textContent = "";
          setIngestButtonEnabled(false);
        })
        .catch(function (err) {
          appendProgress("Error: " + err.message);
          setIngestButtonEnabled(true);
        });
    });
  }
})();
