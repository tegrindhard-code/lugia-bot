import os
import math
import time
import json
import discord
import requests
import xmltodict
import re
import ast
from PIL import Image, ImageSequence
from discord.ext import commands
from discord import app_commands

BOT_TOKEN = ""

# Variables
MAX_DIMENSION = 1024
UPLOAD_URL = "https://apis.roblox.com/assets/user-auth/v1/assets"
USER_INFO_URL = "https://users.roblox.com/v1/users/authenticated"
OPERATION_URL_BASE = "https://apis.roblox.com/assets/user-auth/v1/operations/"
TEMP_DIR = "temp_sheets"
COOKIE_FILE = "cookie.txt"

# Setup bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Roblox api stuff
def get_csrf_token(auth_cookie):
    response = requests.post(UPLOAD_URL, headers={"Cookie": f".ROBLOSECURITY={auth_cookie}"})
    if response.status_code == 403:
        return response.headers.get("x-csrf-token")
    raise Exception("Failed to get CSRF token")

def get_user_id(auth_cookie):
    response = requests.get(USER_INFO_URL, headers={"Cookie": f".ROBLOSECURITY={auth_cookie}"})
    if response.status_code == 200:
        return response.json()["id"]
    raise Exception("Failed to get authenticated user")

def poll_operation(operation_id, auth_cookie):
    for _ in range(10):
        time.sleep(2)
        url = OPERATION_URL_BASE + operation_id
        response = requests.get(url, headers={"Cookie": f".ROBLOSECURITY={auth_cookie}"})
        if response.status_code == 200:
            data = response.json()
            if data.get("done") and data.get("response", {}).get("assetId"):
                return data["response"]["assetId"]
    raise Exception("Asset processing timed out")

def upload_asset(file_path, auth_cookie, user_id, csrf_token):
    with open(file_path, "rb") as f:
        files = {
            "fileContent": (os.path.basename(file_path), f, "image/png")
        }
        payload = {
            "request": json.dumps({
                "displayName": os.path.basename(file_path),
                "description": "Bream so cool",
                "assetType": "Decal",
                "creationContext": {
                    "creator": { "userId": user_id },
                    "expectedPrice": 0
                }
            })
        }
        headers = {
            "x-csrf-token": csrf_token,
            "Cookie": f".ROBLOSECURITY={auth_cookie}"
        }
        response = requests.post(UPLOAD_URL, data=payload, files=files, headers=headers)
        if response.status_code == 200:
            operation_id = response.json().get("operationId")
            if not operation_id:
                raise Exception("Missing operation ID")
            return poll_operation(operation_id, auth_cookie)
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")

