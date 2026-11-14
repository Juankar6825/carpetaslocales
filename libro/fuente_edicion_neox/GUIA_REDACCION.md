# Guía de redacción · El Gran Manifestador (edición con NEOX)

## Qué es el libro
Libro de desarrollo personal "El Gran Manifestador", de Juankar. Siete módulos de siete lecciones. En este libro "manifestar" significa claridad, atención, responsabilidad y acción. Nunca se promete que el pensamiento controle por sí solo sucesos externos, enfermedades o decisiones de otros. El libro no culpa a nadie de lo que no controla.

El módulo 1 ya está bien escrito y es el modelo de tono. Léelo antes de escribir:
/tmp/claude-0/-home-user-carpetaslocales/c3f64bd8-29ea-5a4c-a18b-15e11985b634/scratchpad/libro/modulo1_referencia.txt

Los módulos 2 a 7 existen solo como plantilla vacía (todas las lecciones repiten los mismos párrafos). Hay que escribirlos de verdad, conservando el título, el subtítulo, la idea clave y el ejercicio de cada lección, que están en:
/tmp/claude-0/-home-user-carpetaslocales/c3f64bd8-29ea-5a4c-a18b-15e11985b634/scratchpad/libro/esqueleto_m2_7.json

## Quién es NEOX
NEOX es el personaje que pone cara y voz a las enseñanzas del libro en vídeos y redes. Es un emprendedor. Su vida tiene cuatro áreas: desarrollo personal (consigo mismo), negocio, hijos y pareja (su mujer). Las historias de NEOX son experiencias reales del autor contadas a través del personaje. Por eso:
- Solo puedes usar las historias de NEOX que están en el banco (BANCO_NEOX.md) y solo las que te asigne el encargo. No añadas hechos, resultados, cifras, nombres ni detalles que no estén en el banco. Puedes reformularlas y ampliarlas en reflexión, nunca en hechos.
- Fuera de esas historias, NEOX puede aparecer como voz que comenta (opiniones, preguntas, frases), sin atribuirle vivencias nuevas.
- No hay historias de NEOX con sus hijos. No inventes ninguna.

## Tono
- Español de España, tuteando al lector. Cercano, directo, frases cortas, con ejemplos del día a día. Como alguien que ha estado ahí, no como un gurú.
- Que no parezca escrito por una IA: nada de "en este capítulo exploraremos", "es importante destacar", "en definitiva", "sumérgete", "desbloquear todo tu potencial", "viaje transformador", listas de tres adjetivos huecos, ni frases redondas vacías.
- No uses negritas, ni guiones largos (—) ni medios (–). Usa comas, puntos o paréntesis.
- No inventes estudios, estadísticas, porcentajes, citas de personas famosas ni referencias científicas. Si algo depende de salud, dinero o ley, invita a consultar a un profesional, como hace el módulo 1.
- Puedes usar personajes ilustrativos con nombre propio (como Laura, Marta o Sergio del módulo 1) para las escenas cotidianas. Que sean creíbles y variados (edades, trabajos, situaciones). No repitas nombres ya usados en el módulo 1 (Laura, Marta, Sergio, Inés, Alicia, Daniel) ni nombres que use otro módulo; usa los que te indique el encargo.

## Extensión y estructura de cada lección (550 a 750 palabras de cuerpo)
1. Título y subtítulo (los del esqueleto; puedes pulir el subtítulo).
2. Escena de apertura con encabezado propio: una situación concreta y reconocible.
3. Dos o tres apartados con encabezados propios y concretos (nada de "Lo que de verdad está en juego" ni "Un método para practicarlo"; cada lección con sus propios títulos de apartado, como en el módulo 1).
4. Una cita destacada de una línea, propia del libro.
5. Bloque NEOX: si la lección tiene historia asignada, bloque "Lo que vivió NEOX" (contado por NEOX en primera persona, fiel al banco, 120 a 220 palabras, con el área indicada). Si no tiene, bloque corto "La voz de NEOX" (40 a 80 palabras, una reflexión o pregunta de NEOX, sin vivencias nuevas).
6. Cuaderno de acción: el ejercicio del esqueleto, redactado con naturalidad y concreto.

## Formato de salida (texto plano con etiquetas, respétalo al pie de la letra)

```
@MODULO 02 | REPROGRAMA TU MENTE
@INTRO
Párrafo de presentación del módulo (100 a 160 palabras).
@RUTA
01 Título lección 1
02 Título lección 2
...
@LECCION 01
@TITULO La voz que narra tu vida
@SUBTITULO Una frase repetida termina pareciendo un diagnóstico.
@H Encabezado del apartado
Párrafo.

Otro párrafo.
@H Otro encabezado
Párrafo.
@CITA Frase destacada de una línea.
@NEOX_VIVIO Negocio
Texto de NEOX en primera persona. Puede tener varios párrafos separados por línea en blanco.
@NEOX_VOZ
Texto breve de NEOX.
@CUADERNO
Texto del ejercicio.
@LECCION 02
...
@CIERRE
@TITULO Título del cierre del módulo
Párrafo(s) de cierre (80 a 140 palabras).
@PLAN
Día 1 · ...
Día 2 · ...
...
Día 7 · ...
@FRASE Frase final del módulo.
```

Reglas del formato: cada lección lleva @NEOX_VIVIO (con el área: Desarrollo personal, Negocio, Hijos o Pareja) o @NEOX_VOZ, nunca los dos. Los párrafos se separan con una línea en blanco. No uses markdown (ni #, ni *, ni >).
