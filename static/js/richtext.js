document.addEventListener("DOMContentLoaded", function() {
    tinymce.init({
        selector: '#id_descricao',
        height: 300,
        menubar: false,
        branding: false,
        language: 'pt_BR',
        plugins: 'advlist autolink lists link image charmap \
                  searchreplace code fullscreen media table help wordcount autosave',
        toolbar: 'undo redo | removeformat | bold italic underline strikethrough \
                  | fontselect fontsizeselect forecolor backcolor | alignleft  aligncenter alignright alignjustify | outdent indent \
                  | bullist numlist checklist | table | image media | link unlink | restoredraft | hr subscript superscript charmap | code | fullscreen | searchreplace',
        elementpath: false,
        autosave_ask_before_unload: true,
        paste_data_images: true,
        automatic_uploads: true,
        file_picker_types: 'image',

        file_picker_callback: function(callback, value, meta) {
            if (meta.filetype === 'image') {
                const input = document.createElement('input');
                input.setAttribute('type', 'file');
                input.setAttribute('accept', 'image/*');
                input.setAttribute('multiple', '');

                input.onchange = function() {
                    const files = Array.from(this.files);

                    files.forEach(file => {
                        const reader = new FileReader();

                        reader.onload = function() {
                            const id = 'blobid' + (new Date()).getTime();
                            const blobCache = tinymce.activeEditor.editorUpload.blobCache;
                            const base64 = reader.result.split(',')[1];
                            const blobInfo = blobCache.create(id, file, base64);
                            blobCache.add(blobInfo);
                            callback(blobInfo.blobUri(), { title: file.name });
                        };

                        reader.readAsDataURL(file);
                    });
                };

                input.click();
            }
        },

        images_upload_handler: function (blobInfo, success, failure) {
            const formData = new FormData();
            formData.append('file', blobInfo.blob(), blobInfo.filename());

            fetch('/upload_image/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.location) {
                    success(data.location);
                } else {
                    failure('Erro ao enviar a imagem');
                }
            })
            .catch(err => failure('Erro ao enviar a imagem: ' + err.message));
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i=0; i<cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length+1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue;
}
