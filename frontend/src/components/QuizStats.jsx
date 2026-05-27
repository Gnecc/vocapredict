import { IonCard, IonCardContent, IonCardSubtitle, IonCol, IonLabel, IonNote, IonRow } from "@ionic/react";

export const QuizStats = ({ currentQuestion, questionsLength }) => (

    <IonRow>
        <IonCol size="12">
            <IonCard>
                <IonCardContent className="ion-text-center">
                    <IonLabel className="ion-text-center">
                        <IonCardSubtitle>Preguntas</IonCardSubtitle>
                        <IonNote>{ currentQuestion } / { questionsLength }</IonNote>
                    </IonLabel>
                </IonCardContent>
            </IonCard>
        </IonCol>
    </IonRow>
);
