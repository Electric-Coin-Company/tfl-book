# Terminology

This book relies on the following terminology. We strive to keep these definitions as precise as possible and their definitions may deviate from uses elsewhere.

Definitions are sorted alphabetically.

## Terms

<!-- Unlike true html, it seems `mdbook` requires the span tags to be empty and immediately pre-fix the intended anchor target. -->

<span id="definition-assured-finality"></span>**Assured Finality**: A protocol property that assures that transactions cannot be reverted by that protocol. As with all protocol guarantees, a protocol assumes certain conditions must be met. A transaction may either be final or not: transactions which are not final may not become final, whereas once transactions do achieve finality they retain that property indefinitely (so long as protocol requirements are met).

Importantly, it is not feasible for any protocol to prevent reversing final transactions "out of band" from the protocol, such as if a sufficiently large and motivated group of users forks the network to include a specific new validity rule reverting transactions. In some cases this might be desirable, for example to mitigate exploitation of a security flaw. We are investigating the implications for governance and how to incorporate such situations into our security model. In any case, for this reason we eschew the term "absolute finality" sometimes used in technical discussions about consensus protocols.

<span id="definition-consensus-subprotocols"></span>**Consensus Subprotocols**: The [PoW](#definition-pow) and [PoS](#defintion-pos) subprotocols in [PoW+TFL](#definition-pow-tfl) or other [hybrid protocols](#definition-hybrid-consensus).

<span id="definition-crosslink"></span>**Crosslink**: A [hybrid construction](#definition-hybrid-construction) consensus protocol striving to implement the [TFL](#definition-tfl) design goals. See [Status and Next Steps: Current Components](./introduction/status-and-next-steps.md#current-components) for current status.

<span id="definition-final"></span>**Final**: A protocol property of transactions. In this book, this always implies [assured finality](#definition-assured-finality), in contrast to concepts like "probabilistic finality" provided by [PoW](#definition-pow).

<span id="definition-hybrid-consensus"></span>**Hybrid Consensus**: A consensus protocol that integrates more than one consensus subprotocol. [PoW+TFL](#definition-pow-tfl) is an instance of a hybrid protocol integrating [PoW](#definition-pow) and [PoS](#definition-pos) protocols.

<span id="definition-hybrid-construction"></span>**Hybrid Construction**: The design component of a [hybrid consensus](#defintion-hybrid-consensus) which specifies how to integrate [subprotocols](#definition-consensus-subprotocols) and what modifications, if any, those subprotocols need to be safely integrated. Examples include [Crosslink](#definition-crosslink) and [Snap-and-Chat](#definition-snap-and-chat).

<span id="definition-liveness"></span>**Liveness**: The property of a distributed protocol which ensures that the protocol may progress provided liveness requirements are met. **TODO:** [Fix the definition of Liveness #120](https://github.com/Electric-Coin-Company/tfl-book/issues/120)

<span id="definition-nu5nu6"></span>**NU5/NU6**: The Zcash consensus protocol as of NU5 or NU6 (which do not differ significantly in terms of the base block chain layer).[^new-mainnet-precursors]

<span id="definition-objective-validity"></span>**Objective Validity**: A validity property of a protocol history (such as a ledger) which can be computed purely from that history with no other context. Objective validity is needed to define consensus rules that will lead to the same protocol state being eventually agreed on by all nodes.

<span id="definition-pos"></span>**Proof-of-Stake**: A PoS protocol achieves consensus on transaction status by taking into account the weighting of staking tokens. PoS protocols exist under a large umbrella and may or may not provide [assured finality](#definition-assured-finality) or other properties this design requires of [TFL](#definition-tfl).

<span id="definition-pow"></span>**Proof-of-Work**: A PoW protocol uses Nakamoto consensus pioneered by Bitcoin. The PoW subprotocol within PoW+TFL is a different consensus protocol from [NU5/NU6](#definition-nu5nu6) and encompasses more than narrow Nakamoto PoW consensus, including transaction semantics such as for shielded transfers.

<span id="definition-pow-tfl"></span>**PoW+TFL**: the overall complete, integrated consensus protocol specified in this book.

<span id="definition-safety"></span>**Safety**: The property of a distributed protocol that guarantees a participant may safely rely on a consistent local state, provided safety requirements are met. **TODO:** [Provide a rigorous definition of Safety #121](https://github.com/Electric-Coin-Company/tfl-book/issues/121)

<span id="definition-simtfl"></span>**`simtfl`**: a protocol simulator for analyzing [TFL](#definition-tfl) security and abstract performance. Development lives at <https://github.com/zcash/simtfl></span>. See [Status and Next Steps: Current Components](./introduction/status-and-next-steps.md#current-components) for current status.

<span id="definition-snap-and-chat"></span>**Snap-and-Chat**: A [hybrid construction](#definition-hybrid-construction) consensus protocol introduced in [Ebb-and-Flow Protocols](./references.md#ebb-and-flow-protocols).

<span id="definition-tfl"></span>**TFL**: The *Trailing Finality Layer* subprotocol within PoW+TFL. This is a new [PoS](#definition-pos) subprotocol which provides [assured finality](#definition-assured-finality) for Zcash.

<span id="definition-trailing-finality"></span>**Trailing Finality**: A protocol property wherein transactions become final some time after first appearing in [PoW](#definition-pow) blocks.

<span id="definition-zip"></span>**ZIP**: a Zcash Improvement Proposal is the protocol development process the Zcash community uses to safely define potential protocol improvements. See <https://zips.z.cash></span>.

**TODO:** [Clarify the distinctions between pure PoW, the PoW subprotocol, NU6, and fork-choice vs all of transaction semantics. #119](https://github.com/Electric-Coin-Company/tfl-book/issues/119)

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to PoW+TFL design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)

<!-- This trailing whitespace ensures that readers who follow a link to a definition will always see that term at the top of their view. -->
<pre>







































</pre>
