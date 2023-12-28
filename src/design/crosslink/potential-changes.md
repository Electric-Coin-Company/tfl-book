# Potential Changes to Crosslink

This page documents suggestions that have not had the same attention to security analysis as the [baseline Crosslink construction](./construction.md). Some of them are broken. Some of them also increase the complexity of the protocol (while some simplify it or have a mixed effect on complexity), and so we need to consider the security/complexity trade‑off of each suggestion before we could include it.

## Attempts to improve safety or to simplify the protocol

### [Recommended] Recording more info about the bft‑chain in bc‑blocks

We can allow honest bc‑block‑producers to record information about every proposed and notarized bft‑block, rather than just the one in the $\mathsf{context\_bft}$ field.

Duplicate information that has already been given in an ancestor bc‑block would be omitted.

This would automatically expose the following shenanigans to public view (as long as enough bc‑block‑proposers are honest, which is already assumed):
* any attempt to double‑propose in the same epoch;
* any successful attempt to double‑notarize.

We could also expose attempts to double‑vote.

Note that double‑proposal and double‑voting could be a sign that a proposer or validator's private key is compromised, rather than that it belongs to the adversary per se. However, the security analysis must treat such a proposer/validator as non‑honest in any case.

### Changing the Increasing Score rule to require the score of the tip (rather than the score of the snapshot) to increase

The current [**Increasing Score rule**](./construction.md#%CE%A0bft-proposal-and-block-validity) concerns the score of the snapshot:

**Increasing Snapshot Score rule:** Either $\mathsf{score}(\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1)) < \mathsf{score}(\mathsf{snapshot}(B))$ or $\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1) = \mathsf{snapshot}(B)$.

We could instead require the score of $\mathsf{tip}(B) = B\mathsf{.header\_bc}[\sigma-1]$ to increase:

**Increasing Tip Score rule:** Either $\mathsf{score}(\mathsf{tip}(B \lceil_{\mathrm{bft}}^1)) < \mathsf{score}(\mathsf{tip}(B))$ or $\mathsf{tip}(B \lceil_{\mathrm{bft}}^1) = \mathsf{tip}(B)$.

Pros:
* This more directly reflects the fork‑choice rule in $\Pi_{\mathrm{bc}}$.
* In baseline Crosslink, an [honest bft-proposer](./construction.md#%CE%A0bft-honest-proposal) uses its bc‑best‑chain tip with the highest score *provided that* it is consistent with the **Increasing Snapshot Score rule**. This change removes the caveat, simplifying honest bft‑proposer behaviour.
* As a result of removing that caveat, we always know about an honest bft‑proposer's bc‑best‑chain.

Con:
* The score of the snapshot would not necessarily increase. As a result, it is technically possible that the new snapshot can be an ancestor of a previous snapshot. Whether this can actually happen depends on the value of $\sigma$ and the difficulty adjustment rule. This causes no particular harm other than adding a corner case in ledger sanitization, but is inelegant.
  * This con is removed if we either use the **Combined Increasing Score rule** variant described below, *or* we also apply the "[Making bc‑rollbacks more difficult](#Making-bc-rollbacks-more-difficult)" change in the next section.

Apart from the above con, the original motivations for the **Increasing Snapshot Score rule** also apply to the **Increasing Tip Score rule**. In particular,
* it still prevents potential attacks that rely on proposing a bc‑valid‑chain that forks from a much earlier block;
* it still limits the extent of disruption an adversary can feasibly cause to $\mathsf{LOG}_{\mathrm{bda}}$;
* it still always allows a proposal to be made, which may be needed to preserve liveness of $\Pi_{\mathrm{bft}}$ relative to $\Pi_{\mathrm{origbft}}$;
* it still prevents potential validation cost DoS attacks due to switching between snapshots with the same score.

A variation on this suggestion effectively keeps both the **Increasing Snapshot Score rule** and the **Increasing Tip Score rule**:

**Combined Increasing Score rule:** Either ($\mathsf{score}(\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1)) < \mathsf{score}(\mathsf{snapshot}(B))$ and $\mathsf{score}(\mathsf{tip}(B \lceil_{\mathrm{bft}}^1)) < \mathsf{score}(\mathsf{tip}(B))$), or $\mathsf{tip}(B \lceil_{\mathrm{bft}}^1) = \mathsf{tip}(B)$.

Note that if $\mathsf{tip}(B \lceil_{\mathrm{bft}}^1) = \mathsf{tip}(B)$, both scores are necessarily equal.

This variation does not simplify honest bft‑proposer behaviour.

### Making exploitation of bc‑rollbacks more difficult

Basic idea: Detect the case where the bc‑snapshot is rolling back, and impose a longer confirmation depth to switch to the new bc‑chain. Also temporarily stall finalization of the existing bc‑chain until the conflict has been resolved.

