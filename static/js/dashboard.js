(function () {
  const template = document.getElementById("inline-tester-template");

  if (!template) {
    return;
  }

  let activeEndpointRow = null;
  let activeTesterRow = null;

  function parseMethods(rawMethods) {
    if (!rawMethods) {
      return ["GET"];
    }

    try {
      const parsed = JSON.parse(rawMethods);
      if (Array.isArray(parsed) && parsed.length) {
        return parsed;
      }
    } catch (error) {
      return ["GET"];
    }

    return ["GET"];
  }

  function setMethodOptions(selectElement, methods) {
    const options = Array.from(new Set(methods || [])).filter(Boolean);
    const finalOptions = options.length ? options : ["GET"];

    selectElement.innerHTML = "";

    for (const method of finalOptions) {
      const option = document.createElement("option");
      option.value = method;
      option.textContent = method;
      selectElement.appendChild(option);
    }
  }

  function parseJsonField(value, label) {
    const trimmed = value.trim();
    if (!trimmed) {
      return {};
    }

    try {
      return JSON.parse(trimmed);
    } catch (error) {
      throw new Error(`${label} must be valid JSON.`);
    }
  }

  function normalizeUrl(path, query) {
    if (!path) {
      throw new Error("URL is required.");
    }

    const cleanPath = path.startsWith("http") || path.startsWith("/") ? path : `/${path}`;
    const queryText = query.trim().replace(/^\?/, "");

    if (!queryText) {
      return cleanPath;
    }

    const separator = cleanPath.includes("?") ? "&" : "?";
    return `${cleanPath}${separator}${queryText}`;
  }

  function safeJsonParse(value) {
    if (!value) {
      return null;
    }

    try {
      return JSON.parse(value);
    } catch (error) {
      return value;
    }
  }

  async function sendRequest(testerRoot) {
    const methodSelect = testerRoot.querySelector(".tester-method");
    const urlInput = testerRoot.querySelector(".tester-url");
    const queryInput = testerRoot.querySelector(".tester-query");
    const headersInput = testerRoot.querySelector(".tester-headers");
    const bodyInput = testerRoot.querySelector(".tester-body");
    const responseStatus = testerRoot.querySelector(".response-status");
    const responseTime = testerRoot.querySelector(".response-time");
    const responseBody = testerRoot.querySelector(".response-body");

    responseStatus.textContent = "Sending...";
    responseTime.textContent = "";
    responseBody.textContent = "";

    try {
      const method = methodSelect.value || "GET";
      const requestUrl = normalizeUrl(urlInput.value.trim(), queryInput.value);

      const headers = parseJsonField(headersInput.value, "Headers");
      if (typeof headers !== "object" || headers === null || Array.isArray(headers)) {
        throw new Error("Headers must be a JSON object.");
      }

      const requestOptions = {
        method,
        headers,
        credentials: "include",
      };

      const mayContainBody = !["GET", "HEAD"].includes(method.toUpperCase());
      const parsedBody = parseJsonField(bodyInput.value, "Body");
      const bodyHasContent = Object.keys(parsedBody).length > 0;

      if (mayContainBody && bodyHasContent) {
        const hasContentType = Object.keys(headers).some(
          (key) => key.toLowerCase() === "content-type"
        );
        if (!hasContentType) {
          headers["Content-Type"] = "application/json";
        }
        requestOptions.body = JSON.stringify(parsedBody);
      }

      const startTime = performance.now();
      const response = await fetch(requestUrl, requestOptions);
      const elapsed = Math.round(performance.now() - startTime);

      const responseText = await response.text();
      const responsePayload = safeJsonParse(responseText);
      const responseHeaders = {};

      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      responseStatus.textContent = `${response.status} ${response.statusText}`;
      responseTime.textContent = `${elapsed} ms`;
      responseBody.textContent = JSON.stringify(
        {
          request: {
            method,
            url: requestUrl,
            headers,
            body: requestOptions.body ? safeJsonParse(requestOptions.body) : null,
          },
          response: {
            ok: response.ok,
            status: response.status,
            headers: responseHeaders,
            body: responsePayload,
          },
        },
        null,
        2
      );
    } catch (error) {
      responseStatus.textContent = "Request failed";
      responseBody.textContent = error.message;
    }
  }

  function closeActiveTester() {
    if (activeEndpointRow) {
      activeEndpointRow.classList.remove("is-active");
      activeEndpointRow.setAttribute("aria-expanded", "false");
      activeEndpointRow = null;
    }

    if (activeTesterRow) {
      activeTesterRow.remove();
      activeTesterRow = null;
    }
  }

  function openInlineTester(endpointRow) {
    if (!endpointRow) {
      return;
    }

    if (activeEndpointRow === endpointRow) {
      closeActiveTester();
      return;
    }

    closeActiveTester();

    const testerRow = document.createElement("tr");
    testerRow.className = "tester-inline-row";

    const testerCell = document.createElement("td");
    testerCell.colSpan = endpointRow.children.length;

    testerCell.appendChild(template.content.cloneNode(true));
    testerRow.appendChild(testerCell);

    endpointRow.insertAdjacentElement("afterend", testerRow);

    const testerRoot = testerRow.querySelector(".inline-tester");
    const titleElement = testerRoot.querySelector(".inline-tester-title");
    const methodSelect = testerRoot.querySelector(".tester-method");
    const urlInput = testerRoot.querySelector(".tester-url");
    const queryInput = testerRoot.querySelector(".tester-query");
    const responseStatus = testerRoot.querySelector(".response-status");
    const responseTime = testerRoot.querySelector(".response-time");
    const responseBody = testerRoot.querySelector(".response-body");
    const sendButton = testerRoot.querySelector(".send-request");
    const closeButton = testerRoot.querySelector(".close-inline-tester");
    const bodyInput = testerRoot.querySelector(".tester-body");

    const methods = parseMethods(endpointRow.getAttribute("data-methods"));
    const endpointUrl = endpointRow.getAttribute("data-url") || "";
    const endpointName = endpointRow.getAttribute("data-endpoint") || "Endpoint";

    titleElement.textContent = `Test Endpoint: ${endpointName}`;
    setMethodOptions(methodSelect, methods);
    urlInput.value = endpointUrl;
    queryInput.value = "";
    responseStatus.textContent = `Ready: ${endpointUrl}`;
    responseTime.textContent = "";
    responseBody.textContent = "";

    sendButton.addEventListener("click", () => sendRequest(testerRoot));
    closeButton.addEventListener("click", closeActiveTester);

    bodyInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        sendRequest(testerRoot);
      }
    });

    activeEndpointRow = endpointRow;
    activeTesterRow = testerRow;
    activeEndpointRow.classList.add("is-active");
    activeEndpointRow.setAttribute("aria-expanded", "true");

    urlInput.focus();
  }

  document.querySelectorAll(".endpoint-row").forEach((row) => {
    row.addEventListener("click", () => {
      openInlineTester(row);
    });

    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openInlineTester(row);
      }
    });
  });
})();
