// CarePoint HMS Client-side JavaScript Helpers

document.addEventListener('DOMContentLoaded', function () {
  // 1. Automatic alert dismiss after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // 2. Real-time client-side table filter helper
  const searchInputs = document.querySelectorAll('.table-search-input');
  searchInputs.forEach(function (input) {
    input.addEventListener('keyup', function () {
      const filterValue = this.value.toLowerCase();
      const targetTableId = this.getAttribute('data-table-id');
      const table = document.getElementById(targetTableId);
      if (!table) return;

      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filterValue) ? '' : 'none';
      });
    });
  });

  // 3. Confirmation for destructive actions (e.g. Delete, Discharge)
  const confirmActions = document.querySelectorAll('[data-confirm]');
  confirmActions.forEach(function (element) {
    element.addEventListener('click', function (e) {
      const message = this.getAttribute('data-confirm') || 'Are you sure you want to perform this action?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // 4. Show / Hide Password Toggle
  const toggleButtons = document.querySelectorAll('.toggle-password-btn');
  toggleButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const icon = this.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
  });

  // 5. Password Strength Meter Feedback
  const passwordInputs = document.querySelectorAll('.password-input');
  passwordInputs.forEach(function (pwdInput) {
    const meter = pwdInput.closest('form')?.querySelector('.password-meter');
    if (!meter) return;

    pwdInput.addEventListener('input', function () {
      const val = this.value;
      let score = 0;
      if (val.length >= 6) score += 25;
      if (val.length >= 10) score += 25;
      if (/[A-Z]/.test(val)) score += 25;
      if (/[0-9!@#$%^&*]/.test(val)) score += 25;

      meter.style.width = score + '%';
      if (score <= 25) {
        meter.className = 'progress-bar password-meter bg-danger';
      } else if (score <= 50) {
        meter.className = 'progress-bar password-meter bg-warning';
      } else if (score <= 75) {
        meter.className = 'progress-bar password-meter bg-info';
      } else {
        meter.className = 'progress-bar password-meter bg-success';
      }
    });
  });
});
