import pygame as pg
import os


def load_image(file, alpha=True, colorkey=None):
    try:
        image = pg.image.load(file)
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        if colorkey is not None:
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image
    except pg.error as message:
        print(f"Cannot load image: {file}")
        raise SystemExit(message)

def load_strip(file, frame_size, alpha=True, colorkey=None):
    main_image = load_image(file, alpha, colorkey)
    strips = []
    for x in range(0, main_image.get_width(), frame_size[0]):
        frame = pg.Surface(frame_size, pg.SRCALPHA)
        frame.blit(main_image, (0, 0), (x, 0, frame_size[0], frame_size[1]))
        strips.append(frame)
    return strips


def load_assets(root_dir):
    assets = {}

    for root, _, files in os.walk(root_dir):
        if "Characters" not in root:
            continue

        category = os.path.relpath(root, root_dir).split(os.sep)
        if len(category) < 2:
            continue

        name = category[1].lower()
        if name not in assets:
            assets[name] = {}

        for file in files:
            if not file.endswith(".png"):
                continue

            file_path = os.path.join(root, file)
            base_name, _ = os.path.splitext(file)

            parts = base_name.split("_")
            if len(parts) < 2:
                print(f"File {file} does not follow naming convention.")
                continue

            action = parts[1].lower()
            variant = "base"

            if name == "human":
                if len(parts) > 2 and "_strip" in parts[-1]:
                    variant = "_".join(parts[2:-1]).lower()
                elif len(parts) > 2:
                    variant = parts[0].lower()

            if name not in assets:
                assets[name] = {}
            if action not in assets[name]:
                assets[name][action] = {}

            if variant not in assets[name][action]:
                assets[name][action][variant] = []

            if "_strip" in file:
                strip_info = base_name.split("_strip")[-1]
                try:
                    frame_count = int(strip_info)
                    frame_width = load_image(file_path).get_width() // frame_count
                    frame_height = load_image(file_path).get_height()
                    frames = load_strip(file_path, (frame_width, frame_height))
                except ValueError:
                    print(f"Invalid strip format in file: {file}")
                    continue
            else:
                frames = [load_image(file_path)]

            assets[name][action][variant].extend(frames)

    return assets





if __name__ == "__main__":
    pg.init(); 
    screen = pg.display.set_mode((100,100))
    characters = load_assets("assets")
    for key in characters:
        print(key)
        if characters[key]:
            print("\t", characters[key].keys())
            for action in characters[key]:
                print("\t\t", action)
                for variant in characters[key][action]:
                    print("\t\t\t", variant)
                    for frame in characters[key][action][variant]:
                        screen.fill((70, 70, 70))
                        screen.blit(frame, (0, 0))
                        pg.display.flip()
                        pg.time.wait(150)

