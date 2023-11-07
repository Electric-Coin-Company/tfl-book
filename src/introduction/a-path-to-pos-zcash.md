# A Path to Proof-of-Stake Zcash

The [TFL](../terminology.md#definition-tfl) design provides a possible first step in transitioning [Zcash](https://z.cash) to a [PoS](../terminology.md#definition-pos) protocol. Here we describe how a transition to PoS relates to "the Zcash roadmap" and how TFL fits into one approach to a PoS transition.

## The Zcash Tech-Tree

There are multiple developer orgs working on different proposed features for Zcash. Some of these involve multiple large distinct upgrade steps, and several of these steps depend on other such steps. This could be represented as a directed acyclic graph. We have begun referring to this space of possible future improvements as the *Zcash Tech-Tree*, taking inspiration from an analogous concept in gaming.[^tech-tree-history]

We envision a *proof-of-stake transition path* as one of the potential paths within this tech-tree which is the primary protocol focus of this proposal. An example visualization of this Zcash Tech-Tree might look like this:

```dot process
{{#include ../diagrams/zcash-tech-tree-generic.dot}}
```

## A Proof-of-Stake Transition Path

Given that context, we envision a path within the Zcash Tech-Tree for transitioning Zcash to PoS. At the top level we propose that this path contain at least two major milestones:

1. Transitioning from current Zcash [NU5](../terminology.md#definition-nu5) [PoW](../terminology.md#definition-pow) protocol to a PoW/PoS [hybrid consensus](../terminology.md#definition-hybrid-consensus) protocol dubbed [PoW+TFL](../terminology.md#definition-pow-tfl).
2. Transitioning from [PoW+TFL](../terminology.md#definition-pow-tfl) to pure [PoS](../terminology.md#definition-pow-tfl) protocol.

After this transition to pure PoS, there are likely to be future improvements to the PoS protocol, or the consensus protocol more generally. This TFL book focuses almost exclusively on the first step in this sequence.

Our primary motivation for proposing (at least) two steps is to minimize disruption to usability, safety, security, and the ecosystem during each step.

This book primarily focuses this first step: the transition to [PoW+TFL](../terminology.md#definition-pow-tfl). To understand the specific goals for that, see [Design Goals](../overview/design-goals.md).

With this approach, the Zcash Tech Tree with the [TFL](../terminology.md#definition-tfl) approach might look something like this:

```dot process
{{#include ../diagrams/zcash-tech-tree-tfl-steps.dot}}
```

## Why Two Steps?

One question we've gotten in proposing this approach is why take a two-step process with an intermediate [hybrid consensus](../terminology.md#definition-hybrid-consensus) protocol, rather than a single transition directly to a [PoS](../terminology.md#definition-pos) protocol?

Here's how we think about those trade-offs:

### Considering Single Transition (vs Hybrid Multi-Step)

#### Pros
- We already understand the current PoW protocol well, and if we transition to an existing proven PoS protocol, then we could skip the complexity of an intermediate hybrid stage.
- The node implementation might be simpler.
- Explaining to people what is happening might be simpler. Something like “Zcash has been PoW since it launched, but on $DATE (e.g. at block height X) it will switch to PoS.”
- Given that the issuance in a given time period is bounded by the supply curve, the full amount that was previously allocated to mining rewards becomes immediately available for staking rewards at the switch-over, rather than having to share this amount between mining and staking during the hybrid stage.

#### Cons
- If there is any unforeseen show-stopping problem in the new protocol or the transition process, we’d have to react to a network-wide issue.
- It may be more likely to cause ecosystem disruption; unforeseen differences between PoW and PoS might cause various kinds of snags or papercuts throughout the ecosystem, and these would all pop up around the same time, which may lead to a loss of confidence/retention/adoption or at the very least inconvenience many users for some time.
- Losing miners: since the transition would be all at once, we may lose some number of miners, who are participants and users in the ecosystem. Miners may leave prior to the transition in order to take care of their own needs. If there is some show-stopper in the transition, one possible short-term mitigation would be to fall back on PoW which is well known, but if we’ve lost most miners, that may no longer be viable.

### Considering Hybrid Multi-Step approach (vs Single-Step):

Note: TFL is one instance of a multi-step approach.

#### Pros
- We can hopefully be less disruptive across the ecosystem so that there are fewer snags and disruptions with each step.
- If there is a show-stopping flaw in any step, the fall-back possibility seems more plausible. For example, if there is a show-stopper when transitioning from PoW to [PoW+TFL](../terminology.md#definition-pow-tfl), falling back to pure PoW seems more feasible, since both protocols rely on mainnet PoW infrastructure, so those participants will be present in either case.
- Retaining miners during a hybrid phase: while it is true that a hybrid protocol will lower miner revenue (since we aim to maintain the issuance schedule constraints), there is also more possibility and likelihood of keeping some of these users engaged. For example, they may begin participating in staking services (either as delegators or as infrastructure operators). If that is successful, then they’re also more likely to remain engaged in the subsequent transition to pure PoS.
- This general approach was demonstrated successfully by Ethereum, which is the largest or second largest cryptocurrency network for several important metrics (e.g. market cap, fees paid, user and developer activity, …). So we know this can be done well without disruptions.

#### Cons
- The intermediate hybrid step will be a more novel and less well understood protocol. (It will necessarily be fairly different from Ethereum’s Beacon chain era.)
- Consensus nodes will be more complex, involving logic for both sub-protocols as well as their integration. (Ideally this complexity can be modularized so that the nodes are easier to maintain and improve.)
- This may be more complicated to explain to current and potential new users. Something like “Zcash launched as PoW, and on $DATE (block height X) it will transition to a hybrid system, then later to a pure PoS system.”
- The available issuance must be shared between mining and staking rewards during the hybrid stage. The security of the PoW layer and of the PoS layer during this stage is partially dependent on the funds allocated to issuance for each protocol, and it is not yet clear to what extent splitting rewards would affect overall security.

# Footnotes

[^tech-tree-history]: See [Wikipedia's Technology Tree - History](https://en.wikipedia.org/wiki/Technology_tree#History) section for details.