Let $\mathsf{baseline\_snapshot}$ be the baseline Crosslink definition of $\mathsf{snapshot}$, i.e. $$
\mathsf{baseline\_snapshot}(B) = \begin{cases}
  \mathcal{O}_{\mathrm{bc}},&\text{if } B\mathsf{.headers\_bc} = \varnothing \\
  B\mathsf{.headers\_bc}[0] \lceil_{\mathrm{bc}}^1,&\text{otherwise.}
\end{cases}
$$

When $\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1) \;{\not\preceq}_{\mathrm{bc}}\; \mathsf{baseline\_snapshot}(B)$, we want to go into a mode where we require a longer confirmation <span style="white-space: nowrap">depth $\Sigma$,</span> <span style="white-space: nowrap">say $2\sigma$.</span> Because we don't know in this situation whether the old bc‑chain or the new bc‑chain will win, we stop finalizing both until a winner is clear.

The simplest option is to record the state saying that we are in this mode explicitly, and add a consensus rule requiring it to be correct. That is, add an $\mathsf{bc\_is\_forked}$ field to bft‑proposals and bft‑blocks, and add a bft‑proposal and bft‑block validity rule as follows:

* **Is Forked rule:**
  $B\mathsf{.bc\_is\_forked} = (\mathsf{enter\_forked}(B)$ or $B \lceil_{\mathrm{bft}}^1\mathsf{.bc\_is\_forked})$ and not $\mathsf{exit\_forked}(B)$

where:
* $\mathsf{enter\_forked}(B) := \mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1) \;{\not\preceq}_{\mathrm{bc}}\; \mathsf{baseline\_snapshot}(B)$
* $\mathsf{exit\_forked}(B) := \mathsf{score}(\mathsf{tip}(B) \lceil_{\mathrm{bc}}^\Sigma) > \mathsf{score}(\mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1))$.

It is intentional that $\mathsf{exit\_forked}$ takes precedence over $\mathsf{enter\_forked}$.

Then redefine $\mathsf{snapshot}$ as follows: $$
\mathsf{snapshot}(B) = \begin{cases}
  \mathsf{snapshot}(B \lceil_{\mathrm{bft}}^1),&\text{if } B\mathsf{.bc\_is\_forked} \\
  \mathsf{baseline\_snapshot}(B),&\text{otherwise.}
\end{cases}
$$

Since $\mathcal{O}_{\mathrm{bft}}\mathsf{.bc\_is\_forked} = \mathsf{false}$, the recursion will terminate.

Note that there is an interaction between the **Increasing Snapshot Score rule** and this change: the **Increasing Snapshot Score rule** should arguably use $\mathsf{baseline\_snapshot}$ instead of $\mathsf{snapshot}$. The **Increasing Tip Score rule**, on the other hand, works fine as‑is, and so it makes sense to use both of these changes together. The combination of both changes also fixes the con discussed above for the **Increasing Tip Score rule**; it ensures that the score of the snapshot must increase.

Pros:
* If the winning chain is the chain that was first snapshotted, then there ends up being no disruption whatsoever <span style="white-space: nowrap">to $\mathsf{LOG}_{\mathrm{bda}}$.</span>
* It becomes extremely difficult for an adversary with less than 50% hash power to get the finalized snapshot to switch between two competing chains more than once.

Cons:
* It is potentially easier to cause a temporary finalization stall. An adversary could try to provoke this situation on the honest chain, either as a DoS attack, or so that its own chain that is not so encumbered can finalize more quickly than the honest chain.
  * This does not seem like a practical attack, because such a stall can only happen when the adversary can cause a $\sigma$‑block rollback or has <span style="white-space: nowrap">subverted $\Pi_{\mathrm{bft}}$.</span>
* The definition of $\mathsf{snapshot}$ becomes more complicated, and there is a risk of this complexity introducing problems.
* It can be argued that, unless <span style="white-space: nowrap">$\sigma$ is</span> chosen too small, an adversary that can cause a <span style="white-space: nowrap">$\sigma$‑block rollback</span> likely has 50% of hash power, and therefore can cause a <span style="white-space: nowrap">$\Sigma$‑block rollback.</span> That is, increasing confirmation depth does not help beyond a certain point, and therefore (it could be argued) this change will also not help.
  * This argument may hold for private mining attacks, but does not necessarily hold for partitioning attacks, as discussed in the next section.

### Using tip information to detect rollbacks and partitions

In the case of a private mining attack, the adversary will typically conceal the existence of the overtaking chain until it can be used to cause a rollback <span style="white-space: nowrap">in $\mathsf{LOG}_{\mathrm{bda}}$.</span> So the approach used in the previous section seems to be all we can do against such an attack.

In the case of a partitioning attack, on the other hand, the adversary relies on honest nodes to do mining work on each side of the partition. This relies on the successful miners on each side knowing about their chain, but not the chain on the other side. Subtly, it does not rely on a perfect network partition. An adversary could, for example, attempt to create partitions *around* the most successful mining pools. Occasional leaks of information across a partition also do not necessarily foil the attack unless that information gets to a successful miner. Therefore, measures that constrain the adversary's ability to make use of an *incomplete* partition can be useful.

