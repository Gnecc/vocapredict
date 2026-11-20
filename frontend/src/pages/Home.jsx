import { IonButton, IonCard, IonCardContent, IonCol, IonContent, IonGrid, IonIcon, IonPage, IonRow, useIonActionSheet, useIonRouter } from '@ionic/react';
import styles from "./Home.module.scss";

import { informationCircleOutline, playOutline } from "ionicons/icons";
import { clearResponses, loadResponses } from "../storage";
import { RIASEC_QUESTIONS } from "../questions/riasec";

const Home = () => {

	const [ show ] = useIonActionSheet();
	const router = useIonRouter();

	const startQuestionnaire = () => {
		const responses = loadResponses();
		const shouldResume = responses.length > 0 && responses.length < RIASEC_QUESTIONS.length;

		if (!shouldResume) {
			clearResponses();
		}

		localStorage.removeItem("last_prediction_riasec_v1");
		router.push(`/questions?session=${Date.now()}${shouldResume ? "&resume=1" : ""}`, "forward", "push");
	};

	return (
		<IonPage>
			<IonContent fullscreen>
				<IonGrid className={styles.homeGrid}>
					<IonRow className={styles.logoRow}>
						<IonCol size="12" className="ion-text-center">
							<img src="/assets/logo-home.png" alt="VocaPredict" className={styles.title}/>
						</IonCol>
					</IonRow>

					<IonRow>
						<IonCol size="12">
						<IonCard className={styles.instructions}>
							<IonCardContent>
								<p className={styles.eyebrow}>VocaPredict</p>
								<h1>Cuestionario de intereses RIASEC</h1>
								<p>
									Califica qué tanto te gustaría realizar cada una de las 48 actividades.
									Al finalizar verás tres carreras sugeridas a partir de tus intereses.
								</p>
								<p className={styles.responseHint}>
									Lee cada enunciado con calma y elige la opción que mejor represente qué tanto
									te gustaría realizar la actividad.
								</p>
								<ul>
									<li>1. Me desagrada mucho</li>
									<li>2. No me gusta</li>
									<li>3. Me es indiferente</li>
									<li>4. Me gusta</li>
									<li>5. Me gusta mucho</li>
								</ul>
							</IonCardContent>
						</IonCard>

						<div className={styles.sponsorStrip} aria-label="Instituciones participantes">
							<img src="/assets/logos/LOGO_DOCCOM.svg" alt="Doctorado en Ciencias de la Computacion"/>
							<span aria-hidden="true"/>
							<img src="/assets/logos/LOGO_UAEMEX.png" alt="Universidad Autonoma del Estado de Mexico"/>
						</div>

						<div className={styles.actions}>
						<IonButton onClick={startQuestionnaire} color="primary" expand="block" className={styles.playButton}>
							<IonIcon icon={playOutline} />
							Comenzar cuestionario
						</IonButton>

						<IonButton color="dark" className={styles.helpButton} onClick={() => show({
							buttons: [{text: 'Cerrar'}],
							header: 'Términos y condiciones',
							subHeader: 'El uso de esta aplicación constituye la aceptación de los presentes términos y condiciones. La aplicación se ofrece con fines informativos y educativos, sin garantías de ningún tipo sobre la exactitud o disponibilidad de su contenido. El usuario es responsable del uso que realice y se compromete a hacerlo conforme a la ley. La aplicación no se hace responsable por daños o perjuicios que puedan derivarse de su utilización. Nos reservamos el derecho de modificar o actualizar estos términos en cualquier momento sin previo aviso.'
						})}>
							<IonIcon icon={informationCircleOutline}/> Términos y condiciones
						</IonButton>
						</div>
					</IonCol>
				</IonRow>
				</IonGrid>
			</IonContent>
		</IonPage>
	);
};

export default Home;
