import { IonButton, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCol, IonContent, IonGrid, IonHeader, IonIcon, IonPage, IonRow, IonTitle, IonToolbar, useIonRouter, useIonToast } from '@ionic/react';

import styles from "./Quiz.module.scss";
import { useStoreState } from 'pullstate';
import { SettingsStore } from '../store';
import { getCategories, getChosenCategory, getChosenDifficulty, getDifficulties } from '../store/Selectors';
import { Category, Difficulty } from '../components/Settings';
import { updateChosenCategory, updateChosenDifficulty} from "../store/SettingsStore";

const Quiz = () => {

    const router = useIonRouter();
    const categories = useStoreState(SettingsStore, getCategories);
    const difficulties = useStoreState(SettingsStore, getDifficulties);

    const chosenCategory = useStoreState(SettingsStore, getChosenCategory);
    const chosenDifficulty = useStoreState(SettingsStore, getChosenDifficulty);

    const [ show, hide ] = useIonToast();

    const startQuiz = async () => {
        console.log('start', chosenCategory, chosenDifficulty)
        if (chosenCategory && chosenDifficulty) {
            console.log('enter');
            router.push("/questions");
            return;
            const chosenCategoryElement = document.getElementById(`categoryButton_${ chosenCategory }`);
            const chosenDifficultyElement = document.getElementById(`difficultyButton_${ chosenDifficulty }`);

            const categoriesCardElement = document.getElementById("categoriesCard");
            const difficultiesCardElement = document.getElementById("difficultiesCard");

            chosenCategoryElement.classList.add("ontop");
            chosenDifficultyElement.classList.add("ontop");

            chosenCategoryElement.classList.add("animate__heartBeat");
            chosenDifficultyElement.classList.add("animate__heartBeat");

            setTimeout(() => {
                
                chosenCategoryElement.classList.remove("animate__heartBeat");
                chosenDifficultyElement.classList.remove("animate__heartBeat");
                chosenCategoryElement.classList.remove("ontop");
                chosenDifficultyElement.classList.remove("ontop");
            }, 1000);

            setTimeout(() => {
                
                categoriesCardElement.classList.add("animate__slideOutRight");
                difficultiesCardElement.classList.add("animate__slideOutLeft");

                setTimeout(() => {
                    
                    categoriesCardElement.classList.remove("animate__slideOutRight");
                    difficultiesCardElement.classList.remove("animate__slideOutLeft");
                }, 1000);
            }, 1100);

            setTimeout(() => {
                
                router.push("/questions");
            }, 1700);
        } else {

            show({
                header: "Hang on there!",
                message: "You must choose a category and difficulty!",
                duration: 3000,
                color: "warning"
            })
        }
    }

	return (
		<IonPage>
			<IonHeader>
				<IonToolbar>
                    <IonTitle>
                        <img src="/assets/logo.png" style={{ width: "50%" }} alt="logo" />
                    </IonTitle>
				</IonToolbar>
			</IonHeader>
			<IonContent fullscreen className="background">
                <IonGrid className={ styles.mainGrid }>
                    <IonRow className={ styles.mainRow }>
                        <IonCol size="12">
                            <IonCard id="categoriesCard" className="animate__animated">
                                {/*<IonCardHeader className="ion-text-center">
                                    <IonCardSubtitle>Choose a category</IonCardSubtitle>
                                </IonCardHeader>*/}

                                {/*<IonCardContent>
                                    <IonRow>
                                        { categories.map((category, index) => {

                                            const chosen = category.value === chosenCategory;
                                            updateChosenCategory('code');
                                            updateChosenDifficulty('easy');

                                            return <Category key={ `category_${ index }` } { ...category } chosen={ chosen } />;
                                        })}
                                    </IonRow>
                                </IonCardContent>*/}
                                <IonCardContent>
                                    <IonRow>
                                        { categories.map((category, index) => {

                                            const chosen = category.value === chosenCategory;
                                            updateChosenCategory('code');
                                            updateChosenDifficulty('easy');
                                        })}
                                        <IonCol>
                                            <h2 style={{ fontWeight: "bold", marginBottom: "12px" }}>INSTRUCCIONES</h2>
                                            <p>
                                                Esta no es una prueba, sino solamente una medida de tu interés en algunos
                                                campos profesionales. No hay respuestas correctas, lo único importante es
                                                tu franca opinión.
                                            </p>
                                            <p>
                                                A continuación encontrarás una serie de actividades o cosas por hacer, las
                                                cuales están enumeradas. Por favor indica a cada actividad si te gusta o
                                                desagrada. Usa las escalas siguientes:
                                            </p>

                                            <ul style={{ listStyleType: "none", paddingLeft: 0, lineHeight: "1.8" }}>
                                                <li>1. – Me desagrada mucho</li>
                                                <li>2. – No me gusta</li>
                                                <li>3. – Me es indiferente</li>
                                                <li>4. – Me gusta</li>
                                                <li>5. – Me gusta mucho</li>
                                            </ul>
                                        </IonCol>
                                    </IonRow>
                                </IonCardContent>
                            </IonCard>
                        </IonCol>
                    </IonRow>

                    {/*<IonRow className={ styles.difficultyContainer }>
                        <IonCol size="12">
                            <IonCard id="difficultiesCard" className="animate__animated">
                                <IonCardHeader className="ion-text-center">
                                    <IonCardSubtitle>Choose a difficulty</IonCardSubtitle>
                                </IonCardHeader>

                                <IonCardContent>
                                    <IonRow>
                                        { difficulties.map((difficulty, index) => {

                                            const chosen = difficulty.value === chosenDifficulty;

                                            return <Difficulty key={ `difficulty_${ index }` } { ...difficulty } chosen={ chosen } />;
                                        })}
                                    </IonRow>
                                </IonCardContent>
                            </IonCard>
                        </IonCol>
                    </IonRow>*/}

                    <IonRow>
                        <IonCol size="12">
                            <div className={ styles.startButton } onClick={ startQuiz }>
                                Iniciar cuestionario
                            </div>
                        </IonCol>
                    </IonRow>
                </IonGrid>
			</IonContent>
		</IonPage>
	);
};

export default Quiz;