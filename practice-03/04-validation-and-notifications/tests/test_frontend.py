from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_dirty_tracking_compares_initial_form_data_and_guards_navigation():
    script = (ROOT / "app/static/js/partner-form.js").read_text()

    assert "new FormData(form)" in script
    assert "initialFormData" in script
    assert "isDirty()" in script
    assert "warningModal.show()" in script
    assert 'querySelectorAll("[data-cancel-navigation]")' in script
    assert 'form.addEventListener("submit"' in script
    assert 'window.addEventListener("beforeunload"' in script
    assert "submitting = true" in script


def test_phone_mask_normalizes_russian_numbers_before_dirty_snapshot():
    script = (ROOT / "app/static/js/partner-form.js").read_text()

    assert 'form.querySelector("[data-phone-mask]")' in script
    assert 'value.replace(/\\D/g, "")' in script
    assert 'digits.startsWith("8")' in script
    assert "digits.slice(1, 11)" in script
    assert script.index("phoneInput.value = formatPhone") < script.index("initialFormData")


def test_all_message_boxes_have_titles_roles_aria_and_inline_icons():
    template = (ROOT / "app/templates/_message_boxes.html").read_text()

    for kind, title in (
        ("error", "Ошибка"),
        ("warning", "Предупреждение"),
        ("information", "Информация"),
    ):
        assert f'id="{kind}MessageBox"' in template
        assert f'id="{kind}MessageBoxTitle"' in template
        assert title in template
    assert template.count('aria-modal="true"') == 3
    assert template.count('role="alertdialog"') == 2
    assert "<use href=\"#icon-" in template


def test_icons_are_local_svg_symbols_not_icon_cdn():
    base = (ROOT / "app/templates/base.html").read_text()

    for icon in ("error", "warning", "information"):
        assert f'id="icon-{icon}"' in base
    assert "bootstrap-icons" not in base
