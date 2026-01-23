Instrucciones para owners:
-Agregar a todos como colaboradores (todos write), en teoría el Ruleset les impedirá subir nada a main directamente
- Proteger el main "Branch protection rules", haz clic en Add branch protection rule.Configuración del Ruleset con Require a pull request before merging y Require review from Code Owners
- crear archivo .github/CODEOWNERS

Instrucciones para el resto:
- crear una rama en VS Code: git checkout -b pepitoperez
- Hacen sus cambios y suben la rama: git add . -> git commit -m "mi parte" -> git push origin pepitoperez
- Crean el Pull Request en GitHub: botón verde de "Compare & pull request".
- Tú (o un revisor) va a Files changed -> Review changes -> Approve. Para que luego los revisores verán que el botón de "Merge"
- Al darle a merge... debiera unir el código al proyecto principal.
