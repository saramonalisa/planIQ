document.addEventListener("DOMContentLoaded", function () {
  function togglePasswordVisibility() {
    const passwordField = document.getElementById('id_password');
    const toggleButton = document.getElementById('togglePassword');
    
    if (passwordField && toggleButton) {
      if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleButton.innerHTML = '<i class="bi bi-eye-slash text-light"></i>';
      } else {
        passwordField.type = 'password';
        toggleButton.innerHTML = '<i class="bi bi-eye text-light"></i>';
      }
    }
  }

  function toggleConfirmPasswordVisibility() {
    const confirmPasswordField = document.getElementById('id_confirm_password');
    const toggleButton = document.getElementById('toggleConfirmPassword');
    
    if (confirmPasswordField && toggleButton) {
      if (confirmPasswordField.type === 'password') {
        confirmPasswordField.type = 'text';
        toggleButton.innerHTML = '<i class="bi bi-eye-slash text-light"></i>';
      } else {
        confirmPasswordField.type = 'password';
        toggleButton.innerHTML = '<i class="bi bi-eye text-light"></i>';
      }
    }
  }

  const togglePasswordButton = document.getElementById('togglePassword');
  if (togglePasswordButton) {
    togglePasswordButton.addEventListener('click', togglePasswordVisibility);
  }

  const toggleConfirmPasswordButton = document.getElementById('toggleConfirmPassword');
  if (toggleConfirmPasswordButton) {
    toggleConfirmPasswordButton.addEventListener('click', toggleConfirmPasswordVisibility);
  }


  const toggleBtn = document.getElementById('toggleSidebar');
  if (toggleBtn) {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const footer = document.querySelector('footer');
    const icon = toggleBtn.querySelector('i');
    const navbar = document.querySelector('nav.navbar');

    const updateIcon = (collapsed) => {
      if (icon) {
        icon.classList.toggle('bi-chevron-double-left', !collapsed);
        icon.classList.toggle('bi-chevron-double-right', collapsed);
      }
    };

    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed && sidebar && mainContent && footer) {
      sidebar.classList.add('collapsed');
      mainContent.classList.add('collapsed');
      footer.classList.add('collapsed');
      navbar.classList.add('sidebar-collapsed');
      updateIcon(true);
    }

    toggleBtn.addEventListener('click', () => {
      if (sidebar && mainContent && footer) {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('collapsed');
        footer.classList.toggle('collapsed');

        const collapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebar-collapsed', collapsed);
        updateIcon(collapsed);

        if (collapsed) {
          navbar.classList.add('sidebar-collapsed');
        } else {
          navbar.classList.remove('sidebar-collapsed');
        }
      }
    });

    if (window.innerWidth < 768 && !isCollapsed) {
      if (sidebar && mainContent && footer && navbar) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('collapsed');
        footer.classList.add('collapsed');
        navbar.classList.add('sidebar-collapsed');
        updateIcon(true);
      }
    }
  }

  /* const applyTheme = (theme) => {
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('theme', theme);
  };

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    applyTheme('dark');
  } else {
    applyTheme('light');
  }

  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('change', () => {
      const isDark = themeToggle.checked;
      applyTheme(isDark ? 'dark' : 'light');
    });
  } */

});
