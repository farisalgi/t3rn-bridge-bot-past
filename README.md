# t3rn Transaction Bot

This project provides a Python-based bot to automate t3rn testnet transactions across multiple test networks (Sepolia variants, Blast, SEI, etc.). It supports both **single-network transactions** and **automatic bidirectional bridging** between two networks, with built-in balance checks, retry logic, and transaction monitoring.

---

## Features

- **Single-Network Mode**  
  Send repeated transactions on a chosen network with custom payloads.

- **Automatic Bridge Mode**  
  Swap transactions between two networks with direction switching based on available balances.

- **Retry Logic**  
  Automatic retries with exponential backoff on failed transactions or RPC rate limits.

- **Balance Monitoring**  
  Prevents sending transactions when balances are below the defined threshold.

- **Customizable Network Config**  
  Easily extend supported testnets via `network_config.py`.

---

## Project Structure

```
.
├── t3rn-bot.py            # Main bot script with transaction logic
├── keys_and_addresses.py  # Wallet private keys, addresses, and labels
└── network_config.py      # Network RPC endpoints, chain IDs, and contracts
```

---

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/t3rn-bot.git
   cd t3rn-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install web3 eth-account
   ```

3. **Set up your configuration:**

   - In `keys_and_addresses.py`, add your wallet’s **private key** and **address**.
   - In `network_config.py`, set your RPC URLs for the desired networks.

---

## Usage

### Run the bot
```bash
python t3rn-bot.py
```

You will be prompted to choose between:

1. **Single Network Mode**  
   - Select a network.  
   - Enter data payload (hex string).  
   - Enter transaction amount and number of transactions.

2. **Automatic Swap Mode**  
   - Select FROM and TO networks.  
   - Enter payloads for both directions.  
   - Choose initial direction.  
   - Enter transaction amount and number of transactions.

---

## Example Workflow

**Single Network Example:**
- Select: `Arbitrum Sepolia`  
- Enter payload: `0x1234abcd...`  
- Amount: `0.01 ETH`  
- Transactions: `5`  

The bot will send 5 transactions sequentially on Arbitrum Sepolia.

**Automatic Bridge Example:**
- FROM: `OP Sepolia`  
- TO: `Base Sepolia`  
- Payloads: `0x...` (each direction)  
- Initial Direction: `FROM->TO`  
- Amount: `0.02 ETH`  
- Transactions: `10`  

The bot will alternate directions when balances reach the defined threshold.

---

## How to obtain the transaction payload (hex `data` / input)

The bot expects a **hex payload** (the `data` / `input` field of an Ethereum transaction) when you are asked to enter the "data payload". If you don't already have the payload, use one of these quick ways to obtain it after making a test transaction from your wallet or dApp UI (for example: sending a transaction via t3rn, a contract UI, or a wallet).

### 1) From MetaMask (or similar browser wallets)
1. Send the test transaction in MetaMask (make sure it's a testnet transaction).  
2. On the transaction request, Scroll down and copy the hex string shown.  
3. Paste that hex string when the bot asks for the data payload.

### 2) From a block explorer (Etherscan / Blockscout / Caldera Explorer)
1. After sending a transaction, open the explorer for the network (e.g., Sepolia Arbiscan, Blockscout).  
2. Search for your transaction hash (tx hash).  
3. On the transaction page look for **"Input Data"** / **"Hex"** / **"Data"**.  
4. Copy the full `0x...` hex string and paste it into the bot prompt.

---

## Notes

- Make sure your RPC URLs are valid and accessible.
- Always use testnet ETH, **never expose real private keys** in public repositories.
- Default threshold for balance switching is `1 ETH` (configurable in code).

---

## Disclaimer

This project is for **educational and testing purposes only**.  
Do **not** use with mainnet private keys or funds. I'm not responsible for any loss of assets.
