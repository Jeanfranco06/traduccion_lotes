Revisión
Avanzando en el Cuidado de la Salud con Gemelos Digitales: Metarrevisión
de Aplicaciones y Desafíos de Implementación
Mickaël Ringeval1, PhD; Faustin Armel Etindele Sosso2, DBA; Martin
Cousineau1, PhD; Guy Paré1, PhD
1HEC Montréal, Montréal, QC, Canada
2Centre Intégré Universitaire de Santé et de Services Sociaux du
Nord-de-l?Île-de-Montréal, Montréal, QC, Canada
Autor Correspondiente:
Mickaël Ringeval, PhD
HEC Montréal
3000 Chemin de la Côte-Sainte-Catherine
Montréal, QC, H3T 2A7
Canada
Teléfono: 1 5143406000
Correo electrónico:
Resumen
Antecedentes: Los gemelos digitales (DT, por sus siglas en inglés) son
representaciones digitales de sistemas del mundo real, que permiten
simulaciones avanzadas, modelado predictivo y optimización en tiempo real
en diversos campos, incluido el cuidado de la salud. A pesar del creciente
interés, la integración de los DT en el cuidado de la salud enfrenta desafíos
como aplicaciones fragmentadas, preocupaciones éticas y barreras para su
adopción.
Objetivo: Este estudio revisa sistemáticamente la literatura existente sobre
las aplicaciones de los DT en el cuidado de la salud con tres objetivos: (1)
mapear las aplicaciones principales, (2) identificar los desafíos y limitaciones
clave, y (3) resaltar las brechas que puedan guiar futuras investigaciones.
Métodos: Se realizó una metarrevisión de manera sistemática, adhiriéndose
a las directrices PRISMA-ScR (Preferred Reporting Items for Systematic
Reviews and Meta-Analyses extension for Scoping Reviews), e incluyó 25
revisiones de la literatura publicadas entre 2021 y 2024. La búsqueda abarcó
5 bases de datos: PubMed, CINAHL, Web de la Ciencia (Web of Science),
Página 1
Página 2
Embase y PsycINFO. Se utilizó la síntesis temática para categorizar las
aplicaciones de los DT, las partes interesadas y las barreras para su
adopción.
Resultados: Se identificó un total de 3 aplicaciones principales de los DT en
el cuidado de la salud: medicina personalizada, eficiencia operativa e
investigación médica. Si bien las aplicaciones actuales, como el diagnóstico
predictivo, las simulaciones de tratamientos específicos para pacientes y la
optimización de recursos hospitalarios, se encuentran en sus primeras
etapas de desarrollo, ponen de relieve el importante potencial de los DT. Los
desafíos incluyen la calidad de los datos, cuestiones éticas y barreras
socioeconómicas. Esta revisión también identificó brechas en la
escalabilidad, la interoperabilidad y la validación clínica.
Conclusiones: Los DT tienen un potencial transformador en el cuidado de la
salud, ya que proporcionan atención individualizada, optimización operativa e
investigación acelerada. Sin embargo, su adopción se ve obstaculizada por
barreras técnicas, éticas y financieras. Abordar estos problemas requiere
colaboración interdisciplinaria, protocolos estandarizados y estrategias de
implementación inclusivas para garantizar un acceso equitativo y un impacto
significativo.
(J Med Internet Res 2025;27:e69544)
gemelos digitales; metarrevisión; informática de la salud; aplicaciones;
desafíos; innovación en salud; medicina personalizada; eficiencia operativa
Introducción
Los gemelos digitales (DT) son réplicas digitales de entidades, procesos o
sistemas físicos que se actualizan dinámicamente con datos en tiempo real
para reflejar a sus contrapartes del mundo real [1-4]. Permiten el modelado
predictivo, el apoyo a la toma de decisiones y las simulaciones
personalizadas en el cuidado de la salud. Los DT se presentan a menudo
como modelos 3D o paneles de control (dashboards); por ejemplo, un DT
cardíaco puede aparecer como una simulación visual en tiempo real del
corazón de un paciente. Los clínicos pueden
interactuar con el modelo probando diferentes escenarios de tratamiento,
Página 2
Página 3
como ajustar las dosificaciones de medicamentos o simular intervenciones
quirúrgicas, y observar cómo se comporta el corazón, mostrando cambios en
la función, el flujo sanguíneo o posibles complicaciones en tiempo real. Esta
tecnología aprovecha los sensores, la analítica y el aprendizaje automático
(machine learning) para permitir el seguimiento, la simulación y perspectivas
predictivas. Caracterizados por su capacidad para adaptarse a entradas de
datos en vivo, los DT facilitan la optimización en tiempo real, la evaluación de
riesgos y una mejor toma de decisiones en todas las industrias, desde la
fabricación hasta el cuidado de la salud.
Los DT ofrecen ventajas transformadoras sobre las herramientas
tradicionales al proporcionar información en tiempo real y análisis predictivos
que mejoran la eficiencia operativa y la toma de decisiones. En sectores
como el aeroespacial, los DT han reducido los tiempos de desarrollo hasta
en un 50% y han mejorado significativamente la calidad del producto [5]. A
medida que esta tecnología avanza, se espera que el mercado global de DT
crezca rápidamente, alcanzando los 110.100 millones de dólares
estadounidenses para 2028, con una tasa de crecimiento anual del 60% [6].
Solo en el cuidado de la salud, el mercado se valora en 1.600 millones de
dólares estadounidenses en 2023 y se proyecta que crezca a 21.100
millones de dólares estadounidenses para 2028, lo que representa casi el
20% del mercado total de DT [7].
Las aplicaciones de los DT en el cuidado de la salud ofrecen el potencial de
simular escenarios complejos de pacientes, respaldar diagnósticos
predictivos y permitir una planificación de tratamientos personalizada en
tiempo real basada en datos de salud en vivo [2]. Sin embargo, al ser una
nueva tecnología en el campo biomédico, la investigación sobre DT en el
cuidado de la salud abarca una amplia gama de aplicaciones clínicas y
operativas en diferentes etapas de desarrollo, que van desde modelos
teóricos hasta etapas experimentales avanzadas. Esta diversidad ?desde el
modelado individualizado de pacientes hasta la optimización del flujo de
trabajo hospitalario? crea un cuerpo de investigación fragmentado, donde los
conceptos teóricos y los modelos experimentales varían ampliamente en
Página 3
Página 4
sofisticación. La variabilidad en las fuentes de datos, el diseño de modelos y
los objetivos previstos limita el consenso sobre las mejores prácticas y las
vías de implementación [8]. Estos factores ponen de relieve la necesidad de
una revisión sistemática para sintetizar la investigación existente, mapear las
diversas aplicaciones de los DT e identificar las brechas y desafíos que
persisten.
El objetivo de esta revisión es triple. En primer lugar, busca proporcionar una
visión general estructurada del campo, destacando las diversas aplicaciones
de los DT en el cuidado de la salud. En segundo lugar, identifica y examina
las barreras para la adopción de los DT, junto con las estrategias potenciales
para abordarlas. En tercer lugar, señala las brechas en el conocimiento
existente para guiar futuras investigaciones. Las preguntas de investigación
abordadas son las siguientes: (1) ¿Cuáles son las principales aplicaciones
de los DT en el cuidado de la salud según lo identificado en la literatura
existente? (2) ¿Cuáles son los desafíos y limitaciones clave asociados con la
implementación de DT en el cuidado de la salud? (3) ¿Qué brechas existen
en la investigación actual sobre DT en el cuidado de la salud y cuáles son las
implicaciones para la investigación y la práctica futuras?
del campo y una síntesis más profunda de los hallazgos existentes. Para
abordar esta doble necesidad, nos inspiramos en los enfoques
metodológicos de Sarrami-Foroushani et al [10], incorporando elementos de
metarrevisiones de alcance (scoping meta-reviews). Este enfoque híbrido
nos permitió mapear sistemáticamente la literatura mientras evaluábamos
todas las revisiones existentes, lo que permitió una comprensión integral del
campo sin restringir nuestro análisis únicamente a las revisiones
sistemáticas.
Estrategia de Búsqueda y Criterios de Selección
Se realizó una búsqueda bibliográfica exhaustiva en múltiples bases de
datos electrónicas sin restricciones de fecha, recuperando todos los registros
disponibles hasta el 15 de mayo de 2024. Las bases de datos incluyeron
PubMed, CINAHL, Web of Science, Embase y PsycINFO. La estrategia de
búsqueda y la selección de bases de datos se desarrollaron en colaboración
con un bibliotecario profesional, quien también ejecutó las búsquedas. El
Página 4
Página 5
protocolo de esta revisión está registrado en Open Science Framework [11].
Los términos de búsqueda clave incluyeron ?digital twin,? ?intelligent twin,? y
?mirror twin? combinados con ?review,? ?systematic review,? y
?meta-analysis.? Para garantizar la inclusión de todos los estudios
potencialmente relevantes, se revisaron manualmente las listas de
referencias de los artículos seleccionados (término de la bola de nieve /
snowballing). La estrategia de búsqueda completa para cada base de datos
se proporciona en el Apéndice Multimedia 1.
Establecimos los criterios de inclusión al inicio de este estudio, permitiendo
posibles revisiones durante el proceso. Los artículos eran elegibles para su
inclusión si cumplían con los siguientes criterios: (1) artículo de revisión de la
literatura (de cualquier tipo), (2) específicamente sobre DT, (3) en el contexto
del cuidado de la salud, y (4) accesible en texto completo en inglés o
francés. Si un artículo hacía referencia a aplicaciones de DT tanto en el
cuidado de la salud como en otros entornos, solo se consideraron las
aplicaciones relacionadas con el cuidado de la salud.
Todo
references were organized and deduplicated using EndNote (Clarivate), while
Covidence (Veritas Health Innovation Ltd) was used for this study selection
process.
Study Selection
Two reviewers (MR and FAES) independently screened all titles and
abstracts, with an initial screening of 30 references conducted to ensure a
shared understanding of the selection criteria. This was followed by a full-text
screening of selected studies to confirm eligibility.
Methods The meta-review initially yielded 3377 references. After
Study Design
This meta-review was conducted and reported following the PRISMA-ScR
(Preferred Reporting Items for Systematic
removing duplicates, we screened the titles and abstracts of 2921 references,
retaining 65 for full-text review. Ultimately, 25 references were included in this
review, with reasons for excluding others provided in the figure in the Results
section.
Página 5
Página 6
methodological rigor [9]. The decision to use PRISMA-ScR reflects the
emergent nature of DT research in health care, which requires a scoping
approach to capture the breadth and diversity of this rapidly evolving field.
Despite its emergent status, the field has already produced multiple literature
reviews, indicating a growing maturity in this research stream. This apparent
paradox reflects the rapid pace at which new knowledge is
Two authors (MR and FAES) independently extracted data from each of the
included studies. Discrepancies were resolved through discussion. The
following data were recorded: author, year, type of literature review (as
reported), research questions, search period, included databases, final
sample size, what DT models, DT application, potential or actual applications,
DT provider, DT users, DT impacts, DT challenges, and main study
A mixed methods approach was used, combining descriptive and thematic
analysis to map the landscape of DT technology in health care. Descriptive
analysis was used initially to summarize the general characteristics of the
included studies, covering the range of review types, publication years, and
scope of DT applications.
As most reviews did not specify the type of review conducted (eg, scoping
review and narrative review), we classified all reviews based on predefined
criteria [12,13]. This classification process was conducted by one reviewer
(MR) and verified by a second reviewer (FAES). Any discrepancies were
resolved
Figure 1. Flow diagram.
categorization of review types.
Results
General Characteristics of the Included Reviews
The included studies were published between 2021 and 2024 (Figure 1).
Most of the reviews were categorized as scoping reviews (14/25, 56%)
[1,2,14-25]. The remaining reviews included 6 narrative reviews (6/25, 24%)
[26-31], 2 rapid reviews (2/25, 8%) [8,32], and 3 reviews for which a type
could not be determined (3/25, 12%; see Multimedia Appendix 2 for the
PRISMA-ScR checklist) [3,4,33].
Studied Populations and Key Users of DTs
Página 6
Página 7
Targeted Populations
The reviews cover various populations, defined as the individuals or groups
impacted by the outcomes of the DT
28%) [1,2,14,17,22,30,31] or multiple sclerosis (3/25, 12%) [20,24,25],
suggesting targeted applications of DTs in managing chronic or complex
conditions. Lastly, a small subset of reviews (2/25, 8%) does not specify any
population for particular DT uses [30,32].
application. For example, a DT designed for personalized Users of DTs
medicine would mainly benefit patients, whether or not they were diagnosed
with a specific disease.
Health care providers are a key target in 48% (12/25) of the
DTs are used by various stakeholders, each benefiting uniquely from this
technology. The primary users include patients [4,22-25,28,32,33], hospital
management [8,14,19,21,28-30,32],
general are the focus of another 48% (12/25) of the reviews
[2-4,8,14,19-21,27,28,30,32], underscoring the broad potential of DTs to
impact patient care across diverse contexts. Beyond these general
categories, 32% (8/25) of the reviews examine the general population
[2,8,14,20,21,27-29], highlighting DT applications that extend to broader
public health or societal benefits. Some studies further specify particular
patient populations, such as those with cardiovascular diseases (7/25,
[1,3,4,14,16,17,19,22-27,29-31,33], physicians [14,20,30,32], and
researchers [2-4,14-17,19,20,22-25,27,29-31,33].
For patients, DTs provide tools to actively manage health conditions. For
instance, patients with migraines [32] benefit from DT systems that integrate
data from wearables and health records, offering real-time monitoring and
predicting potential migraine triggers. This capability empowers patients to
make informed decisions about lifestyle adjustments and treatment
adherence, enhancing personal control over their condition by reducing the
frequency or severity of migraine episodes.
In hospital management, DTs enhance operations across four main functions
Página 7
Página 8
[8,14,21]. First, they improve safety by simulating emergency scenarios,
allowing hospitals to identify risks and refine response protocols to protect
patient well-being. Second, DTs streamline information management by
consolidating real-time data from various sources, which
departments. Third, in promoting health and well-being, DTs support
personalized patient care by providing tools that adapt treatment protocols to
individual data and forecast patient health trends, assisting health care
professionals in delivering tailored interventions and preventive care. Lastly,
DTs ensure efficient operational control by optimizing resource allocation,
managing patient flow, and enabling predictive maintenance for equipment,
which reduces patient wait times and enhances overall hospital
changing demands. Clinicians and researchers leverage DTs to simulate
virtual trials, advancing drug development and treatment refinement. These
applications correspond to 3 main areas: personalized medicine, operational
efficiency and resource management, and advancements in medical
research and drug development.
Main Categories of DT Applications and Potential Benefits
DTs have emerged as a transformative tool in health care, offering tailored
solutions across various applications. The following sections present 3 critical
categories of DT applications, each accompanied by tables outlining the
inputs, processes, and outputs relevant to each application. These tables
provide a structured view of how concrete DT applications address specific
health care challenges, optimize resources, and drive advancements in
patient care and medical research.
efficiency. Category 1: Customized Treatment and Care
DTs also serve as valuable tools for health care professionals, Optimization
especially in supporting clinical decision-making and personalized treatment
strategies. For complex cases such as cardiovascular and immune-mediated
diseases, DTs enable clinicians to simulate patient-specific responses by
integrating clinical, genetic, and environmental data. In cardiovascular care
[1,17,19,20,30,31], DTs simulate heart function and disease progression,
supporting tailored interventions based on individual patient profiles. By
predicting and addressing patient-specific risks in real time, DTs enhance
Página 8
Página 9
precision in medical practice, advancing the quality and personalization of
One of the main applications of DTs in health care is customized treatment
and care optimization (Table 1). DTs span various stages of development,
from proof-of-concept models [1,8,14,17,19,20,28,30] to applications under
active research and clinical testing [1,4,8,14-17,19,20,22,30-32]. Companies
such as Dassault Systèmes, through their Living Heart Project
[1,14,17,19,20], and Siemens [14,17,19,26] are at the forefront of these
advancements. Other institutions have also developed some specific DTs,
such as Medtronic with 3D cardiac maps [14,17] and Oklahoma State
University with targeting
care. tumor-only locations [14]. Some studies underscore the potential
In sum, DTs support distinct user groups within health care. Patients and
health care professionals, especially clinicians and physicians, benefit from
DTs by providing precise, individualized care. Hospital management relies on
DTs to enhance resource allocation, patient flow, and adaptability to
for DTs in complex areas [1,8,17,19,20,23,24,26,29,30,32], underscoring the
nascent stage of this innovation in the field. Given its relative novelty, it is
unsurprising that some review articles focus on potential applications while
others concentrate on actual implementations.
Table 1. DTaapplications in customized treatment and care optimization.
timize personalized treatment
plans, suggesting specific
drug doses, dietary adjust
ments, or lifestyle interven
tions tailored to each pa
tient?s condition and medical
history
?
Real-time decision-making: the DT can immediately alert
health care providers to
emerging risks such as ar
Página 9
Página 10
rhythmias or abnormal glu
cose levels, prompting timely
interventions or adjustments
in treatment
aDT: digital twin.
The customized treatment and care optimization approach addresses key
challenges in health care, including variability in patient physiology, delayed
detection of disease progression, and limited predictive capabilities. By
integrating diverse data inputs?such as clinical records, genomic information,
imaging
factors?sourced from electronic health record (EHR) systems, disease
registries, and wearable devices [1,8,14,19,20,23,32,33], DTs enable
comprehensive simulations of patient health profiles.
Through these simulations, DTs model disease progression, evaluate
potential treatment options, and assess various clinical scenarios, such as
predicting patient responses to new medications or lifestyle changes
[1,2,4,14,17,20,22,24,28-30,32]. Beyond simulation, DTs support optimization
by dynamically tailoring treatment plans to a patient?s evolving condition,
which may include adjusting medication dosages, recommending dietary
modifications, or suggesting lifestyle changes to improve outcomes
[1,2,4,8,14,19,20,22-24,30,32].
Moreover, DTs support real-time decision-making by providing health care
providers with alerts about emerging risks, such as abnormal glucose levels
[1,14,30] or arrhythmias [31], enabling
timely interventions. The outputs of this application?real-time monitoring,
improved diagnosis, and personalized health interventions?underscore the
potential of DTs to enhance personalized care and responsiveness in clinical
practice.
Category 2: Operational Efficiency and Resource Management
Another significant category of DT applications in health care refers to
operational efficiency and resource management (Table 2). DT technology
serves as a valuable tool for optimizing hospital operations across various
Página 10
Página 11
stages, from concept development [8,32] to active deployment [4,8,14,30].
For instance, GE HealthCare has developed a Command Center leveraging
DTs to simulate and enhance patient flow in hospitals, including Johns
Hopkins Hospital in Baltimore [8,14]. Similarly, organizations such as
BioSecure and Siemens Healthineers have implemented DT-based solutions
in health care settings [2,8] to optimize supply chain processes, improve
response times for critical patients, and streamline workflows. While many
initiatives demonstrate tangible benefits, others remain at the conceptual or
exploratory stage, showcasing the potential for future DT applications in
operational efficiency and resource management [21,23,32].
Table 2. DTaapplications in operational efficiency and resource management.
recommend ideal staffing
levels, identify underused or
overbooked resources, and
schedule maintenance during
low-demand periods
?Real-time decision-making:
the DT can suggest workflow
shifts, such as rerouting non
critical cases, and improve
discharge planning to free up
beds efficiently
aDT: digital twin.
The operational efficiency and resource management category addresses
critical challenges such as unpredictable patient volumes, the difficulty of
dynamically adapting workflows in critical situations, and the lack of real-time
operational insights that often result in inefficiencies and bottlenecks. By
leveraging inputs such as patient data and historical trends from hospital
information systems [19,23], DTs can simulate various hospital scenarios.
These simulations enable administrators to analyze how changes in patient
flow impact key factors such as wait times, bed availability, staffing needs,
and equipment use, thereby providing foresight into potential bottlenecks
Página 11
Página 12
effective crisis management strategies?highlight the significant potential of
DTs to enhance resource use and operational responsiveness in health care
facilities.
Category 3: Advancements in Medical Research and Drug Development
DT technology holds immense potential to transform medical research and
drug development through in silico clinical trials, encompassing both
prospective initiatives [3,17,19,30] and current applications (Table 3)
[2-4,14,15,17,19,30]. For instance, collaborations involving Unlearn AI,
Merck, Nvidia, and the
[2,8,14,19,23]. University of Florida [14,19] are using DT models to simulate
Beyond simulation, DTs enable optimization by recommending staffing
adjustments, identifying underused or overburdened resources, and
scheduling maintenance during low-demand periods [8,14,19,23,30,32].
Furthermore, DTs support real-time decision-making by suggesting workflow
modifications, such as reallocating noncritical cases or expediting discharge
planning to free up bed capacity [2,4,8,14,19,23]. The outputs of this
category?optimized patient flow, real-time staffing and equipment
adjustments, improved discharge planning, and
patient responses and design virtual clinical trials. These efforts enable the
execution of single-arm studies, which are particularly valuable in scenarios
where traditional randomized controlled trials may be unethical or impractical,
such as rare diseases or high-risk populations. By simulating control groups,
DTs help to reduce the need for placebo arms and contribute to minimizing
adverse drug reactions [14,19,30]. Other applications of DTs focus on
accelerating drug discovery and optimizing drug screening processes,
offering promising avenues in pharmaceutical research [2-4,15,17].
Table 3. DTaapplications in advancements of medical research and drug
development.
risks and costs associated
with traditional clinical tri
als
Página 12
Página 13
?Real-time decision-making:
If adverse reactions are pre
dicted, DTs can recommend
alternative treatment strate
gies, improving patient
safety and the trial?s overall
effectiveness
aDT: digital twin.
This category of DT applications addresses critical challenges Types of DT
in clinical trials, including the high costs and time demands of traditional
physical trials, ethical concerns related to testing on human
participants?particularly in vulnerable populations?and the limited capacity to
predict individualized patient responses. By integrating diverse data inputs
such as clinical, genomic, imaging, and physiological data from sources such
as EHRs, health databases, and pharmaceutical trial data [2,3,30], DTs
enable the simulation of clinical trials in digital environments.
These simulations allow researchers to evaluate early-stage drug efficacy
and safety across diverse patient profiles without the need for large-scale
physical trials. This approach reduces costs and enhances safety through
synthetic control groups [2-4,14,17,19]. Beyond simulation, DTs enable the
optimization of trial parameters by adjusting dosages, selecting ideal patient
cohorts, refining drug formulations, and identifying optimal therapeutic
protocols. These capabilities help minimize unnecessary risks and costs
[2-4,14,15,19].
Additionally, DTs support real-time decision-making by predicting adverse
reactions and suggesting alternative treatment strategies to improve both
patient safety and the trial?s overall
The classification of DT technologies originates from industry practices (eg,
[34]), where DTs are typically categorized based on the scale and scope of
the entities they represent. This framework enables a clear distinction
between DTs by their purpose and level of detail, ranging from individual
components to larger systems and entire processes.
Component or part DTs represent the most granular level, simulating
Página 13
Página 14
individual components within larger systems. Examples include specific
cardiac functions, such as aortic aneurysm [19], coronary anatomy [31], and
coronary vessels [17]. Additionally, they encompass representations of
individual cognitive profiles [25]. Asset or product DTs replicate individual
physical assets, such as organs or medical equipment, to provide insights
into performance and maintenance needs. This category includes organs
[1,3,14,16,17,19,20,22,24,26,30,31], such as the heart [1,14,17,19,20,30,31]
or the brain [14], as well as, to a lesser extent, diseases and therapeutic
equipment [14,33]. System or unit DTs focus on the interactions of multiple
components within a system. Examples include models of the human body
(IDs 4, 21, 22, and 25), patients in various health
applications?including synthetic control groups, predictive modeling of drug
responses, and virtualized patient-specific trials?demonstrate how DTs can
significantly enhance the efficiency, accuracy, and personalization of clinical
trials, making them more adaptable to the needs of diverse patient
populations.
systems [8,14]. Lastly, process DTs simulate entire workflows to optimize
health care operations. These include broader infrastructure models such as
buildings [29], health care systems [8], hospitals [8,19], and physical systems
[23].
DT Implementation Challenges
The implementation of DT technology in health care organizations faces
several critical challenges, which can be
grouped into 3 main categories: data and model integrity; ethical, regulatory,
and governance challenges; and implementation and socioeconomic
disparities.
First, data and model integrity encompasses issues related to data quality,
availability, and the robustness of DT models. Limited access to high-quality
data, difficulties in data integration, and privacy concerns represent
significant barriers to adoption. Additionally, computational power demands
and scalability challenges further complicate implementation
Página 14
Página 15
[1,2,4,8,14-21,23,24,26,27,29,32,33]. Ensuring model validation and
reproducibility remains a pressing issue, as the absence of standardized
methods and randomized controlled trials undermines the clinical credibility of
DTs. Moreover, the need to enhance model complexity to better capture
individual patient variations highlights the current technological limitations of
DTs [3,16,19,22,26,28,31].
Second, ethical, regulatory, and governance challenges address ethical
considerations and the regulatory frameworks surrounding the use of DTs.
Persistent concerns about bias, fairness, and data ownership highlight the
risk of exacerbating existing socioeconomic disparities. Ethical dilemmas
arise regarding informed consent and data ownership, particularly in
optimized treatment plans, particularly in complex domains such as
cardiovascular care and immune-mediated diseases. However, many
applications remain at the proof-of-concept stage, underscoring the need for
further research, data standardization, and validation efforts to transition from
experimentation to widespread clinical adoption.
DTs enhance health care operations by simulating patient flow, resource
allocation, and emergency scenarios, offering actionable insights to improve
efficiency. For instance, GE HealthCare?s Command Center demonstrates
how DTs can reduce bottlenecks, optimize staffing, and enhance patient
experiences [13]. However, adoption remains limited due to resistance to
change, significant computational demands, and challenges in integrating
DTs into existing workflows. Overcoming these barriers will require targeted
training and interdisciplinary collaboration to facilitate the operational
implementation of DTs.
DTs are transforming medical research by facilitating digital clinical trials and
predictive modeling of drug responses. These innovations can significantly
reduce the cost and ethical concerns associated with traditional trials while
improving trial efficiency and safety. For example, collaborations between
the context of data sharing and potential misuse Unlearn AI and Merck
are leveraging synthetic control groups
[2,4,8,14,16,17,19,20,24,29]. Furthermore, regulatory to accelerate drug
development [18]. However, broader
Página 15
Página 16
frameworks for DTs remain underdeveloped, creating uncertainties in legal
governance, intellectual property protection, and alignment with existing
health care regulations
implementation in this domain is contingent upon addressing critical
challenges, including ensuring data quality, achieving scalability, and
navigating regulatory approval processes.
Third, implementation and socioeconomic disparities address the challenges
of integrating DTs into clinical practice and the socioeconomic barriers to
widespread adoption. Health care professionals often express concerns
about trust, transparency, and the risk of job displacement, contributing to
resistance against DT implementation. Additionally, there is a pressing need
for enhanced education and training for both health care providers and
patients to bridge the knowledge gap between clinicians and data scientists
[4,14,16,17,23,30,32]. On a broader scale, the socioeconomic impacts of DTs
include the potential to deepen the digital divide, limit access to advanced
technologies, and enable financial barriers such as cost and reimbursement
issues, which hinder broader implementation
Technology in Health Care
Overview
While our findings highlight the significant promise of DTs in health care, they
also reveal that most current applications remain in their infancy, with many
still at the proof-of-concept or early implementation stage. These initial
deployments, though limited in scope, demonstrate promising results and lay
a solid foundation for future advancements. The potential applications of DTs
extend well beyond these early efforts, offering innovative solutions to
address some of health care?s most pressing challenges. However,
overcoming key barriers is essential to making DT technology more
accessible, trustworthy,
[1,18-20]. and practical for health care providers, thereby paving the way
Discussion
Principal Results
This review highlights the transformative potential of DT technology across 3
critical applications in health care: personalized medicine, operational
Página 16
Página 17
efficiency, and medical research and drug development. While these
advancements present significant opportunities, they also introduce
challenges that require attention to fully realize the benefits of DTs.
In personalized care, DTs leverage diverse data sources?such as clinical
records, genomic information, and real-time inputs from wearable devices?to
create patient-specific health simulations. These simulations serve as a
foundation for predictive modeling, enabling tailored interventions and
for wider adoption and meaningful impact.
First, challenges related to data and model integrity represent a significant
concern for DT technology in health care. Integrating large datasets from
wearables, EHRs, and imaging systems involves complexities in
standardization, quality control, and real-time synchronization [35]. Ensuring
model accuracy and minimizing artificial intelligence biases, as a key
technology supporting DTs, are critical to making DTs reliable for high-stakes
health care applications [36]. Addressing these issues requires standardized
frameworks and rigorous validation protocols. Legal frameworks such as the
European Union?s General Data Protection Regulation could serve as a
model for implementing robust data governance practices within DT
technology. To minimize artificial intelligence biases, validated practices
established in EHRs can be leveraged to enhance data
transparent validation processes, akin to clinical trials for medical devices,
would foster trust and ensure DT reliability in
implementation. Future research should prioritize refining and standardizing
DT definitions to foster alignment between
clinical settings. research and real-world needs, enabling trust among
Next, ethical, regulatory, and governance challenges present significant
concerns, particularly as DTs rely on sensitive health data. Issues such as
data privacy, ownership, and the potential for algorithmic bias must be
addressed to avoid undermining public trust and exacerbating disparities in
care [37]. Adapting regulatory frameworks from virtual reality and internet of
things devices could establish standards for data ownership, informed
Página 17
Página 18
consent, and transparency, thereby mitigating risks of unauthorized data use.
Furthermore, aligning these standards with international ethical guidelines
could enhance public confidence in DT technology. The establishment of
independent monitoring organizations?such as the European Medicines
Agency [38], or ICANN (Internet Corporation for Assigned Names and
Numbers) [39]?could provide consistent oversight and accountability. Such
organizations would play a critical role in ensuring the ethical and responsible
deployment of DTs across health care systems.
Finally, socioeconomic barriers to DT implementation raise concerns about
exacerbating existing disparities in health care [40]. The high costs of
advanced technologies create substantial obstacles for low- and
middle-income countries to access essential tools needed for health
innovation and economic modernization [41]. Moreover, the monopolization
of patents
stakeholders and paving the way for innovative, targeted health care
solutions.
Future research should prioritize the practical implementation of DTs through
detailed case studies and real-world applications, demonstrating their
feasibility and clinical impact. Transparency and explainability are equally
critical for building clinicians?trust in DT recommendations and ensuring they
can effectively interpret these insights. Addressing challenges related to
scalability and data standardization is essential for widespread adoption,
alongside rigorous validation through real-world clinical trials to establish the
accuracy, safety, and seamless integration of DT systems into health care
infrastructures.
Ethical considerations, including AI biases and patient privacy, require
innovative approaches to algorithm development and the refinement of data
ownership and informed consent models. Moreover, research into the
socioeconomic impacts of DTs and cost-effective implementation strategies
is vital to ensure accessibility for underserved populations. Special attention
should be given to low-resource settings, where barriers such as cost,
infrastructure, and training may hinder adoption. Collaboration between
private and governmental sectors can ensure DT technology benefits a
Página 18
Página 19
diverse range of patients and institutions, paving the way for equitable and
sustainable
debt repayment instead of strategic investments in health care infrastructure,
further perpetuating inequality and widening the digital divide. Lessons
learned from the implementation of EHRs and connected medical devices
show that cost-sharing models and collaborative funding initiatives can
promote more equitable access to DT technology [43]. Open-source tools
and public-private partnerships involving technology companies, health care
providers, and research institutions offer additional pathways to reduce costs
and enhance accessibility. Additionally, targeted training programs for health
care professionals can bridge the skills gap, facilitating the successful
adoption of DTs across diverse health care settings [44,45].
Future Directions for DT Technology in Health Care
Expanding DT technology in health care opens several important avenues for
future research. A key challenge is the lack of a universally accepted
definition, particularly in health care. While most studies define the term
consistently, some variability persists, reflecting broader inconsistencies in
the field. This lack of consensus complicates efforts to synthesize findings
and assess the maturity of DT applications. Recognized definitions, such as
those by the National Academies [46] and Drummond and Gonsard [47],
emphasize the dynamic, predictive, and decision-informing attributes that
distinguish DTs from other digital tools, which set them apart from other
digital tools.
This review has limitations that may affect the interpretation of its findings. As
a meta-review, our analysis is constrained by the scope and depth of the
included studies, which may not comprehensively capture all aspects of DT
applications and developments in health care. Furthermore, the rapid growth
of DT research in health care, particularly with significant contributions from
private industry, limits the visibility of current implementation efforts. Industrial
stakeholders often hesitate to publish detailed information about their
proprietary DT technologies and methodologies, a challenge also observed
during the COVID-19 pandemic [48]. This restricts access to real-world data,
reducing insights that could deepen our understanding of DT advancements.
Página 19
Página 20
Conclusions
Though still in their early-stage applications, DTs hold immense potential to
revolutionize health care through personalized medicine, operational
efficiency, and accelerated medical research. However, realizing this
potential requires addressing key challenges related to data integrity, ethical
concerns, and socioeconomic disparities. Strategic investments, supportive
policies, and collaborative research initiatives are crucial to ensuring
equitable development. With an inclusive approach, DTs can transition from a
visionary concept to a practical and transformative tool that enhances health
care outcomes for
Achieving definitional clarity is foundational for advancing diverse
populations.
practical applications, as inconsistent definitions risk
Acknowledgments
The authors would like to thank Jean Charbonneau, MLIS, librarian of the
Centre intégré universitaire de santé et de services sociaux du
Nord-de-l?Île-de-Montréal Documentary Service, who validated the initial
keywords and Medical Subject Headings terms of search queries and then
executed the search strategy in selected databases.
Authors' Contributions
MR conceptualized this study, prepared this study?s protocol, conducted the
coding, drafted the initial paper, and contributed to its review and editing.
FAES conceptualized this study, participated in coding, and reviewed and
edited this paper. GP conceptualized and supervised this study and
contributed to this paper?s review and editing. MC conceptualized this study
and reviewed and edited this paper. MR and FAES accessed and verified the
data. All authors had full access to this study?s data, including supplemental
material, and approved the final version of this paper for submission.
Conflicts of Interest
None declared.
Multimedia Appendix 1
Research queries.
[-]
Página 20
Página 21
Multimedia Appendix 2
PRISMA-ScR checklist.
[-]
References
1. Chu Y, Li S, Tang J, Wu H. The potential of the medical digital twin in
diabetes management: a review. Front Med (Lausanne). 2023;10:1178912. [
2. Katsoulakis E, Wang Q, Wu H, Shahriyari L, Fletcher R, Liu J, et al. Digital
twins for health: a scoping review. NPJ Digit Med. 2024;7(1):77. [
3. Moingeon P, Chenel M, Rousseau C, Voisin E, Guedj M. Virtual patients,
digital twins and causal disease models: paving the ground for in silico
clinical trials. Drug Discov Today. 2023;28(7):103605. [
4. Venkatesh KP, Brito G, Boulos MNK. Health digital twins in life science
and health care innovation. Annu Rev Pharmacol Toxicol.
2024;64(1):159-170. [ 5. Digital twins: the key to smart product development.
McKinsey & Company. URL:  [accessed 2025-02-04] 6. Research and
Markets. URL:
[accessed 2025-02-04]
7. MarketsandMarkets. URL:
[accessed 2025-02-04]
8. Elkefi S, Asan O. Digital twins for managing health care systems: rapid
literature review. J Med Internet Res.
2022;24(8):e37641. [
9. Tricco AC, Lillie E, Zarin W, O'Brien KK, Colquhoun H, Levac D, et al.
PRISMA Extension for Scoping Reviews (PRISMA-ScR): checklist and
explanation. Ann Intern Med. 2018;169(7):467-473. [
10. Sarrami-Foroushani P, Travaglia J, Debono D, Clay-Williams R,
Braithwaite J. Scoping meta-review: introducing a new methodology. Clin
Transl Sci. 2015;8(1):77-81. [ 11. van den Akker O, Peters G-J, Bakker C.
Generalized Systematic Review Registration Form. MetaArXiv. Preprint
posted online on September 22, 2023.
12. Paré G, Wagner G, Prester J. How to develop and frame impactful
review articles: key recommendations. J Decis Syst.
2023;33(4):566-582. [
Página 21
Página 22
13. Paré G, Kitsiou S. Handbook of eHealth evaluation: an evidence-based
approach [internet]. University of Victoria. URL:  [accessed 2025-02-04]
14. Armeni P, Polat I, De Rossi LM, Diaferia L, Meregalli S, Gatti A. Digital
twins in healthcare: is it the beginning of a new era of evidence-based
medicine? A critical review. J Pers Med. 2022;12(8):1255. [
fibrillation. Front Physiol. 2022;13:957604. [ 16. Benson M. Digital twins for
predictive, preventive personalized, and participatory treatment of
immune-mediated diseases.
ATVB. 2023;43(3):410-416. [
17. Coorey G, Figtree GA, Fletcher DF, Snelson VJ, Vernon ST, Winlaw D,
et al. The health digital twin to tackle cardiovascular disease-a review of an
emerging interdisciplinary field. NPJ Digit Med. 2022;5(1):126. [
18. Drummond D, Roukema J, Pijnenburg M. Home monitoring in asthma:
towards digital twins. Curr Opin Pulm Med.
2023;29(4):270-276. [
19. Dumas M, Fay AF, Charpentier E, Matricon J. [Digital twins in
healthcare: state of the art and potential use cases in a hospital setting]. Med
Sci (Paris). 2023;39(12):953-957. [
20. Boulos MNK, Zhang P. Digital twins: from personalised medicine to
precision public health. J Pers Med. 2021;11(8):745.
[
21. Khan A, Milne-Ives M, Meinert E, Iyawa GE, Jones RB, Josephraj AN. A
scoping review of digital twins in the context of the COVID-19 pandemic.
Biomed Eng Comput Biol. 2022;13:11795972221102115. [
22. Sun T, He X, Li Z. Digital twin in healthcare: recent updates and
challenges. Digit Health. 2023;9:20552076221149651.
[
23. Vallée A. Digital twin for healthcare systems. Front Digit Health.
2023;5:1253050. [
24. Voigt I, Inojosa H, Dillenseger A, Haase R, Akgün K, Ziemssen T. Digital
twins for multiple sclerosis. Front Immunol.
2021;12:669811. [
25. Tacchino A, Podda J, Bergamaschi V, Pedullà L, Brichetto G. Cognitive
Página 22
Página 23
rehabilitation in multiple sclerosis: three digital ingredients to address current
and future priorities. Front Hum Neurosci. 2023;17:1130231. [
26. Wu C, Lorenzo G, Hormuth DA, Lima EABF, Slavkova KP, DiCarlo JC,
et al. Integrating mechanism-based modeling with biomedical imaging to
build practical digital twins for clinical oncology. Biophys Rev (Melville).
2022;3(2):021304.
[
27. Meijer C, Uh HW, El Bouhaddani S. Digital twins in healthcare:
methodological challenges and opportunities. J Pers Med.
2023;13(10):1522. [
28. Laubenbacher R, Adler F, An G, Castiglione F, Eubank S, Fonseca LL,
et al. Toward mechanistic medical digital twins: some use cases in
immunology. Front Digit Health. 2024;6:1349595. [
29. Jia P, Liu S, Yang S. Innovations in public health surveillance for
emerging infections. Annu Rev Public Health.
2023;44(1):55-74. [ 30. Fischer R, Volpert A, Antonino P, Ahrens TD. Digital
patient twins for personalized therapeutics and pharmaceutical 
manufacturing. Front Digit Health. 2023;5:1302338. [
31. Cluitmans MJM, Plank G, Heijman J. Digital twins for cardiac
electrophysiology: state of the art and future challenges.
Herzschrittmacherther Elektrophysiol. 2024;35(2):118-123. [
32. Gazerani P. Intelligent digital twins for personalized migraine care. J
Pers Med. 2023;13(8):1255. [
33. Sigawi T, Ilan Y. Using constrained-disorder principle-based systems to
improve the performance of digital twins in biological systems. Biomimetics
(Basel). 2023;8(4):359. [
34. What is a digital twin? IBM. URL: [accessed 2025-02-04] 35. 
Martínez-García M, Hernández-Lemus E. Data integration challenges for
machine learning in precision medicine. Front Med (Lausanne).
2021;8:784455. [
36. Putrama IM, Martinek P. Heterogeneous data integration: challenges and
opportunities. Data Brief. 2024;56:110853. [
37. Alhammad N, Alajlani M, Abd-Alrazaq A, Epiphaniou G, Arvanitis T.
Página 23
Página 24
Patients' perspectives on the data confidentiality, privacy, and security of
mHealth apps: systematic review. J Med Internet Res. 2024;26:e50715. [
38. What we do. European Medicines Agency. URL: [accessed 2025-02-04]
39.
ICANN for Beginners. Internet Corporation for Assigned Names and
Numbers. URL: [accessed 2025-02-04]
(LMIC) in the research literature: ethical issues arising from a survey of five
leading medical journals: have the trends changed? Glob Public Health.
2023;18(1):2229890. [
41. Dinh MN, Nygate J, Tu VHM, Thwaites CL, Global Grand Challenges
Event Vietnam Group. New technologies to improve healthcare in low- and
middle-income countries: Global Grand Challenges satellite event, Oxford
University Clinical Research Unit, Ho Chi Minh City, 17th-18th September
2019. Wellcome Open Res. 2020;5:142. [
42. Sachs JD, Karim SSA, Aknin L, Allen J, Brosbøl K, Colombo F, et al. The
Lancet commission on lessons for the future from the COVID-19 pandemic.
Lancet. 2022;400(10359):1224-1280. [ 43. Tsai CH, Eghdam A, Davoody N,
Wright G, Flowerday S, Koch S. Effects of electronic health record
implementation and barriers to adoption and use: a scoping review and
qualitative analysis of the content. Life (Basel). 2020;10(12):327. [
44.
Franzen SRP, Chandler C, Lang T. Health research capacity development in
low and middle income countries: reality or rhetoric? A systematic
meta-narrative review of the qualitative literature. BMJ Open.
2017;7(1):e012332. [
45. Shumba CS, Lusambili AM. Not enough traction: barriers that aspiring
researchers from low- and middle-income countries face in global health
research. Journal of Global Health Economics and Policy. 2021;1:e2021002.
[ 46. Foundational Research Gaps and Future Directions for Digital Twins.
National Academies. Washington DC. National Academies Press; 2024.
URL: [accessed 2025-02-04] 47. Drummond D, Gonsard A. Definitions and
characteristics of patient digital twins being developed for clinical use:
scoping review. J Med Internet Res. 2024;26:e58504. [
Página 24
Página 25
48. Wouters OJ, Shadlen KC, Salcher-Konrad M, Pollard AJ, Larson HJ,
Teerawattananon Y, et al. Challenges in ensuring global access to
COVID-19 vaccines: production, affordability, allocation, and deployment.
Lancet.
2021;397(10278):1023-1034. [
Abbreviations
DT: digital twin
EHR: electronic health record
ICANN: Internet Corporation for Assigned Names and Numbers
PRISMA-ScR: Preferred Reporting Items for Systematic Reviews and
Meta-Analyses extension for Scoping Reviews
©Mickaël Ringeval, Faustin Armel Etindele Sosso, Martin Cousineau, Guy
Paré. Originally published in the Journal of Medical Internet Research (
19.02.2025. This is an open-access article distributed under the terms of the
Creative Commons Attribution License ( which permits unrestricted use,
distribution, and reproduction in any medium, provided the original work, first
published in the Journal of Medical Internet Research (ISSN 1438-8871), is
properly cited. The complete bibliographic information, a link to the original
publication on as well as this copyright and license information must be
included.
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
Reviews and Meta-Analyses extension for Scoping Reviews)
Reviews and Meta-Analyses extension for Scoping Reviews)
Reviews and Meta-Analyses extension for Scoping Reviews)
Reviews and Meta-Analyses extension for Scoping Reviews)
Reviews and Meta-Analyses extension for Scoping Reviews)
Reviews and Meta-Analyses extension for Scoping Reviews)
Página 25
Página 26
Data Extraction
guidelines
to
ensure
comprehensive
reporting
and
Data Extraction
generated in DT research, necessitating both a broad mapping
results.
results.
results.
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Data Analysis
Ringeval et al
through discussion, ensuring a consistent and accurate
reviews [2,8,19-23,25,29,30,32,33]. Similarly, patients in
and
health
care
professionals,
including
clinicians
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
improves
communication
and
Página 26
Página 27
decision-making
across
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
Problem (and root causes)
Problem (and root causes)
Inputs
Inputs
Inputs
Processes
Processes
Outputs
Outputs
?
Variability in patient
?
Data:
Data:
?
Simulation: the DT can simu
?
Real-time monitoring and
physiology
physiology
?
?
Clinical data
late a patient?s disease pro
late a patient?s disease pro
prognosis
prognosis
Página 27
Página 28
?
Delayed detection
?
?
Genomic data
gression, the impact of treat
gression, the impact of treat
?
Improved diagnosis
?
Limited predictive capa
?
?
Imaging data
ment options, and various
ment options, and various
?
Tailored health interven
bility for disease progres
bility for disease progres
?
?
Biomarkers
clinical scenarios, such as a
clinical scenarios, such as a
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Lifestyle data
Página 28
sudden deterioration in condi
Página 29
sudden deterioration in condi
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Demographic data
tion or the patient?s response
tion or the patient?s response
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Demographic data
to a new medication. It can
to a new medication. It can
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
Sources:
Sources:
to a new medication. It can
to a new medication. It can
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
Página 29
Página 30
Sources:
Sources:
also model the effects of dai
also model the effects of dai
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Electronic health record systems
also model the effects of dai
also model the effects of dai
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Electronic health record systems
ly changes in lifestyle, nutri
ly changes in lifestyle, nutri
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Disease registries
ly changes in lifestyle, nutri
ly changes in lifestyle, nutri
tions and lifestyle guidance
tions and lifestyle guidance
Página 30
Página 31
sion
sion
?
?
Disease registries
tion, and medication adher
tion, and medication adher
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Laboratory reports
tion, and medication adher
tion, and medication adher
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Laboratory reports
ence
ence
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Wearable devices
ence
Página 31
Página 32
ence
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Wearable devices
?
Optimization: based on simu
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Surveys and questionnaires
?
Optimization: based on simu
tions and lifestyle guidance
tions and lifestyle guidance
sion
sion
?
?
Surveys and questionnaires
lation results, the DT can op
lation results, the DT can op
tions and lifestyle guidance
tions and lifestyle guidance
data,
biomarkers,
and
Página 32
Página 33
lifestyle
and
demographic
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
Problem (and root causes)
Problem (and root causes)
Inputs
Inputs
Inputs
Processes
Processes
Outputs
Outputs
?
Unpredictable patient vol
?
Data:
Data:
?
Simulation: the DT can simu
?
Optimized patient flow and
umes
umes
?
?
Patient data
late hospital scenarios. By
late hospital scenarios. By
resource
Página 33
Página 34
resource
?
Difficulty in dynamically
?
?
Historical trends
modeling these patterns, DTs
modeling these patterns, DTs
?
Real-time adjustments in
adapting workflows in high
adapting workflows in high
?
?
Historical trends
can analyze how variations
can analyze how variations
staffing and equipment us
staffing and equipment us
adapting workflows in high
adapting workflows in high
?
Sources:
Sources:
can analyze how variations
can analyze how variations
staffing and equipment us
staffing and equipment us
stakes situations
stakes situations
?
Sources:
Sources:
Página 34
Página 35
in patient flow affect wait
in patient flow affect wait
age based on patient arrivals
age based on patient arrivals
stakes situations
stakes situations
?
?
Hospital information systems
in patient flow affect wait
in patient flow affect wait
age based on patient arrivals
age based on patient arrivals
?
Limited real-time operational
?
?
Hospital information systems
times, bed availability,
times, bed availability,
?
Improved discharge plan
insights that lead to inefficien
insights that lead to inefficien
?
?
Hospital information systems
staffing requirements, and
staffing requirements, and
ning and maintenance
ning and maintenance
cies and bottlenecks
cies and bottlenecks
Página 35
Página 36
?
?
Hospital information systems
equipment usage, giving ad
equipment usage, giving ad
scheduling to ensure opti
scheduling to ensure opti
cies and bottlenecks
cies and bottlenecks
?
?
Hospital information systems
ministrators foresight into
ministrators foresight into
mal bed availability and pa
mal bed availability and pa
cies and bottlenecks
cies and bottlenecks
?
?
Hospital information systems
potential bottlenecks
potential bottlenecks
tient throughput
tient throughput
cies and bottlenecks
cies and bottlenecks
?
?
Hospital information systems
?
Optimization: based on simu
?
Página 36
Página 37
Efficient crisis management
cies and bottlenecks
cies and bottlenecks
?
?
Hospital information systems
lation results, the DT can
lation results, the DT can
strategies
strategies
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
Problem (and root causes)
Problem (and root causes)
Inputs
Inputs
Inputs
Processes
Processes
Outputs
Outputs
?
High costs and time demand
?
Data:
Data:
?
Simulation: the DTs are
?
Synthetic control groups
of physical trials
Página 37
Página 38
of physical trials
?
?
Clinical data
used to simulate in silico
used to simulate in silico
to minimize physical tri
to minimize physical tri
?
Ethical challenges in testing
?
?
Patient data
clinical trials, allowing re
clinical trials, allowing re
als and enhance safety
als and enhance safety
on human participants, espe
on human participants, espe
?
?
Genomic data
searchers to predict drug
searchers to predict drug
?
Predictive modeling of
cially in vulnerable popula
cially in vulnerable popula
?
?
Imaging data
efficacy and safety across
efficacy and safety across
Página 38
Página 39
drug responses and ad
drug responses and ad
tions
tions
?
?
Physiological data
diverse patient profiles
diverse patient profiles
verse reactions, allowing
verse reactions, allowing
?
Limited ability to predict
?
?
Physiological data
without the need for large
without the need for large
for more accurate and
for more accurate and
?
Limited ability to predict
?
Sources:
Sources:
without the need for large
without the need for large
for more accurate and
for more accurate and
individualized responses in
individualized responses in
?
Página 39
Sources:
Página 40
Sources:
scale physical trials
scale physical trials
efficient trials
efficient trials
individualized responses in
individualized responses in
?
?
Electronic health records
scale physical trials
scale physical trials
efficient trials
efficient trials
diverse patient populations
diverse patient populations
?
?
Electronic health records
?
Optimization: with data
?
Simulations for drug effi
diverse patient populations
diverse patient populations
?
?
Wearable and remote monitoring de
?
Optimization: with data
?
Simulations for drug effi
diverse patient populations
Página 40
Página 41
diverse patient populations
?
?
Wearable and remote monitoring de
from DTs, researchers can
from DTs, researchers can
cacy testing, reducing
cacy testing, reducing
diverse patient populations
diverse patient populations
vices
vices
vices
from DTs, researchers can
from DTs, researchers can
cacy testing, reducing
cacy testing, reducing
diverse patient populations
diverse patient populations
vices
vices
vices
optimize trial parameters by
optimize trial parameters by
the need for early-stage
the need for early-stage
diverse patient populations
diverse patient populations
?
?
Health databases
optimize trial parameters by
optimize trial parameters by
Página 41
Página 42
the need for early-stage
the need for early-stage
diverse patient populations
diverse patient populations
?
?
Health databases
adjusting dosages and select
adjusting dosages and select
in-person trials
in-person trials
diverse patient populations
diverse patient populations
?
?
Pharmaceutical and clinical trial data
adjusting dosages and select
adjusting dosages and select
in-person trials
in-person trials
diverse patient populations
diverse patient populations
?
?
Pharmaceutical and clinical trial data
ing ideal patient cohorts.
ing ideal patient cohorts.
?
Virtualized, patient-spe
diverse patient populations
diverse patient populations
?
?
Página 42
Página 43
Pharmaceutical and clinical trial data
This approach refines drug
This approach refines drug
cific trials that allow re
cific trials that allow re
diverse patient populations
diverse patient populations
?
?
Pharmaceutical and clinical trial data
formulations and identifies
formulations and identifies
searchers to adjust
searchers to adjust
diverse patient populations
diverse patient populations
?
?
Pharmaceutical and clinical trial data
optimal therapeutic proto
optimal therapeutic proto
dosages and predict pa
dosages and predict pa
diverse patient populations
diverse patient populations
?
?
Pharmaceutical and clinical trial data
cols, reducing unnecessary
cols, reducing unnecessary
tient outcomes
tient outcomes
success
Página 43
Página 44
[2,3,14,17,19].
The
outputs
of
these
conditions [1-3,14,17,19-21,27-30,32], and intensive care unit
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
[4,8,17-20,24].
Challenges and Opportunities in Advancing DT
XSL?FO
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
undermining
coherence
in
design,
Ringeval et al
Ringeval et al
quality and ensure patient information integrity. Further,
undermining
coherence
in
design,
validation,
and
and restrictive trade agreements by Western countries limits these
nations?ability to develop local solutions [42]. Dependency on international
loans often shifts focus toward
adoption.
Limitations
Página 44
Página 45
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
15.
Bai J, Lu Y, Wang H, Zhao J. How synergy between mechanistic and
statistical models is impacting research in atrial
Bai J, Lu Y, Wang H, Zhao J. How synergy between mechanistic and
statistical models is impacting research in atrial
(page number not for citation purposes)
JOURNAL OF MEDICAL INTERNET RESEARCH
JOURNAL OF MEDICAL INTERNET RESEARCH
Ringeval et al
40.
Woods WA, Watson M, Ranaweera S, Tajuria G, Sumathipala A.
Under-representation of low and middle income countries
Woods WA, Watson M, Ranaweera S, Tajuria G, Sumathipala A.
Under-representation of low and middle income countries
Edited by T de Azevedo Cardoso; submitted 02.12.24; peer-reviewed by D
Drummond, D Madell; comments to author 10.12.24; revised version
received 20.01.25; accepted 24.01.25; published 19.02.25
Please cite as:
Ringeval M, Etindele Sosso FA, Cousineau M, Paré G
Advancing Health Care With Digital Twins: Meta-Review of Applications and
Implementation Challenges J Med Internet Res 2025;27:e69544
URL:
(page number not for citation purposes)
Página 45