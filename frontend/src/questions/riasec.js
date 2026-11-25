// Spanish translations of the 48 OpenPsychometrics RIASEC activities.
// IDs and order match the source codebook (R1..C8); each answer uses 1..5.
const ITEMS = {
    R: [
        "Revisar la calidad de piezas antes de enviarlas",
        "Colocar ladrillos o azulejos",
        "Trabajar en una plataforma petrolera en alta mar",
        "Ensamblar componentes electrónicos",
        "Operar una máquina rectificadora en una fábrica",
        "Reparar una llave de agua averiada",
        "Ensamblar productos en una fábrica",
        "Instalar pisos en viviendas",
    ],
    I: [
        "Estudiar la estructura del cuerpo humano",
        "Estudiar el comportamiento de los animales",
        "Investigar sobre plantas o animales",
        "Desarrollar un tratamiento o procedimiento médico nuevo",
        "Realizar investigación biológica",
        "Estudiar ballenas y otros tipos de vida marina",
        "Trabajar en un laboratorio de biología",
        "Elaborar un mapa del fondo del océano",
    ],
    A: [
        "Dirigir un coro musical",
        "Dirigir una obra de teatro",
        "Diseñar ilustraciones para revistas",
        "Escribir una canción",
        "Escribir libros u obras de teatro",
        "Tocar un instrumento musical",
        "Realizar escenas de riesgo para una película o programa de televisión",
        "Diseñar escenografías para obras de teatro",
    ],
    S: [
        "Orientar a otras personas sobre su carrera profesional",
        "Hacer trabajo voluntario en una organización sin fines de lucro",
        "Ayudar a personas con problemas de drogas o alcohol",
        "Enseñar a una persona una rutina de ejercicio",
        "Ayudar a personas con problemas familiares",
        "Supervisar las actividades de niñas y niños en un campamento",
        "Enseñar a leer a niñas y niños",
        "Ayudar a personas mayores con sus actividades diarias",
    ],
    E: [
        "Vender franquicias de restaurantes a otras personas",
        "Vender productos en una tienda departamental",
        "Dirigir las operaciones de un hotel",
        "Administrar un salón de belleza o una barbería",
        "Dirigir un departamento dentro de una empresa grande",
        "Administrar una tienda de ropa",
        "Vender casas",
        "Dirigir una tienda de juguetes",
    ],
    C: [
        "Preparar los pagos mensuales de nómina de una oficina",
        "Hacer inventario de suministros con una computadora portátil",
        "Usar un programa de computadora para generar facturas a clientes",
        "Mantener actualizados los expedientes del personal",
        "Calcular y registrar datos estadísticos y otros datos numéricos",
        "Usar una calculadora",
        "Atender transacciones bancarias de clientes",
        "Llevar registros de envíos y recepciones",
    ],
};

const ANSWERS = {
    answer_a: "Me desagrada mucho",
    answer_b: "No me gusta",
    answer_c: "Me es indiferente",
    answer_d: "Me gusta",
    answer_e: "Me gusta mucho",
};
const VALUES = { answer_a: 1, answer_b: 2, answer_c: 3, answer_d: 4, answer_e: 5 };

export const RIASEC_AREAS = ["R", "I", "A", "S", "E", "C"];
export const RIASEC_QUESTIONS = RIASEC_AREAS.flatMap(area =>
    ITEMS[area].map((question, index) => ({
        id: `${area}${index + 1}`,
        question,
        category: area,
        type: "riasec",
        answers: ANSWERS,
        likertMap: VALUES,
    }))
);
