import pandas as pd
import requests
from datetime import datetime
import math
import numpy as np
import webcolors
from PIL import Image, ImageDraw, ImageFont
from operator import itemgetter
from instagrapi import Client
from instagrapi.types import Usertag, Location
from dotenv import load_dotenv
import random
import tempfile
import os


def get_latest_block_hash() -> str:
    """
    Retrieves the latest block hash on the Bitcoin blockchain.
    
    Returns:
    str: The latest block hash on the Bitcoin blockchain.
    """
    url = "https://blockstream.info/api/blocks/tip/hash"
    response = requests.get(url)
    block_hash = response.text
    return block_hash





def get_latest_block_height() -> int:
    """
    Retrieves the latest block height on the Bitcoin blockchain.
    
    Returns:
    int: The latest block height on the Bitcoin blockchain.
    """
    url = "https://blockstream.info/api/blocks/tip/height"
    response = requests.get(url)
    block_height = int(response.text)
    return block_height






def get_block_hashes(block_height):
    """
    This function takes in a block height as an argument and returns a list of hashes
    for each block from the given height to the latest block. It first makes a request
    to the blockchain.info API to get the latest block height, then it loops through
    each block from the given height up until the latest one and appends the hash of
    each block to a list. The loop is preceded by an if statement that checks if
    'blocks' is present in the JSON response before looping through it.
    The counter is incremented after each iteration of the loop. 
    """
    block_hash_list = []
    url = f'https://blockchain.info/latestblock'
    response = requests.get(url)
    data = response.json()
    latest_block = data["height"]

    while block_height <= latest_block:
        url = f'https://blockchain.info/block-height/{block_height}?format=json'
        response = requests.get(url)
        data = response.json()

        if 'blocks' in data: # Check if 'blocks' is in the JSON before looping through it 
            for block in data['blocks']: 
                block_hash_list.append(block['hash'])

        block_height += 1 # Increment the counter after each iteration of the loop 

    return block_hash_list 






def get_block_data(block_height: str) -> dict:
    """
    Retrieves statistics for a given block height from the blockstream.info API.
    
    Parameters:
    block_hash (str): The block height of the block for which statistics are to be retrieved.

    Returns:
    dict: A dictionary containing the statistics for the given block hash
    """
    url = f'https://blockchain.info/block-height/{block_height}?format=json'
    response = requests.get(url)
    data = response.json()

    return data





def get_transaction_data(block_height):

    """
    This function takes in a block height and returns a dataframe containing the transaction
    data from that block. It uses the requests library to make a GET request to the blockchain.info
    API for the given block height, parses the response as JSON, and extracts the transaction data
    from it. The extracted data is then stored in a Pandas DataFrame with columns for transaction hash,
    fee, value of outputs, sum of outputs in Satoshis, and sum of outputs in Bitcoin.
    """

    url = f'https://blockchain.info/block-height/{block_height}?format=json'
    response = requests.get(url)
    data = response.json()

    # Access transactions from block and extract Transaction data
    df_transactions = pd.DataFrame([(i['hash'], i['fee'], list(map(itemgetter('value'), i['out'])), sum(list(map(itemgetter('value'), i['out']))), sum(list(map(itemgetter('value'), i['out'])))/100000000) for i in data['blocks'][0]['tx']], 
               columns =['transaction_hash', 'transaction_fee','value_outs','value_outs_sum_sats','value_outs_sum_btc'])

    return df_transactions




def convert_timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)




def get_radius_from_area(area: float) -> float:
    return math.sqrt(area / math.pi)


def generate_second_color(color, seed=None):
    """
    Generates a bright neon-like color based on the input color.
    
    Args:
    - color (str): The base color in hex format (e.g. "#ff0000").
    - seed (int, Optional): The seed value for the random number generator. Default is None.
    
    Returns:
    - str: The generated neon-like color in hex format.
    """
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
    # Set the seed value for the random number generator
    if seed:
        random.seed(seed)
    
    # Randomly adjust one of the color channels to create a bright neon-like color
    channel = random.choice(["r", "g", "b"])
    if channel == "r":
        r = min(255, r + random.randint(70, 255))
    elif channel == "g":
        g = min(255, g + random.randint(70, 255))
    else:
        b = min(255, b + random.randint(70, 255))
    second_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return second_color


# def generate_second_color(color, seed=None):
#     # Generate a second color that is slightly different from the base color
#     r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
#     # Set the seed value for the random number generator
#     if seed:
#         random.seed(seed)
    
#     # Randomly adjust one of the color channels
#     channel = random.choice(["r", "g", "b"])
#     if channel == "r":
#         r = (r + random.randint(0, 255)) % 255
#     elif channel == "g":
#         g = (g + random.randint(0, 255)) % 255
#     else:
#         b = (b + random.randint(0, 255)) % 255
#     second_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
#     return second_color


def create_image(width: int, height: int, color1: str, color2: str, number_of_circles: int, block_height: int, backgroundcolor: str, transaction_values: list,size_factor: int,seed=None,save_as_file=None):

    # Set the seed value for the random number generator
    if seed:
        random.seed(seed)

    color1_rgb = webcolors.hex_to_rgb(color1)
    color2_rgb = webcolors.hex_to_rgb(color2)
    backgroundcolor_rgb = webcolors.hex_to_rgb(backgroundcolor)

    image = Image.new(mode="RGB", size=(width, height), color=backgroundcolor_rgb)

    center_x = width // 2
    center_y = height // 2
    cube_size = width/2.5

    for i in transaction_values:

        circle_radius =  get_radius_from_area(i*size_factor)

        x = center_x + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)
        y = center_y + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)

        percent_x = x / width
        percent_y = y / height
        percent_x_y = percent_x + percent_y
        red = color1_rgb[0] + (color2_rgb[0] - color1_rgb[0]) * percent_x_y
        green = color1_rgb[1] + (color2_rgb[1] - color1_rgb[1]) * percent_x_y
        blue = color1_rgb[2] + (color2_rgb[2] - color1_rgb[2]) * percent_x_y
        circle_shape = [
            (x, y),
            (x + circle_radius, y + circle_radius)]
        draw_image = ImageDraw.Draw(image)
        draw_image.ellipse(circle_shape, fill=(int(red), int(green), int(blue)))

    if save_as_file:
        # Save the image
        image.save(f'images/block_{block_height}_{width}px_{height}px.jpg')
    else:
        return image





def scale_image (image, width, height):
    # Scale the image maintaining aspect ratio
    image.thumbnail((width, height))
    # Return the resized image
    return image.resize((width, height))




def post_image_on_instagram(image, caption, username=None, password=None):
    """
    Posts the given image on Instagram with the provided caption.
    
    Args:
    - image (PIL.Image): The image to be posted on Instagram
    - caption (str): The caption for the image
    - username (str, Optional): The username of the Instagram account. Default is None.
    - password (str, Optional): The password of the Instagram account. Default is None.
    
    Raises:
    - ValueError: If the username and/or password is not provided

    """
    if not all([username, password]):
        raise ValueError("username and password are required.")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp:
        filepath = temp.name
        image.save(filepath)
    
    # Create a new Client object and login
    cl = Client()
    cl.login(username, password)

    # Post the image on Instagram
    cl.photo_upload(filepath, caption=caption)
    cl.logout()
    os.remove(filepath)
