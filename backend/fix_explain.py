with open("app/explainability/routes.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block = """    target_column = session_data.get(\"target_column\", \"\")
    feature_columns = [c for c in df.columns if c != target_column]
    X = df[feature_columns].select_dtypes(include=[\"number\"])

    return model, X, model_name"""

new_block = """    target_column = session_data.get(\"target_column\", \"\")

    # Prefer the exact feature columns saved during training (matches the
    # model''s expected input shape, e.g. excludes identifier columns like ''id'').
    saved_feature_columns = None
    try:
        with open(model_path, \"rb\") as f:
            saved_obj = pickle.load(f)
        if isinstance(saved_obj, dict) and \"feature_columns\" in saved_obj:
            saved_feature_columns = saved_obj[\"feature_columns\"]
            model = saved_obj[\"model\"]
    except Exception:
        pass

    if saved_feature_columns:
        for col in saved_feature_columns:
            if col not in df.columns:
                df[col] = 0
        X = df[saved_feature_columns]
    else:
        feature_columns = [c for c in df.columns if c != target_column]
        X = df[feature_columns].select_dtypes(include=[\"number\"])

    return model, X, model_name"""

if old_block not in content:
    print("OLD BLOCK NOT FOUND - manual check needed")
else:
    content = content.replace(old_block, new_block, 1)
    with open("app/explainability/routes.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fix applied successfully")
