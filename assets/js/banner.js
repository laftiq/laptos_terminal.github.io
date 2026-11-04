document.getElementById("copy").addEventListener("click", async () => {
  const field = document.getElementById("embed"),
    status = document.getElementById("copy-status");
  try {
    await navigator.clipboard.writeText(field.value);
    status.textContent = "Copied.";
  } catch {
    field.focus();
    field.select();
    status.textContent = "Select and copy the HTML above.";
  }
});
