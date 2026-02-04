Configuración Inicial

- git config: Establece tu identidad (nombre y correo) para que Git sepa quién firma los cambios.

- git config --global user.email "tucorreoelectronico"

- git config --global user.name "tunombredegithub"

Gestión del Repositorio

- git init: Crea un nuevo repositorio de Git en la carpeta donde estás parado.

- git status: Te muestra el "estado" actual: qué archivos has modificado, cuáles vas a guardar y en qué rama estás.

- git branch: Lista todas las ramas de tu proyecto.

Guardado de Cambios

- git add .: Prepara todos los archivos modificados para ser guardados (los añade al "escenario" o staging area).

- git commit -m "...": Guarda definitivamente los cambios preparados con un mensaje descriptivo.

Ramas y Remoto

- git checkout -b "nombre": Crea una rama nueva y te cambia a ella automáticamente.

- git push -u origin "nombre": Sube tus cambios locales al servidor (GitHub) y vincula tu rama local con la remota.

- git pull origin "nombre": Descarga y fusiona los cambios más recientes del servidor a tu computadora (para estar al día con lo que subieron otros).
