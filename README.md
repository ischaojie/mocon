# mocon

Mocon is pluggable configuration management tool.
Base on `Pydantic` and `wtforms`.

## Install

```
python -m pip install -U mocon
```

## Basic Usage

```python
from flask import Flask
from mocon import BaseModel, Field, Mocon

app = Flask(__name__)
mocon = Mocon(app)

class User(BaseModel):
    name: str = Field(max_length=12)
    age: int

mocon.register(User)

if __name__ == "__main__":
    app.run()

```

Then, you can open `http://localhost:5000/mocon` get more detail about mocon.
