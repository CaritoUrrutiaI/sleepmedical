(function () {
	function buildBody(form) {
		var lines = [];
		form.querySelectorAll('.pagelayer-contact-holder input, .pagelayer-contact-holder textarea').forEach(function (field) {
			var label = field.getAttribute('placeholder') || field.getAttribute('name') || 'Campo';
			label = label.replace(/:\s*$/, '');
			lines.push(label + ': ' + field.value.trim());
		});
		return lines.join('\n');
	}

	function onSubmit(e) {
		e.preventDefault();
		var form = e.currentTarget;
		var cuerpo = buildBody(form);
		var asunto = 'Contacto desde sleepmedical.cl';

		window.location.href =
			'mailto:contacto@sleepmedical.cl' +
			'?subject=' + encodeURIComponent(asunto) +
			'&body=' + encodeURIComponent(cuerpo);
	}

	document.querySelectorAll('form.pagelayer-contact-form').forEach(function (form) {
		form.addEventListener('submit', onSubmit);
	});
})();
