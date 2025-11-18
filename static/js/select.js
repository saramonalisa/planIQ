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

  function statusToColor(status) {
    switch (status) {
      case 'pendente': return 'bg-warning';
      case 'em_progresso': return 'bg-primary';
      case 'concluida': return 'bg-success';
      default: return '';
    }
  }

  function prioridadeToColor(prioridade) {
    switch (prioridade) {
      case 'alta': return 'bg-danger'; 
      case 'media': return 'bg-warning';
      case 'baixa': return 'bg-success';
      case 'sem_prioridade': return 'bg-secondary';
      default: return '';
    }
  }

  function atualizarBadge(tarefaId, status) {
    const badges = document.querySelectorAll(`.status-selector[data-tarefa-id="${tarefaId}"]`);
    badges.forEach(select => {
      select.value = status;
      select.className = 'form-select form-select-sm status-selector d-inline w-auto ' + statusToColor(status);
    });
  }

  function atualizarPrioridade(tarefaId, prioridade) {
    const selects = document.querySelectorAll(`.prioridade-selector[data-tarefa-id="${tarefaId}"]`);
    selects.forEach(select => {
      select.value = prioridade;
      select.className = 'form-select form-select-sm prioridade-selector d-inline w-auto ' + prioridadeToColor(prioridade);
    });
  }

  document.body.addEventListener('change', function (e) {
    const selectStatus = e.target.closest('.status-selector');
    const selectPrioridade = e.target.closest('.prioridade-selector');

    if (selectStatus) {
      e.preventDefault();
      const tarefaId = selectStatus.dataset.tarefaId;
      const novoStatus = selectStatus.value;

      fetch(`/tarefas/alterar_status/${tarefaId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ status: novoStatus })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Falha ao atualizar o status');
        }
        return response.json();
      })
      .then(data => {
        atualizarBadge(tarefaId, data.status);
      })
      .catch(error => console.error('Erro ao atualizar status:', error));
    }

    if (selectPrioridade) {
      e.preventDefault();
      const tarefaId = selectPrioridade.dataset.tarefaId;
      const novaPrioridade = selectPrioridade.value;

      fetch(`/tarefas/alterar_prioridade/${tarefaId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ prioridade: novaPrioridade })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Falha ao atualizar a prioridade');
        }
        return response.json();
      })
      .then(data => {
        atualizarPrioridade(tarefaId, data.prioridade);
      })
      .catch(error => console.error('Erro ao atualizar prioridade:', error));
    }
  });
});
