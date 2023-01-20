from functions import *
import random

def run():
    # Store the current block height
    current_block_height = 11 #get_latest_block_height()

    while True:
        # Get the latest block height
        latest_block_height = get_latest_block_height()

        # Check if a new block has been generated
        if latest_block_height > current_block_height:
            print("A new block has been generated! Block height:", latest_block_height)
            current_block_height = latest_block_height

            #colormode = random.choice([True,False])
            colormode = True

            # generate svg and png image and return block statistics
            block_data = blockimage_generator(save_image_svg = True, save_image_png = True, block_heigth = current_block_height,color=colormode)

            # post on twitter
            input_file_path = f'images/block_{current_block_height}.svg'
            output_file_path = f'images/block_{current_block_height}.png'

            block_datetime = block_data['block_datetime']
            block_date = block_data['block_datetime'].strftime("%Y-%m-%d")
            block_time = block_data['block_datetime'].strftime("%H:%M:%S")
            block_tx_count = block_data['block_tx_count']
            df_transaction_max = block_data['df_transaction_max']
            transaction_values_total = block_data['transaction_values_total']
            sats_vb = block_data['sats_vb']

            text = f'A new bitcoin block {current_block_height} was mined on {block_date} at {block_time} with a total of {block_tx_count} transactions. The total value of all transactions was {transaction_values_total} BTC. The highest single transaction was {df_transaction_max} BTC. The average fee was {sats_vb} sats/Vb.'
            try:
                tweet_with_picture(text, output_file_path, user='bitcoinblockart',hashtags=['bitcoin'])
            except Exception:
                pass
            time.sleep(10)

        print("Not a new block waiting 60s before next check")

        # Wait for 30 minute before checking again
        time.sleep(30)
        whipe_folder()
        time.sleep(20)

if __name__ == "__main__":
    print("Start Programm:")
    run()
    print("End Programm:")



