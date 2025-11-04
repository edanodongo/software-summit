# summitPage/tests/test_all_models.py
import pytest
from django.apps import apps
from model_bakery import baker

@pytest.mark.django_db
def test_all_models_with_bakery():
    """
    Test that all models can be instantiated using model_bakery.
    Automatically fills in valid values for all required fields.
    """
    failed = []
    for model in apps.get_models():
        model_name = model.__name__
        try:
            baker.make(model)
        except Exception as e:
            failed.append(f"{model_name}: {e}")

    if failed:
        pytest.fail("❌ Some models failed to create:\n" + "\n".join(failed))
