with open("app/explainability/routes.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block_1 = """        model, X, model_name = load_model_and_data(request.session_id, db)
        X_sample = X.sample(min(request.num_samples, len(X)), random_state=42)
        explainer = SHAPExplainer(model, X)
        result = explainer.get_full_explanation(X_sample, request.session_id)"""

new_block_1 = """        model, X, model_name = load_model_and_data(request.session_id, db)
        explainer = SHAPExplainer(model, X)
        effective_samples = request.num_samples
        if type(explainer.explainer).__name__ == \"KernelExplainer\":
            effective_samples = min(request.num_samples, 25)
        X_sample = X.sample(min(effective_samples, len(X)), random_state=42)
        result = explainer.get_full_explanation(X_sample, request.session_id)"""

old_block_2 = """        model, X, model_name = load_model_and_data(request.session_id, db)
        X_sample = X.sample(min(request.num_samples, len(X)), random_state=42)
        explainer = SHAPExplainer(model, X)
        importance = explainer.get_feature_importance(X_sample)"""

new_block_2 = """        model, X, model_name = load_model_and_data(request.session_id, db)
        explainer = SHAPExplainer(model, X)
        effective_samples = request.num_samples
        if type(explainer.explainer).__name__ == \"KernelExplainer\":
            effective_samples = min(request.num_samples, 25)
        X_sample = X.sample(min(effective_samples, len(X)), random_state=42)
        importance = explainer.get_feature_importance(X_sample)"""

found_1 = old_block_1 in content
found_2 = old_block_2 in content

if not found_1 and not found_2:
    print("NEITHER BLOCK FOUND - manual check needed")
else:
    if found_1:
        content = content.replace(old_block_1, new_block_1, 1)
    if found_2:
        content = content.replace(old_block_2, new_block_2, 1)
    with open("app/explainability/routes.py", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fix applied. explain block: {found_1}, feature-importance block: {found_2}")
