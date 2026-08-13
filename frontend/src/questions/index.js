// Inventario de Intereses de Karl Hereford (90 ítems).
// Cada ítem se califica en escala Likert 1..5 (a..e).
// Mantiene 10 reactivos por cada una de las 9 áreas usadas por el backend.

const LIKERT_LABELS = {
    answer_a: "Me desagrada mucho",  // 1
    answer_b: "No me gusta",         // 2
    answer_c: "Me es indiferente",   // 3
    answer_d: "Me gusta",            // 4
    answer_e: "Me gusta mucho"       // 5
};

const LIKERT_MAP = {
    answer_a: 1,
    answer_b: 2,
    answer_c: 3,
    answer_d: 4,
    answer_e: 5
};

// Tabla de categorías por número de reactivo (del concentrado oficial)
const CATEGORIAS = {
    "Cálculo":              new Set([3,11,22,32,37,48,59,64,73,88]),
    "C. Físico":            new Set([8,14,30,39,45,53,57,68,81,84]),
    "C. Biológico":         new Set([5,18,24,36,40,51,61,69,76,90]),
    "Mecánico":             new Set([1,16,26,34,43,46,63,66,79,82]),
    "Servicio Social":      new Set([6,13,19,21,29,49,56,71,77,86]),
    "Literario":            new Set([9,12,25,28,42,52,62,67,78,83]),
    "Persuasivo":           new Set([2,17,27,35,38,47,55,72,75,87]),
    "Artístico":            new Set([7,10,20,31,44,50,58,65,80,85]),
    "Musical":              new Set([4,15,23,33,41,54,60,70,74,89])
};

// Lista original de 90 enunciados (en el orden del cuadernillo).
export const HEREFORD_QUESTIONS = [
    "Reparar una licuadora",                                  // 1
    "Participar en debates y argumentos",                     // 2
    "Resolver rompecabezas numéricos",                        // 3
    "Aprender a leer música",                                 // 4
    "Hacer análisis de sangre",                               // 5
    "Visitar orfelinatos",                                    // 6
    "Pintar paisajes",                                        // 7
    "Tomar fotografías de las fases de un eclipse",           // 8
    "Escribir cuentos para una revista",                      // 9
    "Recibir un juego de pinturas de óleo como regalo",       // 10
    "Ejecutar mecanizaciones aritméticas",                    // 11
    "Ser escritor de novelas",                                // 12
    "Participar en campañas contra la delincuencia juvenil",  // 13
    "Recibir un telescopio como regalo",                      // 14
    "Saber distinguir y apreciar la buena música",            // 15
    "Manejar un torno o taladro eléctrico",                   // 16
    "Ayudar a los candidatos políticos",                      // 17
    "Hacer colecciones de plantas",                           // 18
    "Colaborar con otros para bien de ellos y de mí mismo",   // 19
    "Asistir a exposiciones de pintura",                      // 20
    "Impartir conocimientos a aquellas personas que no los tienen", // 21
    "Convertir radios a grados",                              // 22
    "Tener discos de música clásica",                         // 23
    "Aprender a practicar primeros auxilios",                 // 24
    "Leer a los clásicos",                                    // 25
    "Hacer dibujos de máquinas",                              // 26
    "Hacer campañas estadísticas",                            // 27
    "Saber distinguir y apreciar la buena literatura",        // 28
    "Ayudar a encontrar empleo a personas de escasos recursos", // 29
    "Informarme sobre la energía atómica",                    // 30
    "Leer libros sobre arte",                                 // 31
    "Calcular el área de un cuarto para alfombrarse",         // 32
    "Escuchar los conciertos en las plazas públicas",         // 33
    "Instalar un contacto eléctrico",                         // 34
    "Convencer a otros para que hagan lo que yo creo deben hacer", // 35
    "Cuidar un pequeño acuario",                              // 36
    "Usar una regla de cálculo",                              // 37
    "Ser protagonista de artículos nuevos",                   // 38
    "Hacer una colección de rocas",                           // 39
    "Observar las costumbres de las abejas",                  // 40
    "Obtener el autógrafo de un músico famoso",               // 41
    "Asistir a la biblioteca en una tarde libre",             // 42
    "Observar como el técnico repara la televisión",          // 43
    "Diseñar escenarios para representaciones teatrales",     // 44
    "Observar el movimiento aparente de las estrellas",       // 45
    "Soldar alambres o partes metálicas",                     // 46
    "Defender un punto de vista de alguna persona",           // 47
    "Calcular porcentajes",                                   // 48
    "Servir como consejero en un club de niños",              // 49
    "Hacer mosaicos artísticos para decoraciones",            // 50
    "Asistir a una operación médica",                         // 51
    "Participar en concursos literarios",                     // 52
    "Estudiar el espectro luminoso de la luz",                // 53
    "Asistir a conciertos",                                   // 54
    "Ser “líder” de un grupo",                                // 55
    "Leer cuentos a los ciegos",                              // 56
    "Visitar una exposición científica",                      // 57
    "Hacer diseños para tapices",                             // 58
    "Consultar tablas de logaritmos y raíces",                // 59
    "Estudiar la música de diferentes países como la India, el Japón, etc.", // 60
    "Leer libros sobre el funcionamiento de los organismos vivos", // 61
    "Corregir composiciones o artículos periodísticos",       // 62
    "Observar como los mecánicos hacen reparaciones de coches", // 63
    "Ayudar a otras personas con problemas matemáticos",      // 64
    "Dibujar o delinear personas o cosas",                    // 65
    "Desarmar y armar un reloj",                              // 66
    "Escribir reseñas críticas de libros",                    // 67
    "Estudiar los cambios del tiempo y sus causas",           // 68
    "Hacer colecciones de insectos",                          // 69
    "Tomar parte en un conjunto coral",                       // 70
    "Escuchar a otros con paciencia y comprender su punto de vista", // 71
    "Organizar y dirigir festivales, excursiones o campañas sociales.", // 72
    "Ilustrar problemas geométricos con ayuda de escuadras, regla T y compás", // 73
    "Tocar un instrumento musical",                           // 74
    "Dirigir un grupo o equipo en situaciones difíciles",     // 75
    "Cultivar plantas exóticas",                              // 76
    "Visitar casas humildes para determinar lo que necesitan", // 77
    "Escribir cartas narrativas a mis amigos o parientes",    // 78
    "Armar o componer muebles comunes",                       // 79
    "Saber distinguir y apreciar las buenas pinturas",        // 80
    "Visitar un observatorio astronómico",                    // 81
    "Observar las máquinas cuando las montan",                // 82
    "Escribir artículos en el periódico",                     // 83
    "Experimentar con la necesidad de oxígeno para la combustión", // 84
    "Hacer un proyecto de decoración interior",               // 85
    "Cuidar a mis hermanos menores",                          // 86
    "Mostrar un nuevo producto al público",                   // 87
    "Resolver problemas matemáticos",                         // 88
    "Ser compositor de música",                               // 89
    "Observar a menudo como transportan las hormigas su carga" // 90
];

