// Add Bootstrap classes to forms from allauth's views
(function () {
    const email = document.getElementById("{{ form.login.id_for_label }}");
    const pw = document.getElementById("{{ form.password.id_for_label }}");
    if (email) email.classList.add("form-control");
    if (pw) pw.classList.add("form-control");
})();
