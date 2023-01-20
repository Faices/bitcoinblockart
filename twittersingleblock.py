from functions import *

# Store the current block height
current_block_height = 772795 #get_latest_block_height()

while True:
    # Get the latest block height
    latest_block_height = get_latest_block_height()

    # Check if a new block has been generated
    if latest_block_height > current_block_height:
        print("A new block has been generated! Block height:", latest_block_height)
        current_block_height = latest_block_height

        # generate svg image
        blockimage_generator(save_image_svg = True, block_heigth = current_block_height)
        time.sleep(5)

        # convert png image
        input_file_path = f'images/block_{current_block_height}.svg'
        output_file_path = f'images/block_{current_block_height}.png'
        svg_to_png_converter(input_file_path=input_file_path,output_file_path=output_file_path)
        time.sleep(5)
        
        # post on twitter
        text = 'test'
        tweet_with_picture(text, output_file_path, user=None)

    print("Not a new block waiting 60s before next check")
    
    # Wait for 1 minute before checking again
    time.sleep(60)