// Determina la categoría de un reactivo según su número
function categoriaDeReactivo(n) {
    for (const [cat, set] of Object.entries(CATEGORIAS)) {
        if (set.has(n)) return cat;
    }
    return "Intereses"; // fallback genérico
}

// Construye el objeto de respuestas para la escala Likert.
function buildAnswers() {
    return {
        answer_a: LIKERT_LABELS.answer_a,
        answer_b: LIKERT_LABELS.answer_b,
        answer_c: LIKERT_LABELS.answer_c,
        answer_d: LIKERT_LABELS.answer_d,
        answer_e: LIKERT_LABELS.answer_e,
        answer_f: null
    };
}

function buildCorrectAnswersAllTrue() {
    return {
        answer_a_correct: "true",
        answer_b_correct: "true",
        answer_c_correct: "true",
        answer_d_correct: "true",
        answer_e_correct: "true",
        answer_f_correct: "true"
    };
}

function buildOptions(options) {
    return options.reduce((acc, option, index) => {
        acc[`answer_${index}`] = option;
        return acc;
    }, {});
}

const FOOD_OPTIONS = ["Nunca", "1–2 porciones", "3–5 porciones", "6–10 porciones", "Más de 10"];

export const SOCIOECONOMIC_QUESTIONS = [
    {
        id: "socio_birth_year",
        question: "Año de nacimiento",
        input: true,
    },
    {
        id: "socio_current_grade",
        question: "Grado que cursas actualmente:",
        answers: buildOptions(["Secundaria.", "Preparatoria/Bachillerato.", "Universidad.", "No estoy estudiando actuamente."]),
    },
    {
        id: "socio_family_income",
        question: "¿Cuál es el ingreso familiar mensual?",
        answers: buildOptions(["Menos de $5,000", "$5,001–10,000", "$10,001–20,000", "Más de $20,000"]),
    },
    {
        id: "socio_personal_income",
        question: "¿Cuál es el ingreso personal mensual?",
        answers: buildOptions(["No tengo ingresos", "Menos de $3,000", "$3,001–6,000", "Más de $6,000"]),
    },
    {
        id: "socio_head_education",
        question: "Pensando en el jefe o jefa del hogar, ¿cuál fue el último grado de estudios que aprobó en la escuela?",
        answers: buildOptions([
            "Sin instrucción",
            "Primaria incompleta",
            "Primaria completa",
            "Secundaria incompleta",
            "Secundaria completa",
            "Carrera comercial",
            "Carrera técnica",
            "Preparatoria incompleta",
            "Preparatoria completa",
            "Licenciatura incompleta",
            "Licenciatura completa",
            "Diplomado o maestría",
            "Doctorado",
        ]),
        amaiKey: "education",
    },
    {
        id: "socio_father_occupation",
        question: "Ocupación actual del padre",
        answers: buildOptions(["Empleado", "Trabajo informal/obrero", "Comerciante", "Desempleado", "Profesionista"]),
    },
    {
        id: "socio_mother_occupation",
        question: "Ocupación actual de la madre",
        answers: buildOptions(["Empleada", "Trabajo informal/obrera", "Comerciante", "Desempleada", "Profesionista"]),
    },
    {
        id: "socio_cars",
        question: "¿Cuántos automóviles, camionetas cerradas, vans o pick-ups tiene este hogar?",
        answers: buildOptions(["0", "1", "2", "3", "mas de 3"]),
        amaiKey: "cars",
    },
    {
        id: "socio_services",
        question: "Seleccione los servicios y bienes con los que cuenta en su casa",
        answers: buildOptions([
            "Drenaje",
            "Agua entubada",
            "Alumbrado público",
            "Calles pavimentadas",
            "Recolección periódica de basura",
            "Calentador de gas para agua",
            "Un cuarto propio para dormir",
            "Un lugar exclusivo para estudiar",
            "Teléfono",
            "Teléfono celular",
            "Televisión",
            "Televisión por cable o satélite",
            "Calculadora",
            "Computadora",
            "Diccionario o enciclopedia",
            "Suscripción a revista o periódico",
        ]),
        multiple: true,
    },
    {
        id: "socio_internet",
        question: "Sin tomar en cuenta la conexión móvil desde algún celular, ¿su hogar cuenta con internet?",
        answers: buildOptions(["Si", "No"]),
        amaiKey: "internet",
    },
    {
        id: "socio_bedrooms",
        question: "¿Cuántos cuartos tiene su casa que se utilizan para dormir?",
        answers: buildOptions(["0", "1", "2", "3", "4", "5", "6 o más"]),
        amaiKey: "bedrooms",
    },
    {
        id: "socio_household_people",
        question: "¿Cuántas personas viven en su casa, incluido usted?",
        answers: buildOptions(["1", "2", "3", "4", "5", "6", "7 o más"]),
    },
    {
        id: "socio_bathrooms",
        question: "¿Cuántos baños completos tiene esta vivienda con excusado/WC y regadera?",
        answers: buildOptions(["0", "1", "2", "3 o más"]),
        amaiKey: "bathrooms",
    },
    {
        id: "socio_workers",
        question: "¿Cuántas personas de 14 años o más trabajan actualmente o trabajaron el mes pasado?",
        answers: buildOptions(["0", "1", "2", "3", "4", "5", "6 o más"]),
        amaiKey: "workers",
    },
    ...["Carne", "Huevos", "Leche", "Frutas y verduras", "Frijoles/arroz/lentejas", "Pan", "Cereales"].map(food => ({
        id: `socio_food_${food.toLowerCase().replace(/[^a-záéíóúñ]+/gi, "_")}`,
        question: `A la semana, ¿qué tanto consume los siguientes alimentos? [${food}]`,
        answers: buildOptions(FOOD_OPTIONS),
    })),
].map(question => ({
    ...question,
    category: "Socioeconómico",
    type: "socioeconomic",
    tags: [{ name: question.multiple ? "Opción múltiple" : "Opción única" }],
}));

const HEREFORD_ITEMS = HEREFORD_QUESTIONS.map((texto, idx) => {
    const numero = idx + 1;
    return {
        id: numero,                     // usa el número de reactivo como ID
        question: texto,
        description: null,
        answers: buildAnswers(),
        likertMap: { ...LIKERT_MAP },
        multiple_correct_answers: "true",
        correct_answers: buildCorrectAnswersAllTrue(),
        correct_answer: null,
        tags: [{ name: "Likert" }],
        category: categoriaDeReactivo(numero),
        type: "hereford",
        difficulty: "Easy"
    };
});

export const MOCK_QUESTIONS = [...HEREFORD_ITEMS, ...SOCIOECONOMIC_QUESTIONS];
