---
title: "4. Esquemas de parámetros y quién ejecuta qué"
description: "Cómo los esquemas JSON limitan lo que un modelo puede enviar, y la diferencia entre herramientas de cliente y de servidor"
type: lesson
---

# Lección 4. Esquemas de parámetros y quién ejecuta qué

**Vínculo con la misión:** Escribir el bucle del agente para una tarea dada, y nombrar qué hace cada mensaje de su contexto y qué termina el bucle.
**Fuente principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Requisitos previos:** [Lección 3](0003-the-wire-format-of-a-tool-call.md)

## Calentamiento

1. ▢ Cuando envías una definición de herramienta a un proveedor de modelos, ¿qué papel cumple el esquema JSON?

<details markdown="1"><summary>Comprobación</summary>

Describe qué argumentos acepta la herramienta: nombres, tipos y restricciones. El modelo usa el esquema para decidir qué enviar cuando llama a la herramienta. Un esquema bien formado evita que el modelo envíe argumentos inválidos o malformados.

</details>

2. ▢ Cuando un modelo llama a una herramienta y el harness recibe la llamada, ¿cómo sabe el harness si debe ejecutarla en local o enviarla a un proveedor?

<details markdown="1"><summary>Comprobación</summary>

Debes decírselo al harness cuando defines la herramienta: márcala como herramienta de cliente (se ejecuta en local) o como herramienta de servidor (la maneja el proveedor). El modelo nunca conoce la diferencia; solo ve el nombre y el esquema.

</details>

## Qué debes saber

### Los esquemas como guardarraíl

Un esquema JSON hace dos trabajos. Primero, documenta lo que la herramienta espera: nombres de propiedades, tipos, y si cada propiedad es opcional u obligatoria. Aquí tienes un ejemplo simple:

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "The city name"},
    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature scale"}
  },
  "required": ["city"]
}
```

Este esquema dice: una herramienta toma un objeto con un `city` obligatorio (cadena) y un `units` opcional (ya sea "celsius" o "fahrenheit"). El modelo lee esto y sabe que siempre debe dar una ciudad pero puede omitir las unidades.

Segundo, un esquema actúa como restricción. Cuando un modelo llama a la herramienta, solo puede enviar valores que coincidan con el esquema. Si el esquema dice que `units` debe ser una de dos cadenas, el modelo no puede enviar "kelvin" ni un número. Los esquemas estrictos evitan categorías enteras de llamadas malformadas sin que el harness tenga que validarlas.

### Qué pasa cuando faltan campos obligatorios

Si un modelo omite un campo obligatorio, la API del proveedor lanza un error. La mayoría de los frameworks lo capturan y se lo devuelven al modelo como resultado de herramienta: "Error: missing required field 'city'". Entonces el modelo tiene la oportunidad de corregirlo. Esto no es un fallo catastrófico; es una parte normal del bucle. Un esquema bien descrito reduce la frecuencia con que ocurre, porque el modelo lee el esquema con atención.

### Herramientas de cliente y herramientas de servidor

Una **herramienta de cliente** es una función de tu propio código que ejecuta el harness. Tú eres dueño de la implementación:

```python
def get_weather(city: str, units: str = "celsius"):
    # Your code to fetch weather
    return f"18{units[0]}, partly cloudy"
