document.getElementById("addAchievementBtn").addEventListener("click", openAddAchievementModal);

  
  window.addEventListener("click", function (event) {
    const modal = document.getElementById("addAchievementModal");
    if (event.target === modal) {
      closeAddAchievementModal();
    }
  });

  function openAddAchievementModal() {
    document.getElementById("addAchievementModal").classList.remove("hidden");
  }

  function closeAddAchievementModal() {
    document.getElementById("addAchievementModal").classList.add("hidden");
  }