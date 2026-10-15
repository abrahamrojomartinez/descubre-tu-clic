# descubre-tu-clic

Landing de **VIBRA** (proyecto de Abraham).

- **En producción:** https://vibrasociety.es (proyecto de Netlify `descubre-tu-clic`, https://descubre-tu-clic.netlify.app)
- **Qué es:** web estática de un único `index.html`, sin build, sin framework y sin dependencias.
- **Deploy:** automático al hacer `push` a `main` (Netlify despliega el contenido de la raíz del repo).

## Editar

Todo el contenido vive en `index.html`. Edítalo y haz `push` a `main`; Netlify publica el cambio solo.

## Dominio y /comunidad

- `vibrasociety.es` es el dominio principal de este proyecto de Netlify; `vibrasociety.app` redirige aquí (`netlify.toml`). DNS en DonDominio.
- `vibrasociety.es/comunidad` NO vive en este repo: `netlify.toml` lo reenvía (proxy) al proyecto `que-nunca-te-quiten-tu-vibra` (repo `vibra-platform-pre-release`, Next.js con `basePath: "/comunidad"`). Los botones de "Entrar a VIBRA" apuntan a `/comunidad?utm_source=…`.
- Otras webs servidas bajo el dominio por proxy (cada una en su repo, con una regla que quita el prefijo): `/flow-fest` → sitio `flowfest-madrid` (repo `vibra-business`), `/viaje-vibra-con-liveokey` → sitio `vibra-con-liveokey-trip` (repo `brief-viajero-liveokeypeople`). `descubre-tu-clic.netlify.app/*` redirige a `vibrasociety.es`.
