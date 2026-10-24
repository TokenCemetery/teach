---
title: Diseño de APIs
description: "Diseña una interfaz de la que otros dependen: el contrato, sus errores y cómo cambia sin romperlos"
type: topic
---

# Aprendizaje: Diseño de APIs

Sé capaz de diseñar desde cero una API pública versionada (REST/HTTP o gRPC) y de hacer evolucionar una existente, cambiando su contrato sin romper a los clientes que dependen de ella.

**Última lección:** [19. Dónde encaja GraphQL](lessons/0019-where-graphql-fits.md)

## Cómo se ve el éxito

- Diseñar el contrato de una API REST/HTTP o gRPC, incluido su modelo de errores, para un caso de uso planteado.
- Hacer evolucionar el contrato de una API existente (añadir, deprecar o cambiar un campo o un endpoint) sin romper a los clientes, y explicar la estrategia de versionado o de migración utilizada.
- Tratar la autenticación, la autorización y el rate limiting como parte del contrato del que depende un cliente, no como un añadido atornillado por separado a posteriori.

## Restricciones

- Se asume experiencia profesional construyendo un servicio con HTTP o RPC; no se requiere estudio formal previo de diseño de APIs.
- Cubre tanto REST/HTTP como gRPC, ya que las garantías de la misión se aplican a ambos.

## Fuera de alcance

- Hacer que el compilador rechace un estado imposible dentro de un mismo código base: consulta [`programming/typescript`](../../programming/typescript/) para ese límite. Este espacio de trabajo es el mismo instinto aplicado a través de un límite donde no hay un compilador compartido.

## El arco

