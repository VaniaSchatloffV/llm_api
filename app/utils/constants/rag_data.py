my_data = [
    """
    En la tabla de nombre: "pacientes"
    se almacena información referente a personas que padecen diferentes tipos de cáncer atendidas por la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del paciente. Algunos ejemplos de entradas son: 'Juan', 'Ana', 'Pablo', 'Laura', todos parten con mayuscula.
    'sur' de tipo varchar: este campo  corresponde al apellido del paciente. Algunos ejemplos de entradas son: 'Perez', 'Gomez', 'Martinez', todos parten con mayuscula.
    'tipo_cancer' de tipo varchar: corresponde a la zona afectada del paciente. Algunos ejemplos de entradas son: 'Cáncer de Mama', 'Cáncer de Pulmón', 'Cáncer de Colon', 'Cáncer de Prostata', todos parten con mayuscula y llevan tilde.
    'categoria_cancer' de tipo int: da un numero del 1 al 5 respecto a la severidad.
    """,

    """
    En la tabla de nombre: "doctores"
    se almacena información referente a doctores que trabajan en la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del doctor. Algunos ejemplos de entradas son: 'Juan', 'Ana', 'Pablo', 'Laura', todos parten con mayuscula.
    'sur' de tipo varchar: este campo  corresponde al apellido del doctor. Algunos ejemplos de entradas son: 'Perez', 'Gomez', 'Martinez', todos parten con mayuscula.
    'especialización' de tipo varchar: este campo contiene la especialidad del doctor. Ejemplos incluyen: 'Oncología', 'Pediatría', 'Ginecología', todos parten con mayúscula y llevan tildes.
    'hospital' de tipo varthcar: este campo contiene donde practica el doctor. Ejemplos de entradas incluyen: 'Hospital Central', 'Hospital del Norte' y 'Hospital del Sur', todos parten con mayuscula.
    """,

    """
    En la tabla de nombre "atenciones"
    es una tabla intermedia para las tablas 'pacientes' y 'doctores' donde se almacena información referente a qué doctor ha atendido a qué paciente.
    Las entradas siempre son uno a uno, vale decir en cada entrada un paciente es atendido por un doctor
    La información almacenada comprende las columnas:
    'id_atencion' de tipo int: esta es la clave primaria de la tabla.
    'id_doctor' de tipo int: es clave foránea de la tabla "doctores".
    'id_paciente' de tipo int: es clave foránea de la tabla "pacientes".

    """,
    """
    En la tabla de nombre: "enfermeros"
    se almacena información referente a los enfermeros que trabajan en la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del enfermero. Algunos ejemplos de entradas son: 'Juan', 'Ana', 'Pablo', 'Laura', todos parten con mayúscula.
    'apellido' de tipo varchar: este campo corresponde al apellido del enfermero. Algunos ejemplos de entradas son: 'Perez', 'Gomez', 'Martinez', todos parten con mayúscula.
    'turno' de tipo varchar: este campo indica el turno de trabajo del enfermero. Algunos ejemplos de entradas son: 'Mañana', 'Tarde', 'Noche', todos parten con mayúscula.
    'especialización' de tipo varchar: este campo contiene la especialidad del enfermero. Ejemplos incluyen: 'Cuidados Intensivos', 'Oncología', 'Urgencias', todos parten con mayúscula y llevan tilde.
    """,
    """
    En la tabla de nombre: "medicamentos"
    se almacena información referente a los medicamentos utilizados en el tratamiento de los pacientes de la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del medicamento. Algunos ejemplos de entradas son: 'Paracetamol', 'Ibuprofeno', 'Cisplatino', todos parten con mayúscula.
    'tipo' de tipo varchar: este campo indica la clase de medicamento. Ejemplos incluyen: 'Analgésico', 'Quimioterapia', 'Antiinflamatorio', todos parten con mayúscula y llevan tilde.
    'dosis' de tipo varchar: este campo indica la dosis recomendada para el tratamiento, como '500mg', '1g', '250mg'.
    'frecuencia' de tipo varchar: este campo especifica la frecuencia de administración del medicamento. Ejemplos incluyen: 'Cada 8 horas', 'Una vez al día', 'Cada 12 horas', todos parten con mayúscula.
    """,
    """ En la tabla de nombre: "exámenes"
    se almacena información referente a los exámenes médicos realizados a los pacientes de la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del examen. Algunos ejemplos de entradas son: 'Hemograma', 'Tomografía', 'Biopsia', todos parten con mayúscula.
    'tipo' de tipo varchar: este campo indica la categoría del examen. Ejemplos incluyen: 'Laboratorio', 'Imagenología', 'Patología', todos parten con mayúscula.
    'id_paciente' de tipo int: es clave foránea de la tabla "pacientes", indicando a qué paciente se le realizó el examen.
    """
    
    ]

