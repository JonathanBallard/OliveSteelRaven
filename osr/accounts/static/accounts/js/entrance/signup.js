(function () {
  const inputs = document.querySelectorAll(
    'input[type="text"], input[type="email"], input[type="password"]'
  );
  inputs.forEach(i => i.classList.add("form-control"));

  const checks = document.querySelectorAll('input[type="checkbox"]');
  checks.forEach(c => c.classList.add("form-check-input"));
})();
