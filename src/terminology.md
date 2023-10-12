# Terminology

Prior to providing the [Overview](./overview.md), [Design Specification](./design-specification.md) and other sections, we present our terminology. If you prefer to learn terms in the conceptual flow, jump ahead to the [Overview](./overview.md) and refer back as necessary.

We rely on terms of art specific to this book. A word of caution that in some cases we use similar terms from elsewhere in the blockchain consensus field with distinct meanings specific to this book and different from other uses, for example *validator*.

## Terms

<span id="definition-assured-finality"></span>**Assured Finality**: A protocol property that guarantees that some transactions cannot be reverted by that protocol. As with all protocol guarantees, a protocol assumes certain conditions must be met. A transaction may either be final or not: transactions which are not final may not become final, whereas once transactions do achieve finality they retain that property indefinitely (so long as protocol requirements are met).

Importantly, it is not feasible for any protocol to prevent reversing final transactions "out of band" from the protocol, such as if a sufficiently large and motivated group of users forks the network to include a specific new validity rule reverting transactions. For this reason, we forego the term "absolute finality" sometimes used in consensus protocol technical discussions.

<span id="definition-final"></span>**Final**: A protocol property of transactions. In this book, this always implies [assured finality](#definition-assured-finality), in contrast to concepts like "probabilistic finality" provided by [PoW](#definition-pow).

<span id="definition-trailing-finality"></span>**Trailing Finality**: A protocol property wherein transactions become final some time after first appearing in [PoW](#definition-pow) blocks.

<span id="definition-pow-tfl"></span>**PoW+TFL**: the overall complete, integrated consensus protocol specified in this book.

<span id="definition-nu5"></span>**NU5**: The Zcash consensus protocol as of NU5.[^new-mainnet-precursors]

<span id="definition-pow"></span>**Proof-of-Work**: A PoW protocol uses Nakamoto consensus pioneered by Bitcoin. The PoW subprotocol within PoW+TFL is a different consensus protocol from [NU5](#definition-nu5) and encompasses more than narrow Nakamoto PoW consensus, including transaction semantics such as for shielded transfers.

*TODO*: Clarify the distinctions between PoW (general consensus), [NU5](#definition-nu5) which includes transaction semantics, and the PoW component of [PoW-TFL](#definition-pow-tfl). These distinctions deserve unique terms.

<span id="definition-tfl"></span>**TFL**: The *Trailing Finality Layer* subprotocol within PoW+TFL. This is a new [PoS](#definition-pos) subprotocol which provides [assured finality](#definition-assured-finality) for Zcash.

<span id="definition-pos"></span>**Proof-of-Stake**: A PoS protocol achieves consensus on transaction status via taking into account the weighting of staking tokens. PoS protocols fall into a large umbrella and may or may not provide [assured finality](#definition-assured-finality) or other properties this design requires of [TFL](#definition-tfl).

<span id="definition-hybrid-consensus"></span>**Hybrid Consensus**: A consensus protocol which integrates more than one consensus subprotocol. [PoW+TFL](#definition-pow-tfl) is an instance of a hybrid protocol integrating [PoW](#definition-pow) and [PoS](#definition-pos) protocols.

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to PoW+TFL design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)