This also has the benefit of making the protocol more robust against *non‑malicious* incomplete partitions.

Given that in such an attack the competing chains may be visible to some proposers, there is the possibility of detecting a potential rollback even before it gets snapshotted, by using the fact that previous bft‑blocks created by honest bft‑proposers have been recording the bc‑best‑chain tip <span style="white-space: nowrap">$\sigma$ blocks ahead.</span> Also, depending on what proportion of validators an adversary has, they may rely on honest validators on each side to ensure that a snapshot of each chain appears in a bft‑valid block; in that case, including information about competing chains in validators' votes (see the next subsection) may be useful.

It is still possible that if an adversary has several consecutive proposal slots, it can get its chain snapshotted. However, if there is an intervening slot with an honest proposer, we can potentially compare its tip with the adversary's tip and anticipate the need to go into <span style="white-space: nowrap">$\mathsf{bc\_is\_forked}$ mode.</span>

In order to get this to work, we need to propose a definition to identify bc‑chains that are competing with the current best chain, such that there is some risk of a "long" rollback to a competing chain. <span style="white-space: nowrap">Let $\delta$ be</span> a measure of how close (in terms of bc‑blocks) a competing chain's score needs to be to that of the bc‑best‑chain, and <span style="white-space: nowrap">let $\mu > \delta$ be</span> a lower bound on the rollback depth we would consider significant if the competing chain were to immediately catch up. <span style="white-space: nowrap">(The condition $\mu > \delta$</span> is necessary to avoid false positives that might only be a single‑block fork.)

A node $i$ identifies <span style="white-space: nowrap">$(\delta, \mu)$‑competing chains</span> as follows based on its current view at <span style="white-space: nowrap">time $t$:</span>

* A bc‑block is a tip if it has no known descendants.
* Let $\mathsf{ch}_i^t$ be <span style="white-space: nowrap">node $i$'s bc‑best‑chain.</span>
* Identify all of the <span style="white-space: nowrap">tips $T$</span> such that $\mathsf{score}(T) \geq \mathsf{score}(\mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\delta)$ and <span style="white-space: nowrap">$\textsf{last-common-ancestor}(T, \mathsf{ch}_i^t) \preceq_{\mathrm{bc}} \mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\mu$.</span>

==TODO: Details, including how to modify the $\mathsf{enter\_forked}$ and $\mathsf{exit\_forked}$ conditions.==

==TODO: For now we will assume that all of the competing chain information in a bft‑block has to be checked as bc‑block‑valid in order for that block to be bft‑block‑valid. This might introduce validation DoS attacks and needs to be considered more carefully.==

### Allowing validators to signal the existence of a competing chain in their votes

This complements the above idea by letting a validator that has seen a competing chain signal it in its signed vote. Then, as long as the adversary is reliant on some votes from honest validators that are signalling the existence of competing chains, we would go into <span style="white-space: nowrap">$\mathsf{bc\_is\_forked}$ mode</span> without relying on honest proposers to have an intervening slot.

