

document.addEventListener("DOMContentLoaded", function () {
  
  const editorEl = document.getElementById("editor");
  if (editorEl) {
    window.quill = new Quill("#editor", { theme: "snow" });
  }

  
  document.addEventListener("click", function (e) {
    
    const open = e.target.closest("[data-modal-target]");
    if (open) {
      const id = open.getAttribute("data-modal-target");
      const modal = document.getElementById(id);
      if (modal) {
        modal.classList.remove("hidden");
        modal.classList.add("flex");

        
        const content = modal.querySelector("div");
        if (content) {
          content.classList.remove("scale-95");
          content.classList.add("scale-100");
        }
      }
      return;
    }

    
    const close = e.target.closest("[data-modal-close]");
    if (close) {
      const id = close.getAttribute("data-modal-close");
      const modal = document.getElementById(id);
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
      return;
    }
  });
});
