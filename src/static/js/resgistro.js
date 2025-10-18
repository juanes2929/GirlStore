// JS del registro: envía el formulario como FormData a /registro
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".register-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Capturamos los datos del formulario
    const formData = new FormData(form);

    try {
      const response = await fetch("/registro", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        Swal.fire({
          icon: "success",
          title: "¡Registro exitoso!",
          text: data.message,
          showConfirmButton: false,
          timer: 2000,
        }).then(() => {
          // Redirigir después del mensaje
          window.location.href = data.href;
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: data.message || "Ocurrió un error inesperado.",
          confirmButtonColor: '#e62e7a',
        });
      }
    } catch (error) {
      console.error("Error al enviar el formulario:", error);
      Swal.fire({
        icon: "error",
        title: "Error del servidor",
        confirmButtonColor: '#e62e7a',
        text: "No se pudo conectar con el servidor.",
      });
    }
  });
});
