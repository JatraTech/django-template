(function () {
  const DESKTOP_WIDTH = 1280;
  const DESKTOP_HEIGHT = 720;
  const TABLET_WIDTH = 768;
  const TABLET_HEIGHT = 1024;
  const MIN_WIDTH = 320;
  const MAX_WIDTH = 1920;
  const MIN_HEIGHT = 480;
  const MAX_HEIGHT = 1200;
  const VIEWPORT_STORAGE_KEY = "backstagePreviewViewport";

  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function loadStoredViewport() {
    try {
      const raw = sessionStorage.getItem(VIEWPORT_STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (
        typeof parsed.width === "number" &&
        typeof parsed.height === "number"
      ) {
        return {
          width: clamp(parsed.width, MIN_WIDTH, MAX_WIDTH),
          height: clamp(parsed.height, MIN_HEIGHT, MAX_HEIGHT),
        };
      }
    } catch (_error) {
      return null;
    }
    return null;
  }

  function saveStoredViewport(width, height) {
    try {
      sessionStorage.setItem(
        VIEWPORT_STORAGE_KEY,
        JSON.stringify({ width, height }),
      );
    } catch (_error) {
      // Ignore storage failures.
    }
  }

  function initPreviewPanel() {
    const panel = document.getElementById("backstage-preview-panel");
    const iframe = document.getElementById("backstage-preview-iframe");
    const overlay = document.getElementById("backstage-preview-overlay");
    if (!panel || !iframe || !overlay) return;

    const inlineHost = panel.querySelector("[data-preview-inline-host]");
    const overlayHost = overlay.querySelector("[data-preview-overlay-host]");
    const frameWrap = panel.querySelector("[data-preview-frame-wrap]");
    const expandBtn = panel.querySelector("[data-preview-expand]");
    const expandIcon = expandBtn?.querySelector("[data-preview-expand-icon]");
    const collapseTargets = overlay.querySelectorAll(
      "[data-preview-collapse], [data-preview-close]",
    );
    const refreshBtns = document.querySelectorAll(".backstage-preview-refresh");
    const widthBtns = document.querySelectorAll("[data-preview-width]");

    const storedViewport = loadStoredViewport();
    let customWidth = storedViewport?.width ?? DESKTOP_WIDTH;
    let customHeight = storedViewport?.height ?? DESKTOP_HEIGHT;
    let previewMode = "desktop";
    let isExpanded = false;
    let isResizing = false;

    function getActiveFrameWrap() {
      return document.querySelector("[data-preview-frame-wrap]");
    }

    function getSizeLabels() {
      return document.querySelectorAll("[data-preview-size-label]");
    }

    function updateSizeLabels() {
      const label = `${customWidth} × ${customHeight}`;
      getSizeLabels().forEach((element) => {
        element.textContent = label;
      });
    }

    function getViewportDimensions() {
      if (previewMode === "mobile") {
        return null;
      }
      if (previewMode === "responsive") {
        return { width: customWidth, height: customHeight };
      }
      if (previewMode === "tablet") {
        return { width: TABLET_WIDTH, height: TABLET_HEIGHT };
      }
      return { width: DESKTOP_WIDTH, height: DESKTOP_HEIGHT };
    }

    function clearFrameWrapLayout(activeFrameWrap) {
      activeFrameWrap.style.width = "";
      activeFrameWrap.style.height = "";
      activeFrameWrap.style.aspectRatio = "";
      activeFrameWrap.style.transform = "";
      activeFrameWrap.style.transformOrigin = "";
    }

    function updatePreviewScale() {
      const activeFrameWrap = getActiveFrameWrap();
      const activeScaler = activeFrameWrap?.querySelector("[data-preview-scaler]");
      const activeIframe = activeFrameWrap?.querySelector(".backstage-preview-iframe");
      const activeHost = activeFrameWrap?.parentElement;
      if (!activeFrameWrap || !activeScaler || !activeIframe) return;

      const isOverlayResponsive = isExpanded && previewMode === "responsive";

      if (previewMode === "mobile") {
        activeScaler.style.transform = "none";
        activeScaler.style.transformOrigin = "";
        activeScaler.style.width = "";
        activeScaler.style.height = "";
        activeIframe.style.width = "";
        activeIframe.style.height = "";
        clearFrameWrapLayout(activeFrameWrap);
        return;
      }

      const viewport = getViewportDimensions();
      if (!viewport) return;

      if (isOverlayResponsive) {
        activeFrameWrap.style.width = `${viewport.width}px`;
        activeFrameWrap.style.height = `${viewport.height}px`;
        activeFrameWrap.style.aspectRatio = "auto";

        activeScaler.style.width = `${viewport.width}px`;
        activeScaler.style.height = `${viewport.height}px`;
        activeIframe.style.width = `${viewport.width}px`;
        activeIframe.style.height = `${viewport.height}px`;
        activeScaler.style.transform = "none";
        activeScaler.style.transformOrigin = "";

        const containerWidth = activeHost?.clientWidth || 0;
        const containerHeight = activeHost?.clientHeight || 0;
        if (!containerWidth || !containerHeight) return;

        const widthScale = containerWidth / viewport.width;
        const heightScale = containerHeight / viewport.height;
        const scale = Math.min(widthScale, heightScale);

        activeFrameWrap.style.transformOrigin = "center center";
        activeFrameWrap.style.transform =
          scale < 1 ? `scale(${scale})` : "none";
        return;
      }

      activeFrameWrap.style.transform = "";
      activeFrameWrap.style.transformOrigin = "";

      const containerWidth = activeFrameWrap.clientWidth;
      const containerHeight = activeFrameWrap.clientHeight;
      if (!containerWidth || !containerHeight) return;

      const widthScale = containerWidth / viewport.width;
      const heightScale = containerHeight / viewport.height;
      let scale = Math.min(widthScale, heightScale);

      if (!isExpanded) {
        scale = Math.min(scale, 1);
      }

      const scaledW = viewport.width * scale;
      const scaledH = viewport.height * scale;
      const offsetX = (containerWidth - scaledW) / 2;
      const offsetY = (containerHeight - scaledH) / 2;

      activeScaler.style.width = `${viewport.width}px`;
      activeScaler.style.height = `${viewport.height}px`;
      activeIframe.style.width = `${viewport.width}px`;
      activeIframe.style.height = `${viewport.height}px`;
      activeScaler.style.transformOrigin = "top left";
      activeScaler.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;

      if (previewMode === "responsive") {
        activeFrameWrap.style.width = "100%";
        activeFrameWrap.style.height = "";
        activeFrameWrap.style.aspectRatio = `${viewport.width} / ${viewport.height}`;
      } else {
        clearFrameWrapLayout(activeFrameWrap);
      }
    }

    function syncWidthButtonState() {
      widthBtns.forEach((btn) => {
        const isActive = btn.dataset.previewWidth === previewMode;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }

    function setPreviewMode(mode) {
      previewMode = mode;
      frameWrap?.classList.toggle("is-mobile", mode === "mobile");
      frameWrap?.classList.toggle("is-desktop", mode === "desktop");
      frameWrap?.classList.toggle("is-tablet", mode === "tablet");
      frameWrap?.classList.toggle("is-responsive", mode === "responsive");
      syncWidthButtonState();
      updateSizeLabels();
      updatePreviewScale();
    }

    function refreshPreview() {
      const baseUrl = panel.dataset.previewUrl;
      if (!baseUrl) return;
      const separator = baseUrl.includes("?") ? "&" : "?";
      iframe.src = `${baseUrl}${separator}_t=${Date.now()}`;
    }

    function expandPreview() {
      if (isExpanded || !frameWrap || !overlayHost || !inlineHost) return;

      overlayHost.appendChild(frameWrap);
      overlay.hidden = false;
      overlay.setAttribute("aria-hidden", "false");
      document.body.classList.add("backstage-preview-expanded");
      panel.classList.add("is-collapsed");
      isExpanded = true;

      if (expandBtn) {
        expandBtn.setAttribute("aria-expanded", "true");
      }
      if (expandIcon) {
        expandIcon.textContent = "close_fullscreen";
      }

      updatePreviewScale();
    }

    function collapsePreview() {
      if (!isExpanded || !frameWrap || !inlineHost) return;

      inlineHost.appendChild(frameWrap);
      overlay.hidden = true;
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("backstage-preview-expanded");
      panel.classList.remove("is-collapsed");
      isExpanded = false;

      if (expandBtn) {
        expandBtn.setAttribute("aria-expanded", "false");
      }
      if (expandIcon) {
        expandIcon.textContent = "open_in_full";
      }

      updatePreviewScale();
    }

    function toggleExpand() {
      if (isExpanded) {
        collapsePreview();
      } else {
        expandPreview();
      }
    }

    function initResizeHandles() {
      const handles = frameWrap?.querySelectorAll("[data-preview-resize]");
      if (!handles?.length) return;

      handles.forEach((handle) => {
        handle.addEventListener("pointerdown", (event) => {
          if (previewMode !== "responsive") return;

          event.preventDefault();
          isResizing = true;
          document.body.classList.add("backstage-preview-resizing");

          const axis = handle.dataset.previewResize;
          const startX = event.clientX;
          const startY = event.clientY;
          const startWidth = customWidth;
          const startHeight = customHeight;

          handle.setPointerCapture(event.pointerId);

          function onPointerMove(moveEvent) {
            const deltaX = moveEvent.clientX - startX;
            const deltaY = moveEvent.clientY - startY;

            if (axis === "e" || axis === "se") {
              customWidth = clamp(startWidth + deltaX, MIN_WIDTH, MAX_WIDTH);
            }
            if (axis === "s" || axis === "se") {
              customHeight = clamp(startHeight + deltaY, MIN_HEIGHT, MAX_HEIGHT);
            }

            updateSizeLabels();
            updatePreviewScale();
          }

          function onPointerUp(upEvent) {
            isResizing = false;
            document.body.classList.remove("backstage-preview-resizing");
            handle.releasePointerCapture(upEvent.pointerId);
            handle.removeEventListener("pointermove", onPointerMove);
            handle.removeEventListener("pointerup", onPointerUp);
            handle.removeEventListener("pointercancel", onPointerUp);
            saveStoredViewport(customWidth, customHeight);
            updatePreviewScale();
          }

          handle.addEventListener("pointermove", onPointerMove);
          handle.addEventListener("pointerup", onPointerUp);
          handle.addEventListener("pointercancel", onPointerUp);
        });
      });
    }

    expandBtn?.addEventListener("click", toggleExpand);

    collapseTargets.forEach((target) => {
      target.addEventListener("click", collapsePreview);
    });

    refreshBtns.forEach((btn) => {
      btn.addEventListener("click", refreshPreview);
    });

    widthBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        setPreviewMode(btn.dataset.previewWidth);
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isExpanded && !isResizing) {
        collapsePreview();
      }
    });

    initResizeHandles();
    setPreviewMode("desktop");

    function showPreviewError(message) {
      if (!inlineHost) return;
      let banner = panel.querySelector("[data-preview-error]");
      if (!banner) {
        banner = document.createElement("div");
        banner.dataset.previewError = "1";
        banner.className = "backstage-preview-error";
        banner.setAttribute("role", "status");
        inlineHost.prepend(banner);
      }
      banner.textContent = message;
      banner.hidden = false;
    }

    function hidePreviewError() {
      const banner = panel.querySelector("[data-preview-error]");
      if (banner) {
        banner.hidden = true;
      }
    }

    iframe.addEventListener("load", () => {
      hidePreviewError();
    });

    iframe.addEventListener("error", () => {
      showPreviewError(
        "Preview could not load. Start the public website and confirm the frontend URL under System → Admin appearance.",
      );
    });

    window.addEventListener("resize", debounce(updatePreviewScale, 100));

    if (panel.dataset.autoRefreshPreview === "1") {
      const changeForm = document.querySelector("form[id$='_form']");
      changeForm?.addEventListener("submit", () => {
        window.setTimeout(refreshPreview, 2000);
      });
    }

    const activeFrameWrap = getActiveFrameWrap();
    if (typeof ResizeObserver !== "undefined" && activeFrameWrap) {
      const observer = new ResizeObserver(debounce(updatePreviewScale, 50));
      observer.observe(activeFrameWrap);
      if (overlayHost) {
        observer.observe(overlayHost);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPreviewPanel);
  } else {
    initPreviewPanel();
  }
})();
