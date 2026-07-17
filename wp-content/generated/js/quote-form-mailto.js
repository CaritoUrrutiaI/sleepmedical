(function () {
	function onSubmit(e) {
		var form = e.currentTarget;
		e.preventDefault();

		var nombreEl = form.querySelector('[name$="-nombre"]');
		var correoEl = form.querySelector('[name$="-correoelectrnico"]');
		var telefonoEl = form.querySelector('[name$="-telfono"]');
		var mensajeEl = form.querySelector('[name$="-mensaje"]');

		var nombre = nombreEl ? nombreEl.value.trim() : '';
		var correo = correoEl ? correoEl.value.trim() : '';
		var telefono = telefonoEl ? telefonoEl.value.trim() : '';
		var mensaje = mensajeEl ? mensajeEl.value.trim() : '';
		var producto = form.getAttribute('aria-label') || document.title;

		var asunto = 'Cotización ' + producto;
		var cuerpo =
			'Nombre: ' + nombre + '\n' +
			'Correo electrónico: ' + correo + '\n' +
			'Teléfono: ' + telefono + '\n' +
			'Mensaje: ' + mensaje + '\n' +
			'\n' +
			'Producto: ' + producto;

		window.location.href =
			'mailto:contacto@sleepmedical.cl' +
			'?subject=' + encodeURIComponent(asunto) +
			'&body=' + encodeURIComponent(cuerpo);
	}

	document.querySelectorAll('form.contact-form').forEach(function (form) {
		form.addEventListener('submit', onSubmit);
	});
})();
