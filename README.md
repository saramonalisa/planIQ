# PlanIQ

## Sobre o projeto
A proposta do PlanIQ é servir como um gerenciador de tarefas inteligente voltado especialmente para estudantes, com o objetivo de otimizar a organização das atividades acadêmicas e promover uma gestão eficiente do tempo. 

Este projeto foi desenvolvido para a matéria de Programação e Desenvolvimento de Sistemas para Internet do curso de Informática para Internet, com o objetivo de aplicar, de forma prática, os conhecimentos adquiridos ao longo da formação técnica integrada.

## Funcionalidades

- Autenticação de usuários (registro, login, logout);
- Gerenciamento de tarefas, períodos e matérias;
- Visualização de tarefas em formato de listas e calendário.

**Para instruções detalhadas**, consulte o [Manual do Usuário](https://saramonalisa.github.io/planIQ/)

## Tecnologias Utilizadas
- Python
- Django
- JavaScript
- HTML5
- CSS3
- Banco de dados: MySQL
- Outras bibliotecas: Bootstrap, TinyMCE

## Pré-requisitos
- Python 3.8 ou superior
- MySQL
- Git

## Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/saramonalisa/planIQ.git
cd planiq
```

### 2. Crie e ative um ambiente virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
Este comando irá instalar todas as bibliotecas necessárias listadas no arquivo `requirements.txt`.

### 4. Crie as variáveis de ambiente

```bash
python scripts/env_gen.py
```

### 5. Execute as migrações do banco de dados

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. (Opcional) Crie um superusuário

Para acessar o painel administrativo do Django:

```bash
python manage.py createsuperuser
```

### 7. Execute o servidor
```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## Estrutura do Projeto

```
planIQ/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── templatetags/
│   │   └── dict_filters.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docs/
│   └── manual/
│       └── index.html
├── manage.py
├── requirements.txt
├── scripts/
│   └── env_gen.py
├── static/
│   ├── assets/
│   │   └── svg/
│   │       ├── logo.svg
│   │       └── logo_google.svg
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── richtext.js
│   │   ├── script.js
│   │   └── select.js
│   └── tinymce/
│       └── js/
│           └── tinymce/
│               ├── tinymce.d.ts
│               └── tinymce.min.js
├── templates/
│   ├── academico/
│   │   ├── materias/
│   │   │   ├── detalhar_materia.html
│   │   │   ├── minhas_materias.html
│   │   │   └── nova_materia.html
│   │   └── periodos/
│   │       ├── detalhar_periodo.html
│   │       ├── meus_periodos.html
│   │       └── novo_periodo.html
│   ├── base.html
│   ├── home.html
│   ├── index.html
│   ├── partials/
│   │   ├── _badge.html
│   │   ├── _calendario.html
│   │   ├── _list_tarefas_dia.html
│   │   ├── _lista_tarefas.html
│   │   ├── _mensagens.html
│   │   ├── _navbar.html
│   │   ├── _select_priority.html
│   │   ├── _select_status.html
│   │   ├── _sidebar.html
│   │   └── _tarefa_count.html
│   ├── profile/
│   │   ├── cadastro.html
│   │   ├── configuracoes.html
│   │   └── login.html
│   ├── registration/
│   │   ├── password_reset_complete.html
│   │   ├── password_reset_confirm.html
│   │   ├── password_reset_done.html
│   │   ├── password_reset_email.html
│   │   ├── password_reset_form.html
│   │   └── password_reset_subject.html
│   └── tarefas/
│       ├── calendario.html
│       ├── detalhar_tarefa.html
│       ├── editar_tarefa.html
│       ├── listar_tarefa.html
│       ├── minhas_tarefas.html
│       ├── nova_tarefa.html
│       └── tarefas_do_dia.html
└── usuarios/
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── migrations/
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    └── views.py

```

---

## Autores
- [Maria Clara Ferreira da Silva](https://github.com/Clara66666)
- [Maria Gabriely Souza de Moura](https://github.com/gaabyssouza)
- [Sara Monalisa Carlos da Silva](https://github.com/saramonalisa)

## Orientadora
- Fernanda Lígia
