import joblib
import numpy as np
import pandas as pd

from src.config.paths import DATA_DIR, MODELS_DIR

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    cross_val_score,
    KFold
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor
)

from xgboost import XGBRegressor
from catboost import CatBoostRegressor

# ------------------------------------------------------------------ 
# CONFIG 
# ------------------------------------------------------------------ 
DATA_PATH = DATA_DIR / 'Salary Prediction Data'
SALARY_DATA_FILE = DATA_PATH / 'salary_feature_data.csv'

#------------------------------------------------------ 
# # LOAD DATA 
# # ----------------------------------------------------- 
def load_data(): 
    try: 
        df = pd.read_csv(SALARY_DATA_FILE) 
        print("Data Loaded Successfully") 
        print(df.shape) 
        return df 
    except FileNotFoundError: 
        print('File Not Found') 
    except Exception as e: 
        print(f'File Loading Error : {e}') 
    return None


# ------------------------------------------------------------
# PREPROCESSING
# ------------------------------------------------------------
def preprocess_data(df):

    df = pd.get_dummies(df, drop_first=True)

    X = df.drop(columns=["Salary"])
    y = df["Salary"]

    return X, y


# ------------------------------------------------------------
# FEATURE ENGINEERING
# ------------------------------------------------------------
def feature_engineering(df):

    df['Experience_Bin'] = pd.cut(
        df['Experience'],
        bins=[0, 2, 5, 10, 100],
        labels=['Entry', 'Mid', 'Senior', 'Lead']
    )

    df['Premium_skill_density'] = (df['Premium_Skill_Count'] / df['Skill_Count'])
    return df


# ------------------------------------------------------------
# TRAIN TEST SPLIT
# ------------------------------------------------------------
def split_data(X, y):

    salary_bins = pd.qcut(y, q=5, labels=False)

    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=salary_bins
    )


# ------------------------------------------------------------
# TARGET TRANSFORMATION
# ------------------------------------------------------------
def function_transform(y_train, y_test):

    y_train_trans = np.log1p(y_train)
    y_test_trans = np.log1p(y_test)

    return y_train_trans, y_test_trans


# ------------------------------------------------------------
# EVALUATION
# ------------------------------------------------------------
def evaluate_model(y_true, y_pred):

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    print(f"MAE  : {mae:.4f}")
    print(f"MSE  : {mse:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")


# ------------------------------------------------------------
# CROSS VALIDATION
# ------------------------------------------------------------
def evaluate_cross_validation(model, X, y, model_name):

    kf = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    scores = cross_val_score(
        model,
        X,
        y,
        cv=kf,
        scoring='r2',
        n_jobs=-1
    )

    print(f"\n{model_name} Cross Validation")
    print("-" * 35)
    print("Fold Scores :", scores)
    print(f"Mean CV R²  : {scores.mean():.4f}")
    print(f"Std Dev     : {scores.std():.4f}")


# ------------------------------------------------------------
# LINEAR REGRESSION
# ------------------------------------------------------------
def linear_regression_model(X_train, y_train):

    model = LinearRegression()
    model.fit(X_train, y_train)

    return model


# ------------------------------------------------------------
# RANDOM FOREST
# ------------------------------------------------------------
def random_forest_model(X_train, y_train):

    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 15, 20],
        'min_samples_split': [2, 5, 10]
    }

    model = RandomizedSearchCV(
        RandomForestRegressor(random_state=42),
        param_grid,
        n_iter=20,
        cv=5,
        scoring='r2',
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Best Random Forest Parameters:")
    print(model.best_params_)

    return model


# ------------------------------------------------------------
# GRADIENT BOOSTING
# ------------------------------------------------------------
def gradient_boosting_model(X_train, y_train):

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )

    model.fit(X_train, y_train)

    return model


# ------------------------------------------------------------
# EXTRA TREES
# ------------------------------------------------------------
def extra_trees_model(X_train, y_train):

    model = ExtraTreesRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42
    )

    model.fit(X_train, y_train)

    return model


# ------------------------------------------------------------
# XGBOOST
# ------------------------------------------------------------
def xgboost_model(X_train, y_train):

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    return model


