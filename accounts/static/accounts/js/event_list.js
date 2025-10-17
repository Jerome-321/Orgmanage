function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const createEventForm = document.getElementById("createEventForm");
  if (createEventForm) {
    createEventForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const form = e.target;
      const formData = new FormData(form);

      // clear old errors
      form.querySelectorAll(".error-message").forEach(div => div.textContent = "");

      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const data = await response.json();

      if (data.success) {
        closeModal("modalCreate");
        location.reload();
      } else if (data.errors) {
        Object.entries(data.errors).forEach(([field, messages]) => {
          const errorDiv = form.querySelector(`[data-error-for="${field}"]`);
          if (errorDiv) errorDiv.textContent = messages.join(", ");
        });
      }
    });
  }
});

const openBtn = document.getElementById('openScannerBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const modal = document.getElementById('qrModal');
    const resultDisplay = document.getElementById('result');
    let html5QrCode;

    // Open modal
    openBtn.addEventListener('click', () => {
      modal.classList.remove('hidden');
      startScanner();
    });

    // Close modal
    closeBtn.addEventListener('click', () => {
      modal.classList.add('hidden');
      stopScanner();
    });

    function startScanner() {
      html5QrCode = new Html5Qrcode("qr-reader");
      Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
          html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: 250 },
            onScanSuccess
          );
        }
      });
    }

    function stopScanner() {
      if (html5QrCode) {
        html5QrCode.stop().then(() => {
          console.log("Camera stopped.");
        });
      }
    }

    function onScanSuccess(decodedText) {
      fetch("{% url 'scan_qr' %}", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": "{{ csrf_token }}"
        },
        body: new URLSearchParams({ qr_data: decodedText })
      })
      .then(res => res.json())
      .then(data => {
        resultDisplay.innerText = data.message;
        modal.classList.add('hidden');
        stopScanner();
      });
    }