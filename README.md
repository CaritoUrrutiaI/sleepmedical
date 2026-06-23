# sleepmedical

Copia local estática del sitio [sleepmedical.cl](https://www.sleepmedical.cl/), capturada como punto de partida para una serie de mejoras.

## Qué es esto

Espejo estático del sitio WordPress original, generado con `wget --mirror`. Es HTML/CSS/JS/imágenes servibles sin backend. **No incluye** PHP, base de datos, ni funcionalidad dinámica (formularios, carrito de la tienda, login). Esas piezas habrá que reconstruirlas o sustituirlas.

## Estructura

- `index.html` — portada
- `servicios/`, `producto/`, `tienda/`, `arriendo-equipos/`, `contacto-2/`, `categoria-producto/`, `marca/` — páginas del sitio
- `wp-content/`, `wp-includes/` — assets (temas, plugins, uploads) del WordPress original
- `index.html@p=NNN.html` — páginas que el sitio servía por query string `?p=NNN`
- `.nojekyll` — desactiva el procesamiento Jekyll de GitHub Pages (necesario por los nombres `wp-*` y `@`)

## Hosting

Publicado en GitHub Pages desde la rama `main` (raíz del repo).

## Origen

Capturado el 2026-06-23 con:

```
wget --mirror --convert-links --adjust-extension --page-requisites \
     --no-parent -e robots=off --restrict-file-names=windows \
     https://www.sleepmedical.cl/
```

Los enlaces internos fueron reescritos a rutas relativas para que el sitio funcione offline / en Pages.
