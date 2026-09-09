# Tools Package (`packages/tools`)

Shared tools for agents across apps and examples.

## Available Tools

- `calculator`: Safe mathematical evaluator for agents.
- Custom `@tool` decorators and tool definitions.

## Usage

```python
from tools import calculator

result = calculator.invoke({"expression": "2 + 2 * 10"})
print(result) # 22
```
