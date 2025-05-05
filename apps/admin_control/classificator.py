import pandas as pd
import nltk
import os
import time
import xgboost
from google import genai
from textblob import TextBlob
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from django.conf import settings


class ModelCreator:
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
    def calc_embeddings_features(news, features):
        client = genai.Client(api_key=os.environ["API_KEY"])
        embeddings_features = []
        for i, text in enumerate(news["text"].iloc[:30]):
            success = False
            retry_delay = 60
            while not success:
                try:
                    response = client.models.embed_content(
                        model='text-embedding-004',
                        contents=text,
                        config=genai.types.EmbedContentConfig(task_type="CLASSIFICATION")
                    )
                    print(i)
                    values = response.embeddings[0].values
                    if "сентимент" in features:
                        values.append(TextBlob(text).sentiment.polarity)
                    if "суб'єктивність" in features:
                        values.append(TextBlob(text).sentiment.subjectivity)
                    embeddings_features.append(values)
                    success = True

                    time.sleep(1.0)

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
    
    def create_model(self, name, news, features, params):
        embeddings_features, labels = self.calc_embeddings_features(news, features)
        X = pd.DataFrame(embeddings_features[:30])
        y = labels.iloc[:30].reset_index(drop=True)

        X_train, X_test, y_train, y_test = self.create_train_sets(X, y, 0.25)

        train_matrix = xgboost.DMatrix(X_train, y_train)
        test_matrix = xgboost.DMatrix(X_test, y_test)

        model_xgb = xgboost.train(params, 
          train_matrix, evals=[(train_matrix, "train"), (test_matrix, "validation")], 
          num_boost_round=100, early_stopping_rounds=20)
        model_xgb.save_model(settings.DETECTION_MODELS_PATH / f"{name}.json")
                
