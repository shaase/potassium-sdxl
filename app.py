import sys
from potassium import Potassium, Request, Response
import torch
import base64
from datetime import datetime
from io import BytesIO
from diffusers import DiffusionPipeline

app = Potassium("my_app")

# @app.init runs at startup, and loads models into the app's context
@app.init
def init():
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", 
        torch_dtype=torch.float16, 
        use_safetensors=True, 
        variant="fp16"
    )

    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )

    platform = "m1" in sys.argv[1:] and "m1" or "cuda"
    if platform == "cuda":
        base.to("cuda")
        refiner.to("cuda")
        base.enable_xformers_memory_efficient_attention()
    elif platform == "m1":
        base.to("mps")
        refiner.to("mps")
        base.enable_attention_slicing()

    context = {
        "model": base,
        "refiner": refiner
    }

    return context

# @app.handler runs for every call
@app.handler("/")
def handler(context: dict, request: Request) -> Response:
    prompt = request.json.get("prompt")
    width = request.json.get("width", 1024)
    height = request.json.get("height", 1024)
    num_inference_steps = request.json.get("num_inference_steps", 50)
    guidance_scale = request.json.get("guidance_scale", 0.5)
    negative_prompt = request.json.get("negative_prompt", "low quality")
    high_noise_frac = request.json.get("high_noise_frac", 0.8)
    print(request.json)

    model = context.get("model")
    refiner = context.get("refiner")
    image = model(
        prompt=prompt,
        width=width,
        height=height,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        denoising_end=high_noise_frac,
        negative_prompt=negative_prompt,
        output_type="latent",
    ).images

    image = refiner(
        prompt=prompt,
        num_inference_steps=num_inference_steps,
        denoising_start=high_noise_frac,
        negative_prompt=negative_prompt,
        image=image,
    ).images[0]

    buffered  = BytesIO()
    image.save(buffered, format="PNG")
    output = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3] + ".png"
    # image_bytes = str.encode(output)
    # with open(filename, "wb") as fh:
    #   fh.write(base64.decodebytes(image_bytes))

    return Response(
        json = {"output": output}, 
        status=200
    )

if __name__ == "__main__":
    app.serve()