from dotenv import load_dotenv

load_dotenv()

pytest_plugins = [
    "tests.plugins.hooks",
]
