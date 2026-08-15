# DANZARIEL-QUERO Terminal Chat

Vibe: terminal verde/negro tipo hacker local, pero simple y legible.

Abre el chat desde PowerShell:

```powershell
.\chat_terminal.bat
```

Llave magica:

```powershell
.\danzariel.bat
```

Dentro del chat tambien puedes escribir:

```text
danzariel
```

## Centro visual

Al abrir con:

```powershell
.\danzariel.bat
```

el terminal muestra un centro de control inicial con:

```text
estado de objetos visuales
conteo de areas
preview del clipboard
indice de imagenes
hora local
```

Comandos visuales:

```text
/ui
/toggle matrix
/toggle scan
/toggle clock
/toggle clipboard
/toggle images
scan
clear
```

Los objetos ON/OFF se guardan en:

```text
danzariel_quero_data/memoria/terminal_state.json
```

## Llave Danzariel

Cuando escribas `danzariel`, el sistema muestra 4 acciones principales y una salida de emergencia:

```text
/ui
add
paste add
send
images
image send
rollback multidimensional
backup
sos
```

### add

Te pregunta en que area guardar:

```text
memoria
inbox
trading
documentos
```

### send

Te pregunta el area, luego el bloque, y lo copia al clipboard como Markdown.

### paste add

Lee el contenido actual del clipboard y lo guarda como bloque `.md` en el area que elijas.

Flujo recomendado para trabajar rapido sin afectar el sistema:

```text
1. send
2. pegar en ChatGPT o notas
3. editar/mejorar
4. copiar resultado
5. paste add
6. backup si el bloque ya sera usado como fuente
```

### images / image send

`images` lista imagenes guardadas en `danzariel_quero_data/`.

`image send` copia al clipboard una referencia Markdown a la imagen seleccionada.

### backup

Te pregunta que bloque quieres proteger y crea una copia en `backups/`.

### rollback multidimensional

Te pide elegir un backup y un bloque destino. Solo restaura si escribes `RESTAURAR`.

### sos

Muestra opciones de emergencia:

```text
/server
/url
/context
/diff
backup
/exit
```

`/context` muestra un reporte seguro del sistema para ChatGPT/Codex.
`/diff` hace lo mismo, con un nombre facil de recordar si piensas en cambios de Git.

O directo con Python:

```powershell
.\.venv\Scripts\python.exe chat_terminal.py
```

## Comandos

```text
/server
/start-server
/url
/danzariel
/ui
/toggle objeto
/clip
/files
/search texto
/context
/diff
/history
/note titulo | contenido
paste add
scan
images
image send
clear
/env
/setup
/help
/exit
```

## Comandos recomendados

```text
/server
/url
/start-server
/files
/note idea | contenido de la idea
```

## Donde se guarda

La conversacion queda en:

```text
danzariel_quero_data/memoria/chat.jsonl
```

Las notas creadas con `/note` quedan en:

```text
danzariel_quero_data/memoria/
```

Todavia no hay IA conectada. Por ahora el chat funciona como interfaz conversacional local y memoria.
