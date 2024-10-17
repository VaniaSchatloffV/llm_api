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
    """,

    """Los tomátes son frutas rojas y muy ricas! son mis favoritos!

    """,

    """Una imagen de Bob esponja! Mira kristel! Una imagen de Bob esponja!"""
    
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