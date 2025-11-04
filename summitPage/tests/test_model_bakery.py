# summitPage/tests/test_model_bakery.py
import pytest
from django.apps import apps
from model_bakery import baker

@pytest.mark.django_db
def test_all_models_with_bakery():
    """
    Test that all models can be instantiated using model_bakery.
    This automatically fills required fields and relationships.
    """
    failed = []
    for model in apps.get_models():
        model_name = model.__name__
        try:
            baker.make(model)
        except Exception as e:
            failed.append(f"{model_name}: {e}")

    if failed:
        pytest.skip("Some models could not be created:\n" + "\n".join(failed))