The [notarization proof](./construction.md#%CE%A0bft-proposal-and-block-validity) that appears in a bft‑block would need to be modified to preserve these signals. More precisely, it is necessary for a <span style="white-space: nowrap">bft‑block $B$</span> to preserve at least:
* the best bc‑chain that credibly competes <span style="white-space: nowrap">with $\mathsf{tip}(B)$,</span> if any.
* the best bc‑chain that does not credibly compete <span style="white-space: nowrap">with $\mathsf{tip}(B)$</span> (this necessarily exists because $\mathsf{tip}(B)$ does not credibly compete with itself).

This is also motivated by the suggested change in the next section.

Enforcing this is relatively straightforward if the evidence is a SNARK. It can also be enforced with aggregate signatures even for schemes that only allow aggregation of signatures over a common message: we just collect the distinct messages (corresponding to either "no competing chain" or each distinct competing chain) and aggregate them separately.

### Strengthening the Increasing Tip Score rule

Assume that votes include competing chain information as discussed above. We can assume that an honest proposer has read all of this information from its parent bft‑block. Therefore, we can require the tip score of its proposal to have at least the score of the best tip implied by that information:

Let $\textsf{best-tip}(B)$ be the tip mentioned in <span style="white-space: nowrap">bft‑block $B$</span> with the highest score. <span style="white-space: nowrap">A bft‑block $B$</span> "mentions" the two best tips defined in the previous section.

**Strong Increasing Tip Score rule:** Either $\mathsf{score}(\textsf{best-tip}(B \lceil_{\mathrm{bft}}^1)) < \mathsf{score}(\mathsf{tip}(B))$ or <span style="white-space: nowrap">$\textsf{best-tip}(B \lceil_{\mathrm{bft}}^1) = \mathsf{tip}(B)$.</span>

Note that this rule is really quite constraining for a potential adversary, especially in partitioning attacks. It means that if the adversary does not want to acknowledge the existence of a given chain, it cannot use any votes or build on any previous bft‑block that signals the existence of that chain. Essentially, a partitioning adversary with control over only the minimum one‑third of the stake would have to have ensure a perfectly complete partition; it could not get away with any information leakage between honest validators.

## Attempts to improve finalization latency

### [Broken] Adjusting the last snapshot definition

The current Crosslink design imposes a finalization latency of at least <span style="white-space: nowrap">$2\sigma + 1$ block times.</span> Intuitively, this is because in $$
\mathsf{fin}(H) := [\mathsf{snapshot}(B) \text{ for } B \preceq_{\mathrm{bft}} \textsf{bft-last-final}(H \lceil_{\mathrm{bc}}^\sigma\mathsf{.context\_bft})],
$$ $\mathsf{snapshot}(\textsf{bft-last-final}(H \lceil_{\mathrm{bc}}^\sigma\mathsf{.context\_bft}))$ is at least <span style="white-space: nowrap">$\sigma+1$ blocks</span> back <span style="white-space: nowrap">from $H \lceil_{\mathrm{bc}}^\sigma$</span> (as argued in [Questions about Crosslink](./questions.md#Why-don%E2%80%99t-we-have-a-bc-block-validity-rule-snapshotfinal-bftH-%E2%AA%AFbc-H-)), and therefore <span style="white-space: nowrap">$2\sigma+1$ blocks</span> back <span style="white-space: nowrap">from $H$.</span> So the total finalization latency is <span style="white-space: nowrap">$\sigma$ block times + BFT overhead + $(\sigma + 1)$ block times + snapshot overhead.</span>

However, the snapshot headers contain information about the proposer's bc‑best‑chain.

Define $\mathsf{LF}(H) := \textsf{bft-last-final}(H\mathsf{.context\_bft})$. Although it is not guaranteed, normally $\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$ will be an ancestor <span style="white-space: nowrap">of $H \lceil_{\mathrm{bc}}^\sigma$.</span> What if we were to optimistically allow the last snapshot to be taken as $$
S(H) := \begin{cases}
\textsf{last-common-ancestor}(H \lceil_{\mathrm{bc}}^\sigma,\, \mathsf{tip}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)), &\text{if it extends } \mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)) \\
\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)), &\text{otherwise}
\end{cases}
$$? After all, we know that $\textsf{last-common-ancestor}(H \lceil_{\mathrm{bc}}^\sigma,\, \mathsf{tip}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$ is confirmed.

Oh, this won't work. The problem is that we want safety of $\mathsf{LOG}_{\mathrm{fin}}$ not to depend on safety of $\Pi_{\mathrm{bc}}$. So we cannot assume (for this purpose) that nodes see the <span style="white-space: nowrap">same $H \lceil_{\mathrm{bc}}^\sigma$.</span>

### Replacing $\mathsf{LOG}_{\mathrm{bda}}$ with $\mathsf{LOG}_{\mathrm{opt}}$

What if we instead take this to be the definition of $\mathsf{LOG}_{\mathrm{opt}}$, replacing $\mathsf{LOG}_{\mathrm{bda}}$ ("opt" meaning optimistic)?

As stated, a malicious proposer can try to maximize the latency of $\mathsf{LOG}_{\mathrm{opt}}$ (subject to the Increasing Score rule). For example, if there exists a fork of <span style="white-space: nowrap">length $\mu$,</span> the malicious proposer can force the latency of $\mathsf{LOG}_{\mathrm{opt}}$ to be <span style="white-space: nowrap">$(\sigma + \mu + 1)$ block times + BFT overhead.</span> However, this can be improved by applying the idea to each bft‑block in turn after the one pointed to by the best confirmed bc‑block. Then a malicious proposer cannot do anything that it could not do anyway (keeping the finalization point at its current position).

Pros:
* This is always more conservative in terms of safety than the current design.
* The latency of $\mathsf{LOG}_{\mathrm{opt}}$ will typically be <span style="white-space: nowrap">$\sigma + 1$ bc‑block times,</span> rather than <span style="white-space: nowrap">$2\sigma + 1$ block times.</span>

Cons:
* $\mathsf{LOG}_{\mathrm{opt}}$ is *not* dynamically available in any sense. It just has lower latency and different security characteristics.
* Even under optimistic conditions, $\mathsf{LOG}_{\mathrm{opt}}$ will lag slightly behind where it would be for the original Crosslink design, because $H \lceil_{\mathrm{bc}}^\sigma$ will necessarily be ahead of <span style="white-space: nowrap">$\mathsf{tip}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma))$.</span>

