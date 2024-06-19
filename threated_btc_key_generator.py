import os
import threading
from mnemonic import Mnemonic
import bip32utils
import sys

# Lock for thread-safe file writing
lock = threading.Lock()

# Function to generate a single mnemonic
def generate_mnemonic(length):
    mnemo = Mnemonic("english")
    entropy = os.urandom(length // 8)
    return mnemo.to_mnemonic(entropy)

# Function to generate a private key from a mnemonic
def generate_private_key(mnemonic):
    seed = Mnemonic.to_seed(mnemonic)
    master_key = bip32utils.BIP32Key.fromEntropy(seed)
    private_key = master_key.PrivateKey().encode('hex')
    return private_key

# Function to generate multiple mnemonics
def generate_mnemonics(count, length):
    return [generate_mnemonic(length) for _ in range(count)]

# Function to generate private keys from mnemonics
def generate_private_keys(mnemonics):
    return [generate_private_key(mnemonic) for mnemonic in mnemonics]

# Function to write keys to file
def write_keys_to_file(keys):
    with lock:  # Ensure thread-safe file writing
        with open('keys.txt', 'a') as f:
            for key in keys:
                f.write(key + '\n')

# Worker function to generate and save keys
def worker(mnemonic_chunk):
    try:
        keys = generate_private_keys(mnemonic_chunk)
        write_keys_to_file(keys)
    except Exception as e:
        print >> sys.stderr, "Error in worker: {}".format(e)

if __name__ == "__main__":
    try:
        # Get user input
        num_words = int(raw_input("Enter the number of words for mnemonic (12 or 24): "))
        if num_words not in [12, 24]:
            raise ValueError("Number of words must be 12 or 24")

        num_mnemonics = int(raw_input("Enter the number of mnemonics to generate: "))
        if num_mnemonics <= 0:
            raise ValueError("Number of mnemonics must be a positive integer")

        length = 128 if num_words == 12 else 256

        # Generate mnemonics
        mnemonics = generate_mnemonics(num_mnemonics, length)

        # Split mnemonics into chunks for threading
        num_threads = 4
        chunk_size = len(mnemonics) // num_threads
        chunks = [mnemonics[i:i + chunk_size] for i in range(0, len(mnemonics), chunk_size)]

        # Handle case where mnemonics are not evenly divisible by num_threads
        if len(mnemonics) % num_threads != 0:
            chunks[-1].extend(mnemonics[num_threads * chunk_size:])

        threads = []

        # Create and start threads
        for chunk in chunks:
            thread = threading.Thread(target=worker, args=(chunk,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        print "Generated and saved {} private keys.".format(num_mnemonics)
    
    except ValueError as e:
        print >> sys.stderr, "Input error: {}".format(e)
    except Exception as e:
        print >> sys.stderr, "An unexpected error occurred: {}".format(e)
