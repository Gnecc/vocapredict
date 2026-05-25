import { IonButton, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle, IonCol, IonGrid, IonNote, IonRow, useIonRouter } from "@ionic/react";
import styles from "../pages/Quiz.module.scss";
import { updateChosenCategory, updateChosenDifficulty } from "../store/SettingsStore";

export const CompletedCard = ({ completionContainerRef, score, questionsLength }) => {

    const router = useIonRouter();

    const playAgain = () => {

        updateChosenCategory(false);
        updateChosenDifficulty(false);
        router.push("/");
    }

    return (
        <IonGrid className="animate__animated" ref={ completionContainerRef }>
            <IonRow className="ion-text-center">
                <IonCol size="12">
                    <IonCard>
                        <IonCardHeader>
{/*
                            <IonCardSubtitle>Congratulations</IonCardSubtitle>
*/}
                            <IonCardTitle>Cuestionario completado</IonCardTitle>
                            <p className={ styles.emoji }>🎉</p>
                        </IonCardHeader>

                        <IonCardContent>
                            {/*<IonNote>You scored</IonNote>

                            <IonCardTitle className="ion-margin-bottom">
                                { score }/{ questionsLength }
                            </IonCardTitle>*/}

                            <IonButton expand="block" onClick={() => router.push("/results")}>
                                Ver Resultados
                            </IonButton>
                        </IonCardContent>
                    </IonCard>
                </IonCol>
            </IonRow>
        </IonGrid>
    );
}