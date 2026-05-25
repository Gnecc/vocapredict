import { IonButton, IonCol, IonContent, IonGrid, IonHeader, IonIcon, IonPage, IonRow, IonTitle, IonToolbar, useIonActionSheet } from '@ionic/react';
import styles from "./Home.module.scss";

import { informationCircleOutline } from "ionicons/icons";

const Home = () => {

	const [ show, hide ] = useIonActionSheet();

	return (
		<IonPage>
			<IonContent fullscreen>
				<IonGrid>
					<IonRow>
						<IonCol size="12" className="ion-text-center">
							<img src="/assets/logo.png" alt="title" className={styles.title}/>
						</IonCol>
					</IonRow>
				</IonGrid>

				<div className="sponsor-strip">
					<a
						className="logo"
						rel="noreferrer"
						aria-label="CONAHCYT"
					>
						<img src="/assets/logos/LOGO_CONACYT.png" alt="CONAHCYT"/>
					</a>

					<span className="sep" aria-hidden="true"/>

					<a
						className="logo"
						rel="noreferrer"
						aria-label="Maestría en Ciencias de la Computación UAEMéx"
					>
						<img src="/assets/logos/LOGO_MACSCO.png" alt="Maestría en Ciencias de la Computación UAEMéx"/>
					</a>
				</div>

				<IonRow className={styles.buttons}>
					<IonCol size="12">
						<IonButton routerLink="/quiz" color="light" expand="block"
								   className={styles.playButton}>Comenzar</IonButton>

						<IonButton color="dark" className={styles.helpButton} onClick={() => show({
							buttons: [{text: 'Cerrar'}],
							header: 'Términos y condiciones',
							subHeader: 'El uso de esta aplicación constituye la aceptación de los presentes términos y condiciones. La aplicación se ofrece con fines informativos y educativos, sin garantías de ningún tipo sobre la exactitud o disponibilidad de su contenido. El usuario es responsable del uso que realice y se compromete a hacerlo conforme a la ley. La aplicación no se hace responsable por daños o perjuicios que puedan derivarse de su utilización. Nos reservamos el derecho de modificar o actualizar estos términos en cualquier momento sin previo aviso.'
						})}>
							<IonIcon icon={informationCircleOutline}/> Términos y condiciones
						</IonButton>
					</IonCol>
				</IonRow>
			</IonContent>
		</IonPage>
	);
};

export default Home;
