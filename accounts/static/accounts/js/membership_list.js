

document.addEventListener("click", function (e) {
 
  const open = e.target.closest("[data-modal-target]");
  if (open) {
    const id = open.getAttribute("data-modal-target");
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.remove("hidden");
      modal.classList.add("flex");
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


  if (
    e.target.classList &&
    e.target.classList.contains("fixed") &&
    e.target.classList.contains("inset-0")
  ) {
    const parent = e.target.closest(".fixed");
    if (parent) {
      parent.classList.add("hidden");
      parent.classList.remove("flex");
    }
  }
});
