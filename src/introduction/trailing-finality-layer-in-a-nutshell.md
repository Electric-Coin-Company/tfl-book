# Trailing Finality Layer in a Nutshell

The hybrid PoW/PoS protocol proposed in this book is similar to today's Zcash NU5 protocol with the addition of a *Trailing Finality Layer*:

**TODO**: Add graphic showing nodes connected to each other in the p2p protocol. Each node has two parts: PoW and TFL. Each part has a distinct connection to the neighbors of the same part, so node A's "PoW" connects to node B's "PoW", node A's "TFL" connects to node B's "TFL". Finally, we want some way to visualize that all of the PoW nodes and connections were "pre-existing" and that the TFL pieces are a "new layer".

The Zcash Trailing Finality Layer refers to a new subprotocol of a new hybrid PoW/PoS protocol, which we refer to as *PoW+TFL*. This subprotocol introduces *assured finality* (see [Terminology: Protocol Concepts](../terminology.md#protocol_concepts)) for the Zcash blockchain, ensuring that *final* blocks (and the transactions within them) may never be rolled back.

We use the term "layer" because we can understand this design as introducing a new layer to the Zcash network, making only minimal changes to the existing network and consensus protocol. This modular separation is present in the consensus rules, the network protocol, and the code architecture.

## Why Should Users Care?

There are three categories of users this proposed TFL protocol would impact:

### Current ZEC Users

Existing ZEC users who are primarily concerned with storing or receiving ZEC, whether private or transparent may benefit from this change in the short or medium term, because it may help lower delay times for some services, such as exchange deposits. As exchanges come to rely on the new finality guarantee, they can often reduce their deposit wait times. Other services with similar confirmation-depth-based wait times can be improved in a similar way to lower these wait times. Other than this improvement, these users should notice no other changes.

In the longer term, providing finality will be useful in establishing trust-minimized bridges to other blockchains. We anticipate this can enable better connecting ZEC to the Defi ecosystem, and with the introduction of Zcash Shielded Assets, this can enable other assets to connect to the Zcash shielded pool.

### Proof-of-Stake Users

Users who are interested in providing finality infrastructure, or users who want to delegate ZEC towards finality, will be able to earn rewards from the protocol for doing so, while also taking on some risk to their funds (to prevent malicious abuse of the protocol). This may be an important new category of ZEC users and use cases.

### Miners

Miners who provide Proof-of-Work security will necessarily see some reduction in their block rewards, since this proposal maintains the same issuance schedule and supply cap of ZEC while also spending some rewards on finality.

**Important Note:** The proportion and details of how much mining rewards will be impacted, and conversely how much finality/PoS providers will earn, are not yet specified in this proposal.

## Why is this a Good Approach to a PoS Transition?

This design is appealing as a safer first step in transitioning the Zcash protocol for multiple reasons:

### It Enables Proof-of-Stake Mechanisms Conservatively

This transition would enable PoS mechanisms, including the ability to operate PoS infratructure and delegate ZEC towards those providers to earn protocol rewards. While all PoS transitions would accomplish this, this approach does so in a conservative manner: it introduces these mechanics while striving to minimize the impact on existing use cases and protocol security.

In a sense, we can think of this approach as enabling the Zcash community to "dip our toes in the PoS waters" rather than diving in. If the results pan out well, it gives us confidence for further transitions. If we discover challenges, flaws, or risks, we anticipate their impact will be more limited since this is a more cautious transition step.

### Minimal Use-Case Disruption

In many cases, existing products, services, and tools can continue using the mainnet chain with no changes to code assuming they rely on existingn consensus nodes. We view this as a major benefit which allows Zcash's existing user network effect to continue safely unperturbed.

There will be certain narrow exceptional areas if those products, services, or tools need to be precise in areas where the protocol has changed, such as mining/staking reward calculations, transaction formats (in particular any new PoS-related fields or logic), or chain rollback logic.

### Minimal Consensus Rule Changes

Outside of PoS mechanics (such as bonding/unbonding stake, delegating, etc…), and changes to issuance (due to supporting both PoS and PoW) this design adds precisely one consensus rule:

> Final blocks may not be rolled back.

We believe this presents a minimal change to consensus rules to enable PoS, and is thus one of the safest approaches to a transition in terms of security analysis.

### Modular Design

By conceptualizing the TFL as a distinct "layer" or subprotocol, the consensus rules can be described as the explicit interactions between two subprotocols, one similar to the existing Zcash protcol as of NU5, and the other as a finalizing PoS protocol.

This approach helps in reasoning about failure modes, and how global consensus properties are achieved by which subprotocols.

Finally, since one subprotocol is very similar to the existing Zcash NU5 protocol, this lessens risk that the consensus properties within that subprotocol compromise current NU5 properties.

### Modular Implementation

In addition to the other benefits of protocol design modularity, we anticipate actual implementations can realize this modularity in code. This can help makes implementations more robust, easier to maintain, and more interoperable.

 For example, we can envision a standardized interface between PoW & TFL consensus components, enabling different development teams to provide these different components and for "full node" packagers to mix and match them. This is somewhat reminiscent of Ethereum's execution/consensus layer separation which we believe has shown great success in implementation team and product diversity.

## Cracking the Nutshell

In the rest of the introductory section of this book, we describe the status and next steps for the TFL proposal, provide a motivation for finality, a way to visualize and reason about trailing finality, and suggestions for getting involved.
