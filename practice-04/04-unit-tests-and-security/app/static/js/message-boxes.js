document.querySelectorAll('[data-auto-show="true"]').forEach((element) => {
    bootstrap.Modal.getOrCreateInstance(element).show();
});

document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((element) => {
    bootstrap.Tooltip.getOrCreateInstance(element);
});
