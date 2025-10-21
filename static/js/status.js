document.addEventListener('DOMContentLoaded', function () {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        }
      });
    }
    return cookieValue;
  }

  const csrfToken = getCookie('csrftoken');

  function statusToLabel(status) {
    switch (status) {
      case 'pendente': return 'Pendente';
      case 'em_progresso': return 'Em Progresso';
      case 'concluida': return 'Concluída';
      default: return '';
    }
  }

  function statusToColor(status) {
    switch (status) {
      case 'pendente': return 'bg-warning';
      case 'em_progresso': return 'bg-primary';
      case 'concluida': return 'bg-success';
      default: return '';
    }
  }

  function atualizarBadge(tarefaId, status) {
    const badges = document.querySelectorAll(`.status-selector[data-tarefa-id="${tarefaId}"]`);
    badges.forEach(select => {
      select.value = status; // atualiza o select visualmente
      select.className = 'form-select form-select-sm status-selector d-inline w-auto ' + statusToColor(status);
    });
  }

  // intercepta a mudança do select
  document.body.addEventListener('change', function (e) {
    const select = e.target.closest('.status-selector');
    if (!select) return;

    e.preventDefault(); // impede que o form submeta a página

    const tarefaId = select.dataset.tarefaId;
    const novoStatus = select.value;

    fetch(`/alterar_status_tarefa/${tarefaId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ status: novoStatus })
    })
    .then(response => response.json())
    .then(data => {
      atualizarBadge(tarefaId, data.status);
    })
    .catch(error => console.error('Erro ao atualizar status:', error));
  });
});
