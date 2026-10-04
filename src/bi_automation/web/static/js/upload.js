document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const btnSubmit = document.getElementById('btn-submit');
    const form = document.getElementById('upload-form');

    function handleFile(file) {
        if (file) {
            fileName.textContent = file.name;
            fileName.style.display = 'block';
            btnSubmit.style.display = 'block';
            dropZone.style.borderColor = 'var(--blue)';
            dropZone.style.background = '#f0f6ff';
        }
    }

    fileInput.addEventListener('change', (e) => {
        handleFile(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFile(e.dataTransfer.files[0]);
        }
    });

    form.addEventListener('submit', () => {
        btnSubmit.textContent = 'Uploading...';
        btnSubmit.style.opacity = '0.7';
        btnSubmit.style.pointerEvents = 'none';
    });
});
