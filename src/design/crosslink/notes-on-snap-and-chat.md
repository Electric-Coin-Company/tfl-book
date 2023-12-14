# Notes on Snap-and-Chat

The discussion in [The Argument for Bounded Dynamic Availability and Finality Overrides](https://hackmd.io/sYzi5RW-RKS1j20OO4Li_w?view) is at an abstract level, applying to any ebb-and-flow-like protocol.

This document considers specifics of the snap-and-chat construction proposed in [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) ([arXiv version](https://arxiv.org/pdf/2009.04987.pdf)).

:::info
I am trying to be precise in this note about use of the terms "ebb-and-flow", which is the security model and goal introduced in [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf), vs "snap-and-chat", which is the construction proposed in the same paper to achieve that goal. There could be other ways to design an ebb-and-flow protocol that don't run into the difficulties described in this section (or that run into different difficulties).
:::

### Effect on consensus

A general problem with the snap-and-chat construction is that it does not follow, from enforcement of the original consensus rules on blocks produced in $\Pi_{\mathrm{lc}}$, that the properties they are intended to enforce hold for the $\mathsf{LOG}_{\mathrm{fin},i}^t$ or $\mathsf{LOG}_{\mathrm{da},i}^t$ ledgers. Less obviously, the converse also does not follow: enforcing unmodified consensus rules on $\Pi_{\mathrm{lc}}$ blocks is **both** too lax and too strict.

Recall from the paper how $\mathsf{LOG}_{\mathrm{fin},i}^t$ and $\mathsf{LOG}_{\mathrm{da},i}^t$ are constructed (starting at the end of page 8 of [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf)):

> 3) *Ledger extraction:* Finally, how honest nodes compute $\mathsf{LOG}_{\mathrm{fin},i}^t$ and $\mathsf{LOG}_{\mathrm{da},i}^t$ from $\mathsf{Ch}_i^t$ and $\mathsf{ch}_i^t$ is illustrated in Figure 6. Recall that $\mathsf{Ch}_i^t$ is an ordering of snapshots, i.e., a chain of chains of LC blocks. First, $\mathsf{Ch}_i^t$ is flattened, i.e. the chains of blocks are concatenated as ordered to arrive at a single sequence of LC blocks. Then, all but the first occurrence of each block are removed (sanitized) to arrive at the finalized ledger $\mathsf{LOG}_{\mathrm{fin},i}^t$ of LC blocks. To form the available ledger $\mathsf{LOG}_{\mathrm{da},i}^t$, $\mathsf{ch}_i^t$, which is a sequence of LC blocks, is appended to $\mathsf{LOG}_{\mathrm{fin},i}^t$ and the result again sanitized.

This says that $\mathsf{LOG}_{\mathrm{fin},i}^t$ and $\mathsf{LOG}_{\mathrm{da},i}^t$ are sequences of transactions, *not* sequences of blocks. Therefore, [consensus rules defined at the block level](https://zips.z.cash/protocol/protocol.pdf#blockheader) are not applicable.

:::warning
**Zcash-specific**

Most of these rules are Proof-of-Work-related checks that can be safely ignored at this level. Some are related to the `hashBlockCommitments` field intended for use by the FlyClient protocol. It is not at all clear how to make FlyClient (or other uses of this commitment) work with the snap-and-chat construction. In particular, the `hashEarliest{Sapling,Orchard}Root`, `hashLatest{Sapling,Orchard}Root`, and `n{Sapling,Orchard}TxCount` fields don't make sense in this context since they could only reflect the values in $\mathsf{ch}_i^t$, which have no relation in general to those for any subrange of transactions in $\mathsf{LOG}_{\mathrm{da},i}^t$. However, that problem occurs for unmodified snap-and-chat, and so is outside the scope of this note.
:::

Since $\mathsf{LOG}_{\mathrm{da},i}^t$ does not have blocks, it is not well-defined whether it has "coinbase-only blocks" when in Safety Mode. That by itself is not so much of a problem because it would be sufficient for it to have only coinbase transactions in that mode.

### Effect on issuance

The issuance schedule of Zcash was designed under the assumption that blocks only come from a single chain, and that the difficulty adjustment algorithm keeps the rate of block mining roughly constant over time.

For snap-and-chat, if there is a rollback longer than $\sigma$ blocks in $\Pi_{\mathrm{lc}}$, additional coinbase transactions from the rolled-back chain will be included in $\mathsf{LOG}_{\mathrm{fin}}$.

We can argue that this will happen rarely enough not to cause any significant problem for the overall issuance schedule. However, it does mean that issuance is less predictable, because the block subsidies will be computed according to their depth in the $\Pi_{\mathrm{lc}}$ chain on which they were mined. So it will no longer be the case that coinbase transactions issue a deterministic, non-increasing sequence of block subsidies.

### Effect on transaction ordering

The order of transactions in any particular $\mathsf{ch}_i^t$ is *not* in general preserved in either $\mathsf{LOG}_{\mathrm{fin}}$ or $\mathsf{LOG}_{\mathrm{da}}$. This *is* considered in the paper (middle of the left column on page 10) but it is very easy to miss it:

> Thus, snapshots taken by different nodes or at different times can conflict. However, $\Pi_{\mathrm{bft}}$ is still safe and thus orders these snapshots linearly. Any transactions invalidated by conflicts are sanitized during ledger extraction.

That is, a transaction from one snapshot might double-spend an output already spent in a different transaction of a different snaphot earlier in the flattening order. If it is omitted, then later transactions could depend on the outputs of the omitted one. The paper is saying that each transaction is only included if (in Bitcoin and Zcash terminology) it satisfies contextual checks for double-spending and existence of inputs at the point in the ledger where it would be added.

Since nullifiers for shielded spends are public, it is possible to do this even for shielded transactions. Each node $i$ will construct commitment trees in the order given by $\mathsf{LOG}_{\mathrm{da},i}^t.$

:::info
This means that if $\mathsf{LOG}_{\mathrm{fin},i}$ is extended by a block that is not the next block in $\mathsf{LOG}_{\mathrm{da},i}$ after the finalization point (and that has different note commitments), then *all* shielded transactions from that point onward in the previous $\mathsf{LOG}_{\mathrm{da},i}$ will be invalidated. It could be possible to do better at the expense of a more complicated note commitment tree structure. In any case, this situation is expected to be rare, because it can only occur if there is a rollback of more than $\sigma$ blocks in the $\Pi_{\mathrm{lc}}$ consensus chain or a failure of BFT safety.
:::

### Subtlety in the definition of sanitization

There are two possible ways to interpret how $\mathsf{LOG}_{\{\mathrm{fin},\mathrm{da}\}}$ are constructed in snap-and-chat:

1. Concatenate the transactions from each final BFT block snapshot of an LC chain, and sanitize the resulting transaction sequence by including each transaction iff it is contextually valid.
2. Concatenate the *blocks* from each final BFT block snapshot of an LC chain, remove duplicate *blocks*, and only then sanitize the resulting transaction sequence by including each transaction iff it is contextually valid.

These are equivalent, but the argument for their equivalence is not obvious. We definitely want them to be equivalent: in practice there will be many duplicate blocks from chain prefixes in the input to sanitization, and so a literal implementation of the first variant would have to recheck all duplicate transactions for contextual validity. That would have at least $O(n^2)$ complexity (more likely $O(n^2 \log n)$) in the length $n$ of the block chain, because the length of each final snapshot grows with $n$.

The only reasons for a transaction to be contextually invalid are double-spends and missing inputs. The argument for equivalence is:
* If a transaction is omitted due to a double-spend, then any subsequent time it is checked, that input will still have been double-spent.
* If a transaction is omitted due to a missing input, this can only be because an earlier transaction in the input to sanitization was omitted. So the structure of omitted transactions forms a DAG in which parent links must be to *earlier* omitted transactions. The roots of the DAG are at double-spending transactions, which cannot be reinstated. A child cannot be reinstated until its parents have been reinstated. Therefore, no transactions are reinstated.

Note that any *other* reason for transactions to be contextually invalid might interfere with this argument. Therefore, strictly speaking snap-and-chat should require of $\Pi_{\mathrm{lc}}$ that there is no such other reason. I cannot see this explicitly stated anywhere in [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf).

### Spending finalized outputs

Transactions in $\mathsf{ch}_i^t$ need to be able to spend outputs that are not necessarily from any previous transaction in $\mathsf{ch}_i^t$. This is because, from the point of view of a user of node $i$ at time $t$, the block chain includes all transactions in $\mathsf{LOG}_{\mathrm{da},i}^t$. All of the transactions after the finalization point are guaranteed to also be in $\mathsf{ch}_i^t$, but the ones before the finalization point (i.e. in $\mathsf{LOG}_{\mathrm{fin},i}^t$) are not, because they could be from some other $\mathsf{ch}_j^u$ for $u \leq t$ and $j \neq i$ (intuitively, from some long chain fork that was once considered confirmed by enough nodes).

:::info
Honest nodes only ever vote for confirmed snapshots, that is, prefixes of their best $\Pi_{\mathrm{lc}}$ chain truncated by the confirmation depth $\sigma$. Obviously the whole point of having the BFT protocol is that chain forks longer than $\sigma$ **can** occur in $\Pi_{\mathrm{lc}}$ --- otherwise we'd just use $\Pi_{\mathrm{lc}}$ and have done. So it is not that we expect this case to be common, but if it happens then it will never fix itself: the consensus chain in $\Pi_{\mathrm{lc}}$ will continue on without ever including the transactions from $\mathsf{LOG}_{\mathrm{fin}}^t$ that were obtained from a snapshot of another fork.
:::

A user must be able to spend outputs for which they hold the spending key from **any** finalized transaction, otherwise there would be no point to the finalization.

I think the authors of [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) probably just missed this: the paper only has evidence that they simulated their construction, rather than implementing it for Bitcoin or any other concrete block chain as $\Pi_{\mathrm{lc}}$. Let's try to repair it.

Suppose that node $j$ is trying to determine whether $\mathsf{ch}_i^t$ is a consensus-valid chain, which is necessary for deterministic consensus in $\Pi_{\mathrm{lc}}$. It cannot decide whether to allow transactions in $\mathsf{ch}_i^t$ to spend outputs not in the history of $\mathsf{ch}_i^t$ on the basis of its *own* finalized view $\mathsf{LOG}_{\mathrm{fin},j}^t,$ because $\mathsf{LOG}_{\mathrm{fin},i}^t$ and $\mathsf{LOG}_{\mathrm{fin},j}^t$ are not in general the same.

Of course, we hope that $\mathsf{LOG}_{\mathrm{fin},i}^t$ and $\mathsf{LOG}_{\mathrm{fin},j}^t$ are consistent, i.e. one is a prefix of the other. But even if they are consistent, they are not necessarily the same length. In particular, if $\mathsf{LOG}_{\mathrm{fin},j}^t$ is *shorter* than $\mathsf{LOG}_{\mathrm{fin},i}^t,$ then node $j$ does not have enough information to fill in the gap --- and so it may incorrectly view a transaction in $\mathsf{ch}_i^t$ as spending an output that does not exist, when actually it does exist in $\mathsf{LOG}_{\mathrm{fin},i}^t \setminus \mathsf{LOG}_{\mathrm{fin},j}^t.$ Conversely if $\mathsf{LOG}_{\mathrm{fin},j}^t$ were longer and node $j$ were to allow spending an output in $\mathsf{LOG}_{\mathrm{fin},j}^t \setminus \mathsf{LOG}_{\mathrm{fin},i}^t,$ that would be using information that is not necessarily available to other nodes, and so node $j$ could diverge from consensus.

Consensus validity of the block at the tip of $\mathsf{ch}_i^t$ can only be a deterministic function of the block itself and its ancestors in $\mathsf{ch}_i^t$. It is crucial to be able to *eventually* spend outputs from the finalized chain. We are forced to conclude that the chain $\mathsf{ch}_i^t$ **must include** the information needed to calculate $\mathsf{LOG}_{\mathrm{fin},i}^{t'}$ for some $t'$ not too far behind $t$. That is, $\Pi_{\mathrm{lc}}$ must be modified to ensure that this is the case. This leads us to strengthen the required properties of an ebb-and-flow protocol to include another property, "finalization availability".

## Finalization Availability

In the absence of security flaws and under the security assumptions required by the finality layer, the finalization point will not be seen by any honest node to roll back. However, that does not imply that all nodes will see the same finalized height --- which is impossible given network delays and unreliable messaging.

Both in order to optimize the availability of applications that require finality, and in order to solve the technical issue of spending finalized outputs described in the previous section, we need to consider availability of the information needed to finalize the chain up to a particular point.

Note that in Bitcoin-like consensus protocols, we don't generally consider it to be an availability flaw that a block header only *commits* to the previous block hash and to the Merkle tree of transactions in the block, rather than including them directly. These commitments allow nodes to check that they have the correct information, which can then be requested separately.

Suppose, then, that each block header in $\Pi_{\mathrm{lc}}$ commits to the latest final BFT block known by the $\Pi_{\mathrm{lc}}$ block producer. For a block header $H$, we will refer to this commitment as $\textsf{final-bft}(H)$. 

:::success
We require, as a consensus rule, that if $H$ is not the genesis block header, then this BFT block either descends from or is the same as the final BFT block committed to by the $\Pi_{\mathrm{lc}}$ block's parent: i.e. $\textsf{final-bft}(\mathsf{parent}_{\mathrm{lc}}(H)) \preceq_{\mathrm{bft}} \textsf{final-bft}(H)$.
:::

This rule does not prevent the BFT chain from rolling back, if the security assumptions of $\Pi_{\mathrm{bft}}$ were violated. However, it means that if a node $i$ does not observe a rollback in $\Pi_{\mathrm{lc}}$ at confirmation depth $\sigma$, then it will also not observe any instability in $\mathsf{LOG}_{\mathrm{fin},i}$, *even if* the security assumptions of $\Pi_{\mathrm{bft}}$ are violated. This property holds **by construction**, and in fact regardless of $\Pi_{\mathrm{bft}}$.

:::info
In the snap-and-chat construction, we also have BFT block proposals committing to $\Pi_{\mathrm{lc}}$ snapshots (top of right column of [[NTT2020](https://eprint.iacr.org/2020/1091.pdf), page 7]):
> In addition, $\mathsf{ch}^t_i$ is used as side information in $\Pi_{\mathrm{bft}}$ to boycott the finalization of invalid snapshots proposed by the adversary.

This does not cause any circularity, because each protocol only commits to *earlier* blocks of the other. In fact, BFT validators have to listen to transmission of $\Pi_{\mathrm{lc}}$ block headers anyway, so that *could* be also the protocol over which they get the information needed to make and broadcast their own signatures or proposals. (A possible reason not to broadcast individual signatures to all nodes is that with large numbers of validators, the proof that a sufficient proportion of validators/stake has signed can use an aggregate signature, which could be much smaller. Also, $\Pi_{\mathrm{lc}}$ nodes only need to know about *successful* BFT block proposals.)
:::

Now suppose that, in a snap-and-chat protocol, the BFT consensus finalizes a $\Pi_{\mathrm{lc}}$ snapshot that does not extend the snapshot in the previous block (which can happen if either $\Pi_{\mathrm{bft}}$ is unsafe, or $\Pi_{\mathrm{lc}}$ suffers a rollback longer than $\sigma$ blocks). In that case we will initially not be able to spend outputs from the old snapshot in the new chain. But eventually for some node $i$ that sees the header $H$ at the tip of its best chain at time $t$, $\textsf{final-bft}(H)$ will be such that from then on (i.e. at time $t' \geq t$), $\mathsf{LOG}_{\mathrm{fin},i}^{t'}$ includes the output that we want to spend. This assumes *liveness* of $\Pi_{\mathrm{lc}}$ and *safety* of $\Pi_{\mathrm{bft}}$.

That is, including a reference to a recent final BFT block in  $\Pi_{\mathrm{lc}}$ block headers both incentivizes nodes to propagate this information, *and* can be used to solve the "spending finalized outputs" problem.

Optionally, we could incentivize the block producer to include the latest information it has, for example by burning part of the block reward or by giving the producer some limited mining advantage that depends on how many $\Pi_{\mathrm{lc}}$ blocks back the finalization information is.

This raises the question of how we measure how far ahead a given block is relative to the finalization information it provides. As we said before, $\mathsf{LOG}_{\mathrm{fin},i}^t$ is a sequence of transactions, not blocks. The transactions will in general be in a different order, and also some transactions from $\mathsf{ch}_i^t$ may have been omitted from $\mathsf{LOG}_{\mathrm{fin},i}^t$ (and even $\mathsf{LOG}_{\mathrm{da},i}^t$) because they were not contextually valid.

It turns out there *is* a good way to measure this. Assume that a block unambiguously specifies its ancestor chain. For a block $H$, define:$$
\mathsf{tailhead}(H) := \textsf{last-common-ancestor}(\mathsf{snapshot}(\textsf{final-bft}(H)), H) \\
\textsf{finality-depth}(H) := \mathsf{height}(H) - \mathsf{height}(\mathsf{tailhead}(H))
$$

Here $\textsf{final-bft}(H)$ is the BFT block we are providing information for, and $\mathsf{snapshot}(\textsf{final-bft}(H))$ is the corresponding $\Pi_{\mathrm{lc}}$ snapshot. For a node $i$ that sees $\textsf{final-bft}(H)$ as the most recent final BFT block at time $t$, $\mathsf{LOG}_{\mathrm{fin},i}^t$ will definitely contain transactions from blocks up to $\mathsf{tailhead}(H)$, but usually will not contain subsequent transactions on $H$'s fork.

:::info
Strictly speaking, it is possible that a previous BFT block took a snapshot $H'$ that is between $\mathsf{tailhead}(H)$ and $H$. This can only happen if there have been at least two rollbacks longer than $\sigma$ blocks (i.e. we went more than $\sigma$ blocks down $H$'s fork from $\mathsf{tailhead}(H)$, then reorged to more than $\sigma$ blocks down $\mathsf{snapshot}(\textsf{final-bft}(H))$'s fork, then reorged again to $H$'s fork). In that case, the finalized ledger would already have the non-conflicting transactions from blocks between $\mathsf{tailhead}(H)$ and $H'$ --- and it could be argued that the correct definition of finality depth in such cases is the depth of $H'$ relative to $H$, not of $\mathsf{tailhead}(H)$ relative to $H$.

However,
* The definition above is simpler and easier to compute.
* The effect of overestimating the finality depth in such corner cases would only cause us to enforce Safety Mode slightly sooner, which seems fine (and even desirable) in any situation where there have been at least two rollbacks longer than $\sigma$ blocks.

By the way, the "tailhead" of a tailed animal is the area where the posterior of the tail joins the rump (also called the "dock" in some animals).
:::

We could alternatively just rely on the fact that some proportion of block producers are honest and will include the latest information they have. However, it turns out that having a definition of finality depth will also be useful to enforce going into Safety Mode.

Specifically, if we accept the above definition of finality depth, then the security property we want is

:::success
**Bounded hazard-freeness** for a finality gap bound of $L$ blocks: There is never, for any node $i$ at time $t$, observed to be a more-available ledger $\mathsf{LOG}_{\mathrm{da},i}^t$ with a hazardous transaction that comes from block $H$ of $\mathsf{ch}_i^t$ such that $\textsf{finality-depth}(H) > L$. 
:::

:::info
This assumes that transactions in the non-finalized suffix  $\mathsf{LOG}_{\mathrm{da},i}^t \setminus \mathsf{LOG}_{\mathrm{fin},i}^t$ come from blocks in $\mathsf{ch}_i^t$. In snap-and-chat they do by definition, but ideally we wouldn't depend on that. The difficulty in finding a more general security definition is due to the ledgers in an ebb-and-flow protocol being specified as sequences of transactions, so that a depth in the ledger would have only a very indirect correspondence to time. We could instead base a definition on timestamps, but that could run into difficulties in ensuring timestamp accuracy.

Another possibility would be to count the number of coinbase transactions in $\mathsf{LOG}_{\mathrm{da},i}^t \setminus \mathsf{LOG}_{\mathrm{fin},i}^t$ before the hazardous transaction. This would still be somewhat ad hoc (it depends on the fact that coinbase transactions happen once per block and cannot conflict with any other distinct transaction).

In any case, if $\textsf{finality-depth}$ sometimes overestimates the depth, that cannot weaken this security definition.
:::

Note that a node that is validating a chain $\mathsf{ch}_i^t$ must fetch all the chains referenced by BFT blocks reachable from it (back to an ancestor that it has seen before). In theory, there could be a partition that causes there to be multiple disjoint snapshots that get added to the BFT chain in quick succession. However, in practice we expect such long rollbacks to be rare if $\Pi_{\mathrm{lc}}$ is meeting its security goals.

Going into Safety Mode if there is a long finalization stall helps to reduce the cost of validation when the stall resolves. That is, if there is a partition and nodes build on several long chains, then in unmodified snap-and-chat, it could be necessary to validate an arbitrary number of transactions on each chain when the stall resolves. Having only coinbase transactions after a certain point in each chain would significantly reduce the concrete validation costs in this situation.

Nodes should not simply trust that the BFT blocks are correct; they should check validator signatures (or aggregate signatures) and finalization rules. Similarly, $\Pi_{\mathrm{lc}}$ snapshots should not be trusted just because they are referenced by BFT blocks; they should be fully validated, including the proofs-of-work.

It is also possible for a snapshot reference to include the subsequent $\sigma$ block headers, which are guaranteed to be available for a confirmed snapshot. Having all nodes validate the proofs-of-work in these headers is likely to significantly increase the work that an attacker would need to perform to cause disruption under a partial failure of either $\Pi_{\mathrm{bft}}$ or $\Pi_{\mathrm{lc}}$'s security properties.

:::info
Note that [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) (bottom of right column, page 9) makes a safety assumption about $\Pi_{\mathrm{lc}}$ in order to prove the consistency of $\mathsf{LOG}_{\mathrm{fin}}$ with the output of $\Pi_{\mathrm{lc}}$:

> As indicated by Algorithm 1, a snapshot of the output of $\Pi_{\mathrm{lc}}$ becomes final as part of a BFT block only if that snapshot is seen as confirmed by at least one honest node. However, since $\Pi_{\mathrm{lc}}$ is safe [i.e., does not roll back further than the confirmation depth $\sigma$], the fact that one honest node sees that snapshot as confirmed implies that every honest node sees the same snapshot as confirmed.

I claim that, while this may be a reasonable assumption to make for parts of the security analysis, in practice we should always require any adversary to do the relevant amount of proof-of-work to construct block headers that are plausibly confirmed. This is useful even though we cannot require, for every possible attack, that it had those headers at the time they should originally have appeared.
:::

## Enforcing Finalization Availability and Safety Mode

The following idea for enforcing finalization availability *and* a bound on the finality gap was originally conceived before I had switched to advocating the Safety Mode approach. It's simpler to explain first in that variant; bear with me.

Suppose that for a $L$-block availability bound, we required each block header to include the information necessary for a node to finalize to $L$ blocks back. This would automatically enforce a chain stall after the availability bound without any further explicit check, because it would be impossible to produce a block after the bound.

Note that if full nodes have access to the BFT chain, knowing $\textsf{final-bft}(H)$ is sufficient to tell whether the correct version of any given BFT block in $\textsf{final-bft}(H)$'s ancestor chain has been obtained.

Suppose that the finality gap bound is $L$ blocks. Having already defined $\textsf{finality-depth}$, the necessary $\Pi_{\mathrm{lc}}$ consensus rule is attractively simple:

:::success
For every $\Pi_{\mathrm{lc}}$ block $H$, $\textsf{finality-depth}(H) \leq L$.
:::

To adapt this approach to enforce Safety Mode instead of stalling the chain, we can allow the alternative of producing a block that follows the Safety Mode restrictions:

:::success
For every $\Pi_{\mathrm{lc}}$ block $H$, <font color="blue">either</font> $\textsf{finality-depth}(H) \leq L$<font color="blue">, or $H$ follows the Safety Mode restrictions</font>.
:::

Note that Safety Mode will be exited automatically as soon as the finalization point catches up to within $L$ blocks (if it does without an intentional rollback). Typically, after recovery from whatever was causing the finalization stall, the validators will be able to obtain consensus on the same chain as $\mathsf{LOG}_{\mathrm{da}}$, and so there will be no rollback (or at least not a long one) of $\mathsf{LOG}_{\mathrm{da}}$.

:::info
An earlier iteration of this idea required the finalization information to be included in $\Pi_{\mathrm{lc}}$ block headers. This is not necessary when we assume that full nodes have access to the BFT chain and can obtain arbitrary BFT blocks. This also sidesteps any need to relax the rule in order to bound the size of $\Pi_{\mathrm{lc}}$ block headers. $\Pi_{\mathrm{lc}}$ block producers are still incentivised to make the relevant BFT blocks available, because without them the above consensus rule cannot be checked, and so their $\Pi_{\mathrm{lc}}$ blocks would not be accepted.

There is, however, a potential denial-of-service attack by claiming the existence of a BFT block that is very far ahead of the actual BFT chain tip. This attack is not very serious as long as nodes limit the number of BFT blocks they will attempt to obtain in parallel before having checked validator signatures.
:::

### Comment on security assumptions

Consider Lemma 5:
> Moreover, for a BFT block to become final in the view of an honest node $i$ under $(\mathcal{A}^∗_2, \mathcal{Z}_2)$, at least one vote from an honest node is required, and honest nodes only vote for a BFT block if they view the referenced LC block as confirmed.

The stated assumptions are:

> $(\mathcal{A}_2(\beta), \mathcal{Z}_2)$ formalizes the model of **P2**, a synchronous network under dynamic participation, with respect to a bound $\beta$ on the fraction of awake nodes that are adversarial:
> * At all times, $\mathcal{A}_2$ is required to deliver all messages sent between honest nodes in at most $\Delta$ slots.
> * At all times, $\mathcal{A}_2$ determines which honest nodes are awake/asleep and when, subject to the constraint that at all times at most fraction $\beta$ of awake nodes are adversarial and at least one honest node is awake.

$(\mathcal{A}^∗_2, \mathcal{Z}_2)$ is defined as $(\mathcal{A}_2(\frac{1}{2}, \mathcal{Z}_2))$.

Now consider this statement and figure:

> Even if $\Pi_{\mathrm{bft}}$ is unsafe (Figure 9c), finalization of a snapshot requires at least one honest vote, and thus only valid snapshots become finalized.
>
> ![Figure 9 of [NTT2020]](https://hackmd.io/_uploads/HJklq3xbT.png)

This argument is technically correct but has to be interpreted with care. It only applies when the number of malicious nodes $f$ is such that $n/3 < f < n/2$. What we are trying to do with Crosslink is to ensure that a similar conclusion holds even if $\Pi_{\mathrm{bft}}$ is completely subverted, i.e. the adversary has 100% of validators (but only < 50% of $\Pi_{\mathrm{lc}}$ hash rate).
