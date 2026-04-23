from src.core import greet

def test_greet_default():
    assert "AI Project" in greet()

def test_greet_with_name():
    name = "Gemini"
    assert f"Hello, {name}!" in greet(name)