### [Broken] Using snapshots from the last‑seen bft‑chain when it is consistent with the bc‑best‑chain

The following idea is broken for safety when $\Pi_{\mathrm{bft}}$ has been subverted:

```admonish info
We have two potential sources of information about blocks that could plausibly be considered finalized:
1. $H \lceil_{\mathrm{bc}}^\sigma$
2. the snapshots on the chain of the last *seen* <span style="white-space: nowrap">final bft‑block, $\mathsf{lsf}$.</span>

We cannot rely only on 1. because we want assured finalization even under partition.
We cannot rely only on 2. because if $\Pi_{\mathrm{bft}}$ has been subverted, then the chain of final bft‑blocks could fork.

But intuitively, if we combine these sources of information, using them over the baseline Crosslink finalization only when they are consistent, the resulting protocol should still be as safe as the safer of $\Pi_{\mathrm{bft}}$ <span style="white-space: nowrap">and $\Pi_{\mathrm{bc}}$.</span> In particular, 2. will not roll back *unless* $\Pi_{\mathrm{bft}}$ has been subverted.

If this idea were to pan out, it could improve the latency of finalization by <span style="white-space: nowrap">$\sigma$ block times.</span>

This approach is essentially a hybrid of Snap‑and‑Chat and Crosslink:
* the Snap‑and‑Chat construction gives a finalized ledger under the assumption that $\Pi_{\mathrm{bft}}$ has not been subverted;
* the main crosslink idea is used to make sure that outputs from all finalized transactions are *eventually* spendable;
* safety is still only dependent on the stronger of the safety of $\Pi_{\mathrm{bft}}$ <span style="white-space: nowrap">and $\Pi_{\mathrm{bc}}$,</span> because we use the additional information from snapshots in final bft‑blocks only up to the point at which they agree with the best confirmed bc‑block.
```

To explain the safety problem with this idea: suppose that $\Pi_{\mathrm{bft}}$ has been subverted. In that case it is possible for a snapshot to be finalized without having being confirmed as in any honest node's bc‑best‑chain; that is, it is possible for $\mathsf{LOG}_{\mathrm{fin}}$ to include transactions $T$ from a snapshot $S$ in bft‑block $A$ such that $S$ is not on the consensus bc‑best‑chain. And, because $\Pi_{\mathrm{bft}}$ has been subverted, it is also possible that a conflicting final bft‑block $B$ <span style="white-space: nowrap">omits $S$.</span> And so a node that has seen $B$ will think that it is consistent with the best bc‑chain (so that its $\mathsf{LOG}_{\mathrm{fin}}$ does not include $T$ but does include later transactions on the consensus bc‑best‑chain), but a node that has <span style="white-space: nowrap">seen $A$</span> will compute a $\mathsf{LOG}_{\mathrm{fin}}$ that does <span style="white-space: nowrap">include $T$.</span>

```admonish info collapsible=true title="More detailed specification of the above broken idea."
Define $\mathsf{LF}(H) := \textsf{bft-last-final}(H\mathsf{.context\_bft})$ as before.

For simplicity assume that <span style="white-space: nowrap">$\mathsf{lsf}$ extends $\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)$</span> by only one bft‑block. (This assumption could have been removed if the idea had panned out.)

Then this proposal was to consider this bc‑block as contributing the last finalized snapshot:
$$
S(H) := \begin{cases}
\textsf{last-common-ancestor}(H \lceil_{\mathrm{bc}}^\sigma, \mathsf{snapshot}(\mathsf{lsf})), &\text{if it extends } \mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)) \\
\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)), &\text{otherwise}
\end{cases}
$$

There is no need for a tie‑breaking rule for 2.: if we ever see two context bft‑blocks for which the last‑final blocks are conflicting, we know that $\Pi_{\mathrm{bft}}$ has been subverted, so we should stall or crash.

Caveat: for a given node, <span style="white-space: nowrap">$H \lceil_{\mathrm{bc}}^\sigma$ can</span> in theory roll back <span style="white-space: nowrap">past $\mathsf{snapshot}(\mathsf{lsf})$,</span> therefore $S(H)$ can also roll back. It is okay if we keep state here and refuse to roll back. We should set a "crisis flag", and unset it if at any point <span style="white-space: nowrap">$\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)$ extends $\mathsf{lsf\_at\_crisis}$.</span> <span style="white-space: nowrap">(If $\Pi_{\mathrm{bft}}$</span> is safe and live, it will.)

A similar rule that would give the same result in almost all circumstances is: $$
S(H) := \begin{cases}
H \lceil_{\mathrm{bc}}^\sigma, &\text{if } \mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)) \preceq_{\mathrm{bc}} H \lceil_{\mathrm{bc}}^\sigma \,\preceq_{\mathrm{bc}} \mathsf{snapshot}(\mathsf{lsf}) \\
\mathsf{snapshot}(\mathsf{lsf}), &\text{if } \mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)) \preceq_{\mathrm{bc}} \mathsf{snapshot}(\mathsf{lsf}) \preceq_{\mathrm{bc}} H \lceil_{\mathrm{bc}}^\sigma \\
\mathsf{snapshot}(\mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)), &\text{otherwise}
\end{cases} $$
```

