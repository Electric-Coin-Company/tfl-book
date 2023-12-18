# The Crosslink Construction

We are now ready to give a description of a variant of Snap‑and‑Chat that takes into account the issues described in [Notes on Snap‑and‑Chat](https://hackmd.io/PXs8SOMHQQ6uBs3GXNPQjQ?view), and that implements [bounded dynamic availability](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view). I call this the "Crosslink" construction. I will try to make the description relatively self-contained, but knowledge of the Snap‑and‑Chat construction from [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) ([arXiv version](https://arxiv.org/pdf/2009.04987.pdf)) is assumed.

## Conventions

"$\mathrm{*}$" is a metavariable for the name of a protocol. We also use it as a wildcard in protocol names of a particular type, for example <span style="white-space: nowrap">"$\mathrm{*}$bc"</span> for the name of some best‑chain protocol.

Protocols are referred to as $\Pi_{\mathrm{*}}$ for a <span style="white-space: nowrap">name "$\mathrm{*}$".</span> Where it is useful to avoid ambiguity, when referring to a concept defined by $\Pi_{\mathrm{*}}$ we prefix it with <span style="white-space: nowrap">"$\mathrm{*}$‑".</span>

We do not take synchrony or partial synchrony as an implicit assumption of the communication model; that is, *unless otherwise specified*, messages between protocol participants can be arbitrarily delayed or dropped. A given message is received at most once, and messages are nonmalleably authenticated as originating from a given sender whenever needed by the applicable protocol. Particular subprotocols may require a stronger model.

```admonish info
For an overview of communication models used to analyse distributed protocols, see [this blog post by Ittai Abraham](https://decentralizedthoughts.github.io/2019-06-01-2019-5-31-models/).
```

```admonish info collapsible=true title="Discussion of incorrect applications of the GST formalization of partial synchrony to continuously operating protocols. (You're doing it wrong!)"
The original context for the definition of the partially synchronous model in [[DLS1988]](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf) was for "one‑shot" Byzantine Agreement --- called "the consensus problem" in that paper. The following argument is used to justify assuming that all messages from the Global Stabilization Time onward are delivered within the <span style="white-space: nowrap">upper time bound $\Delta$:</span>

> Therefore, we impose an additional constraint: For each execution there is a global stabilization time (GST), unknown to the processors, such that the message system respects the upper bound $\Delta$ from time GST onward.
>
> This constraint might at first seem too strong: In realistic situations, the upper bound cannot reasonably be expected to hold forever after GST, but perhaps only for a limited time. However, any good solution to the consensus problem in this model would have an upper bound $L$ on the amount of time after GST required for consensus to be reached; in this case it is not really necessary that the bound $\Delta$ hold forever after time GST, but only up to time GST $+\; L$. We find it technically convenient to avoid explicit mention of the interval length $L$ in the model, but will instead present the appropriate upper bounds on time for each of our algorithms.

Several subsequent authors applying the partially synchronous model to block chains appear to have forgotten this context. In particular, the argument depends on the protocol completing soon after GST. Obviously a block-chain protocol does not satisfy this assumption; it is not a <span style="white-space: nowrap">"one‑shot"</span> consensus problem.

This assumption could be removed, but some authors of papers about block-chain protocols have taken it to be an essential aspect of modelling partial synchrony. I believe this is contrary to the intent of [[DLS1988]](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf):

> Instead of requiring that the consensus problem be solvable in the GST model, we might think of separating the correctness conditions into safety and termination properties. The safety conditions are that no two correct processors should ever reach disagreement, and that no correct processor should ever make a decision that is contrary to the specified validity conditions. The termination property is just that each correct processor should eventually make a decision. Then we might require an algorithm to satisfy the safety conditions no matter how asynchronously the message system behaves, that is, even if $\Delta$ does not hold eventually. On the other hand, we might only require termination in case $\Delta$ holds eventually. It is easy to see that these safety and termination conditions are [for the consensus problem] equivalent to our GST condition: If an algorithm solves the consensus problem when $\Delta$ holds from time GST onward, then that algorithm cannot possibly violate a safety property even if the message system is completely asynchronous. This is because safety violations must occur at some finite point in time, and there would be some continuation of the violating execution in which $\Delta$ eventually holds.

This argument is correct as stated, i.e. for the one-shot consensus problem. Subtly, essentially the same argument can be adapted to protocols with *safety* properties that need to be satisfied continuously. However, it cannot correctly be applied to *liveness* properties of non-terminating protocols. The authors (Cynthia Dwork, Nancy Lynch, and Larry Stockmeyer) would certainly have known this: notice how they carefully distinguish "the GST model" from "partial synchrony". They cannot plausibly have intended this GST formalization to be applied unmodified to analyze liveness in such protocols, which seems to be common in the block-chain literature, including in the Ebb-and-Flow paper [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) and the Streamlet paper [[CS2020]](https://eprint.iacr.org/2020/088.pdf). (The latter does refer to "periods of synchrony" which indicates awareness of the issue, but then it uses the unmodified GST model in the proofs.)

This provides further motivation to avoid taking the GST formalization of partial synchrony as a basic assumption.
```
${}$
For simplicity, we assume that all events occur at global times in a total ordering. This assumption is not realistic in an asynchronous communication model, but it is not essential to the design or analysis and could be removed (essentially: replace times with events and use a partial happens-before ordering on events, in place of a total ordering on times).

<span style="white-space: nowrap">A $\mathrm{*}$‑execution</span> is the complete set of events (message sends/receives and decisions by protocol participants) that occur in a particular <span style="white-space: nowrap">run of $\Pi_{\mathrm{*}}$</span> from its initiation up to a given time. A prefix of a <span style="white-space: nowrap">$\mathrm{*}$‑execution</span> is also a <span style="white-space: nowrap">$\mathrm{*}$‑execution.</span> Since executions always start from protocol initiation, a strict suffix of a <span style="white-space: nowrap">$\mathrm{*}$‑execution</span> is not a <span style="white-space: nowrap">$\mathrm{*}$‑execution.</span>

If $\mathrm{*}$ maintains a (single) block chain, $\mathcal{O}_{\mathrm{*}}$ refers to the genesis block of <span style="white-space: nowrap">a $\mathrm{*}$‑chain.</span>

Let $\textsf{chain-txns}(\mathsf{ch})$ be the sequence of transactions in the given <span style="white-space: nowrap">chain $\mathsf{ch}$,</span> starting from genesis.

For convenience we conflate <span style="white-space: nowrap">$\mathrm{*}$‑blocks</span> with <span style="white-space: nowrap">$\mathrm{*}$‑chains;</span> that is, we identify a chain with the block at its tip. This is justified because, assuming that the hash function used for parent links is collision-resistant, there can be only one <span style="white-space: nowrap">$\mathrm{*}$‑chain</span> corresponding to a <span style="white-space: nowrap">$\mathrm{*}$‑block.</span>

If $\mathsf{ch}$ is a <span style="white-space: nowrap">$\mathrm{*}$‑chain,</span> $\mathsf{ch} \lceil_{\mathrm{*}}^\sigma$ means $\mathsf{ch}$ with the last $\sigma$ blocks pruned, except that <span style="white-space: nowrap">if $\sigma \geq \mathsf{len}(\mathsf{ch})$,</span> the result is the $\mathrm{*}$‑chain consisting only <span style="white-space: nowrap">of $\mathcal{O}_{\mathrm{*}}$.</span>

The block at <span style="white-space: nowrap">depth $k \in \mathbb{N}^+$</span> in a <span style="white-space: nowrap">$\mathrm{*}$‑chain $\mathsf{ch}$</span> is defined to be the <span style="white-space: nowrap">tip of $\mathsf{ch} \lceil_{\mathrm{*}}^k$.</span> Thus the block at <span style="white-space: nowrap">depth $k$</span> in a chain is the last one that cannot be affected by a rollback of <span style="white-space: nowrap">length $k$.</span>

```admonish info
Our usage of "depth" is different from [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf), which uses "depth" to refer to what Bitcoin and Zcash call "height". It also differs by $1$ from the convention for confirmation depths in `zcashd`, where the tip is considered to be at <span style="white-space: nowrap">depth $1$,</span> rather <span style="white-space: nowrap">than $0$.</span>
```

For <span style="white-space: nowrap">$\mathrm{*}$‑blocks $B$ and $C$,</span>
* the notation $B \preceq_{\mathrm{*}} C$ means that the <span style="white-space: nowrap">$\mathrm{*}$‑chain</span> with <span style="white-space: nowrap">tip $B$</span> is a prefix of the one with <span style="white-space: nowrap">tip $C$.</span> This includes the <span style="white-space: nowrap">case $B = C$.</span>
* the notation $B \preceq\hspace{-0.5em}\succeq_{\mathrm{*}} C$ means that <span style="white-space: nowrap">either $B \preceq_{\mathrm{*}} C$ or $C \preceq_{\mathrm{*}} B$.</span> That is, <span style="white-space: nowrap">"one of $B$ and $C$</span> is a prefix of the other".

We also use $\mathsf{log} \preceq \mathsf{log}'$ (without a subscript <span style="white-space: nowrap">on $\preceq$)</span> to mean that the transaction ledger $\mathsf{log}$ is a prefix <span style="white-space: nowrap">of $\mathsf{log}'$.</span> Similarly to $\preceq\hspace{-0.5em}\succeq_{\mathrm{*}}$ above, $\mathsf{log} \preceq\hspace{-0.5em}\succeq \mathsf{log}'$ means that either <span style="white-space: nowrap">$\mathsf{log} \preceq \mathsf{log}'$ or $\mathsf{log}' \preceq \mathsf{log}$;</span> that is, <span style="white-space: nowrap">"one of $\mathsf{log}$ and $\mathsf{log}'$</span> is a prefix of the other".

The notation $[f(X) \text{ for } X \preceq_{\mathrm{*}} Y]$ means the sequence of $f(X)$ for each <span style="white-space: nowrap">$\mathrm{*}$‑block $X$</span> in chain order from genesis up to and <span style="white-space: nowrap">including $Y$.</span> <span style="white-space: nowrap">($X$ is</span> a bound variable within this construct.)

## Subprotocols

As in Snap‑and‑Chat, we depend on a <span style="white-space: nowrap">BFT protocol $\Pi_{\mathrm{origbft}}$,</span> and a <span style="white-space: nowrap">best‑chain protocol $\Pi_{\mathrm{origbc}}$.</span>

```admonish info
See [this terminology note](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view#Terminology-note) for why we do not call $\Pi_{\mathrm{origbc}}$ a "longest‑chain" protocol.
```

We modify $\Pi_{\mathrm{origbft}}$ <span style="white-space: nowrap">(resp. $\Pi_{\mathrm{origbc}}$)</span> to give $\Pi_{\mathrm{bft}}$ <span style="white-space: nowrap">(resp. $\Pi_{\mathrm{bc}}$)</span> by adding structural elements, changing validity rules, and potentially changing the specified behaviour of honest nodes.

A Crosslink node must participate in <span style="white-space: nowrap">both $\Pi_{\mathrm{bft}}$ and $\Pi_{\mathrm{bc}}$;</span> that is, it must maintain a view of the state of each protocol. Acting in more specific roles such as bft‑proposer, bft‑validator, or bc‑block‑producer is optional, but we assume that all such actors are Crosslink nodes.

### Model for BFT protocols (Π<sub>{origbft,bft}</sub>)

A player's view in $\Pi_{\mathrm{*bft}}$ includes a set of <span style="white-space: nowrap">$\mathrm{*}$bft‑block chains</span> each rooted at a fixed genesis <span style="white-space: nowrap">$\mathrm{*}$bft‑block $\mathcal{O}_{\mathrm{*bft}}$.</span> There is a <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑validity</span> rule (specified below), which depends only on the content of the block and its ancestors. A non‑genesis block can only be <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑valid</span> if its parent is $\mathrm{*}$bft‑block‑valid. <span style="white-space: nowrap">A $\mathrm{*}$bft‑valid‑chain</span> is a chain of <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑valid</span> blocks.

A <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal</span> refers to a parent <span style="white-space: nowrap">$\mathrm{*}$bft‑block,</span> and specifies an epoch. The content of a proposal is signed by the proposer using a strongly unforgeable signature scheme. We consider the proposal to include this signature. There is a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal‑validity</span> rule, depending only on the content of the proposal and its parent block, and the validity of the proposer's signature.

```admonish info
We will shorten <span style="white-space: nowrap">"$\mathrm{*}$bft‑block‑valid $\mathrm{*}$bft‑block"</span> to <span style="white-space: nowrap">"$\mathrm{*}$bft‑valid‑block",</span> and <span style="white-space: nowrap">"$\mathrm{*}$bft‑proposal‑valid $\mathrm{*}$bft‑proposal"</span> to <span style="white-space: nowrap">"$\mathrm{*}$bft‑valid‑proposal".</span>
```

For each epoch, there is a fixed number of voting units distributed between the players, which they use to vote for a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal.</span> We say that a voting unit has been cast for a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal $P$</span> at a given time in a <span style="white-space: nowrap">$\mathrm{*}$bft‑execution,</span> <span style="white-space: nowrap">if and only if</span> <span style="white-space: nowrap">$P$ is $\mathrm{*}$bft‑proposal‑valid</span> and a ballot <span style="white-space: nowrap">for $P$</span> authenticated by the holder of the voting unit exists at that time.

If, and only if, the votes cast for a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal $P$</span> satisfy a notarization rule at a given time in a <span style="white-space: nowrap">$\mathrm{*}$bft‑execution,</span> then it is possible to obtain a valid <span style="white-space: nowrap">$\mathrm{*}$bft‑notarization‑proof $\mathsf{proof}_P$.</span> The notarization rule must require at least a two‑thirds absolute supermajority of voting units <span style="white-space: nowrap">in $P$'s epoch</span> to have been cast <span style="white-space: nowrap">for $P$.</span> It may also require other conditions.

A voting unit is cast non‑honestly for an epoch's proposal iff:
* it is cast other than by the holder of the unit (due to key compromise or any flaw in the voting protocol, for example); or
* it is double‑cast (i.e. for distinct proposals); or
* the holder of the unit following the conditions for honest voting <span style="white-space: nowrap">in $\Pi_{\mathrm{*bft}}$,</span> according to its view, should not have cast that vote.

```admonish success
An execution of $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property if at any epoch in the execution, *strictly* fewer than one third of the total voting units for that epoch are cast non‑honestly.
```

```admonish info
It may be the case that a ballot marked for $P$ is not in honest view when it is used to create a notarisation proof for $P$. Since we are not assuming synchrony, it may also be the case that such a ballot is in honest view but that any given node has not received it (and perhaps will never receive it).

There may be multiple distinct ballots or distinct ballot messages attempting to cast a given voting unit for the same proposal; this is undesirable for bandwidth usage, but it is not necessary to consider it to be non‑honest behaviour for the purpose of security analysis, as long as such ballots are not double‑counted toward the two‑thirds threshold.
```

A <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> consists <span style="white-space: nowrap">of $(P, \mathsf{proof}_P)$</span> re‑signed by the same proposer using a strongly unforgeable signature scheme. It is <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑valid</span> iff:
* $P$ is <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal‑valid</span>; and
* $\mathsf{proof}_P$ is a valid proof that some subset of votes cast for $P$ are sufficient to satisfy the notarization rule; and
* the proposer's outer signature <span style="white-space: nowrap">on $(P, \mathsf{proof}_P)$</span> is valid.

<span style="white-space: nowrap">A $\mathrm{*}$bft‑proposal's</span> parent reference hashes the entire <span style="white-space: nowrap">parent $\mathrm{*}$bft‑block,</span> i.e. proposal, proof, and outer signature.

```admonish info
Neither $\mathsf{proof}_P$ nor the proposer's outer signature is unique for a <span style="white-space: nowrap">given $P$.</span> The proposer's outer signature is however third‑party nonmalleable, by definition of a strongly unforgeable signature scheme. An <span style="white-space: nowrap">"honest $\mathrm{*}$bft‑proposal"</span> is a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal</span> made for a given epoch by a proposer who is honest in that epoch. Such a proposer will only create one proposal and only sign at most once for each epoch, and so there will be at most one <span style="white-space: nowrap">"honestly submitted"</span> <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> for each epoch.

It is possible for there to be multiple <span style="white-space: nowrap">$\mathrm{*}$bft‑valid‑blocks</span> for the same proposal, with different notarization proofs and/or outer signatures, if the proposer is not honest. However, the property that there will be at most one <span style="white-space: nowrap">"honestly submitted"</span> <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> for each epoch is important for liveness, even though we cannot guarantee that any particular proposer for an epoch is honest. ==TODO check that we are correctly using this in the liveness analysis.==
```

There is an efficiently computable function <span style="white-space: nowrap">$\mathrm{*}\textsf{bft‑last‑final} :: \mathrm{*}\textsf{bft‑block} \to \mathrm{*}\textsf{bft‑block} \cup \{\bot\}$.</span> <span style="white-space: nowrap">For a $\mathrm{*}$bft‑block‑valid</span> input <span style="white-space: nowrap">block $C$,</span> this function outputs the last ancestor of $C$ that is final in the <span style="white-space: nowrap">context of $C.$</span>

```admonish info
The chain of ancestors is unambiguously determined because a <span style="white-space: nowrap"> $\mathrm{*}$bft‑proposal's</span> parent reference hashes the entire parent <span style="white-space: nowrap">$\mathrm{*}$bft‑block;</span> each <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> commits to a proposal; and the parent hashes are collision-resistant. This holds despite the caveat mentioned above that there may be multiple <span style="white-space: nowrap">$\mathrm{*}$bft‑valid‑blocks</span> for the same proposal.
```

<span style="white-space: nowrap">$\mathrm{*}\textsf{bft‑last‑final}$</span> must satisfy all of the following:

* $\mathrm{*}\textsf{bft-last-final}(C) = \bot \iff C$ is not $\mathrm{*}$bft‑block‑valid.
* If $C$ is $\mathrm{*}$bft‑block‑valid, then:
  * $\mathrm{*}\textsf{bft-last-final}(C) \preceq_{\mathrm{*bft}} C$ (and therefore it must also be <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑valid);</span>
  * for all <span style="white-space: nowrap">$\mathrm{*}$bft‑valid‑blocks</span> $D$ such that <span style="white-space: nowrap">$C \preceq_{\mathrm{*bft}} D$,</span> <span style="white-space: nowrap">$\mathrm{*}\textsf{bft-last-final}(C) \preceq_{\mathrm{*bft}} \mathrm{*}\textsf{bft-last-final}(D)$.</span>
* $\mathrm{*}\textsf{bft-last-final}(\mathcal{O}_{\mathrm{*bft}}) = \mathcal{O}_{\mathrm{*bft}}$.

```admonish info
It is correct to talk about the "last final block" of a given chain (that is, each <span style="white-space: nowrap">$\mathrm{*}$bft‑valid-block $C$</span> unambiguously determines a <span style="white-space: nowrap">$\mathrm{*}$bft‑valid-block</span> <span style="white-space: nowrap">$\mathrm{*}\textsf{bft-last-final}(C)$)</span>, but it is not correct to refer to a given <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> as objectively <span style="white-space: nowrap">"$\mathrm{*}$bft‑final".</span>
```

A particular BFT protocol might need adaptations to fit it into this model <span style="white-space: nowrap">for $\Pi_{\mathrm{origbft}}$,</span> *before* we apply the Crosslink modifications to <span style="white-space: nowrap">obtain $\Pi_{\mathrm{bft}}$.</span> Any such adaptions are necessarily protocol-specific. In particular,
* origbft‑proposal‑validity should correspond to the strongest property of an origbft‑proposal that is objectively and feasibly verifiable from the content of the proposal and its parent origbft‑block at the time the proposal is made. It must include verification of the proposer's signature.
* origbft‑block‑validity should correspond to the strongest property of an origbft‑block that is objectively and feasibly verifiable from the content of the block and its ancestors at the time the block is added to an origbft‑chain. It should typically include all of the relevant checks from origbft‑proposal‑validity that apply to the created block (or equivalent checks). It must also include verification of the notarization proof and the proposer's outer signature.
* If a node observes an origbft‑valid block $C$, then it should be infeasible for an adversary to cause a rollback in that node's view <span style="white-space: nowrap">past $\textsf{origbft-last-final}(C)$,</span> and the view of the chain <span style="white-space: nowrap">up to $\textsf{origbft-last-final}(C)$</span> should agree with that of all other honest nodes. This is formalized in the next section.

#### Safety of $\Pi_{\mathrm{*bft}}$

The intuition behind the following safety property is that:
* For $\Pi_{\mathrm{*bft}}$ to be safe, it should never be the case that two honest nodes observe (at any time) <span style="white-space: nowrap">$\mathrm{*}$bft‑blocks $B$ and $B'$</span> respectively that they each consider final in some context, but $B \preceq\hspace{-0.5em}\succeq_{\mathrm{*bft}} B'$ does not hold.
* By definition, an honest node observes a <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> to be final in the context of another <span style="white-space: nowrap">$\mathrm{*}$bft‑block $C$,</span> <span style="white-space: nowrap">iff $B \preceq_{\mathrm{*bft}} \mathrm{*}\textsf{bft-last-final}(C)$.</span>

We say that a <span style="white-space: nowrap">$\mathrm{*}$bft‑block</span> is <span style="white-space: nowrap">"in honest view"</span> if a party observes it at some time at which that party is honest.

```admonish success
An execution of $\Pi_{\mathrm{*bft}}$ has **Final Agreement** iff for all <span style="white-space: nowrap">$\mathrm{*}$bft‑valid blocks $C$</span> in honest view at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$C'$ in honest view</span> at <span style="white-space: nowrap">time $t'$,</span> we have <span style="white-space: nowrap">$\mathrm{*}\textsf{bft-last-final}(C) \preceq\hspace{-0.5em}\succeq_{\mathrm{*bft}} \mathrm{*}\textsf{bft-last-final}(C')\,$.</span>
```

Note that it is possible for this property to hold for an execution of a BFT protocol in an asynchronous communication model. The following caveat applies: if the **one‑third bound on non‑honest voting** property is *ever* broken at any time in an execution, then it may not be possible to maintain **Final Agreement** from that point on. This is an area of possible improvement in the design and analysis, left for future work.

```admonish info collapsible=true title="Adapting the Streamlet BFT protocol."
Streamlet as described in [[CS2020]](https://eprint.iacr.org/2020/088.pdf) has three possible states of a block in a player's view:
* "valid" (but not notarized or final);
* "notarized" (but not final);
* "final".

By "valid" the Streamlet paper means just that it satisfies the structural property of being part of a block chain with parent hashes. The role of <span style="white-space: nowrap">$\mathrm{*}$bft‑block‑validity</span> in our model corresponds roughly to Streamlet's "notarized". It turns out that with some straightforward changes relative to Streamlet, we can identify "origbft‑block‑valid" with "notarized" and consider an origbft‑valid‑chain to only consist of notarized blocks. This is not obvious, but is a useful simplification.

Here is how the paper defines "notarized":

> When a block gains votes from at least $2n/3$ distinct players, it becomes notarized. A chain is notarized if its constituent blocks are all notarized.

This implies that blocks can be added to chains independently of notarization. However, the paper also says that a leader always proposes a block extending from a notarized chain. Therefore, only *notarized* chains really matter in the protocol.

In unmodified Streamlet, the order in which a player sees signatures might cause it to view blocks as notarized out of order. Streamlet's security analysis is in a synchronous model, and assumes for liveness that any vote will have been received by all players within two epochs.

In Crosslink, however, we need origbft‑block‑validity to be an objectively and feasibly verifiable property. We also would prefer reliable message delivery within bounded time not to be a basic assumption of our communication model. (This does not dictate what assumptions about message delivery are made for particular security analyses.) If we did not make a modification to the protocol to take this into account, then some Crosslink nodes might receive a two‑thirds absolute supermajority of voting messages and consider a BFT block to be notarized, while others might never receive enough of those messages.

Obviously a *proposal* cannot include signatures on itself --- but the block formed from it can include proofs about the proposal and signatures. We can therefore say that when a proposal gains a two‑thirds absolute supermajority of signatures, a block is created from it that contains a proof (such as an aggregate signature) that it had such a supermajority. For example, we can have the proposer itself make this proof once it has enough votes, sign the <span style="white-space: nowrap">resulting $(P, \mathsf{proof}_P)$</span> to create a block, then *submit* that block in a separate message. (The proposer has most incentive to do this in order to gain whatever reward attaches to a successful proposal; it can outsource the proving task if needed.) Then the origbft‑block‑validity rule can require a valid supermajority proof, which is objectively and feasibly verifiable. Players that see an origbft‑block‑valid block can immediately consider it notarized.

Note that for the liveness analysis to be unaffected, we need to assume that the combined latency of messages, of collecting and aggregating signatures, and of block submission is such that all players will receive a notarized block corresponding to a given proposal (rather than just all of the votes for the proposal) within two epochs. Alternatively we could re‑do the timing analysis.

With this change, "origbft‑block‑valid" and "notarized" do not need to be distinguished.

Streamlet's finality rule is:

> If in any notarized chain, there are three adjacent blocks with consecutive epoch numbers, the prefix of the chain up to the second of the three blocks is considered final. When a block becomes final, all of its prefix must be final too.

We can straightforwardly express this as an $\textsf{origbft-last-final}$ function of a context block $C$, as required by the model:

For an origbft‑valid block $C$, $\textsf{origbft-last-final}(C)$ is the last origbft‑valid block $B \preceq_{\mathrm{origbft}} C$ such that either $B = \mathcal{O}_{\mathrm{origbft}}$ or $B$ is the second block of a group of three adjacent blocks with consecutive epoch numbers.

Note that "When a block becomes final, all of its prefix must be final too." is implicit in the model.
```

### Model for best-chain protocols (Π<sub>{origbc,bc}</sub>)

A node's view in $\Pi_{\mathrm{*bc}}$ includes a set of <span style="white-space: nowrap">$\mathrm{*}$bc‑block chains</span> each rooted at a fixed <span style="white-space: nowrap">genesis $\mathrm{*}$bc‑block $\mathcal{O}_{\mathrm{*bc}}$.</span> There is a <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑validity rule</span> (often described as a collection of <span style="white-space: nowrap">"consensus rules"),</span> depending only on the content of the block and its ancestors. A non‑genesis block can only be <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑valid</span> if its parent is <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑valid.</span> <span style="white-space: nowrap">By "$\mathrm{*}$bc‑valid‑chain"</span> we mean a chain of <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑valid blocks.</span>

The definition of <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑validity</span> is such that it is hard for a block producer to extend a <span style="white-space: nowrap">$\mathrm{*}$bc‑valid‑chain</span> unless they are selected by a random process that chooses a block producer in proportion to their resources with an approximately known and consistent time distribution, subject to some assumption about the total proportion of resources held by honest nodes.

There is a function $\mathsf{score} :: \mathrm{*}\textsf{bc‑valid‑chain} \to \mathsf{Score}$, with <span style="white-space: nowrap">$<$ a [strict total ordering](https://proofwiki.org/wiki/Definition:Strict_Total_Ordering)</span> <span style="white-space: nowrap">on $\mathsf{Score}$.</span> An honest node will choose one of the <span style="white-space: nowrap">$\mathrm{*}$bc‑valid‑chains</span> with highest score as the <span style="white-space: nowrap">$\mathrm{*}$bc‑best‑chain</span> in its view. Any rule can be specified for breaking ties.

The $\mathsf{score}$ function is required to satisfy $\mathsf{score}(\mathsf{ch} \lceil_{\!\mathrm{*bc}}^1) \lt \mathsf{score}(\mathsf{ch})$ for any non‑genesis <span style="white-space: nowrap">$\mathrm{*}$bc‑valid‑chain $\mathsf{ch}$.</span>

```admonish info
For a Proof‑of‑Work protocol, the score of a <span style="white-space: nowrap">$\mathrm{*}$bc‑chain</span> should be its accumulated work.
```

Unless an adversary is able to censor knowledge of other chains from the node's view, it should be difficult to cause the node to switch to a chain with a last common ancestor more than <span style="white-space: nowrap">$\sigma$ blocks</span> back from the tip of their previous <span style="white-space: nowrap">$\mathrm{*}$bc‑best‑chain.</span>

Following [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf), we use the notation $\mathsf{ch}_i^t$ for <span style="white-space: nowrap">node $i$'s $\mathrm{*}$bc‑best‑chain</span> at time $t$.

A <span style="white-space: nowrap">$\mathrm{*}$bc‑context</span> allows testing whether a given transaction is contextually valid <span style="white-space: nowrap">("$\mathrm{*}$bc‑context‑valid"),</span> and adding it to the context if it is. Given a context $\mathsf{ctx}$, the resulting sequence of contextually valid transactions since genesis can be obtained as $\textsf{context-txns}(\mathsf{ctx})$. It is possible to obtain a <span style="white-space: nowrap">$\mathrm{*}$bc‑context</span> corresponding to the state after the <span style="white-space: nowrap">genesis $\mathrm{*}$bc‑block.</span>

We assume that the only reasons for a transaction to be contextually invalid are that it double‑spends, or that an input is missing.

```admonish info collapsible=true title="Why is this assumption needed?"
It is needed for equivalence of the following two ways to construct <span style="white-space: nowrap">$\mathsf{LOG}_{\{\mathrm{fin},\mathrm{bda}\}}$:</span>

1. Concatenate the transactions from each bft‑block snapshot of a bc‑chain, and sanitize the resulting transaction sequence by including each transaction iff it is contextually valid.
2. Concatenate the *bc‑blocks* from each bft‑block snapshot of a bc‑chain, remove duplicate *blocks*, and only then sanitize the resulting transaction sequence by including each transaction iff it is contextually valid.

We want these to be equivalent to enable a crucial optimization. In practice there will be many duplicate blocks from chain prefixes in the input to sanitization, and so a literal implementation of the first variant would have to recheck all duplicate transactions for contextual validity. That would have at least $O(n^2)$ complexity (more likely $O(n^2 \log n)$) in the length $n$ of the block chain, because the length of each final snapshot grows with $n$. But in the second variant, we can just concatenate suffixes of each snapshot omitting any bc‑blocks that are common to a previous snapshot.

Given that the only reasons for a transaction to be contextually invalid are double‑spends and missing inputs, the argument for equivalence is that:
* If a transaction is omitted due to a double‑spend, then any subsequent time it is checked, that input will still have been double‑spent.
* If a transaction is omitted due to a missing input, this can only be because an earlier transaction in the input to sanitization was omitted. So the structure of omitted transactions forms a DAG in which parent links must be to *earlier* omitted transactions. The roots of the DAG are at double-spending transactions, which cannot be reinstated (that is, included after they had previously been excluded). A child cannot be reinstated until its parents have been reinstated. Therefore, no transactions are reinstated.

It might be possible to relax this assumption, but it would require additional analysis to ensure that the above equivalence still holds.
```
${}$
A <span style="white-space: nowrap">$\mathrm{*}$bc‑block</span> logically contains a sequence of transactions. In addition to other rules, a block is only <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑valid</span> if its transactions, taken in order, are all <span style="white-space: nowrap">$\mathrm{*}$bc‑context‑valid</span> given previous blocks and previous transactions in the block.

```admonish info collapsible=true title="Detail of 'logically contains' for Zcash."
In Zcash, a block logically contains its transactions by having the block header commit to a Merkle tree over txids, and another Merkle tree (in the same transaction order) over witness hashes. A txid and witness hash together authenticate all data fields of a transaction.

For v5 transactions, the txid commits to effecting data (that determines the effect of the transaction) and the witness hash commits to witness data (signatures and proofs). For earlier transaction versions, the witness hash is null and the txid commits to all transaction data.

When a block is downloaded, its transactions are parsed and its header is checked against the transaction data. Assuming no bugs or errors in the design, this is effectively equivalent to the block data being directly authenticated by the header.
```

```admonish info collapsible=true title="Is this model of contextual validity sufficient for Zcash?"
There are several Zcash consensus rules that mention block height or position within a block, or that depend on other transactions in a block:

[Transaction consensus rule](https://zips.z.cash/protocol/protocol.pdf#txnconsensus):
* A coinbase transaction for a non‑genesis block MUST have a script that, as its first item, encodes the block height [in a specified way].

In addition, a coinbase transaction is implicitly able to spend the total amount of fees of other transactions in the block.

[Block consensus rule](https://zips.z.cash/protocol/protocol.pdf#blockheader):
* The first transaction in a block MUST be a coinbase transaction, and subsequent transactions MUST NOT be coinbase transactions.

[Payment of Founders' Reward](https://zips.z.cash/protocol/protocol.pdf#foundersreward):
* [Pre‑Canopy] A coinbase transaction at $\mathsf{height} \in \{1..\mathsf{FoundersRewardLastBlockHeight}\}$ MUST include at least one output that pays exactly $\mathsf{FoundersReward}(\mathsf{height})$ zatoshi with [details of script omitted].

[Payment of Funding Streams](https://zips.z.cash/protocol/protocol.pdf#fundingstreams):
* [Canopy onward] The coinbase transaction at block height $\mathsf{height}$ MUST contain at least one output per funding stream $\mathsf{fs}$ active at $\mathsf{height}$, that pays $\mathsf{fs.Value}(\mathsf{height})$ zatoshi in the prescribed way to the stream’s recipient address [...]

However, none of these need to be treated as contextual validity rules.

The following [transaction consensus rule](https://zips.z.cash/protocol/protocol.pdf#txnconsensus) must be modified:
* A transaction MUST NOT spend a transparent output of a coinbase transaction from a block less than 100 blocks prior to the spend. Note that transparent outputs of coinbase transactions include Founders’ Reward outputs and transparent funding stream outputs.

To achieve the intent, it is sufficient to change this rule to only allow coinbase outputs to be spent if their coinbase transaction has been finalized.

If we assume that coinbase block subsidies and fees, and the position of coinbase transactions as the first transaction in each block have already been checked as <span style="white-space: nowrap">$\mathrm{*}$bc‑block‑validity rules,</span> then the model is sufficient.
```
${}$
A "coinbase transaction" is a <span style="white-space: nowrap">$\mathrm{*}$bc‑transaction</span> that only distributes newly issued funds and has no inputs.

Define $\textsf{is-coinbase-only-block} :: \mathrm{*}\textsf{bc-block} \to \mathsf{boolean}$ so that $\textsf{is-coinbase-only-block}(B) = \mathsf{true}$ iff $B$ has exactly one transaction that is a coinbase transaction.

Each <span style="white-space: nowrap">$\mathrm{*}$bc‑block</span> is summarized by a <span style="white-space: nowrap">$\mathrm{*}$bc‑header</span> that commits to the block. There is a notion of <span style="white-space: nowrap">$\mathrm{*}$bc‑header‑validity</span> that is necessary, but not sufficient, for validity of the block. We will only make the distinction between <span style="white-space: nowrap">$\mathrm{*}$bc‑headers</span> and <span style="white-space: nowrap">$\mathrm{*}$bc‑blocks</span> when it is necessary to avoid ambiguity.

```admonish info collapsible=true title="Header validity for Proof‑of‑Work protocols."
In a Proof‑of‑Work protocol, it is normally possible to check the Proof‑of‑Work of a block using only the header. There is a difficulty adjustment function that determines the target difficulty for a block based on its parent chain. So, checking that the correct difficulty target has been used relies on knowing that the header's parent chain is valid.

Checking header validity before expending further resources on a purported block can be relevant to mitigating denial‑of‑service attacks that attempt to inflate validation cost.
```
${}$
Typically, Bitcoin‑derived best chain protocols do not need much adaptation to fit into this model. The model still omits some details that would be important to implementing Crosslink, but distracting for this level of abstraction.

#### Safety of $\Pi_{\mathrm{*bc}}$

We make an assumption on executions of $\Pi_{\mathrm{origbc}}$ that we will call **Prefix Consistency** (introduced in [[PSS2016](https://eprint.iacr.org/2016/454.pdf), section 3.3] as just "consistency"):

```admonish success
An execution of $\Pi_{\mathrm{*bc}}$ has **Prefix Consistency** at confirmation depth $\sigma$, iff <span style="white-space: nowrap">for all times $t \leq t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> we have that <span style="white-space: nowrap">$\mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma\, \preceq_{\mathrm{*bc}} \mathsf{ch}_j^{t'}$.</span>
```

```admonish info collapsible=true title="Explain the confusion in the literature about what variants of this property are called."
The literature uses the same name, <span style="white-space: nowrap">"common‑prefix property",</span> for two different properties of very different strength.

[[PSS2016](https://eprint.iacr.org/2016/454.pdf), section 3.3] introduced the stronger variant. That paper first describes the weaker variant, calling it the "common‑prefix property by Garay et al [[GKL2015]](https://link.springer.com/chapter/10.1007/978-3-662-46803-6_10)." Then it explains what is essentially a bug in that variant, and describes the stronger variant which it just calls "consistency":

> The common‑prefix property by Garay et al [[GKL2015]](https://link.springer.com/chapter/10.1007/978-3-662-46803-6_10), which was already considered and studied by Nakamoto [[Nakamoto2008]](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.221.9986), requires that in any round $r$, the record chains of any two honest players $i$, $j$ agree on all, but potentially the last $T$, records. We note that this property (even in combination with the other two desiderata [of Chain Growth and Chain Quality]) provides quite weak guarantees: even if any two honest parties perfectly agree on the chains, the chain could be completely different on, say, even rounds and odd rounds. We here consider a stronger notion of consistency which additionally stipulates players should be consistent with their “future selves”.
>
> Let $\mathsf{consistent}^T(\mathsf{view}) = 1$ iff for <span style="white-space: nowrap">all rounds $r \leq r'$,</span> and <span style="white-space: nowrap">all players $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest at $\mathsf{view}^r$</span> and <span style="white-space: nowrap">$j$ is honest at $\mathsf{view}^{r'}$,</span> we have that the prefixes of $\mathcal{C}_i^r(\mathsf{view})$ and $\mathcal{C}_j^{r'}(\mathsf{view})$ consisting of the first $\ell = |\mathcal{C}_i^r(\mathsf{view})| - T$ records are identical.

Unfortunately, [[GKL2020]](https://eprint.iacr.org/2014/765.pdf), which is a revised version of [[GKL2015]](https://link.springer.com/chapter/10.1007/978-3-662-46803-6_10), switches to the stronger variant without changing the name. (The [eprint version history](https://eprint.iacr.org/archive/versions/2014/765) may be useful; the change was made in [version 20181013:200033](https://eprint.iacr.org/archive/2014/765/20181013:200033), page 17.)

Note that [GKL2020] uses an adaptive‑corruption model, "meaning that the adversary is allowed to take control of parties on the fly", and so their wording in Definition 3:
> ... for any pair of <span style="white-space: nowrap">honest players $P_1$, $P_2$</span> adopting the <span style="white-space: nowrap">chains $\mathcal{C}_1$, $\mathcal{C}_2$</span> at rounds $r_1 \leq r_2$ in <span style="white-space: nowrap"><font style="font-variant: small-caps;">view</font>$^{t,n}_{\Pi,\mathcal{A},\mathcal{Z}}$</span> respectively, it holds that <span style="white-space: nowrap">$\mathcal{C}_1^{\lceil k} \preceq \mathcal{C}_2$.</span>

is intended to mean the same as our

> ... <span style="white-space: nowrap">for all times $t \leq t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> we have that <span style="white-space: nowrap">$\mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma\, \preceq_{\mathrm{*bc}} \mathsf{ch}_j^{t'}$.</span>

(The latter is closer to [[PSS2016]](https://eprint.iacr.org/2016/454.pdf).)

Incidentally, I cannot find any variant of this property in [[Nakamoto2008]](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.221.9986). Maybe implicitly, but it's a stretch.
```

```admonish info collapsible=true title="Discussion of [GKL2020]'s communication model and network partition."
**Prefix Consistency** implies that, in the relevant executions, the network of honest nodes is never <span style="white-space: nowrap">partitioned ---</span> unless (roughly speaking) any partition lasts only for a short length of time relative to $\sigma$ block times. <span style="white-space: nowrap">If node $i$</span> is on one side of a full partition and <span style="white-space: nowrap">node $j$</span> on the other, then after <span style="white-space: nowrap">node $i$'s</span> best chain has been extended by more than <span style="white-space: nowrap">$\sigma$ blocks,</span> $\mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma$ will contain information that has no way to get to <span style="white-space: nowrap">node $j$.</span> And even if the partition is incomplete, we cannot guarantee that the Prefix Consistency property will hold for any given pair of nodes.

And yet, [[GKL2020]](https://eprint.iacr.org/2014/765.pdf) claims to *prove* this property from other assumptions. So we know that those assumptions must also rule out a long partition between honest nodes. In fact the required assumption is implicit in the communication model:
* A synchronous network cannot be partitioned.
* A partially synchronous network <span style="white-space: nowrap">---that is,</span> providing reliable delivery with bounded but <span style="white-space: nowrap">unknown delay---</span> cannot be partitioned for longer than the delay.

We might be concerned that these implicit assumptions are stronger than we would like. In practice, the peer‑to‑peer network protocol of Bitcoin and Zcash attempts to flood blocks to all nodes. This protocol might have weaknesses, but it is not intended to (and plausibly does not) depend on all messages being received. (Incidentally, Streamlet also implicitly floods messages to all nodes.)

Also, Streamlet and many other BFT protocols do *not* assume *for safety* that the network is not partitioned. That is, BFT protocols can be safe in a fully asynchronous communication model with unreliable messaging. That is why we avoid taking synchrony or partial synchrony as an implicit assumption of the communication model, or else we could end up with a protocol with weaker safety properties than $\Pi_{\mathrm{origbft}}$ alone.

This leaves the question of whether the **Prefix Consistency** property is still too strong, even if we do not rely on it for the analysis of safety when $\Pi_{\mathrm{bft}}$ has not been subverted. In particular, if a particular <span style="white-space: nowrap">node $h$</span> is not well-connected to the rest of the network, then that will inevitably affect <span style="white-space: nowrap">node $h$'s</span> security, but should not affect other honest nodes' security.

Fortunately, it is not the case that disconnecting a single <span style="white-space: nowrap">node $h$</span> from the network causes the security assumption to be voided. The solution is to view $h$ as not honest in that case (even though it would follow the protocol if it could). This achieves the desired effect within the model, because other nodes can no longer rely on <span style="white-space: nowrap">$h$'s honest input.</span> Although viewing $h$ as potentially adversarial might seem conservative from the point of view of other nodes, bear in mind that an adversary could censor an arbitrary subset of incoming and outgoing messages from the node, and this may be best modelled by considering it to be effectively controlled by the adversary.
```
${}$
Prefix Consistency compares the <span style="white-space: nowrap">$\sigma$-truncated chain</span> of <span style="white-space: nowrap">some node $i$</span> with the *untruncated* chain of <span style="white-space: nowrap">node $j$.</span> For our analysis of safety of the derived ledgers, we will also need to make an assumption on executions of $\Pi_{\mathrm{origbc}}$ that at <span style="white-space: nowrap">any given time $t$,</span> any two <span style="white-space: nowrap">honest nodes $i$ and $j$</span> **agree** on their confirmed <span style="white-space: nowrap">prefixes ---</span> with only the caveat that one may have observed more of the chain than the other. <span style="white-space: nowrap">That is:</span>

```admonish success
An execution of $\Pi_{\mathrm{*bc}}$ has **Prefix Agreement** at confirmation <span style="white-space: nowrap">depth $\sigma$,</span> iff <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> we have <span style="white-space: nowrap">$\mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma\, \preceq\hspace{-0.5em}\succeq_{\mathrm{*bc}} \mathsf{ch}_j^{t'} \lceil_{\!\mathrm{*bc}}^\sigma$.</span>
```

```admonish info collapsible=true title="Why are this property, and Prefix Consistency above, stated as unconditional properties of protocol *executions*, rather than as probabilistic assumptions?"
Our security arguments that depend on these properties will all be of the form "in an execution where (safety properties) are not violated, (undesirable thing) cannot happen".

It is not necessary to involve probability in arguments of this form. Any probabilistic reasoning can be done separately.

In particular, if a statement of this form holds, and (safety properties) are violated with probability <span style="white-space: nowrap">at most $p$</span> under certain conditions, then it immediately follows that under those conditions (undesirable thing) happens with probability <span style="white-space: nowrap">at most $p$.</span> Furthermore, (undesirable thing) can only happen *after* (safety properties) have been violated, because the execution up to that point has been an execution in which (safety properties) are *not* violated.

With few exceptions, involving probability in a security argument is best done only to account for nondeterministic choices in the protocol itself. This is opinionated advice, but I think a lot of security proofs would be simpler if inherently probabilistic arguments were more distinctly separated from unconditional ones.

In the case of the Prefix Agreement property, an alternative approach would be to prove that Prefix Agreement holds with some probability given Prefix Consistency and some other chain properties. This is what [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) does in its <span style="white-space: nowrap">Theorem 2,</span> which essentially says that under certain conditions Prefix Agreement holds except with <span style="white-space: nowrap">probability $e^{-\Omega(\sqrt{\sigma})}$.</span>

The conclusions that can be obtained from this approach are necessarily probabilistic, and depending on the techniques used, the proof may not be tight; that is, the proof may obtain a bound on the probability of failure that is (either asymptotically or concretely) higher than needed. This is the case for <span>[[NTT2020](https://eprint.iacr.org/2020/1091.pdf), Theorem 2];</span> <span style="white-space: nowrap">footnote 10</span> in that paper points out that the expression for the probability can be asymptotically improved:

> Using the recursive bootstrapping argument developed in <span>[[DKT+2020](https://eprint.iacr.org/2020/601.pdf), Section 4.2],</span> it is possible to bring the error <span style="white-space: nowrap">probability $e^{-\Omega(\sqrt{\sigma})}$</span> as close to an exponential decay as possible. In this context, <span style="white-space: nowrap">for any $\epsilon > 0$,</span> it is possible to find <span style="white-space: nowrap">constants $A_\epsilon$, $a_\epsilon$</span> such that $\Pi_{\mathrm{lc}}(p)$ is secure after <span style="white-space: nowrap">*C*$(\max(\mathsf{GST}, \mathsf{GAT}))$</span> with confirmation time $T_{\mathrm{confirm}} = \sigma$ except with <span style="white-space: nowrap">probability $A_\epsilon\, e^{-a_\epsilon\, \sigma^{1 - \epsilon}}$.</span>

(Here $p$ is the probability that any given node gets to produce a block in any given time slot.)

In fact none of the proofs of security properties for Snap‑and‑Chat depend on the particular expression <span style="white-space: nowrap">$e^{-\Omega(\sqrt{\sigma})}$;</span> for example in the proofs of <span style="white-space: nowrap">Lemma 5</span> and <span style="white-space: nowrap">Theorem 1,</span> this probability just "passes through" the proof from the premisses to the conclusion, because the argument is not probabilistic. The same will be true of our safety arguments.

Talking about what is possible in particular executions has further advantages:
* It sidesteps the issue of how to interpret results in the partially synchronous model, when we do not know what <span style="white-space: nowrap">*C*$(\max(\mathsf{GST}, \mathsf{GAT}))$ is.</span> See also the critique of applying the partially synchronous model to block-chain protocols under "Discussion of [GKL2020]'s communication model and network partition" above.
* We do not require $\Pi_{\mathrm{bc}}$ to be a Nakamoto‑style Proof‑of‑Work block chain protocol. Some other kind of protocol could potentially satisfy Prefix Consistency and Prefix Agreement.
* It is not clear whether a $e^{-\Omega(\sqrt{\sigma})}$ probability of failure would be concretely adequate. That would depend on the value of $\sigma$ and the constant hidden by the $\Omega$ notation. The asymptotic property using $\Omega$ tells us whether a sufficiently large $\sigma$ *could* be chosen, but we are more interested in what needs to be assumed for a given concrete choice of $\sigma$.
* If a violation of a required safety property occurs *in a given execution*, then the safety argument for Crosslink that depended on the property fails for that execution, regardless of what the probability of that occurrence was. This approach therefore more precisely models the consequences of such violations.
```

```admonish info collapsible=true title="Why, intuitively, should we believe that Prefix Agreement and Prefix Consistency for a large enough confirmation depth hold with high probability for executions of a PoW‑based best‑chain protocol?"
Roughly speaking, the intuition behind both properties is as follows:

Honest nodes are collectively able to find blocks faster than an adversary, and communication between honest nodes is sufficiently reliable that they act as a combined network racing against that adversary. Then by the argument in [[Nakamoto2008]](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.221.9986), modified by [[GP2020]](https://arxiv.org/pdf/1702.02867.pdf) to correct an error in the concrete analysis, a private mining attack that attempts to cause a <span style="white-space: nowrap">$\sigma$‑block</span> rollback will, with high probability, fail for <span style="white-space: nowrap">large enough $\sigma$.</span> A private mining attack is optimal by the argument in [[DKT+2020]](https://arxiv.org/pdf/2005.10484.pdf).

Any further analysis of the conditions under which these properties hold should be done in the context of a <span style="white-space: nowrap">particular $\Pi_{\mathrm{*bc}}$.</span>
```

```admonish info collapsible=true title="Why is the quantification over two *different* times *t* and *t′*?"
This strengthens the security property, relative to quantifying over a single time. The question can then be split into several parts:

1. What does the strengthened property mean, intuitively?
   Consider the full tree of <span style="white-space: nowrap">$\mathrm{*}$bc‑blocks</span> seen by honest nodes at any times during the execution. This property holds iff, when we strip off all branches of length up to and including <span style="white-space: nowrap">$\sigma$ blocks,</span> the resulting tree is linear.
2. Why is the strengthening needed?
   Suppose that time were split into periods such that honest nodes agreed on one chain in odd periods, and a completely different chain in even periods. This would obviously not satisfy the intent, but it would satisfy a version of the property that did not quantify over different <span style="white-space: nowrap">times $t$ and $t'$.</span>
3. Why should we expect the strengthened property to hold?
   If <span style="white-space: nowrap">node $j$</span> were far ahead, <span style="white-space: nowrap">i.e. $t' \gg t$,</span> then it is obvious that $\mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma\, \preceq_{\mathrm{*bc}} \mathsf{ch}_j^{t'} \lceil_{\!\mathrm{*bc}}^\sigma$ should hold. Conversely, if node $i$ were far ahead then it is obvious that $\mathsf{ch}_j^{t'} \lceil_{\!\mathrm{*bc}}^\sigma\, \preceq_{\mathrm{*bc}} \mathsf{ch}_i^t \lceil_{\!\mathrm{*bc}}^\sigma$ should hold. The case where $t = t'$ is the same as quantifying over a single time. By considering intermediate cases where <span style="white-space: nowrap">$t$ and $t'$</span> converge from the extremes or where they diverge from being equal, you should be able to convince yourself that the property holds for any relative values of <span style="white-space: nowrap">$t$ and $t'$,</span> in executions of a reasonable best‑chain protocol.
```

## Safety Mode

Let $\mathsf{LOG}_{\mathrm{fin},i}^t :: [\textsf{bc-transaction}]$ be the finalized ledger seen by <span style="white-space: nowrap">node $i$</span> at <span style="white-space: nowrap">time $t$,</span> and let $\mathsf{LOG}_{\mathrm{bda},i,\mu}^t :: [\textsf{bc-transaction}]$ be the more-available ledger at <span style="white-space: nowrap">bc‑confirmation‑depth $\mu$</span> seen by <span style="white-space: nowrap">node $i$</span> at <span style="white-space: nowrap">time $t$.</span>

The following definition is rough and only intended to provide intuition.

Consider, at a point in <span style="white-space: nowrap">time $t$,</span> the number of bc‑blocks of transactions that have entered $\mathsf{LOG}_{\mathrm{bda},i,0}^t$ but have not (yet) entered <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{fin},i}^t$.</span> We call this the <span style="white-space: nowrap">"finality gap"</span> at <span style="white-space: nowrap">time $t$.</span> Under an assumption about the distribution of bc‑block intervals, if this gap stays roughly constant then it corresponds to the approximate time that transactions added to $\mathsf{LOG}_{\mathrm{bda},i,0}$ have taken to enter $\mathsf{LOG}_{\mathrm{fin},i}$ (if they do so at all) just prior to <span style="white-space: nowrap">time $t$.</span>

As explained in detail by [The Arguments for Bounded Dynamic Availability and Finality Overrides](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view), if this bound exceeds a reasonable threshold then it likely signals an exceptional or emergency condition, in which it is undesirable to keep accepting user transactions that spend funds into <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{bda},i,0}$.</span>

The condition that the network enters in such cases will be called <span style="white-space: nowrap">"Safety Mode".</span> For a given higher‑level transaction protocol, we can define a policy for which bc‑blocks will be accepted in <span style="white-space: nowrap">Safety Mode.</span> This will be modelled by a predicate <span style="white-space: nowrap">$\textsf{is-safety-block} :: \textsf{bc-block} \to \mathsf{boolean}$.</span> A bc‑block for which $\textsf{is-safety-block}$ returns $\mathsf{true}$ is called a <span style="white-space: nowrap">"safety block".</span>

Note that a bc‑block producer is only constrained to produce safety blocks while, roughly speaking, its view of the finalization point remains stalled. In particular an adversary that has subverted the BFT protocol in a way that does *not* keep it in a stalled state can always avoid being constrained by <span style="white-space: nowrap">Safety Mode.</span>

The desired properties of safety blocks and a possible <span style="white-space: nowrap">Safety Mode</span> policy for Zcash are discussed in the [How to block hazards](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view#How-to-block-hazards) section of [The Arguments for Bounded Dynamic Availability and Finality Overrides](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view).

## Parameters

Crosslink is parameterized by a <span style="white-space: nowrap">bc‑confirmation‑depth $\sigma \in \mathbb{N}^+$</span> (as in Snap‑and‑Chat), and also a finalization gap bound $L \in \mathbb{N}^+$ with $L$ significantly greater <span style="white-space: nowrap">than $\sigma$.</span>

Each node $i$ always uses the fixed confirmation <span style="white-space: nowrap">depth $\sigma$</span> to obtain its view of the finalized ledger <span style="white-space: nowrap">$\mathsf{LOG}_{\mathsf{fin},i} :: [\textsf{bc-transaction}]$.</span>

Each node $i$ chooses a potentially different <span style="white-space: nowrap">bc‑confirmation‑depth $\mu \in \mathbb{N}$</span> to obtain its view of the bounded‑dynamically‑available ledger <span style="white-space: nowrap">$\mathsf{LOG}_{\mathsf{bda},i,\mu} :: [\textsf{bc-transaction}]$.</span> We will assume that <span style="white-space: nowrap">$\mu \leq \sigma$,</span> since there is no reason to <span style="white-space: nowrap">choose $\mu > \sigma$.</span> <span style="white-space: nowrap">Choosing $\mu \lt \sigma$</span> is at the node's own risk and may increase the risk of rollback attacks against $\mathsf{LOG}_{\mathsf{bda},i,\mu}$ (it does not affect <span style="white-space: nowrap">$\mathsf{LOG}_{\mathsf{fin},i}$).</span> The default should <span style="white-space: nowrap">be $\mu = \sigma$.</span>

```admonish info
The definition of $\mathsf{LOG}_{\mathsf{bda},i,\mu}$ is also used internally to the protocol with <span style="white-space: nowrap">$\mu = 0$.</span>
```

## Structural additions

1. Each bc‑header has, in addition to origbc‑header fields, a $\mathsf{context\_bft}$ field that commits to a bft‑block.
2. Each bft‑proposal has, in addition to origbft‑proposal fields, a $\mathsf{headers\_bc}$ field containing a sequence of exactly <span style="white-space: nowrap">$\sigma$ bc‑headers</span> (zero‑indexed, deepest first).
3. Each non‑genesis bft‑block has, in addition to origbft‑block fields, a $\mathsf{headers\_bc}$ field containing a sequence of exactly <span style="white-space: nowrap">$\sigma$ bc‑headers</span> (zero-indexed, deepest first). The genesis bft‑block has <span style="white-space: nowrap">$\mathsf{headers\_bc} = \varnothing$.</span>
4. Each bc‑transaction has, in addition to origbc‑transaction fields, a $\mathsf{block\_bc}$ field labelling it with the bc‑block that it comes from. (This is not used directly by Crosslink but it may be needed to check $\Pi_{\mathrm{bc}}$ consensus rules.)

For a bft‑block or bft‑proposal $B$, define $$
\mathsf{snapshot}(B) = \begin{cases}
  \mathcal{O}_{\mathrm{bc}},&\text{if } B\mathsf{.headers\_bc} = \varnothing \\
  B\mathsf{.headers\_bc}[0] \lceil_{\mathrm{bc}}^1,&\text{otherwise.}
\end{cases}
$$

```admonish info collapsible=true title="Use of the headers_bc field, and its relation to the ch field in Snap‑and‑Chat."
For a bft‑proposal or <span style="white-space: nowrap">bft‑block $B$,</span> the role of the bc‑chain snapshot referenced by $B\mathsf{.headers\_bc}[0] \lceil_{\mathrm{bc}}^1$ is comparable to the <span style="white-space: nowrap">$\Pi_{\mathrm{lc}}$ snapshot</span> referenced by $B\mathsf{.ch}$ in the Snap‑and‑Chat construction from [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf). The motivation for the additional headers is to demonstrate, to any party that sees a bft‑proposal (resp. bft‑block), that the snapshot had been confirmed when the proposal (resp. the block's proposal) was made.

Typically, a node that is validating an honest bft‑proposal or bft‑block will have seen at least the snapshotted bc‑block (and possibly some of the subsequent bc‑blocks in the $\mathsf{header\_bc}$ chain) before. For this not to be the case, the validator's bc‑best‑chain would have to be more than <span style="white-space: nowrap">$\sigma$ bc‑blocks</span> behind the honest proposer's bc‑best‑chain at a given time, which would violate the **Prefix Consistency** property <span style="white-space: nowrap">of $\Pi_{\mathrm{bc}}$.</span>

If the headers do not connect to any bc‑valid‑chain known to the validator, then the validator should be suspicious that the proposer might not be honest. It can assign a lower priority to validating the proposal in this case, or simply drop it. The latter option could drop a valid proposal, but this does not in practice cause a problem as long as a sufficient number of validators are properly synced (so that **Prefix Consistency** holds for them).

If the headers *do* connect to a known bc‑valid‑chain, it could still be the case that the whole header chain up to and including $B\mathsf{.headers\_bc}[\sigma-1]$ is not a bc‑valid‑chain. Therefore, to limit denial‑of‑service attacks the validator should first check the Proofs‑of‑Work and difficulty adjustment <span style="white-space: nowrap">---which it can do locally using only the headers---</span> before attempting to download and validate any bc‑blocks that it has not already seen. This is why we include the full headers rather than just the block hashes. 
```

```admonish info collapsible=true title="Why is a distinguished value needed for the headers_bc field in the genesis bft‑block?"
It would be conceptually nice for $\mathcal{O}_{\mathrm{bft}}\mathsf{.headers}[0] \lceil_{\mathrm{bc}}^1$ to refer to $\mathcal{O}_{\mathrm{bc}}$, as well as $\mathcal{O}_{\mathrm{bc}}\mathsf{.context\_bft}$ being $\mathcal{O}_{\mathrm{bft}}$ so that <span style="white-space: nowrap">$\textsf{bft-last-final}(\mathcal{O}_{\mathrm{bc}}\mathsf{.context\_bft}) = \mathcal{O}_{\mathrm{bft}}$.</span> That reflects the fact that we know <span style="white-space: nowrap">"from the start"</span> that neither genesis block can be rolled back.

This is not literally implementable using block hashes because it would involve a hash cycle, but we achieve the same effect by defining a $\mathsf{snapshot}$ function that allows us to "patch" $\mathsf{snapshot}(\mathcal{O}_{\mathrm{bft}})$ <span style="white-space: nowrap">to be $\mathcal{O}_{\mathrm{bc}}$.</span> We do it this way around rather than "patching" the link from a bc‑block to a bft‑block, because the genesis bft‑block already needs a special case since there are not <span style="white-space: nowrap">$\sigma$ bc‑headers</span> available.
```

```admonish info collapsible=true title="Why is the context_bft field needed? Why not use a final_bft field to refer directly to the last final bft‑block before the context block?"
The finality of some bft‑block is only defined in the context of another bft‑block. One possible design would be for a bc‑block to have both $\mathsf{final\_bft}$ and $\mathsf{context\_bft}$ fields, so that the finality of $\mathsf{final\_bft}$ could be checked objectively in the context <span style="white-space: nowrap">of $\mathsf{context\_bft}$.</span>

However, specifying just the context block is sufficient information to determine its last final ancestor. There would never be any need to give a context block and a final ancestor that is not the last one. The $\textsf{bft-last-final}$ function can be computed efficiently for typical BFT protocols. Therefore, having just the $\mathsf{context\_bft}$ field is sufficient.
```

## Π<sub>bft</sub> changes from Π<sub>origbft</sub>

### Π<sub>bft</sub> proposal and block validity

$\mathcal{O}_{\mathrm{bft}}$ is bft‑valid.

A bft‑proposal (resp. non‑genesis bft‑block) $B$ is bft‑proposal‑valid (resp. bft‑block‑valid) iff all of the following hold:

* **Inherited origbft rules:** The corresponding origbft‑proposal‑validity (resp. origbft‑block‑validity) rules hold for $B$.
* **Increasing Score rule:** Either $\mathsf{score}(\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1)) \lt \mathsf{score}(\mathsf{snapshot}(B))$ or <span style="white-space: nowrap">$\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1) = \mathsf{snapshot}(B)$.</span>
* **Tail Confirmation rule:** $B\mathsf{.headers\_bc}$ form the $\sigma$‑block tail of a bc‑valid‑chain.

The "corresponding validity rules" are assumed to include the **Parent rule** that $B$'s parent is bft‑valid.

Note: origbft‑block‑validity rules may be different to origbft‑proposal‑validity rules. For example, in adapted Streamlet, a origbft‑block needs evidence that it was voted for by a supermajority, and an origbft‑proposal doesn't. Such differences also apply to bft‑block‑validity vs bft‑proposal‑validity.

```admonish info collapsible=true title="What about making the bc‑block producer the bft‑proposer?"
If this were enforced, it could be an alternative way of ensuring that every bft‑proposal snapshots a new bc‑block with a higher score than previous snapshots, potentially making the **Increasing Score rule** redundant. However, it would require merging bc‑block producers and bft‑proposers, which could have concerning knock‑on effects (such as concentrating security into fewer participants).

For a contrary view, see [What about making the bc‑block producer the bft‑proposer?](https://hackmd.io/n8ZDPeTRQj-wa7JWb293oQ?view#What-about-making-the-bc-block-producer-the-bft-proposer) in [Potential changes to Crosslink](https://hackmd.io/n8ZDPeTRQj-wa7JWb293oQ?view).
```

```admonish info collapsible=true title="Why have validity rules been separated from the honest voting condition below?"
The reason to separate the validity rules from the honest voting condition, is that the validity rules are objective: they don't depend on an observer's view of the bc‑best‑chain. Therefore, they can be checked independently of validator signatures. Even a proposal voted for by 100% of validators will not be considered bft‑proposal‑valid by other nodes unless it satisfies the above rules. If more than two thirds of voting units are cast for an **invalid** proposal, something is seriously *and visibly* wrong; in any case, the block will not be accepted as a valid bft‑block. Importantly, a purportedly valid bft‑block will not be recognized as such by *any* honest Crosslink node even if it includes a valid notarization proof, if it does not meet other bft‑block‑validity rules.

This is essential to making $\mathsf{LOG}_{\mathrm{fin}}$ safe against a flaw in $\Pi_{\mathrm{bft}}$ or its security assumptions (even, say, a complete break of the validator signature algorithm), as long as $\Pi_{\mathrm{bc}}$ remains safe.
```

```admonish info collapsible=true title="What does the **Increasing Score rule** do?"
This rule ensures that each snapshot in a bft‑valid‑chain is strictly "better" than the last distinct snapshot (and therefore any earlier distinct snapshot), according to the same metric used to choose the bc‑best‑chain.

This rule has several positive effects:
* It prevents potential attacks that rely on proposing a bc‑valid‑chain that forks from a much earlier block. This is necessary because the difficulty (or stake threshold) at that point could have been much lower.
* It limits the extent of disruption an adversary can feasibly cause to <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{bda},i}$,</span> *even if* it has <span style="white-space: nowrap">subverted $\Pi_{\mathrm{bft}}$.</span> In particular, if transactions are inserted into $\mathsf{LOG}_{\mathrm{bda},i}$ at the finalization point, this rule ensures that they can only come from a bc‑valid‑chain that has a higher score than the previous snapshot. And since the adversary must prove that its snapshot is confirmed, there must be at least <span style="white-space: nowrap">$\sigma$ blocks'</span> worth of Proof‑of‑Work on top of that snapshot, at a difficulty close to the current network difficulty.
  Note that the adversary could take advantage of an "accidental" fork and start its attack from the base of that fork, so that not all of this work is done by it alone. This is also possible in the case of a standard "private mining" attack, and is not so much of a problem in practice because accidental forks are expected to be short. In any case, <span style="white-space: nowrap">$\sigma$ should</span> be chosen to take it into account.
* A snapshot with a higher score than any previous snapshot cannot be a prefix of a previous snapshot (because score strictly increases within a bc‑valid‑chain). So, this excludes proposals that would be a no‑op for that reason.

The increase in score is intentionally always relative to the snapshot of the parent bft‑block, even if it is not final in the context of the current bft‑block. This is because the rule needs to hold if and when it becomes final in the context of some descendant bft‑block.

==PoS Desideratum: we want leader selection with good security / performance properties that will be relevant to this rule. (Suggested: [PoSAT](https://arxiv.org/pdf/2010.08154.pdf).)==
```

```admonish info collapsible=true title="Why does the **Increasing Score rule** allow keeping the same snapshot as the parent?"
This is necessary in order to preserve liveness of $\Pi_{\mathrm{bft}}$ relative <span style="white-space: nowrap">to $\Pi_{\mathrm{origbft}}$.</span> Liveness of $\Pi_{\mathrm{origbft}}$ might require honest proposers to make proposals at a minimum rate. That requirement could be consistently violated if it were not always possible to make a valid proposal. But given that it is allowed to repeat the same snapshot as in the parent bft‑block, neither the **Increasing Score rule** nor the **Tail Confirmation rule** can prevent making a valid <span style="white-space: nowrap">proposal ---</span> and all other rules of $\Pi_{\mathrm{bft}}$ affecting the ability to make valid proposals are the same as <span style="white-space: nowrap">in $\Pi_{\mathrm{origbft}}$.</span> <span style="white-space: nowrap">(In principle,</span> changes to voting in $\Pi_{\mathrm{bft}}$ could also affect its liveness; we'll discuss that in the liveness proof later.)

For example, Streamlet requires three notarized blocks *in consecutive epochs* in order to finalize <span style="white-space: nowrap">a block [[CS2020](https://eprint.iacr.org/2020/088.pdf), section 1.1].</span> Its proof of liveness depends on the assumption that in each epoch for which the leader is honest, that leader will make a proposal, and that during a "period of synchrony" this proposal will be received by <span style="white-space: nowrap">every node [[CS2020](https://eprint.iacr.org/2020/088.pdf), section 3.6].</span> This argument can also be extended to adapted‑Streamlet.

We could alternatively have allowed to always make a "null" proposal, rather than to always make a proposal with the same snapshot as the parent. We prefer the latter because the former would require specifying the rules for null proposals <span style="white-space: nowrap">in $\Pi_{\mathrm{origbft}}$.</span>

As a clarification, no BFT protocol that uses leader election can *require* a proposal in each epoch, because the leader might be dishonest. The above issue concerns liveness of the protocol when assumptions about the attacker's share of bft‑validators or stake are met, so that it can be assumed that sufficiently long periods with enough honest leaders to make progress <span style="white-space: nowrap">(5 consecutive</span> epochs in the case of Streamlet), will occur with significant probability.
```

```admonish info collapsible=true title="Why is it not allowed to switch between snapshots with the same score?"
Consider the following variant of the **Increasing Score rule**: $\mathsf{score}(\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1)) \leq \mathsf{score}(\mathsf{snapshot}(B))$.

This would allow keeping the same snapshot as the parent as discussed in the previous answer. However, it would also allow continually cycling within a given set of snapshots, without making progress and without needing any new Proof‑of‑Work to be performed. This is worse than not making progress due to the same snapshot continually being proposed, because it increases the number of snapshots that need to be considered for sanitization, and therefore it could potentially be used for a denial‑of‑service.
```

### Π<sub>bft</sub> block finality in context

The finality rule for bft‑blocks in a given context is unchanged from origbft‑finality. That is, $\textsf{bft-last-final}$ is defined in the same way as $\textsf{origbft-last-final}$ (modulo referring to bft‑block‑validity and $\mathcal{O}_{\mathrm{bft}}$).

### Π<sub>bft</sub> honest proposal

An honest proposer of a bft‑proposal $P$ chooses $P\mathsf{.headers\_bc}$ as the $\sigma$‑block tail of its bc‑best‑chain, provided that it is consistent with the **Increasing Score rule**. If it would not be consistent with that rule, it sets $P\mathsf{.headers\_bc}$ to the same $\mathsf{headers\_bc}$ field as $P$'s parent bft‑block. It does not make proposals until its bc‑best‑chain is at least $\sigma + 1$ blocks long.

```admonish info collapsible=true title="Why σ + 1?"
If the length were less than $\sigma + 1$ blocks, it would be impossible to construct the $\mathsf{headers\_bc}$ field of the proposal.

Note that when the length of the proposer' bc‑best‑chain is exactly $\sigma + 1$ blocks, the snapshot must be of $\mathcal{O}_{\mathrm{bc}}.$ But this does not violate the **Increasing Score rule**, because $\mathcal{O}_{\mathrm{bc}}$ matches the previous snapshot by $\mathcal{O}_{\mathrm{bft}}$.
```

```admonish info collapsible=true title="How is it possible that the **Increasing Score rule** would not be satisfied by choosing headers from the proposer's bc‑best‑chain?"
Assume for this discussion that $\Pi_{\mathrm{bc}}$ uses PoW.

Depending on the value of $\sigma$, the timestamps of bc‑blocks, and the difficulty adjustment rule, it could be the case that the difficulty on the new bc‑best‑chain increases relative to the chain of the previous snapshot. In that case, when there is a fork, the new chain could reach a higher score than the previous chain in less than $\sigma$ blocks from the fork point, and so its <span style="white-space: nowrap">$\sigma$‑confirmed</span> snapshot could be before the previous snapshot.

(For [Zcash's difficulty adjustment algorithm](https://zips.z.cash/protocol/protocol.pdf#diffadjustment), the difficulty of each block is adjusted based on the median timestamps and difficulty target thresholds over a range of $\mathsf{PoWAveragingWindow} = 17$ blocks, where each median is taken over $\mathsf{PoWMedianBlockSpan} = 11$ blocks. Other damping factors and clamps are applied in order to prevent instability and to reduce the influence that adversarially chosen timestamps can have on difficulty adjustment. This makes it unlikely that an adversary could gain a significant advantage by manipulating the difficulty adjustment.)

For a variation on the **Increasing Score rule** that would be automatically satisfied by choosing headers from the proposer's bc‑best‑chain, see [Potential changes to Crosslink](https://hackmd.io/n8ZDPeTRQj-wa7JWb293oQ?view#Changing-the-Increasing-Score-rule-to-require-the-score-of-the-tip-rather-than-the-score-of-the-snapshot-to-increase).
```

### Π<sub>bft</sub> honest voting

An honest validator considering a proposal $P$, first updates its view of both subprotocols with the bc‑headers given in $P\mathsf{.headers\_bc}$, downloading bc‑blocks for these headers and checking their bc‑block‑validity.

For each downloaded bc‑block, the bft‑chain referenced by its $\mathsf{context\_bft}$ field might need to be validated if it has not been seen before.

```admonish info collapsible=true title="Wait what, how much validation is that?"
In general the entire referenced bft‑chain needs to be validated, not just the referenced block --- and for each bft‑block, the bc‑chain in $\mathsf{headers\_bc}$ needs to be validated, and so on recursively. If this sounds overwhelming, note that:
* We should check the requirement that a bft‑valid‑block must have been voted for by a two‑thirds absolute supermajority of validators, and any other *non‑recursive* bft‑validity rules, *first*.
* Before validating a bc‑chain referenced by a $\mathsf{headers\_bc}$ field, we check that it connects to an already-validated bc‑chain and that the Proofs‑of‑Work are valid. This implies that the amount of bc‑block validation is constrained by how fast the network can find valid Proofs‑of‑Work.

In other words, the order of validation is important to avoid denial‑of‑service. But it already is in Bitcoin and Zcash.
```
${}$
After updating its view, the validator will vote for a proposal $P$ *only if*:

* **Valid proposal criterion:** it is bft‑proposal‑valid, and
* **Confirmed best‑chain criterion:** $\mathsf{snapshot}(P)$ is part of the validator's bc‑best‑chain at a bc‑confirmation‑depth of at least $\sigma$.

```admonish info collapsible=true title="Blocks in a bc‑best‑chain are by definition bc‑block‑valid. If we're checking the **Confirmed best‑chain criterion**, why do we need to have separately checked that the blocks referenced by the headers are bc‑block‑valid?"
The **Confirmed best‑chain criterion** is quite subtle. It ensures that $\mathsf{snapshot}(P) = P\mathsf{.headers\_bc}[0] \lceil_{\mathrm{bc}}^1$ is bc‑block‑valid and has $\sigma$ bc‑block‑valid blocks after it in the validator's bc‑best‑chain. However, it need not be the case that $P\mathsf{.headers\_bc}[\sigma-1]$ is part of the validator's bc‑best‑chain after it updates its view. That is, the chain could fork after $\mathsf{snapshot}(P)$.

The bft‑proposal‑validity rule must be objective; it can't depend on what the validator's bc‑best‑chain is. The validator's bc‑best‑chain *may* have been updated to $P\mathsf{.headers\_bc}[\sigma-1]$ (if it has the highest score), but it also may not.

However, if the validator's bc‑best‑chain *was* updated, that makes it more likely that it will be able to vote for the proposal.

In any case, if the validator does not check that all of the blocks referenced by the headers are bc‑block‑valid, then its vote may be invalid.
```

```admonish info collapsible=true title="How does this compare to Snap‑and‑Chat?"
Snap‑and‑Chat already had the voting condition:
> An honest node only votes for a proposed BFT block $B$ if it views $B\mathsf{.ch}$ as confirmed.

but it did *not* give the headers potentially needed to update the validator's view, and it did not require a proposal to be for an *objectively confirmed* snapshot as a matter of validity.

If a Crosslink‑like protocol were to require an objectively confirmed snapshot but without including the bc‑headers in the proposal, then validators would not immediately know which bc‑blocks to download to check its validity. This would increase latency, and would be likely to lead proposers to be more conservative and only propose blocks that they think will *already* be in at least a two‑thirds absolute supermajority of validators' best chains.

That is, showing $P\mathsf{.headers\_bc}$ to all of the validators is advantageous to the proposer, because the proposer does not have to guess what blocks the validators might have already seen. It is also advantageous for the protocol goals in general, because it improves the trade‑off between finalization latency and security.
```

## Π<sub>bc</sub> changes from Π<sub>origbc</sub>

### Definitions of LOG<sup>t</sup><sub>fin,i</sub> and LOG<sup>t</sup><sub>bda,i,μ</sub>

In Snap‑and‑Chat, a node $i$ at time $t$ obtains $\mathsf{LOG}_{\mathrm{fin},i}^t$ from its latest view of bft‑finality.

In Crosslink, it obtains $\mathsf{LOG}_{\mathrm{fin},i}^t$ from the view of bft‑finality given by $\mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\sigma$, i.e. the block at depth $\sigma$ in node $i$'s' bc‑best‑chain at time $t$.

Specifically,$$
\begin{array}{rcl}
\textsf{san-ctx} &::& [\textsf{bc-chain}] \to \textsf{bc-context} \\
\textsf{san-ctx}(S) &:=& \mathsf{sanitize}(\mathsf{concat}([\textsf{chain-txns}(C) \text{ for } C \text{ in } S])) \\
\mathsf{LF}(H) &:=& \textsf{bft-last-final}(H\mathsf{.context\_bft}) \\
\textsf{fin} &::& \textsf{bc-block} \to [\textsf{bc-chain}] \\
\mathsf{fin}(H) &:=& [\mathsf{snapshot}(B) \text{ for } B \preceq_{\mathrm{bft}} \mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)] \\
\textsf{fin-ctx}(H) &:=& \textsf{san-ctx}(\mathsf{fin}(H)) \\
\textsf{bda-ctx}(H, \mu) &:=& \textsf{san-ctx}(\mathsf{fin}(H) \,||\, [H \lceil_{\mathrm{bc}}^\mu]) \\
\mathsf{LOG}_{\mathrm{fin},i}^t &:=& \textsf{context-txns}(\textsf{fin-ctx}(\mathsf{ch}_i^t)) \\
\mathsf{LOG}_{\mathrm{bda},i,\mu}^t &:=& \textsf{context-txns}(\textsf{bda-ctx}(\mathsf{ch}_i^t, \mu))
\end{array}
$$

For the definitions that use it, $\mu \in \mathbb{N}$ is a confirmation depth.

```admonish warning
Using small values of $\mu$ is not recommended. $\mu = 0$ is an allowed value only because it is used in the definition of contextual validity in the next section.
```

Sanitization is the same as in Snap‑and‑Chat: it does a left fold over an input sequence of transactions, adding each of them to a running bc‑context if they are bc‑context‑valid. The initial bc‑context for this fold corresponds to the state after the genesis bc‑block. This process can be optimized by immediately discarding duplicate bc‑blocks in the concatenated snapshot chains after their first occurrence.

```admonish info
Implementation advice: memoize the $\textsf{san-ctx}$ function. If you see an input to $\textsf{san-ctx}$ that extends a previous input (either adding a new snapshot, or adding blocks to the last snapshot), compute the result incrementally from the previous result.
```

```admonish success
**Ledger prefix property**: For all nodes $i$, times $t$, and confirmation depths $\mu$, <span style="white-space: nowrap">$\mathsf{LOG}_{\mathsf{fin},i} \preceq \mathsf{LOG}_{\mathsf{bda},i,\mu}$.</span>

Proof: By construction of $\mathsf{LOG}_{\mathsf{fin},i}$ and <span style="white-space: nowrap">$\mathsf{LOG}_{\mathsf{bda},i,\mu}$.</span>
```

### Π<sub>bc</sub> contextual validity change

In Crosslink or Snap‑and‑Chat, contextual validity is used in three different cases:

a) sanitization of the constructed ledgers $\mathsf{LOG}_{\mathrm{fin},i}$ and <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{bda},i,\mu}$;</span>
b) checking whether a block is bc‑block‑valid in order to append it to a chain;
c) checking whether a transaction in the mempool could be included in a block.

