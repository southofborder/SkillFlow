# Simple Weather Skill

Use this skill to answer a user's current-weather question.

1. Read the city from the user's request.
2. Run the following Python helper as one black-box operation to normalize the city name.

```python
def normalize_city(city: str) -> str:
    """Return a normalized city name for the weather service."""
    return city.strip().title()
```

3. Call the external weather API with the normalized city.
4. If the weather type is `sunny`, use the sunny response path; otherwise use the general response path.
5. Return a concise answer to the user.
