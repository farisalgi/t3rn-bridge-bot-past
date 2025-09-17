from web3 import Web3
from eth_account import Account
import time
import os
from decimal import Decimal
import random
from keys_and_addresses import private_keys, my_addresses, labels
from network_config import networks

# Function to center text in the terminal
def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    return "\n".join(line.center(terminal_width) for line in lines)

# Function to clear the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Explorer URLs for transaction links
def get_explorer_url(name):
    base_urls = {
        'OP Sepolia': 'https://sepolia.arbiscan.io/tx/',
        'Base Sepolia': 'https://unichain-sepolia.blockscout.com/tx/',
        'BRN': 'https://b2n.explorer.caldera.xyz/tx/'
    }
    return base_urls.get(name, '')

# Function to get ETH balance
def get_balance(web3, address):
    bal = web3.eth.get_balance(address)
    return web3.from_wei(bal, 'ether')

# Check and switch direction based on balances
def check_and_switch_bridge(current, web3_from, web3_to, addr, amount_from, amount_to, threshold=Decimal('1')):
    while True:
        bal_from = get_balance(web3_from, addr)
        bal_to = get_balance(web3_to, addr)
        print(f"[Bridge] From Balance: {bal_from} ETH | To Balance: {bal_to} ETH")
        if bal_from <= threshold and bal_to <= threshold:
            print(f"Both balances below threshold {threshold}. Waiting 10 minutes...")
            time.sleep(600)
            continue
        # If current direction still viable
        if current == 'FROM->TO' and bal_from - amount_from >= threshold:
            return current
        elif current == 'TO->FROM' and bal_to - amount_to >= threshold:
            return current
        # Else switch if opposite direction viable
        if current == 'FROM->TO' and bal_to - amount_to >= threshold:
            print("Switching to TO->FROM")
            return 'TO->FROM'
        elif current == 'TO->FROM' and bal_from - amount_from >= threshold:
            print("Switching to FROM->TO")
            return 'FROM->TO'
        print("No viable direction. Waiting 10 minutes...")
        time.sleep(600)

# Send transaction with retry logic
def send_transaction(web3, account, addr, data, cfg, value):
    retries, delay = 5, 60
    for i in range(retries):
        nonce = web3.eth.get_transaction_count(addr, 'pending')
        val_wei = web3.to_wei(value, 'ether')
        try:
            gas_est = web3.eth.estimate_gas({'to': cfg['contract_address'], 'from': addr, 'data': data, 'value': val_wei})
            gas_lim = gas_est + 1
        except Exception as e:
            print(f"Gas estimation error: {e}")
            return None, None
        block = web3.eth.get_block('latest')
        base_fee = block['baseFeePerGas']
        pri_fee = web3.to_wei(1, 'gwei')
        max_fee = base_fee + pri_fee
        txn = {
            'nonce': nonce,
            'to': cfg['contract_address'],
            'value': val_wei,
            'gas': gas_lim * 2,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': pri_fee,
            'chainId': cfg['chain_id'],
            'data': data
        }
        try:
            signed = account.sign_transaction(txn)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            rec = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"TX sent: {web3.to_hex(tx_hash)} | Gas used: {rec['gasUsed']} | Block: {rec['blockNumber']}")
            return web3.to_hex(tx_hash), value
        except Exception as e:
            msg = str(e).lower()
            if 'rate limit' in msg or 'ro#7' in msg:
                print(f"Rate limit hit. Retry {i+1}/{retries} in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error: {e}")
                return None, None
    print("Exceeded retries. TX failed.")
    return None, None

# Main logic
def main():
    clear_terminal()
    # Select mode
    print("Select mode:")
    print("1. Single network")
    print("2. Automatic swap between two networks")
    mode = None
    while mode not in ('1', '2'):
        mode = input("Enter mode (1 or 2): ")

    names = list(networks.keys())
    for idx, name in enumerate(names, 1):
        print(f"{idx}. {name}")

    if mode == '1':
        choice = int(input("Select network by number: ")) - 1
        sel_net = names[choice]
        web3 = Web3(Web3.HTTPProvider(networks[sel_net]['rpc_url']))
        data_hex = input(f"Enter the data payload for transactions on {sel_net}: ")
    else:
        print("Select first network (FROM):")
        frm = int(input("Number: ")) - 1
        print("Select second network (TO):")
        to = int(input("Number: ")) - 1
        net_from = names[frm]
        net_to = names[to]
        web3_from = Web3(Web3.HTTPProvider(networks[net_from]['rpc_url']))
        web3_to = Web3(Web3.HTTPProvider(networks[net_to]['rpc_url']))
        data_from = input(f"Enter data payload for {net_from} -> {net_to}: ")
        data_to = input(f"Enter data payload for {net_to} -> {net_from}: ")
        print("Select initial direction:")
        print("1. FROM->TO")
        print("2. TO->FROM")
        dir_choice = input("Choice (1 or 2): ")
        current = 'FROM->TO' if dir_choice == '1' else 'TO->FROM'

    # Common inputs
    try:
        amount = Decimal(input("Enter transaction amount in ETH: "))
        total_txs = int(input("Enter desired number of successful transactions: "))
    except Exception:
        print("Invalid input.")
        return

    successful = 0

    if mode == '1':
        account = Account.from_key(private_keys[0])
        addr = my_addresses[0]
        cfg = networks[sel_net]
        while successful < total_txs:
            if not web3.is_connected():
                print(f"Cannot connect to {sel_net}")
                break
            bal = get_balance(web3, addr)
            print(f"[{sel_net}] Current balance: {bal} ETH")
            print(f"Sending transaction #{successful+1} on {sel_net} with amount {amount} ETH")
            tx, val = send_transaction(web3, account, addr, data_hex, cfg, amount)
            if tx:
                successful += 1
            time.sleep(random.uniform(1, 3))
    else:
        account = Account.from_key(private_keys[0])
        addr = my_addresses[0]
        while successful < total_txs:
            current = check_and_switch_bridge(current, web3_from, web3_to, addr, amount, amount)
            if current == 'FROM->TO':
                web3 = web3_from; cfg = networks[net_from]; data = data_from; direction = f"{net_from}->{net_to}"
            else:
                web3 = web3_to; cfg = networks[net_to]; data = data_to; direction = f"{net_to}->{net_from}"
            bal = get_balance(web3, addr)
            print(f"[{direction}] Current balance: {bal} ETH")
            print(f"Attempting {direction} (#{successful+1}) amount {amount} ETH")
            tx, val = send_transaction(web3, account, addr, data, cfg, amount)
            if tx:
                successful += 1
            time.sleep(random.uniform(1, 3))

if __name__ == '__main__':
    main()