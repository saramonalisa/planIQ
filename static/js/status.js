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
    const badges = document.querySelectorAll(`.status-badge[data-tarefa-id="${tarefaId}"]`);
    badges.forEach(badge => {
      badge.textContent = statusToLabel(status);
      badge.className = 'badge status-badge me-3 ' + statusToColor(status);
    });
  }

  document.body.addEventListener('click', function(e) {
    const button = e.target.closest('.btn-status');
    if (!button) return;

    const url = button.dataset.url;
    const status = button.dataset.status;
    if (!url || !status) return;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) throw new Error("Erro ao atualizar status");
      return response.json();
    })
    .then(data => {
      const tarefaId = data.id || data.tarefa_id;
      const novoStatus = data.status || data.novo_status;

      if (!tarefaId || !novoStatus) throw new Error('JSON retornado inválido');

      atualizarBadge(tarefaId, novoStatus);

      const parent = button.closest('li, .card-footer');
      if(parent) {
        const btns = parent.querySelectorAll('.btn-status');
        btns.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
      }
    })
    .catch(error => {
      alert("Erro ao atualizar o status. Veja o console para detalhes.");
      console.error(error);
    });
  });

  document.body.addEventListener('change', function (e) {
    const select = e.target.closest('.status-selector');
    if (!select) return;

    const tarefaId = select.dataset.tarefaId;
    const novoStatus = select.value;

    if (!tarefaId || !novoStatus) return;

    fetch(`/alterar_status_tarefa/${tarefaId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ status: novoStatus })
    })
    .then(response => {
      if (!response.ok) throw new Error("Erro ao atualizar status");
      return response.json();
    })
    .then(data => {
      const novo = data.status;
      atualizarBadge(tarefaId, novo);
    })
    .catch(error => {
      alert("Erro ao atualizar o status. Veja o console para detalhes.");
      console.error(error);
    });
  });

  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
      window.location.reload();
    }
  });

});
