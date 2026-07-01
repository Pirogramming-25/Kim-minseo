document.querySelectorAll(".form-row").forEach((row) => {
  const control = row.querySelector("input, select, textarea");

  if (!control) {
    return;
  }

  row.addEventListener("pointerdown", (event) => {
    if (event.target.closest("input, select, textarea, button, a")) {
      return;
    }

    event.preventDefault();
    control.focus();

    if (control.matches("input[type='text'], textarea")) {
      const cursorPosition = control.value.length;
      control.setSelectionRange(cursorPosition, cursorPosition);
    }
  });
});
