(() => {
    const phoneInput = document.querySelector("[data-phone-mask]");
    if (!phoneInput) return;

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
})();