```

Cuando el modelo llama a `get_weather`, tu harness ejecuta tu función y recoge el resultado.

Una **herramienta de servidor** es algo que el proveedor ejecuta en su propia infraestructura: una búsqueda web, ejecución de código en un sandbox, acceso al sistema de archivos o una llamada a una API alojada. Tú defines qué hace (nombre y esquema), pero nunca escribes la implementación. El proveedor la ejecuta, recoge el resultado y el harness lo lee de la respuesta.

### Por qué importa la distinción

Cuando dices "el modelo llamó a una herramienta", estás siendo impreciso con el lenguaje. El modelo nunca ejecuta nada. Emite una petición estructurada que dice "ejecuta esta herramienta con estos argumentos". Un harness recibe esa petición y la ejecuta, ya sea:

1. Llamando a una función que escribiste (herramienta de cliente), o
2. Pidiéndole al proveedor que ejecute algo alojado (herramienta de servidor), o
3. Enviándola a un servicio de terceros por la red.

Al modelo no le importa cuál sea. La distinción es tuya: afecta a dónde vive el código, cómo lo escribes y dónde pueden ocurrir los fallos.

### Por qué esto importa para el bucle

En un bucle de agente, el modelo genera llamadas a herramientas y el harness las ejecuta. Si una herramienta falla, el resultado es un resultado de herramienta que lleva un error, no una excepción que tumba el bucle. Esto es cierto tanto si la herramienta es de cliente como de servidor:

- Una herramienta de cliente devuelve un error porque la red estaba caída, la consulta a la base de datos falló o tu lógica de validación rechazó la entrada.
- Una herramienta de servidor devuelve un error porque el sandbox del proveedor agotó el tiempo, el código lanzó una excepción o se alcanzó el límite de tasa de la API.

De cualquier forma, el error es solo otro resultado de herramienta, y el modelo decide qué hacer a continuación.

### Permisos y herramientas de servidor

Una herramienta de servidor añade una pregunta: ¿tiene el modelo permiso para llamarla? Si le das a un modelo acceso a ejecución de código, lectura de archivos o acceso a la web, estás confiando en que (dentro del límite que fija el esquema) use esa capacidad de forma segura. Esto es una decisión de seguridad, no técnica. El esquema impone qué argumentos puede recibir la herramienta, pero no puede impedir que el modelo use la capacidad para algo que no pretendías. Por eso importa el diseño del conjunto de herramientas, y por eso no toda herramienta es apropiada para todo agente.

## Práctica

1. ▢ Un esquema de herramienta exige un campo `query` (cadena) pero no tiene definido ningún campo `max_results`. ¿Puede el modelo enviar un argumento `max_results`? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No, en un esquema estricto. Las definiciones de esquema JSON pueden permitir o prohibir propiedades adicionales. Si el esquema no menciona `max_results`, el modelo no puede enviarlo (o el proveedor lo rechazará). El esquema es exhaustivo: solo pueden aparecer las propiedades listadas, a menos que el esquema permita explícitamente propiedades adicionales.

</details>

2. ▢ Tienes una herramienta de cliente que consulta una base de datos. El esquema dice que `user_id` es obligatorio, pero el modelo envía una llamada sin él. ¿Qué pasa después?

<details markdown="1"><summary>Pista</summary>

¿Qué hace el harness cuando el proveedor rechaza una llamada malformada?

</details>

<details markdown="1"><summary>Comprobación</summary>

El proveedor la rechaza, y el harness envía el error de vuelta al modelo como resultado de herramienta: "Error: missing required field 'user_id'". El modelo lee este error y tiene la oportunidad de corregir la llamada. El bucle no se cae; el error es un resultado normal.

</details>

3. ▢ ¿Qué afirmación describe mejor lo que pasa cuando un modelo llama a una herramienta de servidor frente a una de cliente?

    - a) Una herramienta de servidor corre en tu infraestructura; una de cliente corre en la infraestructura del proveedor
    - b) El modelo envía una petición para la herramienta; el harness decide dónde ejecutarla
    - c) Una herramienta de servidor siempre termina más rápido porque el proveedor la optimiza
    - d) Escribes la implementación de ambas, pero de forma distinta

<details markdown="1"><summary>Comprobación</summary>

**b)** El modelo emite la misma petición estructurada en ambos casos. El harness lee la definición de la herramienta, decide si es de cliente o de servidor y enruta la ejecución en consecuencia. (a) es al revés: las herramientas de cliente son tuyas, las de servidor son del proveedor. (c) es falsa: la velocidad depende de la implementación, no de si es de servidor o de cliente. (d) es en parte cierta pero pasa por alto que nunca escribes herramientas de servidor, solo las defines.

</details>

4. ▢ Defines una herramienta de servidor para "search_the_web" con un esquema que exige solo un campo `query`. El modelo la llama con `query="python", limit=5`. ¿Qué hace el proveedor?

<details markdown="1"><summary>Comprobación</summary>

O ejecuta la llamada solo con la consulta e ignora el límite, o rechaza la llamada porque el esquema no permite el campo extra `limit`. El resultado depende de si la definición del esquema permite propiedades adicionales. Si el esquema es estricto (el valor por defecto), el campo extra es un error.

</details>

## Prácticas en el mundo real

- [ ] Encuentra o escribe un esquema de herramienta para una tarea real (buscar, recuperar, calcular u obtener). Marca qué campos son obligatorios, cuáles tienen restricciones (enums, longitud de cadena, rangos numéricos) y cuáles son opcionales. Reescribe la descripción de un campo para que sea más clara.
- [ ] Ejecuta un agente o escribe un harness que llame a una herramienta y envíale a propósito un argumento inválido (omite un campo obligatorio, envía el tipo equivocado, envía un valor fuera de un enum). Observa cómo responde el proveedor y cómo lo maneja tu harness o tu framework.
- [ ] Mañana: diseña una herramienta de cliente y una de servidor para la misma tarea (por ejemplo "listar archivos"). Escribe los esquemas de ambas. Explica un compromiso entre dónde vive cada herramienta.

## Para profundizar

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