Note that the model we presented earlier considers only adding a transaction to an origbc‑context. It is straightforward to apply this to the sanitization use case a), as described in the previous section. However, the other two use cases raise the question of which starting bc‑context to use.

We resolve this by saying that new blocks and mempool transactions are checked in the bc‑context obtained from <span style="white-space: nowrap">$\textsf{bda-ctx}(H', 0)$,</span> where $H'$ is the relevant parent bc‑block.

### Π<sub>bc</sub> block validity

**Genesis rule:** For the genesis bc‑block we must have <span style="white-space: nowrap">$\mathcal{O}_{\mathrm{bc}}\mathsf{.context\_bft} = \mathcal{O}_{\mathrm{bft}}$,</span> and therefore <span style="white-space: nowrap">$\textsf{bft-last-final}(\mathcal{O}_{\mathrm{bc}}\mathsf{.context\_bft}) = \mathcal{O}_{\mathrm{bft}}$.</span>

A bc‑block $H$ is bc‑block‑valid iff all of the following hold:
* **Inherited origbc rules:** $H$ satisfies the corresponding origbc‑block‑validity rules.
* **Valid context rule:** $H\mathsf{.context\_bft}$ is bft‑block‑valid.
* **Extension rule:** <span style="white-space: nowrap">$\mathsf{LF}(H \lceil_{\mathrm{bc}}^1) \preceq_{\mathrm{bft}} \mathsf{LF}(H)$.</span>
* **Finality depth rule:** Define: $$
\begin{array}{rl}
\mathsf{tailhead}(H) :=&\!\!\!\! \textsf{last-common-ancestor}(\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)), H) \\
\textsf{finality-depth}(H) :=&\!\!\!\! \mathsf{height}(H) - \mathsf{height}(\mathsf{tailhead}(H))
\end{array}
$$ Then either $\textsf{finality-depth}(H) \leq L$ or <span style="white-space: nowrap">$\textsf{is-safety-block}(H)$.</span>

