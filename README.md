**Documentación del proyecto**
[Presentación](https://docs.google.com/presentation/d/1HoPTf3qFUyXaOB4XI_P66ttOBEf0U9TzJmu1wIcJYys/edit?slide=id.g3b53158b3fe_0_67#slide=id.g3b53158b3fe_0_67), dentro de ella links a grupos, seguimiento de tareas, documentación extra etc...
Es resposabilidad individual y/o de los grupos responsables de cada área del proyecto mantener la documentación actualizada para el resto. 

**Instrucciones**
**Instrucciones para owners:**
-Agregar a todos como colaboradores (todos write), en teoría el Ruleset les impedirá subir nada a main directamente
- Proteger el main "Branch protection rules", haz clic en Add branch protection rule.Configuración del Ruleset con Require a pull request before merging y Require review from Code Owners
- crear archivo .github/CODEOWNERS

**Instrucciones para el resto:**
- Solo primera vez, en terminal vscode: git clone https://github.com/Badel-git/E1B_Proyecto2025.git Luego debe abrir la carpeta del proyecto en VS Code: Archivo > Abrir carpeta
- crear una rama en VS Code: git checkout -b pepitoperez. A partir de ahí, abres el archivo modificas y guardas sin mas. 
- Después de tus cambios haces ad + commit para que se entere desde consola: git add . -> git commit -m "mi parte" -> git push origin pepitoperez
- Crean el Pull Request en GitHub (web): botón verde de "Compare & pull request". comenten o expliquen que cambiaron
- Tú (o un revisor) va a Files changed -> Review changes -> Approve. Para que luego los revisores verán que el botón de "Merge"
- Al darle a merge... debiera unir el código al proyecto principal.
