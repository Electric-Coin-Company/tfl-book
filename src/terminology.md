# Terminology

Prior to providing the [Overview](./overview.md), [Design Specification](./design-specification.md) and other sections, we present our terminology. If you prefer to learn terms in the conceptual flow, jump ahead to the [Overview](./overview.md) and refer back as necessary.

We rely on terms of art specific to this book. A word of caution that in some cases we use similar terms from elsewhere in the blockchain consensus field with distinct meanings specific to this book and different from other uses, for example *validator*.

We group terms into related categories as follows:

## Protocol Concepts

<span id="definition-assured-finality"></span>**Assured Finality**: A protocol property that guarantees that final transactions cannot be reverted by that protocol. As with all protocol guarantees, a protocol assumes certain conditions must be met.

Importantly, it is not feasible for any protocol to prevent reversing final transactions "out of band" from the protocol, such as if a sufficiently large and motivated group of users forks the network to include a specific new validity rule reverting transactions. For this reason, we forego the term "absolute finality" sometimes used in consensus protocol technical discussions.

## Protocol Components

<span id="definition-pow-tfl"></span>**PoW+TFL**: the overall complete, integrated consensus protocol specified in this book.

<span id="definition-pow"></span>**PoW**: the PoW subprotocol within [PoW+TFL](./terminology.md#definition-pow-tfl). Note that this is a different consensus protocol from [NU5](#definition-nu5) and encompasses more than narrow Nakamoto PoW consensus, including transaction semantics such as for shielded transfers.

<span id="definition-tfl"></span>**TFL**: the *Trailing Finality Layer* subprotocol within [PoW+TFL](./terminology.md#definition-pow-tfl).

<span id="definition-nu5"></span>**NU5**: the Zcash consensus protocol as of NU5.[^new-mainnet-precursors]

## Infrastructure Roles

These are roles of infrastructure components (not human users). Keep in mind a given product or service may fill multiple roles, for example a wallet application may provide *validator*, *wallet viewer*, and *wallet spender* roles to provide users with safe access to private funds.


<span id="definition-validator"></span>**Validator**: a component which locally verifies the correctness of consensus. This includes verifying that the local view of chain history matches consensus requirements, encompassing block tip selection, block validity, and transaction validity.[^validator-distinction]

<span id="definition-block-proposer"></span>**Block Proposer**: a component which proposes a block of transactions to the network. If accepted by network consensus, this block extends the consensus state of the ledger.

<span id="definition-pow-proposer"></span>**PoW Proposer**: a Block Proposer which uses PoW as the proposal mechanism. In [NU5](#definition-nu5) and [PoW+TFL](./terminology.md#definition-pow-tfl), the only Block Proposers are PoW Proposers. In practice, PoW Proposers are typically mining pools, although a solo miner is also a PoW Proposer. We use this term to be more precise than the common term "miner" which can conflate this role with the following.

<span id="definition-pow-hashrate-provider"></span>**PoW Hashrate Provider**: a component which contributes mining resources towards PoW block proposals. In practice, mining pools rely on a userbase of Hashrate Providers to scale their operation, and solo miners have this capacity "in-house".

<span id="definition-block-finalizer"></span>**Block Finalizer**: a component which contributes to consensus progress on the *finality* of a block.

<span id="definition-wallet-viewer"></span>**Wallet Viewer**: a component which provides a view into the history of funds for particular addresses, given appropriate *viewing keys*. This history may include both transparent and private details.

<span id="definition-wallet-spender"></span>**Wallet Spender**: a component that enables generating new transactions which transfer funds to recipients.

## Blockchain State


<span id="definition-transaction"></span>**Transaction**: a modification of the ledger, issued (by definition) by a Wallet Spender. A transaction cannot become part of the consensus ledger unless all Validators would accept it as valid according to *Transaction Validity Rules*.

<span id="definition-block"></span>**Block**: **\[TODO\]**

<span id="definition-block-history"></span>**Block History**: **\[TODO\]** _(nodes can see multiple local histories and select one as canonical according to consensus)

<span id="definition-pending-blocks"></span>**Pending Blocks**: **\[TODO\]**

<span id="definition-pending-transactions"></span>**Pending Transactions**: **\[TODO\]**

<span id="definition-final-blocks"></span>**Final Blocks**: **\[TODO\]**

<span id="definition-final-transactions"></span>**Final Transactions**: **\[TODO\]**

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to [PoW+TFL](./terminology.md#definition-pow-tfl) design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)

[^validator-distinction]: Our use of the term "validator" deviates from common industry usage. Our usage focuses on literally validating consensus state, and does not imply any participation in maintaining the network or extending the ledger. This is distinct from widespread usage of "validator" to include the role or responsibility of proposing new blocks or achieving network consensus on ledger updates.
