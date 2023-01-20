from functions import *

current_block_height = get_latest_block_height()

block_data = blockimage_generator(save_image_svg = True, save_image_png = True, block_heigth = current_block_height,color=False)

print(block_data['block_datetime'])
print(block_data['block_tx_count'])
print(block_data['df_transaction_max'])
print(block_data['transaction_values_total'])
print(block_data['sats_vb'])

print(block_data['block_datetime'].strftime("%Y-%m-%d"))
