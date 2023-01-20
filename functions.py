import pandas as pd
import time
import random
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
import tempfile
import os
import statistics
from PIL import Image
import io
from lxml import etree
from reportlab.graphics import renderPM
import random
from svgwrite import Drawing
from svgwrite.shapes import Circle
from svgwrite.utils import rgb
import tweepy
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def blockimage_generator(save_image_svg = False, save_image_png = False, block_heigth = None):

    """
    blockimage_generator((save_image_svg=False, block_height=None)

    This function loads a block's data from the Bitcoin blockchain, and then processes it to generate various statistics, such as the median transaction fee and the total value of all transactions in the block. It also creates an SVG image of the block, using the block's data to determine the image's colors and number of circles.

    Parameters:
    save_image_svg (bool): Indicates whether the image should be saved to the 'images' folder. Default is False.
    block_height (int): The height of the block to be processed. If not provided, the function will use the latest block height.

    Returns:
    A dictionary containing all the data processed from the block.
    """

    load_dotenv('.env')

    # load global vars from .env
    secret_size_factor = os.getenv('SECRET_SIZE_FACTOR') # Secret parameter "secret_size_factor" for unique picture
    secret_seed = os.getenv('SECRET_SEED') # Secret parameter "secret_seed" for unique picture

    # load block data
    block_height = block_heigth or get_latest_block_height()
    block = get_block_data(block_height)
    print(f"start loading block data from block: {block_height}")

    block_hash = block['blocks'][0]['hash']
    block_tx_count = block['blocks'][0]['n_tx']
    block_fee = block['blocks'][0]['fee']
    block_time = block['blocks'][0]['time']
    block_datetime = convert_timestamp_to_datetime(block_time)
    # color_first = '#'+ block_hash[-6:]
    # color_second = neon_color(color_first)
    color_first,color_second = generate_neon_hex_colors(block_hash)
    print(f"finished loading block data from block: {block_height}")

    print(f"start loading transaction data from block: {block_height}")
    # get transaction dataframe for the block
    df_transactions = get_transaction_data(block_height)
    df_transaction_min = min(df_transactions.value_outs_sum_btc)
    df_transaction_max = max(df_transactions.value_outs_sum_btc)
    df_transaction_max = round(df_transaction_max,1)
    print(f"finished loading transaction data from block: {block_height}")

    print(f"start calculation block statistics from block: {block_height}")
    # get transaction values as list in btc
    transaction_values = list(df_transactions.value_outs_sum_btc)
    transaction_fees = list(df_transactions.transaction_fee)
    transaction_fees_median = statistics.median(transaction_fees)
    transaction_values_total = sum(transaction_values)
    sats_vb = round(transaction_fees_median / block_tx_count*10, 0)
    print(f"finished calculation block statistics from block: {block_height}")

    # save all block data in a dictionary
    block_data = {
    'block_hash': block_hash,
    'block_height': block_height,
    'block_tx_count': block_tx_count,
    'block_fee': block_fee,
    'block_time': block_time,
    'block_datetime': block_datetime,
    'color_first': color_first,
    'color_second': color_second,
    'df_transaction_min': df_transaction_min,
    'df_transaction_max': df_transaction_max,
    'transaction_values': transaction_values,
    'transaction_fees': transaction_fees,
    'transaction_fees_median': transaction_fees_median,
    'transaction_values_total': transaction_values_total,
    'sats_vb': sats_vb
    }

    print(f"start generating svg image from block: {block_height}")
    image_svg =create_image_svg_bicolor(
        width = 2500,
        height = 2500,
        color1 = color_first,
        color2 = color_second,
        number_of_circles = block_tx_count,
        block_height = block_height,
        backgroundcolor = '#000000',
        transaction_values = transaction_values,
        size_factor = int(secret_size_factor),
        seed = int(secret_seed)
        )
    print(f"finished generating svg image from block: {block_height}")


    if save_image_svg is True:
        print(f"start saving svg image from block: {block_height}")
        image_svg.saveas(f'images/block_{block_height}.svg')
        print(f"finished saving svg image from block: {block_height}")

    if save_image_png is True:
        print(f"start convertig svg image to png conversion from block: {block_height}")
        input_file_path = f'images/block_{block_height}.svg'
        output_file_path = f'images/block_{block_height}.png'
        svg_to_png_converter(input_file_path,output_file_path)
        print(f"start finished svg image to png conversion from block: {block_height}")


    return block_data


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




