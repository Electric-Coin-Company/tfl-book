# Terminology

This book relies on the following terminology. We strive to keep these definitions as precise as possible and their definitions may deviate from uses elsewhere.

Definitions are sorted alphabetically.

## Terms

<span id="definition-assured-finality">**Assured Finality**</span>: A protocol property that assures that transactions cannot be reverted by that protocol. As with all protocol guarantees, a protocol assumes certain conditions must be met. A transaction may either be final or not: transactions which are not final may not become final, whereas once transactions do achieve finality they retain that property indefinitely (so long as protocol requirements are met).

Importantly, it is not feasible for any protocol to prevent reversing final transactions "out of band" from the protocol, such as if a sufficiently large and motivated group of users forks the network to include a specific new validity rule reverting transactions. In some cases this might be desirable, for example to mitigate exploitation of a security flaw. We are investigating the implications for governance and how to incorporate such situations into our security model. In any case, for this reason we eschew the term "absolute finality" sometimes used in technical discussions about consensus protocols.

<span id="definition-crosslink">**Crosslink**</span>: A hybrid consensus protocol construction striving to implement the [TFL](#definition-tfl) design goals. See [Status and Next Steps: Current Components](./introduction/status-and-next-steps.md#current-components) for current status.

<span id="definition-final">**Final**</span>: A protocol property of transactions. In this book, this always implies [assured finality](#definition-assured-finality), in contrast to concepts like "probabilistic finality" provided by [PoW](#definition-pow).

<span id="definition-hybrid-consensus">**Hybrid Consensus**</span>: A consensus protocol that integrates more than one consensus subprotocol. [PoW+TFL](#definition-pow-tfl) is an instance of a hybrid protocol integrating [PoW](#definition-pow) and [PoS](#definition-pos) protocols.

<span id="definition-liveness">**Liveness**</span>: The property of a distributed protocol which ensures that the protocol may progress provided liveness requirements are met. **TODO:** Fix this definition, which begs the question by failing to define "progress".

<span id="definition-nu5">**NU5**</span>: The Zcash consensus protocol as of NU5.[^new-mainnet-precursors]

<span id="definition-pos">**Proof-of-Stake**</span>: A PoS protocol achieves consensus on transaction status by taking into account the weighting of staking tokens. PoS protocols exist under a large umbrella and may or may not provide [assured finality](#definition-assured-finality) or other properties this design requires of [TFL](#definition-tfl).

<span id="definition-pow">**Proof-of-Work**</span>: A PoW protocol uses Nakamoto consensus pioneered by Bitcoin. The PoW subprotocol within PoW+TFL is a different consensus protocol from [NU5](#definition-nu5) and encompasses more than narrow Nakamoto PoW consensus, including transaction semantics such as for shielded transfers.

<span id="definition-pow-tfl">**PoW+TFL**</span>: the overall complete, integrated consensus protocol specified in this book.

<span id="definition-safety">**Safety**</span>: The property of a distributed protocol that guarantees a participant may safely rely on a consistent local state, provided safety requirements are met. **TODO:** Fix this definition.

<span id="definition-simtfl">**`simtfl`**</span>: a protocol simulator for analyzing [TFL](#definition-tfl) security and abstract performance. Development lives at <https://github.com/zcash/simtfl>. See [Status and Next Steps: Current Components](./introduction/status-and-next-steps.md#current-components) for current status.

<span id="definition-tfl">**TFL**</span>: The *Trailing Finality Layer* subprotocol within PoW+TFL. This is a new [PoS](#definition-pos) subprotocol which provides [assured finality](#definition-assured-finality) for Zcash.

<span id="definition-trailing-finality">**Trailing Finality**</span>: A protocol property wherein transactions become final some time after first appearing in [PoW](#definition-pow) blocks.

<span id="definition-zip">**ZIP**</span>: a Zcash Improvement Proposal is the protocol development process the Zcash community uses to safely define potential protocol improvements. See <https://zips.z.cash>.

*TODO*: Clarify the distinctions between PoW (general consensus), [NU5](#definition-nu5) which includes transaction semantics, and the PoW component of [PoW-TFL](#definition-pow-tfl). These distinctions deserve unique terms.

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to PoW+TFL design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)

<pre>







































</pre>
