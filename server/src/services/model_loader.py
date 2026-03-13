"""
Safe Model Loader
==================
Wraps joblib.load with graceful handling for version mismatches between
the training environment and the current runtime (e.g., numpy._core
ModuleNotFoundError or sklearn version UserWarnings).

Usage:
    from .model_loader import safe_load_model

    artifact = safe_load_model(Path("models/kidney_disease_model.pkl"))
    if artifact is None:
        logger.error("Model could not be loaded — running in degraded mode")
"""

import warnings
import logging
from pathlib import Path

import joblib
import sklearn
import numpy as np

logger = logging.getLogger(__name__)


class ModelVersionMismatchError(Exception):
    """Raised when a pkl was trained with incompatible library versions."""


def _get_runtime_versions() -> dict:
    """Return a dict of currently installed library versions."""
    versions = {
        "numpy": np.__version__,
        "scikit-learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }
    try:
        import xgboost
        versions["xgboost"] = xgboost.__version__
    except ImportError:
        pass
    try:
        import lightgbm
        versions["lightgbm"] = lightgbm.__version__
    except ImportError:
        pass
    try:
        import catboost
        versions["catboost"] = catboost.__version__
    except ImportError:
        pass
    return versions


def safe_load_model(path: Path) -> object | None:
    """Load a .pkl model file with robust error handling.

    Returns the deserialized object on success, or None on failure.
    All errors are logged with actionable instructions instead of crashing.

    Handles:
    - ModuleNotFoundError (e.g. numpy._core missing → numpy version mismatch)
    - UserWarning from sklearn about version mismatches
    - Generic unpickling failures
    """
    path = Path(path)
    if not path.exists():
        logger.error("Model file not found: %s", path)
        return None

    runtime_versions = _get_runtime_versions()
    collected_warnings: list[warnings.WarningMessage] = []

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            artifact = joblib.load(path)
            collected_warnings = list(caught)

    except ModuleNotFoundError as e:
        # Classic symptom: pkl trained with numpy>=2.0 loaded in numpy<2.0
        # numpy 2.0 moved numpy.core → numpy._core
        module_name = getattr(e, "name", str(e))
        logger.error(
            "❌ Failed to load %s: %s\n"
            "   This usually means the model was trained with a different "
            "version of a core library.\n"
            "   Missing module : %s\n"
            "   Runtime versions: %s\n"
            "   FIX: Run 'pip install -r server/requirements.txt' to install "
            "matching versions,\n"
            "        then run 'python ml/scripts/retrain_kidney_model.py' to "
            "re-save the model.",
            path.name, e, module_name, runtime_versions,
        )
        return None

    except Exception as e:
        logger.error(
            "❌ Failed to load %s: %s (%s)\n"
            "   Runtime versions: %s\n"
            "   FIX: Retrain the model in the current environment with "
            "'python ml/scripts/train_all_models.py'.",
            path.name, e, type(e).__name__, runtime_versions,
        )
        return None

    # ── Process any sklearn version mismatch warnings ────────────────────
    for w in collected_warnings:
        msg = str(w.message)
        if "unpickle" in msg.lower() and "version" in msg.lower():
            # Extract trained-with vs runtime version from the warning text
            logger.warning(
                "⚠️  Version mismatch while loading %s: %s\n"
                "   Runtime sklearn=%s, numpy=%s\n"
                "   The model may produce incorrect results. "
                "Retrain with 'python ml/scripts/retrain_kidney_model.py'.",
                path.name, msg,
                runtime_versions.get("scikit-learn", "?"),
                runtime_versions.get("numpy", "?"),
            )
        else:
            # Re-emit non-version warnings normally
            logger.debug("Warning during load of %s: %s", path.name, msg)

    # ── Log successful load with version info ────────────────────────────
    version_info = "unknown"
    if isinstance(artifact, dict) and "version" in artifact:
        version_info = artifact["version"]

    logger.info(
        "✅ Loaded %s (model version=%s) with runtime: sklearn=%s, numpy=%s",
        path.name,
        version_info,
        runtime_versions.get("scikit-learn", "?"),
        runtime_versions.get("numpy", "?"),
    )

    return artifact