```admonish info collapsible=true title="Explain the definition of finality‑depth."
We need a way to measure how far ahead a given bc‑block is relative to the corresponding finalization point. $\mathsf{LOG}_{\mathrm{fin},i}^t$ is a sequence of transactions, not blocks, so it is not entirely obvious how to do this.

Let $H = \mathsf{ch}_i^t$, i.e. the tip of <span style="white-space: nowrap">node $i$'s bc‑best‑chain</span> <span style="white-space: nowrap">at time $t$.</span>

Then, $\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)$ is the bft‑block providing the last $\Pi_{\mathrm{bc}}$ snapshot that will be used to construct <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{fin},i}^t$.</span> $\mathsf{tailhead}(H)$ is the last common ancestor of that snapshot <span style="white-space: nowrap">and $H$.</span>

The idea behind the above definition is that:
* If $\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$ is an ancestor <span style="white-space: nowrap">of $H$,</span> then it is <span style="white-space: nowrap">equal to $\mathsf{tailhead}(H)$,</span> and that is the last bc‑block that contributes <span style="white-space: nowrap">to $\mathsf{LOG}_{\mathrm{fin},i}^t$.</span> If the best chain were to continue from $H$ without a rollback, then the bc‑blocks to be finalized next would be the ones <span style="white-space: nowrap">from $\mathsf{tailhead}(H)$</span> <span style="white-space: nowrap">to $H$,</span> and so the number of those blocks gives the finality depth.
* Otherwise, $\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$ must be on a different fork, and the bc‑blocks to be finalized next would resume from the fork point <span style="white-space: nowrap">toward $H$ ---</span> unless some of those blocks have already been included, as discussed below. $\mathsf{LOG}_{\mathrm{fin},i}^t$ will definitely contain transactions from blocks up to $\mathsf{tailhead}(H)$, but usually not subsequent transactions <span style="white-space: nowrap">on $H$'s fork.</span> So it is still reasonable to measure the finality depth from <span style="white-space: nowrap">$\mathsf{tailhead}(H)$ to $H$.</span>

Strictly speaking, it is possible that a previous bft‑block took a snapshot $H'$ that is between <span style="white-space: nowrap">$\mathsf{tailhead}(H)$ and $H$.</span> This can only happen if there have been at least two rollbacks longer than $\sigma$ blocks (i.e. we went more than $\sigma$ blocks down <span style="white-space: nowrap">$H$'s fork</span> <span style="white-space: nowrap">from $\mathsf{tailhead}(H)$,</span> then reorged to more than <span style="white-space: nowrap">$\sigma$ blocks</span> down the fork to <span style="white-space: nowrap">$\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$,</span> then reorged again to <span style="white-space: nowrap">$H$'s fork).</span> In that case, the finalized ledger would already have the non‑conflicting transactions from blocks between <span style="white-space: nowrap">$\mathsf{tailhead}(H)$ and $H'$ ---</span> and it could be argued that the correct definition of finality depth in such cases is the number of blocks <span style="white-space: nowrap">from $H'$ to $H$,</span> not <span style="white-space: nowrap">from $\mathsf{tailhead}(H)$ to $H$.</span>

However,
* The definition above is simpler and easier to compute.
* The effect of overestimating the finality depth in such corner cases would only cause us to enforce Safety Mode slightly sooner, which seems fine (and even desirable) in any situation where there have been at least two rollbacks longer than <span style="white-space: nowrap">$\sigma$ blocks.</span>

By the way, the "tailhead" of a tailed animal is the area where the posterior of the tail joins the rump (also called the "dock" in some animals).
```

