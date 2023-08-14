from potassium import Potassium, Request, Response
import torch
import base64
from PIL import Image
from io import BytesIO
from diffusers import DiffusionPipeline, StableDiffusionXLImg2ImgPipeline

app = Potassium("my_app")


# @app.init runs at startup, and loads models into the app's context
@app.init
def init():
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    base.to("cuda")
    base.enable_xformers_memory_efficient_attention()
    base.unet = torch.compile(base.unet, mode="reduce-overhead", fullgraph=True)

    # imager = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    #     "stabilityai/stable-diffusion-xl-base-1.0",
    #     torch_dtype=torch.float16,
    #     use_safetensors=True,
    #     variant="fp16",
    # )
    # imager.to("cuda")
    # imager.enable_xformers_memory_efficient_attention()
    # imager.unet = torch.compile(imager.unet, mode="reduce-overhead", fullgraph=True)

    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    refiner.to("cuda")
    refiner.unet = torch.compile(refiner.unet, mode="reduce-overhead", fullgraph=True)

    context = {"model": base,  "refiner": refiner}

    return context


# @app.handler runs for every call
@app.handler("/")
def handler(context: dict, request: Request) -> Response:
    model = context.get("model")
    # imager = context.get("imager")
    refiner = context.get("refiner")

    prompt = request.json.get("prompt")
    width = request.json.get("width", 1024)
    height = request.json.get("height", 1024)
    num_steps = request.json.get("num_steps", 50)
    high_noise_frac = request.json.get("high_noise_frac", 0.8)
    # init_image = request.json.get("image")

    # if init_image:
    #     im_bytes = base64.b64decode(init_image)
    #     im_file = BytesIO(im_bytes)
    #     im_input = Image.open(im_file)
    #     image = imager(
    #         prompt=prompt,
    #         image=im_input,
    #         num_inference_steps=num_steps,
    #         denoising_end=high_noise_frac,
    #         output_type="latent",
    #     ).images
    # else:
    #     image = model(
    #         prompt=prompt,
    #         width=width,
    #         height=height,
    #         num_inference_steps=num_steps,
    #         denoising_end=high_noise_frac,
    #         output_type="latent",
    #     ).images

        
    image = model(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=num_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
        ).images

    image = refiner(
        prompt=prompt,
        num_inference_steps=num_steps,
        denoising_start=high_noise_frac,
        image=image,
    ).images[0]

    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    output = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Response(json={"output": output}, status=200)


if __name__ == "__main__":
    app.serve()