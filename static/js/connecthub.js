/* ============================================================================
   CONNECTHUB MAIN JAVASCRIPT
   Loaded after Bootstrap 5 JS bundle in base.html
   No framework dependency – plain JS, works with Django template rendering
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Auto-dismiss flash messages after 5 seconds ──────────────────── */
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  /* ── 2. Avatar preview before upload (profile_edit.html) ─────────────── */
  const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
  if (avatarInput) {
    avatarInput.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (!file) return;

      // Basic client-side validation (server still validates – this is UX only)
      const maxSizeMB = 5;
      if (file.size > maxSizeMB * 1024 * 1024) {
        alert('Image is too large. Please choose a file under ' + maxSizeMB + 'MB.');
        avatarInput.value = '';
        return;
      }

      const reader = new FileReader();
      reader.onload = function (ev) {
        let preview = document.getElementById('avatar-preview');
        if (!preview) {
          preview = document.createElement('img');
          preview.id = 'avatar-preview';
          preview.className = 'rounded-circle mb-2';
          preview.style.width = '80px';
          preview.style.height = '80px';
          preview.style.objectFit = 'cover';
          avatarInput.parentElement.insertBefore(preview, avatarInput);
        }
        preview.src = ev.target.result;
      };
      reader.readAsDataURL(file);
    });
  }

  /* ── 3. Debounced live search on the Members directory ────────────────── */
  const searchInput = document.querySelector('input[name="q"]');
  if (searchInput && searchInput.form) {
    let debounceTimer;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        // Only auto-submit if the user paused typing for 600ms
        // and has typed at least 2 characters (or cleared the field)
        if (searchInput.value.length === 0 || searchInput.value.length >= 2) {
          searchInput.form.submit();
        }
      }, 600);
    });
  }

  /* ── 4. Bootstrap tooltip initialization (for icon-only buttons) ──────── */
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipTriggerList.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ── 5. Confirm before destructive actions (delete account, delete post) */
  const confirmForms = document.querySelectorAll('form[data-confirm]');
  confirmForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const message = form.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  /* ── 6. Character counter for bio textarea (max 500 chars per Day 1 model) */
  const bioField = document.querySelector('textarea[name="bio"]');
  if (bioField) {
    const maxLen = 500;
    const counter = document.createElement('small');
    counter.className = 'form-text text-muted d-block text-end';
    bioField.parentElement.appendChild(counter);

    function updateCounter() {
      const remaining = maxLen - bioField.value.length;
      counter.textContent = remaining + ' characters remaining';
      counter.classList.toggle('text-danger', remaining < 0);
    }
    bioField.addEventListener('input', updateCounter);
    updateCounter();
  }

});
