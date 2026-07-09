# sleepmedical

Copia local estática del sitio [sleepmedical.cl](https://www.sleepmedical.cl/), capturada como punto de partida para una serie de mejoras.

## Qué es esto

Espejo estático del sitio WordPress original, generado con `wget --mirror`. Es HTML/CSS/JS/imágenes servibles sin backend. **No incluye** PHP, base de datos, ni funcionalidad dinámica (formularios, carrito de la tienda, login). Esas piezas habrá que reconstruirlas o sustituirlas.

## Estructura

- `index.html` — portada
- `servicios/`, `producto/`, `tienda/`, `arriendo-equipos/`, `contacto-2/`, `categoria-producto/`, `marca/` — páginas del sitio
- `wp-content/`, `wp-includes/` — assets (temas, plugins, uploads) del WordPress original
- `wp-content/generated/` — CSS/JS que WordPress inyectaba inline y repetía byte a byte en cada página (boilerplate de core/plugins/tema). Se extrajo a archivos compartidos, referenciados con `<link>`/`<script src>`, para eliminar esa duplicación sin cambiar el resultado renderizado. Ver "Limpieza" más abajo.
- `index.html@p=NNN.html` — páginas que el sitio servía por query string `?p=NNN`
- `.nojekyll` — desactiva el procesamiento Jekyll de GitHub Pages (necesario por los nombres `wp-*` y `@`)

### Código propio vs. vendored

Casi todo el árbol (`wp-includes/`, y dentro de `wp-content/`: `plugins/`, la mayor parte de `themes/` y `uploads/`) es código de WordPress core, plugins de terceros (Jetpack, Pagelayer, WooCommerce, WP WhatsApp) y librerías vendored — no se debe "limpiar" ni reescribir, es contenido de terceros congelado en el mirror.

El único código propio del sitio (tema `popularfx`, personalizaciones sobre el theme base) son estos 4 archivos:

- `wp-content/themes/popularfx/js/navigation.js@ver=1.2.7`
- `wp-content/themes/popularfx/sidebar.css@ver=1.2.7.css`
- `wp-content/themes/popularfx/woocommerce.css@ver=1.2.7.css`
- `wp-content/uploads/popularfx-templates/medlife/style.css@ver=1.2.7.css`

## Limpieza (rama `refactor/cleanup-wordpress-mirror`)

El mirror venía con mucha duplicación típica de un sitio WordPress exportado a estático: cada página HTML repetía, byte a byte, los mismos bloques `<style>`/`<script>` de boilerplate (core, tema, WooCommerce, bloques de Gutenberg). Se hizo una limpieza mecánica y verificada, sin tocar apariencia ni navegación:

- **19 bloques `<style id="...">` idénticos** en 68 páginas (~1.2 MB de duplicación) se extrajeron a `wp-content/generated/css/*.css`, referenciados con `<link rel='stylesheet'>` en el mismo lugar del `<head>` donde vivía el `<style>` original (mismo orden de cascada).
- **6 bloques `<script id="...">` clásicos idénticos** (config de WooCommerce/WhatsApp, sin `type` especial) se extrajeron a `wp-content/generated/js/*.js`, referenciados con `<script src>`. Se dejaron inline a propósito los bloques `type="application/json"` / `type="importmap"` (un `src` externo no se llega a cargar para esos tipos, según el spec de HTML) y los que legítimamente varían por página (nonces, IDs de producto, etc.).
- Cada extracción se verificó comparando el contenido extraído byte a byte contra el original, y resolviendo las rutas relativas generadas en distintas profundidades de carpeta.
- En el código propio (los 4 archivos de arriba) se eliminaron reglas CSS muertas (bloques vacíos, una declaración comentada) y se fusionaron dos bloques `.comment-metadata` redundantes en `sidebar.css`.

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