Doce etapas, del contrato a la entrega asíncrona y a la verificación del propio contrato frente al comportamiento real. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. El contrato | 0001 | Aquello en lo que un cliente puede confiar es más amplio que lo documentado (la ley de Hyrum) | Puedes nombrar la superficie implícita de un contrato más allá de la documentada |
| 2. Modelos de errores | 0002 a 0003 | Códigos de estado HTTP, RFC 9457 Problem Details, códigos de estado de gRPC | Puedes diseñar un modelo de errores para una API planteada |
| 3. Diseño REST/HTTP | 0004 a 0005 | Modelado de recursos, paginación y filtrado, pautas al estilo de las AIP | Puedes diseñar un contrato REST para un caso de uso planteado |
| 4. Diseño gRPC | 0006 a 0007 | proto3, diseño de servicios, streaming | Puedes diseñar un contrato gRPC para el mismo caso de uso |
| 5. Versionado y evolución | 0008 a 0009 | Cambios aditivos, deprecación, estrategia de migración | Puedes hacer evolucionar el contrato de una API existente sin romper a sus clientes |
| 6. Auth, authz y rate limiting como contrato | 0010 | Tratarlos como parte de aquello de lo que depende un cliente, no como un añadido a posteriori | Puedes diseñar la autenticación y el rate limiting como contrato, no atornillados por separado |
| 7. Idempotencia y reintentos seguros | 0011 | La cabecera `Idempotency-Key`, las huellas de idempotencia y la distinción entre reintento y petición concurrente | Puedes diseñar un mecanismo de idempotencia que haga que un método no idempotente sea realmente seguro de reintentar |
| 8. La caché HTTP como contrato | 0012 | `ETag`, validadores débiles frente a fuertes, peticiones condicionales, concurrencia optimista con `If-Match`, `Cache-Control` | Puedes diseñar un contrato de caché y de control de concurrencia, y sabes qué fuerza de comparación necesita cada cabecera condicional |
| 9. Operaciones de larga duración y entrega asíncrona | 0013 a 0014 | El recurso de operación y el polling, la firma de webhooks, los reintentos y el orden | Puedes diseñar un contrato asíncrono (operación consultada por polling o webhook enviado) y sus garantías de fallo, reintento y orden |
| 10. Operaciones masivas y respuestas parciales | 0015 | Métodos batch atómicos frente a éxito parcial, notificación de errores por elemento, field masks | Puedes diseñar la semántica de fallo de un método batch y un contrato de respuesta parcial |
| 11. El contrato legible por máquina | 0016 a 0017 | Documentos OpenAPI y archivos `.proto` como artefactos generados, detección de cambios incompatibles con Buf, Spectral y oasdiff | Puedes explicar lo que permite un contrato legible por máquina y en qué se diferencia un linter de estilo de un detector de cambios incompatibles |
| 12. Pruebas de contrato y el lugar de GraphQL | 0018 a 0019 | Pruebas de contrato guiadas por el consumidor y `can-i-deploy`, y dónde se sitúa GraphQL respecto a REST y gRPC | Puedes explicar cómo una prueba de contrato verifica el comportamiento real más allá de un esquema, y situar con precisión la evolución sin versiones de GraphQL frente al material REST/gRPC de este arco |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-the-contract.md) | El contrato | Aquello en lo que un cliente puede confiar es más amplio que lo que documentaste, y el diseño tiene que tener en cuenta ambas cosas |
| [0002](lessons/0002-http-status-codes-and-error-semantics.md) | Códigos de estado HTTP y semántica de errores | Lo que un código de estado le promete realmente a un cliente sobre seguridad, idempotencia y qué hacer a continuación, más allá de la vaga agrupación 2xx/4xx/5xx |
| [0003](lessons/0003-problem-details-and-grpc-status-codes.md) | RFC 9457 Problem Details y códigos de estado de gRPC | Un formato de error estructurado y legible por máquina para HTTP, el vocabulario paralelo de códigos de estado de gRPC y el diseño de un único modelo de errores que funcione en ambos |
| [0004](lessons/0004-resource-modeling-for-rest.md) | Modelado de recursos para REST | Por qué REST modela una API en torno a sustantivos y estado, no a verbos, y cómo una jerarquía de recursos da forma a lo que significa una URL |
| [0005](lessons/0005-pagination-and-filtering.md) | Paginación, filtrado y diseño de un contrato REST | Por qué la paginación basada en cursor supera a los offsets a escala, cómo el filtrado se mantiene como un contrato estable y cómo juntar el modelado de recursos en un diseño REST completo |
| [0006](lessons/0006-proto3-and-grpc-service-design.md) | Proto3 y diseño de servicios gRPC | Cómo los números de campo de proto3, y no los nombres de campo, son el verdadero contrato en la red, y cómo un servicio gRPC se estructura en torno a métodos RPC en lugar de recursos |
| [0007](lessons/0007-grpc-streaming.md) | Streaming en gRPC y diseño del mismo caso de uso | Los cuatro tipos de RPC de gRPC, cuándo encaja cada uno y el diseño de un mismo caso de uso como contrato REST y como contrato gRPC |
| [0008](lessons/0008-additive-changes-and-deprecation.md) | Cambios aditivos y deprecación | Por qué añadir suele ser seguro y eliminar o cambiar el significado normalmente no, y cómo deprecar un campo o un endpoint sin romper a los clientes de golpe |
| [0009](lessons/0009-versioning-and-migration-strategy.md) | Estrategia de versionado y de migración | Cómo publicar un cambio realmente incompatible sin romper todas las integraciones existentes a la vez, con la estrategia de versionado de Stripe como ejemplo resuelto |
| [0010](lessons/0010-auth-authz-and-rate-limiting-as-contract.md) | Auth, authz y rate limiting como contrato | Por qué los scopes, no solo los tokens, y un estado de rate limit visible, no solo un 429, son lo que convierte el control de acceso y las cuotas en parte del contrato deliberado |
| [0011](lessons/0011-idempotency-keys-and-safe-retries.md) | Claves de idempotencia y reintentos seguros | Una clave por sí sola solo deduplica; una huella es lo que le dice al servidor si una clave repetida es la misma petición reintentada o una distinta que la reutiliza por error, y un reintento que llega mientras la original sigue en curso recibe un conflicto, no una repetición |
| [0012](lessons/0012-http-caching-as-contract.md) | La caché HTTP como contrato | El mismo validador ETag sirve para dos trabajos distintos según la comparación que necesite: la comparación débil basta para evitar una descarga redundante, pero solo una comparación fuerte es segura para detectar la escritura concurrente de otra persona |
| [0013](lessons/0013-the-operation-resource-and-polling.md) | El recurso de operación y el polling | Un método de larga duración devuelve un recurso con forma de promesa en lugar de bloquearse, y un fallo durante la ejecución se notifica de forma distinta a un fallo que impide siquiera que la operación empiece |
| [0014](lessons/0014-webhooks-and-callbacks-as-delivery.md) | Webhooks y callbacks como entrega | Enviar una notificación en lugar de esperar a que te consulten invierte quién inicia la petición, y esa inversión es exactamente la razón por la que la firma, los reintentos y el orden necesitan cada uno su propio contrato explícito en el lado receptor |
| [0015](lessons/0015-bulk-operations-and-partial-responses.md) | Operaciones masivas y respuestas parciales | Un método batch tiene que elegir de antemano si falla todo o nada o si notifica éxito y fallo por elemento, y un cliente que pide un subconjunto de campos necesita que ese subconjunto se solicite fuera del cuerpo al que da forma |
| [0016](lessons/0016-openapi-and-protobuf-as-artifacts.md) | OpenAPI y Protobuf como artefactos | Una vez que el contrato existe como documento legible por máquina y no solo como prosa, el propio documento pasa a ser algo que versionar, revisar y a partir de lo cual generar otras cosas, en lugar de una descripción escrita a posteriori |
| [0017](lessons/0017-breaking-change-linting.md) | Linting de cambios incompatibles | Un linter que comprueba el estilo de un contrato y una herramienta de diff que comprueba si rompió a un cliente responden a dos preguntas distintas, y a la propia herramienta de diff hay que hacerle la correcta de entre tres |
| [0018](lessons/0018-contract-testing.md) | Pruebas de contrato | Un artefacto de esquema comprueba la forma y un linter de cambios incompatibles comprueba la compatibilidad, pero ninguno confirma que un proveedor se comporte realmente como esperan las pruebas de un consumidor real, que es lo que verifica una prueba de contrato mediante interacciones de ejemplo grabadas |
| [0019](lessons/0019-where-graphql-fits.md) | Dónde encaja GraphQL | GraphQL resuelve el mismo problema de versionado al que este espacio de trabajo dedicó dos lecciones haciendo que cada petición sea ya una field mask, a costa de un contrato al que no se aplican las herramientas de este espacio de trabajo |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Modelos de errores](reference/error-models.md): códigos de estado HTTP, miembros de Problem Details y códigos de estado de gRPC lado a lado, para cuando estás diseñando un modelo de errores y no aprendiendo por qué es contrato
- [Diseño de recursos REST](reference/rest-resource-design.md): nombres de recursos, los métodos estándar y personalizados, paginación y filtrado, con la regla AIP que debe cumplir cada decisión
- [Diseño gRPC](reference/grpc-design.md): números de campo de proto3, qué cambios de esquema son seguros en la red binaria y cuáles rompen JSON, los cuatro tipos de RPC y la semántica de llamada que hereda un contrato gRPC
- [Versionado y evolución](reference/versioning-and-evolution.md): qué cambios rompen qué tipo de compatibilidad, las cabeceras que hacen visible una deprecación para las herramientas y los modelos de versionado entre los que elegir
- [Auth y rate limiting](reference/auth-and-rate-limiting.md): scopes y tipos de concesión como contrato, los códigos de error que un servidor de recursos le debe a un cliente y los campos RateLimit que hacen visible una cuota antes de alcanzarla

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
