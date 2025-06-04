import asyncio
import pandas as pd
import nltk
import os
import time
import xgboost
import re
import matplotlib.pyplot as plt
import io
import numpy as np
import urllib, base64
from google import genai
from textblob import TextBlob
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, roc_curve, auc, accuracy_score, precision_score, log_loss, recall_score, f1_score
from sklearn.manifold import TSNE
from sklearn.neighbors import KNeighborsClassifier
from typing import List
from django.conf import settings
from .models import Model


class ModelManager:
    @staticmethod
    def remove_stopwords(text):
        english_stopwords = set(stopwords.words('english'))
        words = text.split()
        filtered = [word for word in words if word.lower() not in english_stopwords]
        return " ".join(filtered)

    def prepare_data(self):
        nltk.download('stopwords')
        df = pd.read_csv(settings.DATASET_PATH / "news.csv")
        df["text"] = df["text"].fillna('').astype(str)
        news = df[["text", "label"]]
        news["text"] = news["text"].str.lower()
        re_expression = r"[.,!?;:\"'“”‘’—–\-–…(){}\[\]«»<>%№@#&*/\\|^~=+]"
        news["text"] = news["text"].str.replace(re_expression, '', regex=True)
        news["text"] = news["text"].apply(self.remove_stopwords)

        return news

    @staticmethod
    async def calc_embeddings_features(news: pd.DataFrame, features):
        client = genai.Client(api_key=os.environ["API_KEY"])
        embeddings_features = []
        subarray_size = 100
        for i in range(0, (news.shape[0] - subarray_size + 1), subarray_size):
            success = False
            retry_delay = 60
            sub_texts = news['text'].iloc[i:i + subarray_size].tolist()
            while not success:
                try:
                    response = await client.aio.models.embed_content(
                        model='text-embedding-004',
                        contents=sub_texts,
                        config=genai.types.EmbedContentConfig(task_type="CLASSIFICATION")
                    )
                    for idx, vector in enumerate(response.embeddings):
                        values = vector.values
                        text = sub_texts[idx]
                        if "сентимент" in features:
                            values.append(TextBlob(text).sentiment.polarity)
                        if "суб'єктивність" in features:
                            values.append(TextBlob(text).sentiment.subjectivity)
                        embeddings_features.append(values)
                    print(i)
                    success = True

                except Exception as e:
                    error_message = str(e).lower()
                    if "quota" in error_message or "rate limit" in error_message:
                        print(f"Quota exceeded at index {i}. Waiting {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"Non-quota error at index {i}: {e}")
                        embeddings_features.append(None)
                        success = True
        return embeddings_features, news["label"]

    @staticmethod
    def create_train_sets(X, y, test_size):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
        return X_train, X_test, y_train, y_test
    
    async def create_model(self, name, news, features, params):
        embeddings_features, labels = await self.calc_embeddings_features(news, features)
        X = pd.DataFrame(embeddings_features)
        y = labels.reset_index(drop=True)

        X_train, X_test, y_train, y_test = self.create_train_sets(X, y, 0.25)

        train_matrix = xgboost.DMatrix(X_train, y_train)
        test_matrix = xgboost.DMatrix(X_test, y_test)

        if "n_estimators" in params:
            n_estimators = params["n_estimators"]
            del params["n_estimators"]
            model_xgb = xgboost.train(params, 
            train_matrix, evals=[(train_matrix, "train"), (test_matrix, "validation")], 
            num_boost_round=n_estimators, early_stopping_rounds=20)
        else:
            model_xgb = xgboost.train(params, 
            train_matrix, evals=[(train_matrix, "train"), (test_matrix, "validation")], 
            num_boost_round=100, early_stopping_rounds=20)
        model_xgb.save_model(settings.DETECTION_MODELS_PATH / f"{name}.json")

    def detect_fake(self, text: str, model: Model):
        nltk.download('stopwords')
        text = text.lower()
        re_expression = r"[.,!?;:\"'“”‘’—–\-–…(){}\[\]«»<>%№@#&*/\\|^~=+]"
        text = re.sub(re_expression, '', text)
        text = self.remove_stopwords(text)

        client = genai.Client(api_key=os.environ["API_KEY"])
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=text,
            config=genai.types.EmbedContentConfig(task_type="CLASSIFICATION")
        )
        embeddings_features = response.embeddings[0].values
        if model.featureinmodel_set.filter(feature__name="сентимент").exists():
            embeddings_features.append(TextBlob(text).sentiment.polarity)
        if model.featureinmodel_set.filter(feature__name="суб'єктивність").exists():
            embeddings_features.append(TextBlob(text).sentiment.subjectivity)
        
        df_input = pd.DataFrame([embeddings_features])
        matrix = xgboost.DMatrix(df_input)
        model_xgb = xgboost.Booster()
        model_xgb.load_model(settings.DETECTION_MODELS_PATH / f"{model.name}.json")
        result = model_xgb.predict(matrix)

        return result
    
    def prepare_performance_data(self, news: pd.DataFrame, model_id: int):
        model = Model.objects.get(pk=model_id)
        features_in_model = model.featureinmodel_set.all()
        features_names = []
        for feature_in_model in features_in_model:
            features_names.append(feature_in_model.feature.name)

        model_xgb = xgboost.Booster()
        model_xgb.load_model(settings.DETECTION_MODELS_PATH / f"{model.name}.json")
        
        embeddings_features, y_true = asyncio.run(self.calc_embeddings_features(news, features_names))
        y_pred_xgb = []
        for vector in embeddings_features:
            df = pd.DataFrame([vector])
            matrix = xgboost.DMatrix(df)
            y_pred_xgb.append(model_xgb.predict(matrix))
        y_pred_xgb_binary = [1 if p >= 0.5 else 0 for p in y_pred_xgb]

        precision, recall, thresholds = precision_recall_curve(y_true, y_pred_xgb)
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'Запропонований метод (AUC = {auc(recall, precision):.2f})', color='green')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall')
        plt.legend()
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        precision_recall = base64.b64encode(image_png)
        precision_recall = precision_recall.decode('utf-8')

        fpr, tpr, _ = roc_curve(y_true, y_pred_xgb)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'Запропонований метод (AUC = {auc(fpr, tpr):.2f})', color='green')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        roc_auc = base64.b64encode(image_png)
        roc_auc = roc_auc.decode('utf-8')

        tsne = TSNE(n_components=2)
        embeddings_features_reduced = tsne.fit_transform(np.array(embeddings_features))
        colors = ['blue', 'orange']
        labels = ['Правда', 'Фейк']
        plt.figure(figsize=(8, 6))
        for class_index in [0, 1]:
            mask = np.array(y_true) == class_index
            plt.scatter(
                embeddings_features_reduced[mask, 0],
                embeddings_features_reduced[mask, 1],
                c=colors[class_index],
                label=labels[class_index],
                alpha=0.7
            )
        plt.title("t-SNE Embeddings")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.legend(title="Клас")
        plt.grid(True)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        t_sne_plot = base64.b64encode(image_png)
        t_sne_plot = t_sne_plot.decode('utf-8')

        accuracy = round(accuracy_score(y_true, y_pred_xgb_binary),2)
        precision = round(precision_score(y_true, y_pred_xgb_binary),2)
        loss = round(log_loss(y_true, y_pred_xgb),2)
        recall = round(recall_score(y_true, y_pred_xgb_binary), 2)
        f1 = round(f1_score(y_true, y_pred_xgb_binary), 2)

        scores = {
            "accuracy": accuracy,
            "precision": precision,
            "log_loss": loss,
            "recall": recall,
            "f1": f1
        }
        plots = {
            "precision_recall": precision_recall,
            "roc_auc": roc_auc,
            "t_sne": t_sne_plot
        }
        return scores, plots
        