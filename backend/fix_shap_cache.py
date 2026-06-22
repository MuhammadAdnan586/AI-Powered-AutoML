with open("app/explainability/shap_service.py", "r", encoding="utf-8") as f:
    content = f.read()

old_init = """        self.explainer = None
        self.shap_values = None
        self._init_explainer()"""

new_init = """        self.explainer = None
        self.shap_values = None
        self._cached_X_sample = None
        self._init_explainer()"""

old_compute = """    def compute_shap_values(self, X_sample: pd.DataFrame) -> np.ndarray:
        self.shap_values = self.explainer.shap_values(X_sample)
        return self.shap_values"""

new_compute = """    def compute_shap_values(self, X_sample: pd.DataFrame) -> np.ndarray:
        # Avoid recomputing the same SHAP values multiple times within one
        # explanation request (feature importance + summary plot + waterfall
        # plot all call this with the identical X_sample, which is expensive
        # for KernelExplainer-based models like KNN/SVM).
        if self.shap_values is not None and self._cached_X_sample is X_sample:
            return self.shap_values
        self.shap_values = self.explainer.shap_values(X_sample)
        self._cached_X_sample = X_sample
        return self.shap_values"""

if old_init not in content or old_compute not in content:
    print(f"NOT FOUND - init: {old_init in content}, compute: {old_compute in content}")
else:
    content = content.replace(old_init, new_init, 1)
    content = content.replace(old_compute, new_compute, 1)
    with open("app/explainability/shap_service.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fix applied successfully")
