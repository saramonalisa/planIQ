document.addEventListener("DOMContentLoaded", function () {
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
