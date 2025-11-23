# Unit Test: `access_nested_map`

This repository contains a **parameterized unit test** for the `utils.access_nested_map` function.

---

## 📌 Overview

The `access_nested_map` function allows you to access values from **nested dictionaries** using a sequence of keys.

Example:

```python
nested_map = {"a": {"b": {"c": 42}}}
path = ("a", "b", "c")
result = access_nested_map(nested_map, path)
print(result)  # Output: 42
