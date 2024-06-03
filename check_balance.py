import ecdsa
import hashlib
import base58
import requests

# Function to generate Bitcoin address from private key
def generate_address_from_private_key(private_key):
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b"\04" + vk.to_string()
    sha256_hash = hashlib.sha256(public_key)
    ripe_hash = hashlib.new('ripemd160', sha256_hash.digest())
    return base58.b58encode_check(b"\x00" + ripe_hash.digest())

# Function to check balance for a Bitcoin address using Blockexplorer API
def check_balance(address):
    try:
        response = requests.get(f"https://blockexplorer.com/api/addr/{address}/balance")
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        balance = float(response.text) / 100000000  # Convert from Satoshi to Bitcoin
        return balance
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e}"
    except Exception as e:
        return f"Error: {e}"

# Read private keys from file
def read_private_keys(filename):
    with open(filename, 'r') as file:
        private_keys = file.readlines()
    # Remove newline characters
    private_keys = [key.strip() for key in private_keys]
    return private_keys

# Main function
def main():
    # File containing private keys
    filename = 'key.txt'
    private_keys = read_private_keys(filename)

    # Iterate over each private key
    for key in private_keys:
        try:
            # Convert private key to bytes
            private_key = bytes.fromhex(key)
            # Generate Bitcoin address from private key
            address = generate_address_from_private_key(private_key)
            # Check balance for the address
            balance = check_balance(address.decode())
            print("Address:", address.decode())
            print("Balance:", balance)
        except Exception as e:
            print("Error:", str(e))
            continue

if __name__ == "__main__":
    main()