# Sprite sheet processing
def create_sprite_sheets(gif_path, gif_name):
    gif = Image.open(gif_path)
    frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(gif)]
    num_frames = len(frames)
    width, height = frames[0].size
    columns = MAX_DIMENSION // width
    frames_per_sheet = columns * (MAX_DIMENSION // height)
    num_sheets = math.ceil(num_frames / frames_per_sheet)
    os.makedirs(TEMP_DIR, exist_ok=True)

    sheet_paths = []
    rows_per_sheet = []

    for sheet_index in range(num_sheets):
        start = sheet_index * frames_per_sheet
        end = min(start + frames_per_sheet, num_frames)
        frames_in_sheet = end - start
        rows = min(MAX_DIMENSION // height, math.ceil(frames_in_sheet / columns))
        sheet = Image.new('RGBA', (columns * width, rows * height))

        x, y = 0, 0
        for i in range(frames_in_sheet):
            frame = frames[start + i]
            sheet.paste(frame, (x * width, y * height), mask=frame)
            x += 1
            if x == columns:
                x = 0
                y += 1

        path = os.path.join(TEMP_DIR, f"{gif_name}_sheet_{sheet_index + 1}.png")
        sheet.save(path)
        sheet_paths.append(path)
        rows_per_sheet.append(rows)

    return sheet_paths, rows_per_sheet, num_frames, width - 1, height - 1, columns

# super sigma decal to image id converter
def grab_image_id(decal_id, auth_cookie):
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={decal_id}"
    headers = {
        "Cookie": f".ROBLOSECURITY={auth_cookie}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = xmltodict.parse(response.text)
        content_url = data.get("roblox", {}).get("Item", {}).get("Properties", {}).get("Content", {}).get("url")

        if content_url:
            if "rbxassetid://" in content_url:
                return content_url.split("rbxassetid://")[1]
            elif "?id=" in content_url:
                return content_url.split("?id=")[1]
    except Exception as e:
        print(f"Failed to fetch asset ID: {e}")

    return None

# lua to python dictionary
def lua_to_python_dict(gif_str):
    gif_str = re.sub(r'(\w+)=', r'"\1":', gif_str)
    gif_str = gif_str.replace("{{", "[{").replace("}}", "}]")
    try:
        return ast.literal_eval(gif_str)
    except Exception as e:
        raise ValueError(f"Failed to parse input: {e}")

def slice_frames(sheet_img, frame_width, frame_height, frames_per_row, total_frames):
    frames = []
    for i in range(total_frames):
        row = i // frames_per_row
        col = i % frames_per_row
        x = col * frame_width
        y = row * frame_height
        frame = sheet_img.crop((x, y, x + frame_width, y + frame_height))
        frames.append(frame)
    return frames

def rebuild_gif_from_gifdata(gif_input, image_paths, output_path="rebuilt.gif", fps=24):
    data = lua_to_python_dict(gif_input)

    fWidth = data["fWidth"] + 1
    fHeight = data["fHeight"] + 1
    total_needed_frames = data["nFrames"]

    all_frames = []

    for i, sheet in enumerate(data["sheets"]):
        image_path = image_paths[i]
        try:
            img = Image.open(image_path).convert("RGBA")
        except Exception as e:
            print(f"Failed to load image at {image_path}: {e}")
            continue

        rows = sheet.get("rows", 1)
        frames_per_sheet = rows * data["framesPerRow"]
        remaining_frames = total_needed_frames - len(all_frames)
        frames_to_extract = min(frames_per_sheet, remaining_frames)

        if frames_to_extract <= 0:
            break

        frames = slice_frames(
            img,
            fWidth,
            fHeight,
            data["framesPerRow"],
            frames_to_extract
        )
        all_frames.extend(frames)

    if all_frames:
        frame_duration = int(1000 / fps)
        all_frames[0].save(
            output_path,
            save_all=True,
            append_images=all_frames[1:],
            duration=frame_duration,
            loop=0,
            disposal=2
        )
        return output_path
    else:
        raise Exception("No frames extracted.")

# Discord Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="set_cookie", description="Set or update your .ROBLOSECURITY")
@app_commands.describe(auth_cookie="Your .ROBLOSECURITY")
async def set_cookie(interaction: discord.Interaction, auth_cookie: str):
    try:
        with open(COOKIE_FILE, "w") as f:
            f.write(auth_cookie)
        await interaction.response.send_message("Cookie saved successfully!")
    except Exception as e:
        await interaction.response.send_message(f"Failed to save cookie: {e}")


@bot.tree.command(name="sprite_to_gifdata", description="Converts sprite to gifdata")
@app_commands.describe(
    gif1="Front Sprite",
    gif2="Back Sprite",
    gif3="Front Shiny Sprite",
    gif4="Back Shiny Sprite"
)
@app_commands.checks.cooldown(1, 30.0)
async def upload_gif(
    interaction: discord.Interaction,
    gif1: discord.Attachment,
    gif2: discord.Attachment = None,  # type: ignore
    gif3: discord.Attachment = None,  # type: ignore
    gif4: discord.Attachment = None   # type: ignore
):
    await interaction.response.defer()

    if not os.path.exists(COOKIE_FILE):
        await interaction.followup.send("No cookie found. Use `/set_cookie` first.")
        return

    with open(COOKIE_FILE, "r") as f:
        auth_cookie = f.read().strip()

    os.makedirs(TEMP_DIR, exist_ok=True)

    gifs = [gif1, gif2, gif3, gif4]
    gif_datas = []
    error_messages = []

    for gif in gifs:
        if gif is None:
            continue

        if not gif.filename.lower().endswith(".gif"):
            error_messages.append(f"`{gif.filename}` is not a `.gif` file.")
            continue

        gif_path = os.path.join(TEMP_DIR, gif.filename)
        await gif.save(gif_path)  # type: ignore
        gif_name = os.path.splitext(gif.filename)[0]

        try:
            sheet_paths, rows_per_sheet, nFrames, fWidth, fHeight, framesPerRow = create_sprite_sheets(gif_path, gif_name)
            csrf_token = get_csrf_token(auth_cookie)
            user_id = get_user_id(auth_cookie)

            sheets_info = []
            for path, rows in zip(sheet_paths, rows_per_sheet):
                asset_id = upload_asset(path, auth_cookie, user_id, csrf_token)
                image_id = grab_image_id(asset_id, auth_cookie)
                sheets_info.append(f'{{id={image_id},rows={rows}}}')

            gif_data = (
                f"['{gif_name}']={{"
                f"sheets={{{','.join(sheets_info)}}},"
                f"nFrames={nFrames},fWidth={fWidth},fHeight={fHeight},framesPerRow={framesPerRow}"
                f"}},"
            )
            gif_datas.append(gif_data)
        except Exception as e:
            error_messages.append(f"Error with `{gif.filename}`: {e}")

    if gif_datas:
        labels = ["Front", "Back", "Shiny Front", "Shiny Back"]
        msg = "Sprites Processed!\n"
        for i, data in enumerate(gif_datas):
            label = labels[i] if i < len(labels) else f"Sprite {i+1}"
            msg += f"{label}:\n```lua\n{data}\n```\n"
    else:
        msg = "No valid sprites processed.\n"

    if error_messages:
        msg += "\nErrors:\n" + "\n".join(error_messages)

    await interaction.followup.send(msg[:2000] if len(msg) > 2000 else msg)

    # Cleanup
    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except Exception:
            pass

@bot.tree.command(name="download_gifdata", description="Download and rebuild a gif from gifdata")
@app_commands.describe(data="Gifdata here without the comma at the end")
async def download_gifdata(interaction: discord.Interaction, data: str):
    await interaction.response.defer()

    if not os.path.exists(COOKIE_FILE):
        await interaction.followup.send("No cookie found. Use `/set_cookie` first.")
        return

    try:
        auth_cookie = open(COOKIE_FILE).read().strip()
        match = re.match(r"\s*\[\s*'(.+?)'\s*\]\s*=\s*(\{.+?\})\s*,?\s*$", data)
        if not match:
            await interaction.followup.send("Invalid gifdata format.")
            return

        gif_name, gtable = match.groups()

        # Parse the table
        parsed = lua_to_python_dict(gtable)
        sheet_ids = [sheet["id"] for sheet in parsed["sheets"]]

        # Download each image
        image_paths = []
        os.makedirs(TEMP_DIR, exist_ok=True)
        for sheet_id in sheet_ids:
            url = f"https://assetdelivery.roblox.com/v1/asset/?id={sheet_id}"
            headers = {"Cookie": f".ROBLOSECURITY={auth_cookie}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            file_path = os.path.join(TEMP_DIR, f"{sheet_id}.png")
            with open(file_path, "wb") as f:
                f.write(response.content)
            image_paths.append(file_path)

        # Build the GIF
        gif_path = os.path.join(TEMP_DIR, f"{gif_name}.gif")
        output_path = rebuild_gif_from_gifdata(gtable, image_paths, output_path=gif_path, fps=24)

        await interaction.followup.send(file=discord.File(output_path))

    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

    # Cleanup
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))


bot.run(BOT_TOKEN)
