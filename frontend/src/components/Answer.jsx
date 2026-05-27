import { IonButton, IonCol, IonRow } from "@ionic/react";
import styles from "../pages/Quiz.module.scss";

export const Answer = ({ answer, handleAnswerClick, question, disabled = false, selected = false }) => (

    <IonRow>
        <IonCol size="12">
            <IonButton
                onClick={e => handleAnswerClick(e, answer, question)}
                disabled={disabled}
                expand="block"
                color="light"
                className={`ion-text-wrap ${styles.answerButton} ${selected ? styles.answerButtonSelected : ""}`}
            >
                {question.answers[answer]}
            </IonButton>
        </IonCol>
    </IonRow>
)
