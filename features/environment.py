from splinter import Browser
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment, teardown_test_environment


def before_all(context):
    try:
        # Limpiar el entorno primero
        teardown_test_environment()
    except:
        pass

    context.browser = Browser('firefox', headless=True)
    context.test_runner = DiscoverRunner()
    setup_test_environment()
    context.test_db = context.test_runner.setup_databases()
    context.get_url = lambda path: f'http://localhost:8000{path}'


def after_scenario(context, scenario):
    # Limpiar después de cada escenario
    pass


def after_all(context):
    try:
        if hasattr(context, 'browser'):
            context.browser.quit()
        if hasattr(context, 'test_db'):
            context.test_runner.teardown_databases(context.test_db)
        teardown_test_environment()
    except Exception as e:
        print(f"Error en teardown: {e}")