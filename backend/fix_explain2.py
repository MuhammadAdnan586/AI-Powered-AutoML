with open("app/explainability/routes.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block = """    # Prefer the exact feature columns saved during training (matches the
    # model''s expected input shape, e.g. excludes identifier columns like ''id'').
    saved_feature_columns = None
    try:
        with open(model_path, \"rb\") as f:
            saved_obj = pickle.load(f)
        if isinstance(saved_obj, dict) and \"feature_columns\" in saved_obj:
            saved_feature_columns = saved_obj[\"feature_columns\"]
            model = saved_obj[\"model\"]
    except Exception:
        pass"""

new_block = """    # Prefer the exact feature columns saved during training (matches the
    # model''s expected input shape, e.g. excludes identifier columns like ''id'').
    saved_feature_columns = None
    best_model_file = MODELS_DIR / f\"{session_id}_best_model.pkl\"
    try:
        with open(best_model_file, \"rb\") as f:
            saved_obj = pickle.load(f)
        if isinstance(saved_obj, dict) and \"feature_columns\" in saved_obj:
            saved_feature_columns = saved_obj[\"feature_columns\"]
            model = saved_obj[\"model\"]
    except Exception:
        pass"""

if old_block not in content:
    print("OLD BLOCK NOT FOUND - manual check needed")
else:
    content = content.replace(old_block, new_block, 1)
    with open("app/explainability/routes.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fix applied successfully")
