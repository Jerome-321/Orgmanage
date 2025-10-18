function openCertificateModal(achievementId, fileUrl, deleteUrl) {
  const modal = document.getElementById('certificateModal');
  const content = document.getElementById('certificateContent');
  const deleteForm = document.getElementById('deleteAchievementForm');

  // Set delete form action
  deleteForm.action = deleteUrl;

  // Clear old content
  content.innerHTML = '';

  // If the file is PDF
  if (fileUrl.endsWith('.pdf')) {
    content.innerHTML = `
      <iframe src="${fileUrl}" width="100%" height="500px" class="rounded-lg border"></iframe>
    `;
  } else {
    // Image (jpg, png, etc.)
    content.innerHTML = `
      <img src="${fileUrl}" alt="Certificate" class="max-h-[500px] rounded-lg shadow">
    `;
  }

  // Show modal
  modal.classList.remove('hidden');
}

function closeCertificateModal() {
  document.getElementById('certificateModal').classList.add('hidden');
}


function openDeleteModal(achievementId) {
  const modal = document.getElementById("deleteAchievementModal");
  const form = document.getElementById("deleteAchievementForm");
  form.action = `/profile/delete-achievement/${achievementId}/`;
  modal.classList.remove("hidden");
}

function closeDeleteModal() {
  const modal = document.getElementById("deleteAchievementModal");
  modal.classList.add("hidden");
}