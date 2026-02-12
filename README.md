# PRIORIDAD, modificado por Badel.
**Documentación del proyecto**
[Presentación](https://docs.google.com/presentation/d/1HoPTf3qFUyXaOB4XI_P66ttOBEf0U9TzJmu1wIcJYys/edit?slide=id.g3b53158b3fe_0_67#slide=id.g3b53158b3fe_0_67), dentro de ella links a grupos, seguimiento de tareas, documentación extra etc...
Es resposabilidad individual y/o de los grupos responsables de cada área del proyecto mantener la documentación actualizada para el resto. 

**Instrucciones**
**Instrucciones para owners:**
-Agregar a todos como colaboradores (todos write), en teoría el Ruleset les impedirá subir nada a main directamente
- Proteger el main "Branch protection rules", haz clic en Add branch protection rule.Configuración del Ruleset con Require a pull request before merging y Require review from Code Owners
- crear archivo .github/CODEOWNERS

# Guía de Trabajo en GitHub para el Proyecto E1B
Sigue estos pasos en orden para evitar borrar el trabajo de los demás.

1. Configuración Inicial (Solo la primera vez)
Si acabas de instalar Git, esto es obligatorio para que sepa quién eres.

Abre la terminal en VS Code (Ctrl + ñ) y escribe esto (cambiando los datos por los tuyos):

> Terminal  
`git config --global user.email "tucorreo@ejemplo.com"`  
`git config --global user.name "TuNombreUsuario"`

*(Nota: Usa el mismo email de tu cuenta de GitHub para que te cuente las contribuciones).* 

2. Descargar el proyecto (Solo la primera vez)

> Terminal  
`git clone https://github.com/Badel-git/E1B_Proyecto2025.git`

**IMPORTANTE**: Ahora ve a Archivo > Abrir carpeta y selecciona la carpeta E1B_Proyecto2025 que se acaba de crear.

3. Flujo de Trabajo Diario (Cada vez que trabajes)

- A. Antes de tocar nada: Asegúrate de tener la última versión del proyecto para no trabajar sobre código viejo.

> Terminal  
`git checkout "main"`  
`git pull origin "main"`

*(Nota: Si la rama principal se llama "master", cambia main por master).* 

- B. Crear tu rama de trabajo: Nunca trabajes directamente en main. Crea una rama con tu nombre o la tarea:

> Terminal  
`git checkout -b "nombre-tarea"`

# Ejemplo: git checkout -b pepito-login

- C. Trabajar y Guardar:

Modifica tus archivos y guarda con Ctrl + S.

Cuando termines, sube tus cambios a la nube:

> Terminal  
`git add .`  
`git commit -m "Descripción breve de lo que hice"`  
`git push origin "nombre-tarea"`

4. Unir código (Pull Request)
Una vez hayas hecho el git push, ve a la página de GitHub.

Verás un botón verde llamado "Compare & pull request". Haz clic ahí.

Escribe un título y explica brevemente qué has cambiado.

Dale a "Create Pull Request".

Revisión: Pide a un compañero que revise, y si todo está bien, le dé a Review changes -> Approve.

Merge: Una vez aprobado, aparecerá el botón "Merge pull request". Púlsalo y luego "Confirm merge".

# USO DE BOT DENTRO DE VISUAL 
5. Usar el Bot para sincronizar tu rama local 

> Terminal 
SOLO UNA VEZ 

`git config --global alias.sync '!f() { br=$(git rev-parse --abbrev-ref HEAD); git fetch origin $br; git reset --hard origin/$br; }; f'`  
`git sync`  
