# Terminology

Prior to providing the [Overview](./overview.md), [Design Specification](./design-specification.md) and other sections, we present our terminology. If you prefer to learn terms in the conceptual flow, jump ahead to the [Overview](./overview.md) and refer back as necessary.

We rely on terms of art specific to this book. A word of caution that in some cases we use similar terms from elsewhere in the blockchain consensus field with distinct meanings specific to this book and different from other uses, for example *validator*.

We group terms into related categories as follows:

## Protocol Components

- *PoW+TFL*: the overall complete, integrated consensus protocol specified in this book.
- *NU5*: the Zcash consensus protocol as of NU5.[^new-mainnet-precursors]
- *PoW*: the PoW subprotocol within PoW+TFL. Note that this is a different consensus protocol from NU5 and encompasses more than narrow Nakamoto PoW consensus, including transaction semantics such as for shielded transfers.
- *TFL*: the *Trailing Finality Layer* subprotocol within PoW+TFL.

## Infrastructure Roles

These are roles of infrastructure components (not human users). Keep in mind a given product or service may fill multiple roles, for example a wallet application may provide *validator*, *wallet viewer*, and *wallet spender* roles to provide users with safe access to private funds.

- *Validator*: a component which locally verifies the correctness of consensus. This includes verifying that the local view of chain history matches consensus requirements, encompassing block tip selection, block validity, and transaction validity.[^validator-distinction]
- *Block Proposer*: a component which proposes a block of transactions to the network. If accepted by network consensus, this block extends the consensus state of the ledger.
- *PoW Proposer*: a Block Proposer which uses PoW as the proposal mechanism. In NU5 and PoW+TFL, the only Block Proposers are PoW Proposers. In practice, PoW Proposers are typically mining pools, although a solo miner is also a PoW Proposer. We use this term to be more precise than the common term "miner" which can conflate this role with the following:
- *PoW Hashrate Provider*: a component which contributes mining resources towards PoW block proposals. In practice, mining pools rely on a userbase of Hashrate Providers to scale their operation, and solo miners have this capacity "in-house".
- *Block Finalizer*: a component which contributes to consensus progress on the *finality* of a block.
- *Wallet Viewer*: a component which provides a view into the history of funds for particular addresses, given appropriate *viewing keys*. This history may include both transparent and private details.
- *Wallet Spender*: a component that enables generating new transactions which transfer funds to recipients.

## Blockchain State

- *Transaction*: a modification of the ledger, issued (by definition) by a Wallet Spender. A transaction cannot become part of the consensus ledger unless all Validators would accept it as valid according to *Transaction Validity Rules*.
- *Block*: **\[TODO\]**
- *Block History*: **\[TODO\]** _(nodes can see multiple local histories and select one as canonical according to consensus)
- *Pending Blocks*: **\[TODO\]**
- *Pending Transactions*: **\[TODO\]**
- *Final Blocks*: **\[TODO\]**
- *Final Transactions*: **\[TODO\]**

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to PoW+TFL design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)

[^validator-distinction]: Our use of the term "validator" deviates from common industry usage. Our usage focuses on literally validating consensus state, and does not imply any participation in maintaining the network or extending the ledger. This is distinct from widespread usage of "validator" to include the role or responsibility of proposing new blocks or achieving network consensus on ledger updates.
