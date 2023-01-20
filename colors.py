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


color1, color2 = generate_neon_hex_colors('00000000000000000004e796b40567cafbad5c0c2ac19a40f072aae99c6e4e29')

print(color1)
print(color2)