my_data2 = [
    """
    Doctores es una tabla de la base de datos con informacion
    """,
    """
    Atenciones es una tabla de la base de datos con informacion
    """,
    """
    Pacientes es una tabla de la base de datos con informacion
    """
]

my_data3 = [
    """
    'consulta':
    Pregunta relacionada a doctores, pacientes y/o atenciones o algo que pueda estar relacionado con estos y consideres que tiene potencial de convertirse en una consulta para la base de datos.
    """,

    """
    'archivo'
    Solicitud, peticion o favor de obtener informacion en formato xlsx (tambien te pueden pedir esto como 'excel' o 'Excel') o comma separated values (csv), si se te pide una tabla de estos formatos,
    asume que es este tipo de mensaje. Si ves cualquiera de las palabras xlsx/excel/Excel/XLSX o CSV/csv escritas, asume que es este tipo de mensaje.
    Esta ultima condicion toma prioridad por sobre cualquier otro tipo de mensaje.
    """,

    """
    'grafico'
    Solicitud, peticion o favor para graficar la informacion obtenida, cualquier tipo de mensaje que haga referencia a graficos o a modificar algo de estos,
    considerala un mensaje de este tipo.
    """,

    """
    'conversacion':
    Una conversacion en lenguaje natural que NO sea: 
    Una solicitud referente al ambito de un hospital, la fundacion, nombres de pacientes o doctores etc
    Una peticion para graficar algo 
    Una peticion para generar algun tipo de archivo.
    """

]


my_data4 = [
    """
    'consulta':
    Pregunta relacionada a doctores, pacientes y/o atenciones o algo que pueda estar relacionado con estos.
    Si es que clasificas la pregunta como tipo 'consulta' responde solamente con "SQL

    """,

    """
    'archivo'
    Solicitud, peticion o favor de obtener informacion en formato xlsx (tambien te pueden pedir esto como 'excel' o 'Excel') o comma separated values (csv), si se te pide una tabla de estos formatos,
    asume que es este tipo de mensaje. Si ves cualquiera de las palabras xlsx/excel/Excel/XLSX o CSV/csv escritas, asume que es este tipo de mensaje.
    Esta ultima condicion toma prioridad por sobre cualquier otro tipo de mensaje.

    Si es que clasificas la pregunta como tipo 'archivo', y hay mensajes anteriores en la conversación, responde exclusivamente con "xlsx" o "csv" según lo soliciten.
    Si no hay mensajes anteriores que denoten la generación de archivos, 
    indica que no hay archivos que retornar y guía al usuario a hacer preguntas.
    Ejemplo: Deseo la informacion en formato csv. Respuesta esperada: csv
    Ejemplo: Puedes generarme un xlsx de la data que has obtenido. Respuesta esperada: xlsx
    """,

    """
    'grafico'
    Solicitud, peticion o favor para graficar la informacion obtenida, cualquier tipo de mensaje que haga referencia a graficos o a modificar algo de estos,
    considerala un mensaje de este tipo.

    Si es que clasificas la pregunta como 'grafico', responde solamente con "graph"
    si no hay mensajes anteriores con los que se pueda trabajar en la creacion de un grafico, indica al usuario que no hay archivos con los que se pueda graficar, y guialo a preguntar algo.
        
    """,

    """
    'conversacion':
    Una conversacion en lenguaje natural que NO sea: 
    Una solicitud referente al ambito de un hospital, la fundacion, nombres de pacientes o doctores etc
    Una peticion para graficar algo 
    Una peticion para generar algun tipo de archivo.

    Si es que clasificas la pregunta como 'conversacion', Responde de manera amigable las preguntas presentándote y orientando al usuario a que te haga una pregunta sobre la informacion que
    maneja FALP sobre pacientes doctores y atenciones. En caso de ser mencion de un nombre sin mencion de un rol o labor, solicita el rol o labor de la persona en cuestion. Una vez tengas esta informacion 
    consideralo un mensaje tipo consulta. 
    """

]