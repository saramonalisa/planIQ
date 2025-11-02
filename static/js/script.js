document.addEventListener("DOMContentLoaded", function () {

  function togglePasswordVisibility() {
    const passwordField = document.getElementById('id_password');
    const toggleButton = document.getElementById('togglePassword');
    
    if (passwordField.type === 'password') {
      passwordField.type = 'text';
      toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
      passwordField.type = 'password';
      toggleButton.innerHTML = '<i class="bi bi-eye"></i>';
    }
  }

  function toggleConfirmPasswordVisibility() {
    const confirmPasswordField = document.getElementById('id_confirm_password');
    const toggleButton = document.getElementById('toggleConfirmPassword');
    
    if (confirmPasswordField.type === 'password') {
      confirmPasswordField.type = 'text';
      toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
      confirmPasswordField.type = 'password';
      toggleButton.innerHTML = '<i class="bi bi-eye"></i>';
    }
  }

  function validateField(field, errorId, errorMessage) {
    const value = field.value.trim();
    const errorElement = document.getElementById(errorId);

    if (!value) {
      errorElement.innerText = errorMessage || "Este campo é obrigatório.";
      return false;
    }

    if (field.id === "id_email" && !/\S+@\S+\.\S+/.test(value)) {
      errorElement.innerText = "Por favor, insira um e-mail válido.";
      return false;
    }

    if (field.id === "id_password" && value.length < 6) {
      errorElement.innerText = "A senha deve ter pelo menos 6 caracteres, incluindo números e letras maiúsculas.";
      return false;
    }

    errorElement.innerText = "";
    return true;
  }

  function validatePasswordMatch() {
    const password = document.getElementById("id_password").value;
    const confirmPassword = document.getElementById("id_confirm_password").value;
    const errorElement = document.getElementById("confirmPasswordError");

    if (password !== confirmPassword) {
      errorElement.innerText = "As senhas não coincidem.";
      return false;
    } else {
      errorElement.innerText = "";
      return true;
    }
  }

  function validateForm() {
    let isValid = true;

    isValid &= validateField(document.getElementById("id_username"), "usernameError", "O nome de usuário é obrigatório.");
    isValid &= validateField(document.getElementById("id_email"), "emailError", "O e-mail é obrigatório.");
    isValid &= validateField(document.getElementById("id_password"), "passwordError", "A senha é obrigatória.");
    isValid &= validateField(document.getElementById("id_nome"), "nomeError", "O nome de exibição é obrigatório.");
    
    isValid &= validatePasswordMatch();

    return isValid;
  }

  document.querySelectorAll('input').forEach(input => {
    input.addEventListener('blur', function(event) {
      validateField(event.target, event.target.id + "Error");
      if (event.target.id === "id_password" || event.target.id === "id_confirm_password") {
        validatePasswordMatch();
      }
    });
  });

  document.getElementById("registrationForm").addEventListener("submit", function(event) {
    if (!validateForm()) {
      event.preventDefault();
    }
  });

  document.getElementById('togglePassword').addEventListener('click', togglePasswordVisibility);
  document.getElementById('toggleConfirmPassword').addEventListener('click', toggleConfirmPasswordVisibility);

  const toggleBtn = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const footer = document.querySelector('footer');
  const icon = toggleBtn.querySelector('i');
  const themeToggle = document.getElementById('themeToggle');
  const navbar = document.querySelector('nav.navbar');

  const updateIcon = (collapsed) => {
    icon.classList.toggle('bi-chevron-double-left', !collapsed);
    icon.classList.toggle('bi-chevron-double-right', collapsed);
  };

  const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  if (isCollapsed) {
    sidebar.classList.add('collapsed');
    mainContent.classList.add('collapsed');
    footer.classList.add('collapsed');
    navbar.classList.add('sidebar-collapsed');
    updateIcon(true);
  }

  toggleBtn.addEventListener('click', () => {
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
  });

  if (window.innerWidth < 768 && !isCollapsed) {
    sidebar.classList.add('collapsed');
    mainContent.classList.add('collapsed');
    footer.classList.add('collapsed');
    navbar.classList.add('sidebar-collapsed');
    updateIcon(true);
  }

  const applyTheme = (theme) => {
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      themeToggle.checked = true;
    } else {
      document.body.classList.remove('dark-mode');
      themeToggle.checked = false;
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

  themeToggle.addEventListener('change', () => {
    const isDark = themeToggle.checked;
    applyTheme(isDark ? 'dark' : 'light');
  });

});
