
alumnos = ["Badel", "xyz"]

# Formatear la lista de alumnos
if len(alumnos) == 1:
    resultado = alumnos[0]
elif len(alumnos) == 2:
    resultado = f"{alumnos[0]} y {alumnos[1]}"
else:
    todos_excepto_ultimo = ", ".join(alumnos[:-1])
    resultado = f"{todos_excepto_ultimo} y {alumnos[-1]}"

print(f"Los alumnos capaces de hacer merge con main son: {resultado}.")
