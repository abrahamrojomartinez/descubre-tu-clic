# descubre-tu-clic

Landing de **VIBRA** (proyecto de Abraham).

- **En producción:** https://vibrasociety.es (proyecto de Netlify `descubre-tu-clic`, https://descubre-tu-clic.netlify.app)
- **Qué es:** web estática de un único `index.html`, sin build, sin framework y sin dependencias.
- **Deploy:** automático al hacer `push` a `main` (Netlify despliega el contenido de la raíz del repo).

## Editar

Todo el contenido vive en `index.html`. Edítalo y haz `push` a `main`; Netlify publica el cambio solo.

## Cómo cambiar el calendario

El calendario 26·27 vive en **un solo sitio**: `calendario-26-27.json`, en la raíz del repo. Lo pintan dos cosas:

- esta landing (sección «Calendario»), a través de `scripts/calendario.py`, que vuelca el JSON en las filas de `index.html`;
- el formulario `vibrasociety.es/comunidad`, que lee `https://vibrasociety.es/calendario-26-27.json` directamente en el navegador (`netlify.toml` lo sirve con CORS abierto y 5 minutos de caché).

Para cambiar una fecha, añadir o quitar un plan:

1. Edita `calendario-26-27.json`. Cada plan lleva: `id` (**nunca se reutiliza** para otro evento), `mes` (`ENE`…`DIC`), `fecha` (`"7"`, `"2–8"` o `""` si aún no hay día), `titulo` y `linea` (landing), `etiqueta` y `meta` (formulario), `valor` (texto exacto que se guarda en Supabase/HubSpot), `con` (aliados tal cual se muestran, con @), `globos` (archivos de `img/aliados/` sin `.webp`), `nota` (`"+ teletrabajo"` o `""`), `paginaPropia` (`"/flow-fest/"` o `null`), `hasta` (`AAAA-MM-DD`: a partir de ese día deja de verse), `reservable`, `stripeUrl` y `agotado`.
2. `python3 scripts/calendario.py` (Python 3 de serie, sin instalar nada). Regenera **solo** el bloque entre `<!-- calendario:inicio -->` y `<!-- calendario:fin -->` de `index.html` y avisa si falta algún globo. Con `--check` no toca nada: solo dice si `index.html` está al día.
3. `git commit` de los dos archivos y `push` a `main`. **Una sola publicación**: el formulario lo lee solo.

No lo regenera el script (se editan a mano, tienen su propio `data-hasta`): la píldora «Lo próximo · 7 NOV · Flow Fest» del hero y los enlaces a Flow Fest de la cabecera y del pie.

## Dominio y /comunidad

- `vibrasociety.es` es el dominio principal de este proyecto de Netlify; `vibrasociety.app` redirige aquí (`netlify.toml`). DNS en DonDominio.
- `vibrasociety.es/comunidad` NO vive en este repo: `netlify.toml` lo reenvía (proxy) al proyecto `que-nunca-te-quiten-tu-vibra` (repo `vibra-platform-pre-release`, Next.js con `basePath: "/comunidad"`). Los botones de "Entrar a VIBRA" apuntan a `/comunidad?utm_source=…`.
- Otras webs servidas bajo el dominio por proxy (cada una en su repo, con una regla que quita el prefijo): `/flow-fest` → sitio `flowfest-madrid` (repo `vibra-business`), `/viaje-vibra-con-liveokey` → sitio `vibra-con-liveokey-trip` (repo `brief-viajero-liveokeypeople`). `descubre-tu-clic.netlify.app/*` redirige a `vibrasociety.es`.
