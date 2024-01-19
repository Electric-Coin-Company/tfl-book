# The Arguments for Bounded Dynamic Availability and Finality Overrides

This document considers disadvantages of allowing transactions to continue to be included at the chain tip while the gap from the last finalized block becomes unbounded, and what I think should be done instead. This condition is allowed by Ebb‑and‑Flow protocols [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf).

I also argue that it is necessary to allow for the possibility of overriding finalization in order to respond to certain attacks, and that this should be explicitly modelled and subject to a well-defined governance process.

This is a rewritten version of [this forum post](https://forum.zcashcommunity.com/t/the-trailing-finality-layer/45133/10), adapting the main argument to take into account the discussion of “tail-thrashing attacks” and finalization availability from the Addendum. More details of how bounded dynamic availability could be implemented in the context of a Snap‑and‑Chat protocol are in [Notes on Snap‑and‑Chat](./notes-on-snap-and-chat.md).

The proposed changes end up being significant enough to give our construction a new name: “[Crosslink](./construction.md)”, referring to the cross-links between blocks of the BFT and best-chain protocols. Crosslink has evolved somewhat, and now includes other changes not covered in either this document or [Notes on Snap‑and‑Chat](./notes-on-snap-and-chat.md).

## Background

“Ebb‑and‑Flow”, as described in [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) ([arXiv version](https://arxiv.org/pdf/2009.04987.pdf)), is a security model for consensus protocols that provide two transaction logs, one with dynamic availability, and a prefix of it with finality.

The paper proposes an instantiation of this security model called a “Snap‑and‑Chat” construction. It composes two consensus subprotocols, a BFT subprotocol and a best-chain subprotocol (it calls this the “longest chain protocol”). The above logs are obtained from the output of these subprotocols in a non-trivial way.

This is claimed by the paper to “resolve” the tension between finality and dynamic availability. However, a necessary consequence is that in a situation where the “final” log stalls and the “available” log does not, the “finalization gap” between the finalization point and the chain tip can grow without bound. In particular, this means that transactions that spend funds can remain unfinalized for an arbitrary length of time.

In this note, we argue that this is unacceptable, and that it is preferable to sacrifice strict dynamic availability. However, we also argue that the main idea behind Ebb‑and‑Flow protocols is a good one, and that allowing the chain tip to run ahead of the finalization point does make sense and has practical advantages. However, we also argue that it should not be possible to include transactions that spend funds in blocks that are too far ahead of the finalization point.

```admonish info
Naive ways of preventing an unbounded finalization gap, such as stopping the chain completely in the case of a finalization stall, turn out to run into serious security problems &mdash; at least when the best-chain protocol uses Proof-of-Work. We’ll discuss those in detail.

Our proposed solution will be to require coinbase-only blocks during a long finalization stall. This solution has the advantage that, as far as this change goes, the security analysis of the Snap‑and‑Chat construction from [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) can still be applied.
```

We argue that losing strict dynamic availability in favour of “bounded dynamic availability” is preferable to the consequences of the unbounded finality gap, if/when a “long finalization stall” occurs.

We also argue that it is beneficial to explicitly allow “finality overrides” under the control of a well-documented governance process. Such overrides allow long rollbacks that may be necessary in the case of an exploited security flaw. This is complementary to the argument for bounded dynamic availability, because the latter limits the period of user transactions that could be affected. The governance process can impose a limit on the length of this long rollback if desired.

## Finality + Dynamic availability implies an unbounded finalization gap

Since partition between nodes sufficient for finalization cannot be prevented, loosely speaking the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem) implies that any consistent protocol (and therefore any protocol with finality) may stall for at least as long as the partition takes to heal.

```admonish info "Background"
That “loosely speaking” is made precise by [[LR2020]](https://arxiv.org/pdf/2006.10698.pdf).
```

Dynamic availability implies that the chain tip will continue to advance, and so the finalization gap increases without bound.

Partition is not necessarily the only condition that could cause a finalization stall, it is just the one that most easily proves that this conclusion is impossible to avoid.

## Problems with allowing spends in an unbounded finalization gap

Both the available protocol, and the subprotocol that provides finality, will be used in practice &mdash; otherwise, one or both of them might as well not exist. There is always a risk that blocks may be rolled back to the finalization point, by definition.

Suppose, then, that there is a long finalization stall. The final and available protocols are not separate: there is no duplication of tokens between protocols, but the rules about how to determine best-effort balance and guaranteed balance depend on both protocols, how they are composed, and how the history after the finalization point is interpreted.

```admonish info
The guaranteed minimum balance of a given party is not just the minimum of their balance at the finalization point and their balance at the current tip. It is the minimum balance taken over all possible transaction histories that extend the finalized chain &mdash; taking into account that a party’s previously published transactions might be able to be reapplied in a different context without its explicit consent. The extent to which published transactions can be reapplied depends on technical choices that we must make, subject to some constraints (for example, we know that shielded transactions cannot be reapplied after their anchors have been invalidated). It may be desirable to further constrain re-use in order to make guaranteed minimum balances easier to compute.
```

As the finalization gap increases, the negative consequences of rolling back user transactions that spend funds increase. (Coinbase transactions do not spend funds; they are a special case that we will discuss later.)

There are several possible &mdash;not mutually exclusive&mdash; outcomes:

* Users of the currency start to consider the available protocol increasingly unreliable.
* Users start to consider a rollback to be untenable, and lobby to prevent it or cry foul if it occurs.
* Users start to consider finalization increasingly irrelevant. Services that depend on finality become unavailable.
  * There is no free lunch that would allow us to avoid availability problems for services that also depend on finality.
* Service providers adopt temporary workarounds that may not have had adequate security analysis.

Any of these might precipitate a crisis of confidence, and there are reasons to think this effect might be worse than if the chain had switched to a “Safety Mode” designed to prevent loss of user funds. Any such crisis may have a negative effect on token prices and long-term adoption.

Note that adding finalization using an Ebb‑and‑Flow protocol does not by itself increase the probability of a rollback in the available chain, provided the PoW remains as secure against rollbacks of a given length as before. But that is a big proviso. We have a design constraint (motivated by limiting token devaluation and by governance issues) to limit issuance to be no greater than that of the original Zcash protocol up to a given height. Since some of the issuance is likely needed to reward staking, the amount of money available for mining rewards is reduced, which may reduce overall hash rate and security of the PoW. Independently, there may be a temptation for design decisions to rely on finality in a way that reduces security of PoW (“risk compensation”). There is also pressure to reduce the energy usage of PoW, which necessarily reduces the global hash rate, and therefore the cost of performing an attack that depends on the adversary having any given proportion of global hash rate.

It could be argued that the issue of availability of services that depend on finality is mainly one of avoiding over-claiming about what is possible. Nevertheless I think there are also real usability issues if balances as seen by those services can differ significantly and for long periods from balances at the chain tip.

Regardless, incorrect assumptions about the extent to which the finalized and available states can differ are likely to be exposed if there is a finalization stall. And those who made the assumptions may (quite reasonably!) not accept “everything is fine, those assumptions were always wrong” as a satisfactory response.

## What is Bounded Dynamic Availability?

An intuitive notion of “availability” for blockchain protocols includes the ability to use the protocol as normal to spend funds. So, just to be clear, in a situation where that cannot happen we have lost availability, *even if* the block chain is advancing.

```admonish info "Background"
For an explanation of *dynamic* availability and its advantages, I recommend [[DKT2020]](https://arxiv.org/abs/2010.08154) and its [accompanying talk](https://www.youtube.com/watch?v=SacUT_53Pg8).
```

Bounded dynamic availability is a weakening of dynamic availability. It means that we intentionally sacrifice availability when some potentially hazardous operation &mdash;a “hazard” for short&mdash; would occur too far after the current finalization point. For now, assume for simplicity that our only hazard is spending funds. More generally, the notion of bounded dynamic availability can be applied to a wider range of protocols by tailoring the definition of “hazard” to the protocol.

### Terminology note

[[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) calls the dynamically available blockchain protocol $\Pi_{\mathrm{lc}}$ that provides input to the rest of the contruction, the “longest chain” protocol. There are two reasons to avoid this terminology:
* In Bitcoin, Zcash, and most other PoW-based protocols, what is actually used by each node is not its longest observed chain, but its observed consensus-valid chain with most accumulated work. In Zcash this is called the node’s “[best valid block chain](https://zips.z.cash/protocol/protocol.pdf#blockchain)”, which we shorten to “best chain”.
* As footnote 2 on page 3 of [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) says, that paper does not require $\Pi_{\mathrm{lc}}$ to be a “longest chain” protocol anyway.

```admonish info "Historical note"
The error in conflating the “longest chain” with the observed consensus-valid chain with most accumulated work, originates in the Bitcoin whitepaper. [[Nakamoto2008](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.221.9986), page 3]
```

We will use the term “best-chain protocol” instead. Note that this means $\Pi_{\mathrm{lc}}$ in the Snap‑and‑Chat construction, *not* any node’s view of the sanitized ledger $\mathsf{LOG}_{\mathrm{da}}$.

### How to block hazards

We have not yet decided *how* to block hazards during a long finalization stall. We could do so directly, or by stopping block production in the more-available protocol. For reasons explained in the [section on “Tail-thrashing attacks”](#tail-thrashing-attacks) below, it’s desirable *not* to stop block production. And so it’s consistent to have bounded dynamic availability together with another liveness property &mdash;which can be defined similarly to dynamic availability&mdash; that says the more-available protocol’s chain is still advancing. This is what we will aim for.

We will call this method of blocking hazards, without stopping block production, “going into Safety Mode”.

```admonish info "Historical note"
This concept of Safety Mode is very similar to a [feature that was discussed early in the development of Zcash](https://github.com/zcash/zcash/issues/3311), but never fully designed or implemented. (After originally being called “Safety Mode”, it was at some point renamed to “Emergency Mode”, but then the latter term was used for [something else](https://electriccoin.co/blog/update-addressing-zcash-wallet-performance-issues/).)
```

For Zcash, I propose that the main restriction of Safety Mode should be to require coinbase-only blocks. This achieves a similar effect, for our purposes, as actually stalling the more-available protocol’s chain. Since funds cannot be spent in coinbase-only blocks, the vast majority of attacks that we are worried about would not be exploitable in this state.

```admonish info
It is possible that a security flaw could affect coinbase transactions. We *might* want to turn off shielded coinbase for Safety Mode blocks in order to reduce the chance of that.

Also, mining rewards cannot be spent in a coinbase-only block; in particular, mining pools cannot distribute rewards. So there is a risk that an unscrupulous mining pool might try to do a rug-pull after mining of non-coinbase-only blocks resumes, if there were a very long finalization stall. But this approach works at least in the short term, and probably for long enough to allow manual intervention into the finalization protocol, or governance processes if needed.
```

A analogy for the effect of this on availability that may be familiar to many people, is that it works like video streaming. All video streaming services use a buffer to paper over short-term interruptions or slow-downs of network access. In most cases, this buffer is bounded. This allows the video to be watched uninterrupted and at a constant rate in most circumstances. But if there is a longer-term network failure or insufficient sustained bandwidth, the playback will unavoidably stall. In our case, block production does not literally stall, but it’s the same as far as users’ ability to perform “hazardous” operations is concerned.

### Why is this better?

So, why do I advocate this over:

1. A protocol that only provides dynamic availability;
2. A protocol that only provides finality;
3. An unmodified Ebb‑and‑Flow protocol?

The reason to reject option 1 is straightforward: finality is a valuable security property that is necessary for some use cases.

If a protocol only provides finality (option 2), then short-term availability is directly tied to finalization. It may be possible to make finalization stalls sufficiently rare or short-lived that this is tolerable. But that is more likely to be possible if and when there is a well-established staking ecosystem. Before that ecosystem is established, the protocol may be particularly vulnerable to stalls. Furthermore, it’s difficult to get to such a protocol from a pure PoW system like current Zcash.

We argued in the previous section that allowing hazards in an unbounded finalization gap is bad. Option 3 entails an unbounded finalization gap that *will* allow hazards. However, that isn’t sufficient to argue that bounded dynamic availability is better. Perhaps there are no good solutions! What are we gaining from a bounded dynamic availability approach that would justify the complexity of a hybrid protocol without obtaining strict dynamic availability?

My argument goes like this:

* It is likely that a high proportion of the situations in which a sustained finalization stall happens will require human intervention. If the finality protocol were going to recover without intervention, there is no reason to think that it wouldn’t do so in a relatively short time.
* When human intervention is required, the fact that the chain tip is still proceeding apace (in protocols with strict dynamic availability) makes restarting the finality protocol harder, for many potential causes of a finalization stall. This may be less difficult when only “non-hazardous” transactions are present&mdash; in particular, when only coinbase transactions (which are subject to fairly strict rules in Zcash and other Bitcoin-derived chains) are present. This argument carries even more force when the protocol also allows “finality overrides”, as discussed later in the Complementarity section.
* Nothing about bounded dynamic availability prevents us from working hard to design a system that makes finalization stalls as infrequent and short-lived as possible, just as we would for any other option that provides finality.
* We want to optimistically minimize the finalization gap under good conditions, because this improves the usability of services that depend on finality. This argues against protocols that try to maintain a fixed gap, and motivates letting the gap vary.
* In practice, the likelihood of short finalization stalls is high enough that heuristically retaining availability in those situations is useful.

The argument that it is difficult to completely prevent finalization stalls is supported by [experience on Ethereum in May 2023](https://www.coindesk.com/tech/2023/05/17/ethereums-loss-of-finality-what-happened/), when there were two stalls within 24 hours, [one for about 25 minutes and one for about 64 minutes](https://offchain.medium.com/post-mortem-report-ethereum-mainnet-finality-05-11-2023-95e271dfd8b2). This experience is consistent with my arguments:

* Neither stall required short-term human intervention, and the network did in fact recover from them quickly.
* The stalls were caused by a resource exhaustion problem in the Prysm consensus client when handling attestations. It’s plausible to think that if this bug had been more serious, or possibly if Prysm clients had made up more of the network, then it would have required a hotfix release (and/or a significant proportion of nodes switching to another client) in order to resolve the stall. So this lines up with my hypothesis that longer stalls are likely to require manual intervention.
* A bounded dynamic availability protocol would very likely have resulted in either a shorter or no interruption in availability. If, say, the availability bound were set to be roughly an hour, then the first finalization stall would have been “papered over” and the second would have resulted in only a short loss of availability.

Retaining short-term availability does not result in a risk compensation hazard:

* A finalization stall is still very visible, and directly affects applications relying on finality.
* Precisely because of the availability bound, it is obvious that it could affect all applications if it lasted long enough.

A potential philosophical objection to lack of strict dynamic availability is that it creates a centralization risk to availability. That is, it becomes more likely that a coalition of validators can deliberately cause a denial of service. I think this objection may be more prevalent among people who would object to adding a finality layer or PoS at all.

## Finality Overrides

Consensus protocols sometimes fail. Potential causes of failure include:

* A design problem with the finality layer that causes a stall, or allows a stall to be provoked.
* A balance violation or spend authorization flaw that is being exploited or is sufficiently likely to be exploited.
* An implementation bug in a widely used node implementation that causes many nodes to diverge from consensus.

In these situations, overriding finality may be better than any other alternative.

An example is a [balance violation flaw due to a 64-bit integer overflow](https://bitcointalk.org/index.php?topic=822.0) that was [exploited on Bitcoin mainnet](https://en.bitcoin.it/wiki/Value_overflow_incident) on 15th August 2010. The response was to roll back the chain to before the exploitation, which is widely considered to have been the right decision. The time between the exploit (at block height 74638) and the forked chain overtaking the exploited chain (at block height 74691) was 53 blocks, or around 9 hours.

Of course, Bitcoin used and still uses a pure PoW consensus. But the applicability of the example does not depend on that: the flaw was independent of the consensus mechanism.

Another example of a situation that prompted this kind of override was the [DAO recursion exploit](https://hackingdistributed.com/2016/06/18/analysis-of-the-dao-exploit/) on the Ethereum main chain [in June 2016](https://www.coindesk.com/learn/understanding-the-dao-attack/). The response to this was the forced balance adjustment hard fork on 20th July 2016 commonly known as the [DAO fork](https://ethereum.org/en/history/#dao-fork). Although this adjustment was not implemented as a rollback, and although Ethereum was using PoW at the time and did not make any formal finality guarantees, it did override transfers that would heuristically have been considered final at the fork height. Again, this flaw was independent of the consensus mechanism.

The DAO fork was of course much more controversial than the Bitcoin fork, and a substantial minority of mining nodes split off to form Ethereum Classic. In any case, the point of this example is that it’s always possible to override finality in response to an exceptional situation, and that a chain’s community may decide to do so. The fact that Ethereum 2.0 now does claim a finality guarantee, would not in practice prevent a similar response in future that would override that guarantee.

The question then is whether the procedure to override finality should be formalised or ad hoc. I argue that it should be formalised, including specifying the governance process to be used.

This makes security analysis — of the consensus protocol per se, of the governance process, and of their interaction — much more feasible. Arguably a complete security analysis is not possible at all without it.

It also front-loads arguing about what procedure should be followed, and so it is more likely that stakeholders will agree to follow the process in any time-critical incident.

### A way of modelling overrides that is insufficient

There is another possible way to model a protocol that claims finality but can be overridden in practice. We could say that the protocol after the override is a brand new protocol and chain (inheriting balances from the previous one, possibly modulo adjustments such as those that happened in the DAO fork).

Although that would allow saying that the finality property has technically not been violated, it does not match how users think about an override situation. They are more likely to think of it as a protocol with finality that can be violated in exceptional cases — and they would reasonably want to know what those cases are and how they will be handled. It also does nothing to help with security analysis of such cases.

## Complementarity

Finality overrides and bounded dynamic availability are complementary in the following way: if a problem is urgent enough, then validators can be asked to stop validating. For genuinely harmful problems, it is likely to be in the interests of enough validators to stop that this causes a finalization stall. If this lasts longer than the availability bound then the protocol will go into Safety Mode, giving time for the defined governance process to occur and decide what to do. And because the unfinalized consensus chain will contain only a limited period of user transactions that spend funds, the option of a long rollback remains realistically open.

If, on the other hand, there is time pressure to make a governance decision about a rollback in order to reduce its length, that may result in a less well-considered decision.

A possible objection is that there might be a coalition of validators who ignore the request to stop (possibly including the attacker or validators that an attacker can bribe), in which case the finalization stall would not happen. But that just means that we don’t gain the advantage of more time to make a governance decision; it isn’t actively a disadvantage relative to alternative designs. This outcome can also be thought of as a feature rather than a bug: going into Safety Mode should be a last resort, and if the argument given for the request to stop failed to convince a sufficient number of validators that it was reason enough to do so, then perhaps it wasn’t a good enough reason.

```admonish info "Rationale"
This resolves one of the main objections to the [original Safety Mode idea](https://github.com/zcash/zcash/issues/3311) that stopped us from implementing it in Zcash. The original proposal was to use a signature with a key held by ECC to trigger Safety Mode, which would arguably have been too centralized. The Safety Mode described in this document, on the other hand, can only be entered by consensus of a larger validator set, or if there is an availability failure of the finalization protocol.
```

It is also possible to make the argument that the threshold of stake needed is imposed by technical properties of the finality protocol and by the resources of the attacker, which might not be ideal for the purpose described above. However, I would argue that it does not need to be ideal, and will be in the right ballpark in practice.

There’s a caveat related to doing intentional rollbacks when using the Safety Mode approach, where block production in the more-available protocol continues during a long finalization stall. What happens to incentives of block producers (miners in the case of Proof-of-Work), given that they know the consensus chain might be intentionally rolled back? They might reasonably conclude that it is less valuable to produce those blocks, leading to a reduction of hash rate or other violations of the security assumptions of $\Pi_{\mathrm{lc}}$.

This is actually fairly easy to solve. We have the governance procedures say that if we do an intentional rollback, the coinbase-only mining rewards will be preserved. I.e. we produce a block or blocks that include those rewards paid to the same addresses (adjusting the consensus to allow them to be created from thin air if necessary), have everyone check it thoroughly, and require the chain to restart from that block. So as long as block producers believe that this governance procedure will be followed and that the chain will eventually recover at a reasonable coin price, they will still have incentive to produce on $\Pi_{\mathrm{lc}}$, at least for a time.

```admonish info "Rationale"
Although the community operating the governance procedures has already obtained the security benefit of mining done on the rolled-back chain by the time it creates the new chain, there is a strong incentive not to renege on the agreement with miners, because the same situation may happen again.
```

## Tail-thrashing attacks

Earlier we said that there were two possible approaches to preventing hazards during a long finalization stall:

a) go into a Safety Mode that directly disallows hazardous transactions (for example, by requiring $\Pi_{\mathrm{lc}}$ blocks to be coinbase-only in Zcash);

b) temporarily cause the more-available chain to stall.

This section describes an important class of potential attacks on approach b) that are difficult to resolve. They are based on the fact that when the unfinalized chain stalls, an adversary has more time to find blocks, and this might violate security assumptions of the more-available protocol. For instance, if the more-available protocol is PoW-based, then its security in the steady state is predicated on the fact that an adversary with a given proportion of hash power has only a limited time to use that power, before the rest of the network finds another block.

```admonish info "Background"
For an analysis of the concrete security of Nakamoto-like protocols, see [[DKT+2020]](https://arxiv.org/abs/2005.10484) and [[GKR2020]](https://eprint.iacr.org/2020/661). These papers confirm the intuition that the “private attack” &mdash;in which an adversary races privately against the rest of the network to construct a forking chain&mdash; is optimal, obtaining the same tight security bound independently using different techniques.
```

During a chain stall, the adversary no longer has a limited time to construct a forking chain. If, say, the adversary has 10% hash power, then it can on average find a block in 10 block times. And so in 100 block times it can create a 10-block fork.

It may in fact be worse than this: once miners know that a finalization stall is happening, their incentive to continue mining is reduced, since they know that there is a greater chance that their blocks might be rolled back. So we would expect the global hash rate to fall &mdash;even before the finality gap bound is hit&mdash; and then the adversary would have a greater proportion of hash rate.

```admonish info
Even in a pure Ebb‑and‑Flow protocol, a finalization stall could cause miners to infer that their blocks are more likely to be rolled back, but the fact that the chain is continuing would make that more difficult to exploit. This issue with the global hash rate is mostly specific to the more-available protocol being PoW: if it were PoS, then its validators might as well continue proposing blocks because it is cheap to do so. There might be other attacks when the more-available protocol is PoS; we haven’t spent much time analysing that case.
```

The problem is that the more-available chain does not necessarily *just halt* during a chain stall. In fact, for a finality gap bound of $k$ blocks, an adversary could cause the $k$-block “tail” of the chain as seen by any given node to “thrash” between different chains. I will call this a **tail-thrashing attack**.

If a protocol allowed such attacks then it would be a regression relative to the security we would normally expect from an otherwise similar PoW-based protocol. It only occurs during a finalization stall, but note that we cannot exclude the possibility of an adversary being able to provoke a finalization stall.

Note that in the Snap‑and‑Chat construction, snapshots of $\Pi_{\mathrm{lc}}$ are used as input to the BFT protocol. That implies that the tail-thrashing problem could also affect the input to that protocol, which would be bad (not least for security analysis of availability, which seems somewhat intractable in that case).

Also, when restarting $\Pi_{\mathrm{lc}}$, we would need to take account of the fact that the adversary has had an arbitrary length of time to build long chains from every block that we could potentially restart from. It could be possible to invalidate those chains by requiring blocks after the restart to be dependent on fresh randomness, but that sounds quite tricky (especially given that we want to restart *without* manual intervention if possible), and there may be other attacks we haven’t thought of. This motivates using approach a) instead.

Note that we have still glossed over precisely how consensus rules would change to enforce a). I recommend reading [Notes on Snap‑and‑Chat](./notes-on-snap-and-chat.md) next, followed by [The Crosslink Construction](./construction.md).
