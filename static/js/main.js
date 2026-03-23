// eS@deq - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Confirmation for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = button.getAttribute('data-confirm') || 'Êtes-vous sûr de vouloir supprimer cet élément?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // File input custom styling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Aucun fichier sélectionné';
            const label = e.target.nextElementSibling;
            if (label && label.classList.contains('help-text')) {
                label.textContent = 'Fichier sélectionné: ' + fileName;
            }
        });
    });

    // Table row hover effect
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    tableRows.forEach(function(row) {
        row.style.cursor = 'pointer';
    });

    // PDF download without navigation/blank tab
    const pdfLinks = document.querySelectorAll('.js-pdf-download');
    pdfLinks.forEach(function(link) {
        link.addEventListener('click', async function(e) {
            e.preventDefault();
            const url = link.getAttribute('href');
            const fallbackName = link.getAttribute('data-filename') || 'programme.pdf';

            try {
                const response = await fetch(url, { credentials: 'same-origin' });
                if (!response.ok) {
                    window.location.href = url;
                    return;
                }
                const contentType = (response.headers.get('Content-Type') || '').toLowerCase();
                if (!contentType.includes('application/pdf')) {
                    window.location.href = url;
                    return;
                }

                let filename = fallbackName;
                const dispo = response.headers.get('Content-Disposition') || response.headers.get('content-disposition');
                if (dispo) {
                    const match = dispo.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
                    if (match && match[1]) {
                        filename = decodeURIComponent(match[1].replace(/"/g, '').trim());
                    }
                }

                const blob = await response.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = blobUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(blobUrl);
            } catch (err) {
                window.location.href = url;
            }
        });
    });
});
