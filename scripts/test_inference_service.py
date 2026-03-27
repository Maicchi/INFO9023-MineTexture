import argparse

from minetexture.inference.service import generate_from_prompt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt",
        default="minecraft stone texture, pixel art, seamless, game asset",
    )
    parser.add_argument("--use-lcm", action="store_true")
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--guidance-scale", type=float, default=None)
    parser.add_argument("--negative-prompt", default=None)
    parser.add_argument("--base-model", default=None)
    parser.add_argument("--lora-path", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--width", type=int, default=None)
    args = parser.parse_args()

    output_path = generate_from_prompt(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        steps=args.steps,
        guidance_scale=args.guidance_scale,
        use_lcm=args.use_lcm,
    )
    print(f"Generated image: {output_path}")


if __name__ == "__main__":
    main()