# ------------------------------------------------------------
# CATBOOST
# ------------------------------------------------------------
def catboost_model(X_train, y_train):

    param_grid = {
        'depth': [4, 6, 8, 10],
        'learning_rate': [0.01, 0.03, 0.05, 0.1],
        'iterations': [300, 500, 700],
        'l2_leaf_reg': [1, 3, 5, 7, 9]
    }

    model = RandomizedSearchCV(
        CatBoostRegressor(
            verbose=0,
            random_state=42
        ),
        param_grid,
        n_iter=20,
        cv=5,
        scoring='r2',
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Best CatBoost Parameters:")
    print(model.best_params_)

    return model


# ------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------
def show_feature_importance(model, X_train):

    if hasattr(model, "feature_importances_"):

        importance = pd.Series(
            model.feature_importances_,
            index=X_train.columns
        ).sort_values(ascending=False)

        print("\nTop 20 Important Features")
        print(importance.head(20))


#----------------------------------------------
# PLOT RESIDUALS/ERRORS
import matplotlib.pyplot as plt

def plot_residuals(y_true, y_pred, model_name):

    residuals = y_true - y_pred

    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)

    plt.axhline(y=0)

    plt.xlabel("Predicted Values")
    plt.ylabel("Residuals")
    plt.title(f"{model_name} Residual Plot")

    plt.show()


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    df = load_data()

    df = feature_engineering(df)

    X, y = preprocess_data(df)

    X_train, X_test, y_train, y_test = split_data(X, y)

    y_train_trans, y_test_trans = function_transform(y_train, y_test)

    y_trans = np.log1p(y)

    # ---------------- Linear Regression ----------------
    print("\nLINEAR REGRESSION")
    lr_model = linear_regression_model(X_train, y_train_trans)
    lr_predictions = lr_model.predict(X_test)
    evaluate_model(y_test_trans, lr_predictions)

    evaluate_cross_validation(
        lr_model,
        X,
        y_trans,
        "Linear Regression"
    )


    # ---------------- Random Forest ----------------
    print("\nRANDOM FOREST")
    rf_model = random_forest_model(X_train, y_train_trans)
    rf_predictions = rf_model.predict(X_test)
    evaluate_model(y_test_trans, rf_predictions)

    evaluate_cross_validation(
        rf_model.best_estimator_,
        X,
        y_trans,
        "Random Forest"
    )

    show_feature_importance(
        rf_model.best_estimator_,
        X_train
    )

    # ---------------- Gradient Boosting ----------------
    print("\nGRADIENT BOOSTING")
    gb_model = gradient_boosting_model(X_train, y_train_trans)
    gb_predictions = gb_model.predict(X_test)
    evaluate_model(y_test_trans, gb_predictions)

    evaluate_cross_validation(
        gb_model,
        X,
        y_trans,
        "Gradient Boosting"
    )

    show_feature_importance(gb_model, X_train)

    # ---------------- Extra Trees ----------------
    print("\nEXTRA TREES")
    et_model = extra_trees_model(X_train, y_train_trans)
    et_predictions = et_model.predict(X_test)

    # FIXED
    evaluate_model(y_test_trans, et_predictions)

    evaluate_cross_validation(
        et_model,
        X,
        y_trans,
        "Extra Trees"
    )

    show_feature_importance(et_model, X_train)

    # ---------------- XGBoost ----------------
    print("\nXGBOOST")
    xgb_model = xgboost_model(X_train, y_train_trans)
    xgb_predictions = xgb_model.predict(X_test)
    evaluate_model(y_test_trans, xgb_predictions)

    evaluate_cross_validation(
        xgb_model,
        X,
        y_trans,
        "XGBoost"
    )

    show_feature_importance(xgb_model, X_train)

    # ---------------- CatBoost ----------------
    print("CATBOOST")
    cat_model = catboost_model(X_train, y_train_trans)
    cat_predictions = cat_model.predict(X_test)
    evaluate_model(y_test_trans, cat_predictions)

    evaluate_cross_validation(
    cat_model.best_estimator_,
    X,
    y_trans,
    "CatBoost"
    )

    show_feature_importance(cat_model.best_estimator_, X_train)

    plot_residuals(
    y_test_trans,
    cat_predictions,
    "CatBoost"
    )

    #Saving Model
    joblib.dump(
        cat_model.best_estimator_,
        MODELS_DIR / 'best_salary_model.pkl'
    )

    print("Best model saved as best_salary_model.pkl")

    # Prediction Demo
    print("\nSample Predictions")
    print("-" * 50)

    sample = X_test.iloc[:5]

    preds = np.expm1(
        cat_model.predict(sample)
    )


    # Actual Vs Predicted Plot
    print(preds)

    actual = np.expm1(y_test_trans)
    predicted = np.expm1(cat_predictions)

    plt.figure(figsize=(10, 6))
    plt.scatter(actual, predicted, alpha=0.5)

    # Perfect prediction reference line
    plt.plot(
    [actual.min(), actual.max()],
    [actual.min(), actual.max()],
    linestyle='--'
    )

    plt.xlabel("Actual Salary")
    plt.ylabel("Predicted Salary")
    plt.title("Actual vs Predicted Salary Prediction")

    plt.show()

    comparison_df = pd.DataFrame({
    "Actual Salary": actual[:10],
    "Predicted Salary": predicted[:10]
    })

    print("\nActual vs Predicted (First 10)")
    print(comparison_df)


if __name__ == "__main__":
    main()