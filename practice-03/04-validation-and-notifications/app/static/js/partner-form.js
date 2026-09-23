(() => {
    const form = document.getElementById("partnerForm");
    if (!form) return;

    const phoneInput = form.querySelector("[data-phone-mask]");
    const formatPhone = (value) => {
        let digits = value.replace(/\D/g, "");
        if (!digits) return "";

        if (digits.startsWith("8")) {
            digits = `7${digits.slice(1)}`;
        } else if (!digits.startsWith("7")) {
            digits = `7${digits}`;
        }

        const subscriber = digits.slice(1, 11);
        let formatted = "+7";
        if (subscriber.length) formatted += ` (${subscriber.slice(0, 3)}`;
        if (subscriber.length >= 3) formatted += ")";
        if (subscriber.length > 3) formatted += ` ${subscriber.slice(3, 6)}`;
        if (subscriber.length > 6) formatted += `-${subscriber.slice(6, 8)}`;
        if (subscriber.length > 8) formatted += `-${subscriber.slice(8, 10)}`;
        return formatted;
    };

    phoneInput.value = formatPhone(phoneInput.value);
    phoneInput.addEventListener("input", () => {
        phoneInput.value = formatPhone(phoneInput.value);
    });
    phoneInput.addEventListener("keydown", (event) => {
        if (event.key === "Backspace" && phoneInput.value === "+7") {
            phoneInput.value = "";
        }
    });

    const cancelControls = document.querySelectorAll("[data-cancel-navigation]");
    const discardButton = document.getElementById("discardChangesButton");
    const warningElement = document.getElementById("warningMessageBox");
    const warningModal = bootstrap.Modal.getOrCreateInstance(warningElement);
    const initialFormData = new URLSearchParams(new FormData(form)).toString();
    let submitting = false;

    const isDirty = () => new URLSearchParams(new FormData(form)).toString() !== initialFormData;
    const leaveForm = () => {
        submitting = true;
        window.location.assign(form.dataset.cancelUrl);
    };

    form.addEventListener("submit", () => {
        submitting = true;
    });

    cancelControls.forEach((control) => {
        control.addEventListener("click", (event) => {
            event.preventDefault();
            if (isDirty()) {
                warningModal.show();
            } else {
                leaveForm();
            }
        });
    });

    discardButton.addEventListener("click", leaveForm);

    window.addEventListener("beforeunload", (event) => {
        if (!submitting && isDirty()) {
            event.preventDefault();
            event.returnValue = "";
        }
    });
})();
