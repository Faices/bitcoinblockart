from functions import *
import sys
import dotenv
import statistics

def run(save_image = False, block_heigth = None):

    load_dotenv('.env')

    # load insta username and password
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    secret_size_factor = os.getenv('SECRET_SIZE_FACTOR') # Secret parameter "secret_size_factor" for unique picture
    secret_seed = os.getenv('SECRET_SEED') # Secret parameter "secret_seed" for unique picture

    # load specific block / to load latest just leave "None"
    block_heigth = block_heigth

    # load block
    if block_heigth is None:
        # code to run if variable is None
        block = get_block_data(get_latest_block_height())
        print("loaded newest block")
    else:
        # code to run if variable is not None
        block = get_block_data(block_heigth)
        print(f"loaded block {block_heigth}")


    # extract main values
    block_hash = block['blocks'][0]['hash']
    block_height = block['blocks'][0]['height']
    block_tx_count = block['blocks'][0]['n_tx']
    block_fee = block['blocks'][0]['fee']
    block_time = block['blocks'][0]['time']
    block_datetime = convert_timestamp_to_datetime(block_time)
    print(block_datetime)

    color_first = '#'+ block_hash[-6:]
    print("first color: ",color_first)
    color_second = generate_second_color(color_first,seed=21)
    print("second color: ",color_second)

    # get transaction dataframe for the block
    df_transactions = get_transaction_data(block_height)
    df_transaction_min = min(df_transactions.value_outs_sum_btc)
    df_transaction_max = max(df_transactions.value_outs_sum_btc)
    df_transaction_max = round(df_transaction_max,1)
    print(df_transaction_min,'=',df_transaction_max)

    # get transaction values as list in btc
    transaction_values = list(df_transactions.value_outs_sum_btc)
    transaction_fees = list(df_transactions.transaction_fee)
    transaction_fees_median = statistics.median(transaction_fees)
    sats_vb = transaction_fees_median / block['blocks'][0]['n_tx']*10
    sats_vb = round(sats_vb, 0)
    print(transaction_fees_median)
    print(sats_vb)


    # create image
    image = create_image(
        width = 9504,
        height = 9504,
        color1 = color_first,
        color2 = color_second,
        number_of_circles = block_tx_count,
        block_height = block_height,
        backgroundcolor = '#000000',
        transaction_values = transaction_values,
        size_factor = int(secret_size_factor),
        seed = int(secret_seed),
        )
    if save_image is True:
        image.save(f'images/block_{block_height}.jpg')


    # create instagram caption
    caption = caption = f'#Bitcoin Block {block_height} at {block_datetime} had {block_tx_count} transactions and a average fee of ~ {sats_vb} sats/vB. The biggest transfer of a single transaction was {df_transaction_max} Bitcoin.'
    print(caption)

    # post on instagram
    # post_image_on_instagram(image=image, caption=caption,username=username,password=password)

if __name__ == "__main__":
    print("Start Programm:")
    run(block_heigth=200,save_image=True)
    print("End Programm:")
