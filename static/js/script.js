document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('backup-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Evita o envio normal do formulário

        var formData = new FormData(this);
        var submitButton = document.getElementById('submit-button');
        var loading = document.getElementById('loading');

        // Exibe a animação de carregamento e oculta o botão de envio
        submitButton.style.display = 'none';
        loading.style.display = 'inline-block';

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Oculta a animação de carregamento e exibe o botão de envio
            loading.style.display = 'none';
            submitButton.style.display = 'inline-block';
            
            // Exibe a mensagem de sucesso
            alert('Backup realizado e enviado com sucesso!');
            // Recarrega a página após 2 segundos
            setTimeout(function() {
                location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error('Erro:', error);
            // Oculta a animação de carregamento e exibe o botão de envio
            loading.style.display = 'none';
            submitButton.style.display = 'inline-block';
            alert('Ocorreu um erro ao realizar o backup.');
        });
    });
});