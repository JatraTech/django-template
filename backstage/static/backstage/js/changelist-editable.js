(function () {
  "use strict";

  function initChangelistEditableUx() {
    const form = document.getElementById("changelist-form");
    const footerSave = document.getElementById("changelist-footer-save");
    if (!form || !footerSave) {
      return;
    }

    function isEditableField(el) {
      if (!(el instanceof HTMLElement)) {
        return false;
      }
      if (el.classList.contains("action-select")) {
        return false;
      }
      if (el.closest(".action-checkbox-column")) {
        return false;
      }
      const tag = el.tagName;
      if (tag !== "INPUT" && tag !== "SELECT" && tag !== "TEXTAREA") {
        return false;
      }
      if (el.type === "hidden") {
        return false;
      }
      return true;
    }

    function getEditableFields() {
      return Array.from(form.querySelectorAll("input, select, textarea")).filter(
        isEditableField
      );
    }

    function readFieldValue(el) {
      if (el instanceof HTMLInputElement && el.type === "checkbox") {
        return el.checked;
      }
      return el.value;
    }

    const initialSnapshot = new Map();
    for (const el of getEditableFields()) {
      if (el instanceof HTMLInputElement && el.type === "checkbox") {
        initialSnapshot.set(el, el.defaultChecked);
      } else {
        initialSnapshot.set(el, el.defaultValue);
      }
    }

    function formIsDirty() {
      for (const [el, initial] of initialSnapshot) {
        if (readFieldValue(el) !== initial) {
          return true;
        }
      }
      return false;
    }

    function syncEditableSaveUi() {
      if (formIsDirty()) {
        footerSave.classList.remove("hidden");
      } else {
        footerSave.classList.add("hidden");
      }
    }

    form.addEventListener("change", function (event) {
      if (isEditableField(event.target)) {
        syncEditableSaveUi();
      }
    });

    form.addEventListener("input", function (event) {
      if (isEditableField(event.target)) {
        syncEditableSaveUi();
      }
    });

    form.addEventListener("submit", function () {
      const rows = form.querySelectorAll("#result_list tbody tr");
      for (const row of rows) {
        row.classList.add("backstage-row-save-flash");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChangelistEditableUx);
  } else {
    initChangelistEditableUx();
  }
})();