def neon_color(hex_color: str) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    r, g, b = min(255, int(r * 1.5)), min(255, int(g * 1.5)), min(255, int(b * 1.5))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)



# def create_image(width: int, height: int, color1: str, color2: str, number_of_circles: int, block_height: int, backgroundcolor: str, transaction_values: list,size_factor: int,seed=None):

#     # Set the seed value for the random number generator
#     if seed:
#         random.seed(seed)

#     color1_rgb = webcolors.hex_to_rgb(color1)
#     color2_rgb = webcolors.hex_to_rgb(color2)
#     backgroundcolor_rgb = webcolors.hex_to_rgb(backgroundcolor)

#     image = Image.new(mode="RGB", size=(width, height), color=backgroundcolor_rgb)

#     center_x = width // 2
#     center_y = height // 2
#     cube_size = width/2.5

#     for i in transaction_values:

#         circle_radius =  get_radius_from_area(i*size_factor)

#         x = center_x + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)
#         y = center_y + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)

#         percent_x = x / width
#         percent_y = y / height
#         percent_x_y = percent_x + percent_y
#         red = color1_rgb[0] + (color2_rgb[0] - color1_rgb[0]) * percent_x_y
#         green = color1_rgb[1] + (color2_rgb[1] - color1_rgb[1]) * percent_x_y
#         blue = color1_rgb[2] + (color2_rgb[2] - color1_rgb[2]) * percent_x_y
#         circle_shape = [
#             (x, y),
#             (x + circle_radius, y + circle_radius)]
#         draw_image = ImageDraw.Draw(image)
#         draw_image.ellipse(circle_shape, fill=(int(red), int(green), int(blue)))

#     return image



def create_image_svg_bicolor(width: int, height: int, color1: str, color2: str, number_of_circles: int, block_height: int, backgroundcolor: str, transaction_values: list, size_factor: int, seed=None):
    if seed:
        random.seed(seed)

    color1_rgb = webcolors.hex_to_rgb(color1)
    color2_rgb = webcolors.hex_to_rgb(color2)
    backgroundcolor_rgb = webcolors.hex_to_rgb(backgroundcolor)

    dwg = Drawing(size=(width, height))

    # Create a black background rectangle
    dwg.add(dwg.rect((0,0), (width,height), fill='black'))
    
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
        red = int(min(255,max(0,color1_rgb[0] + (color2_rgb[0] - color1_rgb[0]) * percent_x_y)))
        green = int(min(255,max(0,color1_rgb[1] + (color2_rgb[1] - color1_rgb[1]) * percent_x_y)))
        blue = int(min(255,max(0,color1_rgb[2] + (color2_rgb[2] - color1_rgb[2]) * percent_x_y)))
        circle_color = webcolors.rgb_to_hex((red, green, blue))
        # circle = Circle(center=(x, y), r=circle_radius, fill=circle_color, fill_opacity= transparency/100)
        # dwg.add(circle)

                # Calculate the distance of the circle from the center
        distance_from_center = math.sqrt((center_x - x)**2 + (center_y - y)**2)

        # Adjust the opacity of the circle based on the distance from the center
        if distance_from_center <= cube_size/2:
            # For circles in the middle, use a higher opacity
            opacity = 0.80
        else:
            # For circles further away from the center, use a lower opacity
            opacity = 0.90

        circle = Circle(center=(x, y), r=circle_radius, fill=circle_color, opacity=opacity)
        dwg.add(circle)
        
    dwg.add(dwg.text(f'BLOCK  {str(block_height)}', insert=(width-200, height-50), fill='#36454F', font_size=20,font_family='Helvetica'))
    dwg.add(dwg.text(f'Designed by bitcoinblockart', insert=(width-200, height-30), fill='#36454F', font_size=11.2,font_family='Helvetica'))

    return dwg


