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

  const statusColors = {
    'pendente': '#fce8a5',
    'em_progresso': '#a5e1e9',
    'concluida': '#d5edb9'
  };

  const statusTextos = {
    'pendente': 'pendente',
    'em_progresso': 'em andamento',
    'concluida': 'concluída'
  };

  function aplicarEstiloConcluida(elemento, isConcluida) {
    const titulo = elemento.querySelector('strong');
    if (titulo) {
      if (isConcluida) {
        titulo.classList.add('text-decoration-line-through');
        titulo.style.opacity = '0.7';
      } else {
        titulo.classList.remove('text-decoration-line-through');
        titulo.style.opacity = '1';
      }
    }
  }

  function atualizarContadorSecao(secao, contagem) {
    const header = secao.previousElementSibling;
    if (header && header.tagName === 'H4') {
      const spanAnterior = header.querySelector('.contador-tarefas');
      if (spanAnterior) {
        spanAnterior.remove();
      }
      
      const contador = document.createElement('span');
      contador.className = 'contador-tarefas badge bg-secondary ms-2';
      contador.textContent = contagem;
      header.appendChild(contador);
    }
  }

  function moverTarefaParaSecao(tarefaItem, novoStatus) {
    const secaoAtual = tarefaItem.closest('.secao-tarefas');
    const secaoAtualStatus = secaoAtual.dataset.status;
    
    if (secaoAtualStatus === novoStatus) {
      return;
    }
    
    const novaSecao = document.getElementById(`secao-${novoStatus}`);
    
    if (!novaSecao) {
      console.error(`Seção para status ${novoStatus} não encontrada`);
      return;
    }
    
    tarefaItem.remove();
    
    const mensagemSemTarefas = novaSecao.querySelector('.sem-tarefas');
    if (mensagemSemTarefas) {
      mensagemSemTarefas.remove();
    }
    
    aplicarEstiloConcluida(tarefaItem, novoStatus === 'concluida');
    
    novaSecao.appendChild(tarefaItem);
    
    verificarSecaoVazia(secaoAtual);
    
    if (typeof atualizarContadorSecao === 'function') {
      const tarefasAtual = secaoAtual.querySelectorAll('.tarefa-item').length;
      const tarefasNova = novaSecao.querySelectorAll('.tarefa-item').length;
      atualizarContadorSecao(secaoAtual, tarefasAtual);
      atualizarContadorSecao(novaSecao, tarefasNova);
    }
    
    tarefaItem.style.animation = 'fadeIn 0.5s ease';
  }

  function verificarSecaoVazia(secao) {
    const temTarefas = secao.querySelector('.tarefa-item');
    const temMensagem = secao.querySelector('.sem-tarefas');
    const status = secao.dataset.status;
    
    if (!temTarefas && !temMensagem) {
      const mensagem = document.createElement('li');
      mensagem.className = 'list-group-item text-center text-muted sem-tarefas py-3';
      
      let texto = '';
      switch(status) {
        case 'pendente':
          texto = 'Nenhuma tarefa pendente.';
          break;
        case 'em_progresso':
          texto = 'Nenhuma tarefa em andamento.';
          break;
        case 'concluida':
          texto = 'Nenhuma tarefa concluída.';
          break;
        default:
          texto = 'Nenhuma tarefa.';
      }
      
      mensagem.textContent = texto;
      secao.appendChild(mensagem);
    } else if (temTarefas && temMensagem) {
      temMensagem.remove();
    }
  }

  function atualizarSelectStatus(tarefaId, status) {
    const selects = document.querySelectorAll(`.status-selector[data-tarefa-id="${tarefaId}"]`);
    selects.forEach(select => {
      select.value = status;
      select.style.backgroundColor = statusColors[status] || '#ffffff';
    });
  }

  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0.5; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .tarefa-item {
      transition: all 0.3s ease;
    }
    
    .status-selector {
      transition: background-color 0.3s ease;
    }
    
    .contador-tarefas {
      font-size: 0.8rem;
      vertical-align: middle;
    }
  `;
  document.head.appendChild(style);

  document.body.addEventListener('change', function (e) {
    const selectStatus = e.target.closest('.status-selector');
    
    if (selectStatus) {
      e.preventDefault();
      
      const tarefaId = selectStatus.dataset.tarefaId;
      const novoStatus = selectStatus.value;
      const tarefaItem = selectStatus.closest('.tarefa-item');
      const valorAntigo = selectStatus.dataset.oldValue || selectStatus.value;
      
      if (!['pendente', 'em_progresso', 'concluida'].includes(novoStatus)) {
        console.error('Status inválido:', novoStatus);
        selectStatus.value = valorAntigo;
        return;
      }
      
      selectStatus.disabled = true;
      
      const loadingIndicator = document.createElement('span');
      loadingIndicator.className = 'spinner-border spinner-border-sm ms-2';
      loadingIndicator.role = 'status';
      selectStatus.parentNode.appendChild(loadingIndicator);
      
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
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        atualizarSelectStatus(data.id, data.status);
        
        moverTarefaParaSecao(tarefaItem, data.status);
        
        selectStatus.dataset.oldValue = data.status;
      })
      .catch(error => {
        console.error('Erro ao atualizar status:', error);
        selectStatus.value = valorAntigo;
        alert('Erro ao atualizar o status. Tente novamente.');
      })
      .finally(() => {
        loadingIndicator.remove();
        selectStatus.disabled = false;
      });
    }
  });

  document.body.addEventListener('focus', function(e) {
    const selectStatus = e.target.closest('.status-selector');
    if (selectStatus) {
      selectStatus.dataset.oldValue = selectStatus.value;
    }
  });

  function inicializar() {
    document.querySelectorAll('.status-selector').forEach(select => {
      const status = select.value;
      select.style.backgroundColor = statusColors[status] || '#ffffff';
    });
    
    document.querySelectorAll('.secao-tarefas').forEach(secao => {
      verificarSecaoVazia(secao);
    });
    
    document.querySelectorAll('#secao-concluida .tarefa-item').forEach(item => {
      aplicarEstiloConcluida(item, true);
    });
  }

  inicializar();
});