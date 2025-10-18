 // Edit Profile toggle
  const editBtn = document.getElementById("editBtn");
  const profileForm = document.getElementById("profileForm");
  const editActions = document.getElementById("editActions");
  const cancelEdit = document.getElementById("cancelEdit");
  editBtn.addEventListener("click", () => {
    profileForm.querySelectorAll("input").forEach(input => input.removeAttribute("readonly"));
    editActions.classList.remove("hidden");
    editBtn.classList.add("hidden");
  });
  cancelEdit.addEventListener("click", () => {
    profileForm.querySelectorAll("input").forEach(input => input.setAttribute("readonly", true));
    editActions.classList.add("hidden");
    editBtn.classList.remove("hidden");
  });

  