# def create_image_svg_gradient(width: int, height: int, color: str, number_of_circles: int, block_height: int, backgroundcolor: str, transaction_values: list, size_factor: int, transparency: int = 100, seed=None):
#     if seed:
#         random.seed(seed)

#     color_rgb = webcolors.hex_to_rgb(color)
#     backgroundcolor_rgb = webcolors.hex_to_rgb(backgroundcolor)

#     dwg = Drawing(size=(width, height))
#     dwg.add(dwg.rect((0,0), (width,height), fill=backgroundcolor))
    
#     center_x = width // 2
#     center_y = height // 2
#     cube_size = width/2.5

#     # Create a radial gradient definition
#     gradient = dwg.defs.add(dwg.radialGradient(id="gradient"))
#     gradient.add_stop_color(offset="100%", color=color, opacity=1.0)
#     gradient.add_stop_color(offset="100%", color=color, opacity=1.0)
#     gradient.focal_point = "100%"

#     for i in transaction_values:
#         circle_radius =  get_radius_from_area(i*size_factor)

#         x = center_x + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)
#         y = center_y + random.uniform(-cube_size+circle_radius, cube_size-circle_radius)

#         # Calculate the distance of the circle from the center
#         distance_from_center = math.sqrt((center_x - x)**2 + (center_y - y)**2)

#         # Use the gradient as the fill color for the circle
#         circle_color = "url(#gradient)"

#         # Adjust the opacity of the gradient based on the distance from the center
#         if distance_from_center <= cube_size/2:
#             # For circles in the middle, use a higher opacity
#             gradient.add_stop_color(offset="100%", color=color, opacity=0.8)
#             gradient.add_stop_color(offset="100%", color=color, opacity=0.8)
#         else:
#             # For circles further away from the center, use a lower opacity
#             gradient.add_stop_color(offset="100%", color=color, opacity=0.2)
#             gradient.add_stop_color(offset="100%", color=color, opacity=0.2)

#         circle = Circle(center=(x, y), r=circle_radius, fill=circle_color)
#         dwg.add(circle)

#     return dwg


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


def generate_gif(folder_path):
    frames = []
    # Get all file names in the specified folder
    file_names = os.listdir(folder_path)
    file_names.sort()
    # Load each image and add it to the frames list
    for file_name in file_names:
        if file_name.endswith(".jpg"):
            file_path = os.path.join(folder_path, file_name)
            frames.append(Image.open(file_path))
    # Save the frames as an animated GIF
    frames[0].save('animated.gif', format='gif', save_all=True, append_images=frames[1:])


def tweet_with_picture(text, picture, user=None):
    load_dotenv('.env')
    consumer_key = os.getenv('APIKEY')
    consumer_secret = os.getenv('APIKEYSECRET')
    access_token = os.getenv('ACCESSTOKEN')
    access_token_secret = os.getenv('ACCESSTOKENSECRET')
    bearertoken = os.getenv('APIBEARERTOKEN')

    client = tweepy.Client(bearertoken,consumer_key,consumer_secret,access_token,access_token_secret)
    auth = tweepy.OAuth1UserHandler(consumer_key,consumer_secret,access_token,access_token_secret)
    api = tweepy.API(auth)
    media = api.media_upload(picture)
    media_id = media.media_id_string

    if user:
        text = f"{text} @{user}"
    client.create_tweet(text=text, media_ids=[media_id])



def svg_to_png_converter(input_file_path,output_file_path):
    # read svg -> write png
    renderPM.drawToFile(svg2rlg(input_file_path), output_file_path, fmt='PNG')




def generate_neon_hex_colors(seed):
    '''Generates two harmonic neon hex colors and takes a 6 character hex number as input for a seed generation and returns 2 hex neon color.'''

    # Convert seed to int
    seed = int(seed[-6:], 16) #we use the bicoin hash as the seed to generate a unique color

    # Generate two random numbers from the seed
    rand1 = (seed * 2) % 0xFFFFFF
    rand2 = (seed * 3) % 0xFFFFFF

    # Create two harmonic colors from the random numbers
    color1 = '#{:06x}'.format(rand1)
    color2 = '#{:06x}'.format(rand2)

    # Return the two colors as a tuple
    return (color1, color2)