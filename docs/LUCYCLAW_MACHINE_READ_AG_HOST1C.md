# LucyClaw Machine Read (AG-HOST1C)

## Objetivo
Agregar lectura segura y de solo lectura de documentos permitidos desde Telegram/OpenClaw mediante comandos directos.

## Comandos
- `/machine_read <path>`: extrae texto literal de un documento soportado dentro de rutas permitidas.
- `/machine_doc_brief <path>`: devuelve metadata del archivo y un extracto literal acotado.

## Formatos soportados
- Texto plano: `.txt`, `.md`, `.json`, `.csv`, `.log`
- DOCX: `.docx` usando `zipfile` + `xml.etree.ElementTree`
- PDF: `.pdf` usando `pdftotext -layout -enc UTF-8 <path> -`

## Rutas permitidas
- `/home/lucy-ubuntu`
- `/home/lucy-ubuntu/Descargas`
- `/home/lucy-ubuntu/Downloads`
- `/home/lucy-ubuntu/Escritorio`
- `/home/lucy-ubuntu/Documentos`
- `/home/lucy-ubuntu/Imágenes`

## Rutas prohibidas
- `.env`
- `.ssh`
- `.gnupg`
- `.config`
- `n8n_data`
- `memoria`
- `boveda`
- `vault`
- `tokens`
- `credentials`
- `.agents`
- `node_modules`
- `~/.openclaw`
- `~/.gemini`

## Límites de salida
- Máximo por defecto: `6000` caracteres
- Si el contenido es más largo, devuelve `truncated=true`
- Metadata incluida: `path`, `name`, `extension`, `size_bytes`, `modified`, `chars_returned`

## Errores controlados
- `Missing path argument`
- `Access denied or unsafe path`
- `Path not found`
- `Path is not a file`
- `Unsupported file format`
- `pdftotext not available`
- `Document read timed out`

## Seguridad
- Solo lectura; no modifica ni mueve archivos del usuario
- Sin `sudo`
- Sin `shell=True`
- Sin red
- Sin ejecución de comandos arbitrarios
- Sin OCR por ahora
- No lee secretos ni runtime sensible

## Cómo probar desde Telegram
- `/machine_read /home/lucy-ubuntu/Descargas/Markdown.md pegado`
- `/machine_read /home/lucy-ubuntu/Descargas/Platon El banquete.pdf`
- `/machine_doc_brief /home/lucy-ubuntu/Descargas/Platon El banquete.pdf`
- `/machine_read /home/lucy-ubuntu/Descargas/201721562-Roles-Ars-Magica-4a-Ed-1_convertido_3.docx`

## Rollback
- `openclaw plugins uninstall lucy-machine-read-command` o quitar el link del plugin
- reiniciar `openclaw-gateway.service`
- revertir el commit `feat(lucyclaw): add read-only document reading commands`
