

document.addEventListener("DOMContentLoaded", () => {
  const editBtn = document.getElementById("editBtn");
  const editActions = document.getElementById("editActions");
  const inputs = document.querySelectorAll("#profileForm input");

  if (!editBtn) return;

  editBtn.addEventListener("click", () => {
    inputs.forEach(input => input.removeAttribute("readonly"));
    editBtn.classList.add("hidden");
    editActions.classList.remove("hidden");
  });
});