### Π<sub>bc</sub> honest block production

An honest producer of a <span style="white-space: nowrap">bc‑block $H$</span> must follow the consensus rules under [$\Pi_{\mathrm{bc}}$ block validity](#Πbc-block-validity) above. In particular, it must produce a safety block if required to do so by the **Finality depth rule**. It also must only include transactions that are valid in the context specified under [$\Pi_{\mathrm{bc}}$ contextual validity change](#Πbc-contextual-validity-change) above.

To <span style="white-space: nowrap">choose $H\mathsf{.context\_bft}$,</span> the producer considers a subset of the tips of bft‑valid‑chains in its view: $$
\{ T : T \text{ is bft‑block‑valid and } \mathsf{LF}(H \lceil_{\mathrm{bc}}^1) \preceq_{\mathrm{bft}} \textsf{bft-last-final}(T) \}
$$ It chooses one of the longest of these chains, $C$, breaking ties by maximizing <span style="white-space: nowrap">$\mathsf{score}(\mathsf{snapshot}(\textsf{bft-last-final}(C)))$.</span> If there is still a tie then it is broken arbitrarily.

The honest block producer then sets <span style="white-space: nowrap">$H\mathsf{.context\_bft} := C$.</span>

```admonish info collapsible=true title="Why not choose *T*  such that *H* ⌈<sup>1</sup><sub>bc</sub> . context_bft  ⪯<sub>bft</sub>  bft‑last‑final(*T* )?"
The effect of this would be to tend to more often follow the last bft‑block seen by the producer of the parent bc‑block, if there is a choice. It is not always possible to do so, though: the resulting set of candidates <span style="white-space: nowrap">for $C$</span> might be empty.

Also, it is not clear that giving the parent bc‑block‑producer the chance to "guide" what bft‑block should be chosen next is beneficial, since that producer might be adversarial and the resulting incentives are difficult to reason about.
```

```admonish info collapsible=true title="Why choose the longest *C*, rather than the longest bft‑last‑final(*C* )?"
We could have instead chosen $C$ to maximize the length <span style="white-space: nowrap">of $\textsf{bft-last-final}(C)$.</span> The rule we chose follows Streamlet, which builds on the longest notarized chain, not the longest finalized chain. This may call for more analysis specific to the chosen BFT protocol.
```

```admonish info collapsible=true title="Why this tie‑breaking rule?"
Choosing the bft‑chain that has the last final snapshot with the highest score, tends to inhibit an adversary's ability to finalize its own chain if it has a lesser score. (If it has a greater score, then it has already won a hash race and we cannot stop the adversary chain from being finalized.)

If we [switch to using the Increasing Tip Score rule](https://hackmd.io/n8ZDPeTRQj-wa7JWb293oQ?view#Changing-the-Increasing-Score-rule-to-require-the-score-of-the-tip-rather-than-the-score-of-the-snapshot-to-increase), then it would be more consistent to also change this tie‑breaking rule to use the tip score, <span style="white-space: nowrap">i.e. $\mathsf{score}(\mathsf{tip}(\textsf{bft-last-final}(C)))$.</span>
```
${}$
At this point we have completed the definition of Crosslink. In [Security Analysis of Crosslink](https://hackmd.io/YboxY2yLQDujpdkHj7JNMA), we will prove it secure.
