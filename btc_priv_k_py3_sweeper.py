from bit import PrivateKey
from bit.network import NetworkAPI

def sweep_keys(input_file, destination_address):
    with open(input_file, 'r') as file:
        private_keys = file.readlines()

    for key in private_keys:
        key = key.strip()
        try:
            priv_key = PrivateKey.from_hex(key)
            balance = priv_key.get_balance('btc')
            
            if float(balance) > 0:
                print(f"Private key {key} has balance {balance} BTC")
                tx = priv_key.create_transaction([(destination_address, balance, 'btc')])
                NetworkAPI.broadcast_tx(tx)
                print(f"Sent {balance} BTC from {priv_key.address} to {destination_address}")
            else:
                print(f"Private key {key} has no balance")
        except Exception as e:
            print(f"Error with key {key}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python sweep_keys.py keys.txt destination_address")
    else:
        input_file = sys.argv[1]
        destination_address = sys.argv[2]
        sweep_keys(input_file, destination_address)
