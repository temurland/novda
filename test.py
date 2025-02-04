from dataclasses import dataclass

@dataclass
class Test:
    id: int
    name: str

test = Test(id='df', name="<NAME>")
print(test)

