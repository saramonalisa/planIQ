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

  function prioridadeToLabel(prioridade) {
    switch (prioridade) {
      case 'alta': return 'Alta';
      case 'media': return 'Média';
      case 'baixa': return 'Baixa';
      default: return '';
    }
  }

  function prioridadeToColor(prioridade) {
    switch (prioridade) {
      case 'alta': return 'bg-danger';
      case 'media': return 'bg-warning';
      case 'baixa': return 'bg-success';
      default: return '';
    }
  }

  function atualizarBadge(tarefaId, status, tipo) {
    const badges = document.querySelectorAll(`.${tipo}-badge[data-tarefa-id="${tarefaId}"]`);
    badges.forEach(badge => {
      if (tipo === 'status') {
        badge.textContent = statusToLabel(status);
        badge.className = 'badge status-badge me-3 ' + statusToColor(status);
      } else if (tipo === 'prioridade') {
        badge.textContent = prioridadeToLabel(status);
        badge.className = 'badge prioridade-badge me-3 ' + prioridadeToColor(status);
      }
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

      atualizarBadge(tarefaId, novoStatus, 'status');

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
    const select = e.target.closest('.prioridade-selector');
    if (!select) return;

    const tarefaId = select.dataset.tarefaId;
    const novaPrioridade = select.value;

    if (!tarefaId || !novaPrioridade) return;

    fetch(`/alterar_prioridade_tarefa/${tarefaId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ prioridade: novaPrioridade })
    })
    .then(response => {
      if (!response.ok) throw new Error("Erro ao atualizar prioridade");
      return response.json();
    })
    .then(data => {
      const novaPrioridade = data.prioridade;
      atualizarBadge(tarefaId, novaPrioridade, 'prioridade');
    })
    .catch(error => {
      alert("Erro ao atualizar a prioridade. Veja o console para detalhes.");
      console.error(error);
    });
  });

  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
      window.location.reload();
    }
  });

});