## What about making the bc‑block‑producer the bft‑proposer?

The answer given for this question at [The Crosslink Construction](./construction.md#%CE%A0bft-proposal-and-block-validity) is:
> If this were enforced, it could be an alternative way of ensuring that every bft‑proposal snapshots a new bc‑block with a higher score than previous snapshots, potentially making the **Increasing Score rule** redundant. However, it would require merging bc‑block‑producers and bft‑proposers, which could have concerning knock‑on effects (such as concentrating security into fewer participants).

This may have been too hasty. It is not clear that merging bc‑block‑producers and bft‑proposers actually does "concentrate security into fewer participants" in a way that can have any harmful effect.

Remember, the job of a bft‑proposer in Crosslink is primarily to snapshot the bc‑best‑chain (even more so if the [Increasing Tip Score rule](#changing-the-increasing-score-rule-to-require-the-score-of-the-tip-rather-than-the-score-of-the-snapshot-to-increase) is adopted). An honest miner *by definition* is claiming to build on the best chain, and miners have a strong economic incentive to do so. Therefore, it is entirely reasonable for every newly produced block to be treated as a bft‑proposal. This arguably decentralizes the task of proposing bft‑blocks more effectively than using a leader election protocol would &mdash; especially given that in a hybrid protocol we *necessarily* still rely on there being sufficient honest miners.

[[DKT2021]](https://arxiv.org/pdf/2010.08154.pdf), for example, argues for the importance of "the complete unpredictability of who will get to propose a block next, even by the winner itself." The main basis of this argument is that it makes subversion of the proposer significantly more difficult. A PoW protocol has that property, and most PoS protocols do not. (It is not that PoS protocols are unable to provide this property; indeed, [[DKT2021]](https://arxiv.org/pdf/2010.08154.pdf) constructs a PoS protocol, "PoSAT", that provides it.)

So let's explore this in more detail. A newly produced bc‑block would implicitly be a bft‑proposal with itself as the tip. The $\mathsf{bc\_headers}$ field is therefore not needed. The [**Tail Confirmation rule**](./construction.md#%CE%A0bft-proposal-and-block-validity) goes away since its intent is automatically satisfied. This is already a significant simplification.

The inner proposer signature is also not needed (since the bc‑header is self-authenticating), but the block producer would have to include a <span style="white-space: nowrap">public key $H\mathsf{.pubkey}$</span> that can be used to verify its outer signature. It would sign the notarized bft‑block with the corresponding private key. This change is a wash in terms of protocol complexity. 

Considered as a bft‑proposal, a bc‑block needs to refer to a parent bft‑block, which requires a <span style="white-space: nowrap">$\mathsf{parent\_bft}$ field</span> in the bc‑header. With some caveats depending on the design <span style="white-space: nowrap">of $\Pi_{\mathrm{origbft}}$,</span> it might be possible to merge this with the <span style="white-space: nowrap">$\mathsf{context\_bft}$ field,</span> but for now we will assume that it is not merged.

```admonish info collapsible=true title="What are the caveats?"
If we are in an execution where **Final Agreement** holds <span style="white-space: nowrap">for $\Pi_{\mathrm{bft}}$,</span> then it is possible to show that merging the two fields has no negative effect, *provided* that $\Pi_{\mathrm{origbft}}$ has no additional rules that could disallow it in some cases.

This is because, by **Final Agreement**, $\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \preceq\hspace{-0.5em}\succeq_{\mathrm{*bft}} \textsf{bft-last-final}(C)\,$ for any potential <span style="white-space: nowrap">bft‑block $C$</span> that the bc‑block‑producer of a new block $H$ could choose <span style="white-space: nowrap">as $H\mathsf{.context\_bft}$.</span> Suppose that the bc‑block‑producer freely chooses $H\mathsf{.parent\_bft}$ according to the desired honest behaviour for a bft‑proposer <span style="white-space: nowrap">in $\Pi_{\mathrm{bft}}$,</span> and then chooses $C$ to be the same block (which is always reasonable as long as it is allowed).

In the case <span style="white-space: nowrap">$\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \preceq_{\mathrm{*bft}} \textsf{bft-last-final}(C)$,</span> we are done, because this choice of $H\mathsf{.context\_bft}$ is allowed by the **Extension rule**.

In the case <span style="white-space: nowrap">$\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \;⪲_{\mathrm{*bft}}\; \textsf{bft-last-final}(C)$,</span> we can argue that $H'\mathsf{.context\_bft}$ would be a better choice than $C$ for $H\mathsf{.parent\_bft}$ as well as for <span style="white-space: nowrap">$H\mathsf{.context\_bft}$,</span> because it has a later final ancestor. This is where the argument might fall down if $\Pi_{\mathrm{origbft}}$ <span style="white-space: nowrap">(and therefore $\Pi_{\mathrm{bft}}$)</span> has any additional rules that could disallow this choice. For now let's suppose that situtation does not arise, but it is one of the caveats.

Another potential problem is that in an execution where **Final Agreement** does *not* hold for <span style="white-space: nowrap">$\Pi_{\mathrm{bft}}$,</span> we can no longer infer that either $\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \preceq_{\mathrm{*bft}} \textsf{bft-last-final}(C)$ or $\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \;⪲_{\mathrm{*bft}}\; \textsf{bft-last-final}(C)$. In particular it could be the case that the producer of $H'$ was adversarial, and chose $H'\mathsf{.context\_bft}$ in such a way as to favour its own bft‑block that is final in that context.

However, in that situation it must be possible for the bc‑block‑producer to see (and prove) that the bft‑chain has a final fork. That is, it can produce a <span style="white-space: nowrap">witness $C$</span> to the violation of **Final Agreement**, showing that $\textsf{bft-last-final}(H'\mathsf{.context\_bft}) \preceq\hspace{-0.5em}\succeq_{\mathrm{*bft}} \textsf{bft-last-final}(C)\,$ does not hold, as discussed in the section [Recording more info about the bft‑chain in bc‑blocks](#recommended-recording-more-info-about-the-bftchain-in-bcblocks) above.

The second caveat is that in that situation, we still need to set $H\mathsf{.parent\_bft}$ and $H\mathsf{.context\_bft}$ in order to be able to recover, and they typically should not be the same in order to do so.
```

The **Increasing Tip Score rule** is still needed, but it can be simplified. A newly produced <span style="white-space: nowrap">bc-block $H$</span> is also a bft‑proposal <span style="white-space: nowrap">such that $\mathsf{snapshot}(H) = H$.</span> This would yield the following bft‑proposal / bc‑block validity rule:

> [Candidate rule for discussion] Either $\mathsf{score}(\mathsf{tip}(H\mathsf{.parent\_bft})) < \mathsf{score}(H)$ <span style="white-space: nowrap">or $\mathsf{tip}(H\mathsf{.parent\_bft}) = H$.</span>

except that $\mathsf{tip}(H\mathsf{.parent\_bft})$ *cannot* <span style="white-space: nowrap">be $H$,</span> because $H$ is newly produced. It turns out we can just drop that part: 

> **Increasing Tip Score (producer = proposer) rule:** $\mathsf{score}(\mathsf{tip}(H\mathsf{.parent\_bft})) < \mathsf{score}(H)$.

This works because, if $H$ does not have a higher score than the <span style="white-space: nowrap">bc‑block $\mathsf{tip}(H\mathsf{.parent\_bft})$,</span> the bc‑block‑producer should instead have built on top of that bc‑block &mdash; which was necessarily known to the producer in order for it to set $H\mathsf{.parent\_bft}$ in the header of the new block.

The voting would be the same, performed by the same parties. Therefore, there is no concentration of voting into fewer parties.  There is no change in the producer/proposer's incentive to make the bft‑notarization‑proof or its soundness properties. Everything else is roughly the same, including the use of the <span style="white-space: nowrap">$\mathsf{context\_bft}$ field</span> of a bc‑block and the validity rules related to it. As far as I can see, all of the security analysis goes through essentially unchanged.

There may be some complication due to the fact that BFT protocols are typically designed to use epochs with a fixed period, whereas bc‑blocks are found at less predictable intervals. However, as long as BFT messages are labelled with the bc‑block they apply to, it seems like most BFT protocols would be tolerant to this change. In fact the adaptations of Snap‑and‑Chat to Hotstuff and PBFT in [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) already assume that BFT messages can be queued and processed at a later time, and rely on those BFT protocols' tolerance to this.

```admonish info
In most PoS protocols, the requirement to have a minimum amount of stake in order to make a proposal acts as a gatekeeping filter on *proposals*, and potentially allows parties that make invalid *proposals* to be slashed.

Strictly speaking, whether there is a stake requirement to make a proposal is independent of whether bc‑block‑producers (e.g. miners) are merged with bft‑proposers. It could be, for example, that a miner is still able to produce bc‑blocks, but is not able to make them into a proposal unless they satisfy a stake requirement. (This would have significant effects on the economics of mining that would need to be analysed, and that might have governance consequences.)

In a system that uses PoS, validators by definition need to have stake in order to control the ability to vote. This also allows validators to be slashed.

On the other hand, there is no *technical* reason why the ability to make a bft‑proposal has to be gatekept by a stake requirement &mdash; given the situation of Zcash in which we already have a mining infrastructure, and that in a Snap‑and‑Chat or Crosslink‑style hybrid protocol we necessarily still rely on miners not to censor transactions. The potential to make proposals that are expensive to validate as a denial of service is made sufficiently difficult by proof‑of‑work. This option has probably been underexplored by previous PoS protocols because they cannot assume an existing mining infrastructure. 
```

It could be argued that this approach goes less far toward a pure PoS‑based blockchain protocol, leaving more to be done in the second stage. However, there is a clear route to that second stage, by replacing PoW with a protocol like PoSAT that has full unpredictabilty and dynamic availability. PoSAT does this using a VDF, and as it happens, Halo 2 is a strong candidate to be used to construct such a VDF.

If the arguments in [[DKT2021]](https://arxiv.org/pdf/2010.08154.pdf) about the need for proposer unpredictability are persuasive, then this approach defers the complexity of requiring a VDF without losing any security, since Zcash's PoW is already unpredictable.

### Do we need an explicit bft‑chain at all?

Building on the previous idea, we can try to eliminate the explicit bft‑chain by piggybacking the information it would hold onto a bc‑block (in the header and/or the block contents). In the previous section we merged the concepts of a bft‑proposal and a bc-block; the $\mathsf{parent}_{\mathrm{bft}}(P)$ and <span style="white-space: nowrap">$P\mathsf{.context\_bft}$ fields</span> of a bft‑proposal were moved into the $H\mathsf{.parent\_bft}$ and <span style="white-space: nowrap">$H\mathsf{.context\_bft}$ fields</span> of a bc‑header respectively. <span style="white-space: nowrap">A field $H\mathsf{.pubkey}$</span> was also added to hold the producer's public key, so that the producer can sign the bft‑block constructed from it using the corresponding private key.

This left the concept of a bft‑block intact. Recall that in baseline Crosslink, a <span style="white-space: nowrap">bft‑block $B$</span> consists of $(P, \mathsf{proof}_P)$ signed by the proposer. So in "Crosslink with proposer = producer", a bft‑block consists of $(H, \mathsf{proof}_H)$ signed by the producer.

What if a <span style="white-space: nowrap">bc‑block $H$</span> were to "inline" its parent and context bft‑blocks rather than referring to them? <span style="white-space: nowrap">I.e. a bc‑block $H$</span> with $H\mathsf{.parent\_bft}$ *referring to* <span style="white-space: nowrap">$(H', \mathsf{proof}_{H'})$ signed for $H'\mathsf{.pubkey}$,</span> would instead <span style="white-space: nowrap">*literally include*</span> (either in the header or the coinbase transaction) $(H', \mathsf{proof}_{H'})$ signed <span style="white-space: nowrap">for $H'\mathsf{.pubkey}$ &mdash;</span> and similarly <span style="white-space: nowrap">for $H\mathsf{.context\_bft}$.</span>

It would still be necessary to have the message type that the proposer/producer previously used to submit a notarized bft‑block. (It cannot be merged with a bc‑block announcement: the producer of a new block is not in general the producer of its parent, and their incentives may differ; also we cannot wait until a new block is found before publishing the previous notarization.) It would also still be necessary for Crosslink nodes to keep track of notarizations that have not made it into any bc‑block. Nevertheless, this is a potential simplification.

Note that unless notarization proofs are particularly short and constant-length, it would not be appropriate to include them in the bc‑block headers, and so they would have to go into the coinbase transaction or another similar variable-length data structure. In that case we would still have an indirection to obtain the bft‑block information; it would just be merged with the indirection to obtain a coinbase transaction (or similar) &mdash; which is already needed in order to check validity of the bc‑block.

As discussed under "[Recording more info about the bft‑chain in bc‑blocks](#recommended-recording-more-info-about-the-bftchain-in-bcblocks)" above, we might in any case want to record information about other proposed and notarized bft‑blocks, and the data structure needed for this would necessarily be variable-length. The complexity burden of doing so would be shared between these two changes.

It would be possible to save some space in headers (while keeping them fixed-length), by inlining only one of $H\mathsf{.parent\_bft}$ and $H\mathsf{.context\_bft}$ in the header and keeping the other as a hash. As discussed under "What are the caveats?" above, the only reason for the two bft‑blocks referred to by these fields to be different, is that the bc‑block producer has observed a violation of **Final Agreement** <span style="white-space: nowrap">in $\Pi_{\mathrm{bft}}$.</span> In that case, we can include an inlining of the other <span style="white-space: nowrap">$H\mathsf{.*\_bft}$ block,</span> and any other information needed to prove that a violation of **Final Agreement** has occurred, in a variable-length overflow structure.

Pros:
* No additional mechanism or messages are needed to obtain bft‑blocks given their hashes.
* It could be a performance/latency improvement to not have to separately fetch bft‑blocks.

Con:
* Additional complexity of the variable-length overflow mechanism suggested above, if it is used.
* Assumes that notarization proofs are not too large.
