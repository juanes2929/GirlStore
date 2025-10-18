// JS del login: captura el submit, envía POST a /login
document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    fetch('/login', {
    method: 'POST',
    body: new FormData(e.target),
    credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
    if (data.success) {
        window.location.href = '/home'; // redirige a la interfaz
    } else {
        Swal.fire({
            title: "ATENCIÓN",
            text: `${data.message}`,
            icon: 'warning',
            confirmButtonColor: '#e62e7a',
            confirmButtonText: 'OK',

        })
    }
    });
});

