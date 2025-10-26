function openCertificateModal(achievementId, fileUrl, deleteUrl) {
  const modal = document.getElementById('certificateModal');
  const content = document.getElementById('certificateContent');
  const deleteForm = document.getElementById('deleteAchievementForm');

  
  deleteForm.action = deleteUrl;

  
  content.innerHTML = '';

  
  if (fileUrl.endsWith('.pdf')) {
    content.innerHTML = `
      <iframe src="${fileUrl}" width="100%" height="500px" class="rounded-lg border"></iframe>
    `;
  } else {
    
    content.innerHTML = `
      <img src="${fileUrl}" alt="Certificate" class="max-h-[500px] rounded-lg shadow">
    `;
  }


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