// Script pour l'application DPMG Coyah
document.addEventListener('DOMContentLoaded', function() {
    // Activer tous les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activer les popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Gestion des alertes temporaires
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-temporary');
        alerts.forEach(function(alert) {
            // Créer un élément Bootstrap alert
            var bsAlert = new bootstrap.Alert(alert);
            // Le fermer après un délai
            setTimeout(function() {
                bsAlert.close();
            }, 5000); // 5 secondes
        });
    }, 0);

    // Validation des formulaires côté client
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Fonction pour prévisualiser les images avant upload
    const fileInputs = document.querySelectorAll('.file-input-preview');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.dataset.preview;
            const preview = document.getElementById(previewId);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Filtres dynamiques pour les tableaux
    const tableFilter = document.getElementById('table-filter');
    if (tableFilter) {
        tableFilter.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.querySelector('.table-filterable');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                const cells = row.querySelectorAll('td');
                let found = false;

                cells.forEach(function(cell) {
                    if (cell.textContent.toLowerCase().indexOf(searchText) > -1) {
                        found = true;
                    }
                });

                if (found) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Validation sécurisée des fichiers côté client
    const secureFileInputs = document.querySelectorAll('.secure-file-input');
    const allowedExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'];
    const maxFileSize = 10 * 1024 * 1024; // 10MB

    secureFileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            const errorContainer = document.getElementById(this.dataset.error || 'file-error');
            
            if (!errorContainer) return;
            errorContainer.textContent = '';
            
            if (files.length > 0) {
                const file = files[0];
                const fileExt = file.name.split('.').pop().toLowerCase();
                
                // Vérifier l'extension
                if (!allowedExtensions.includes(fileExt)) {
                    errorContainer.textContent = 'Type de fichier non autorisé. Extensions autorisées: ' + allowedExtensions.join(', ');
                    this.value = ''; // Effacer la sélection
                    return;
                }
                
                // Vérifier la taille
                if (file.size > maxFileSize) {
                    errorContainer.textContent = 'Le fichier est trop volumineux. Taille maximale: 10MB';
                    this.value = ''; // Effacer la sélection
                    return;
                }
            }
        });
    });
});
