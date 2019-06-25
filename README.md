# Python Blockchain Parser
## Instructions
To correctly clone the submodule, use `git clone --recursive` instead of the standard `git clone`

## Assignment
Develop a web app that works on Bitcoin Blockchain that works as follows:
- It proposes a webpage with an input form that requires to enter a transaction ID
- It searches in the blockchain the block that contains that transaction and shows: the input transactions, the output transactions, the signature of the transaction
- optional: it checks if a transaction has done double spending: How to do it? Suppose the transaction uses i1, i2, ..., in as inputs. You must find the inputs specified as output of a previous transaction and check along the way that those outputs have not been used as inputs of other transactions.

Resources: 

- The bitcoin blockchain can be downloaded by torrent from: https://getbitcoinblockchain.com
- Alternatively, the miner software https://bitcoin.org/en/ that automatically download the blockchain (can be stopped before the end)
- The Python library: https://github.com/alecalve/python-bitcoin-blockchain-parser

It is highly recommended to develop the project by using Python.
