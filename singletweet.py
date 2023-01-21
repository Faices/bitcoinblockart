from functions import *
import random


current_block_height = 771934 #get_latest_block_height()

#colormode = random.choice([True,False])
colormode = False

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

user = 'fabthefoxx'
#text = f'A new bitcoin block {current_block_height} was mined on {block_date} at {block_time} with a total of {block_tx_count} transactions. The total value of all transactions was {transaction_values_total} BTC. The highest single transaction was {df_transaction_max} BTC. The average fee was {sats_vb} sats/Vb.'
text = f'A special block for a special occasion! congratulations @{user}, J. & M.'
try:
    tweet_with_picture(text, output_file_path, user='bitcoinblockart',hashtags=['bitcoin','hope'])
except Exception:
    pass


print("Not a new block waiting 60s before next check")




