# Stable Diffusion XL Base v1.0 App

Implementation of [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
This is a Potassium HTTP server, created with `banana init` CLI

## Testing

1. `. ./venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python3 download.py`
4. `python3 app.py m1`
5. `deactivate` (when finished)

### Test with CURL

```bash
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Software developers start with a Hello, [MASK]! script."}' \
    http://localhost:8000/
```
