# sleepmedical

Copia local estática del sitio [sleepmedical.cl](https://www.sleepmedical.cl/), capturada como punto de partida para una serie de mejoras.

## Qué es esto

Espejo estático del sitio WordPress original, generado con `wget --mirror`. Es HTML/CSS/JS/imágenes servibles sin backend. **No incluye** PHP, base de datos, ni funcionalidad dinámica (formularios, carrito de la tienda, login). Esas piezas habrá que reconstruirlas o sustituirlas.

## Estructura

- `index.html` — portada
- `servicios/`, `producto/`, `tienda/`, `arriendo-equipos/`, `contacto-2/`, `categoria-producto/`, `marca/` — páginas del sitio
- `wp-content/`, `wp-includes/` — assets (temas, plugins, uploads) del WordPress original
- `wp-content/generated/` — CSS/JS que WordPress inyectaba inline y repetía byte a byte en cada página (boilerplate de core/plugins/tema). Se extrajo a archivos compartidos, referenciados con `<link>`/`<script src>`, para eliminar esa duplicación sin cambiar el resultado renderizado. Ver "Limpieza" más abajo.
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
- Cada extracción se verificó comparando el contenido extraído byte a byte contra el original, resolviendo las rutas relativas generadas en distintas profundidades de carpeta, y confirmando que ningún `href`/`src` interno del sitio quedó roto (se revisaron ~7300 referencias).
- En el código propio (los 4 archivos de arriba) se eliminaron reglas CSS muertas (bloques vacíos, una declaración comentada) y se fusionaron dos bloques `.comment-metadata` redundantes en `sidebar.css`.
- La extracción quedó automatizada en `scripts/extract_inline_assets.py` (sin dependencias, solo `stdlib`). Si se vuelve a capturar el sitio con `wget --mirror`, correr `python3 scripts/extract_inline_assets.py` de nuevo aplica la misma limpieza sobre el HTML nuevo (es idempotente: si ya no queda nada duplicado, no toca nada). `--dry-run` reporta sin escribir, `--clean` borra `wp-content/generated/` antes de regenerar para no dejar archivos huérfanos de una corrida anterior.
- Se eliminaron las 25 páginas `index.html@p=NNN.html`: eran el mismo post/página que su URL bonita equivalente (el mirror las capturó dos veces porque `wget` siguió tanto la permalink limpia como el shortlink `?p=NNN` que WordPress agrega a cada página). Se confirmó comparando `og:url` y el ID de post embebido en cada una: contenido idéntico salvo la profundidad de rutas relativas. Se reescribieron ~1000 enlaces internos (menú, "productos relacionados", `action` de formularios, `<link rel="canonical">`) que apuntaban a esas URLs para que apunten directo a la URL bonita, y de paso se corrigió un bug preexistente del sitio original: el ítem de menú activo no se resaltaba cuando se entraba por la URL `?p=NNN` porque WordPress comparaba contra la permalink, no contra el ID. Verificado con un barrido de ~4650 referencias internas en las 83 páginas restantes: cero enlaces rotos.
- Se confirmó por análisis de alcanzabilidad (`href`/`src`/`action`/`srcset`/`data-src`/`url()` en CSS, incluyendo URLs absolutas a `sleepmedical.cl`) que no queda ningún archivo huérfano en el repo.
- Se quitó el polyfill de emojis de WordPress (`wp-emoji-settings` + `wp-emoji-loader`, ~2.5KB de JS inline por página) y su CSS asociado, presentes en 43 páginas. Es código que en cada carga testea si el navegador soporta ciertos emojis nativamente y, si no, carga un polyfill — en la práctica nunca se activa en navegadores modernos. Se confirmó que el sitio no tiene ningún `<img class="emoji">` que dependiera del CSS que se quitó.

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
