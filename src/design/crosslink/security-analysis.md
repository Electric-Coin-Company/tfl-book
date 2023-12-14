# Security Analysis of Crosslink

This document analyses the security of Crosslink in terms of liveness and safety. It assumes that you have read [The Crosslink Construction](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view) which defines the protocol.

## Liveness argument

First note that Crosslink *intentionally* sacrifices **availability** if there is a long finalization stall.

:::info
This is technically independent of the other changes; you can omit the **Finality depth rule** and the protocol would still have security advantages over Snap‑and‑Chat, as well as solving its "spending from finalized outputs" issue. In that case the incentives to "pull" the finalization point forward to include new final bft‑blocks would be weaker, but honest bc‑block‑producers would still do it.
:::

It would still be a bug if there were any situation in which $\Pi_{\mathrm{bc}}$ failed to be **live**, though, because that would allow tail‑thrashing attacks.

Crosslink involves a bidirectional dependence between $\Pi_{\mathsf{bft}}$ and $\Pi_{\mathsf{bc}}$. The Ebb‑and‑Flow paper [[NTT2020]](https://eprint.iacr.org/2020/1091.pdf) argues in Appendix E ("Bouncing Attack on Casper FFG") that it can be more difficult to reason about liveness given a bidirectional dependence between protocols:

> To ensure consistency among the two tiers [of Casper FFG], the fork choice rule of the blockchain is modified to always respect ‘the justified checkpoint of the greatest height [*]’ [[22]](https://arxiv.org/abs/1710.09437). There is thus a bidirectional interaction between the block proposal and the finalization layer: blocks proposed by the blockchain are input to finalization, while justified checkpoints constrain future block proposals. This bidirectional interaction is intricate to reason about and a gateway for liveness attacks.

:::info
[*] The quotation changes this to "[depth]", but our terminology is consistent with Ethereum here and not with [NTT2020]'s idiosyncratic use of "depth" to mean "block height".
:::

The argument is correct as far as it goes. The main reason why this does not present any great difficulty to proving liveness of Crosslink, is due to a fundamental difference from Casper FFG: in Crosslink the fork‑choice rule of $\Pi_{\mathrm{bc}}$ is not modified.

Let $\mathcal{S}$ be the subset of bc‑blocks $\{ B : \textsf{is-coinbase-only-block}(B) \text{ and } \textsf{is-safety-block}(B) \}$. Assume that $\mathcal{S}$ is such that a bc‑block‑producer can always produce a block in $\mathcal{S}$.

In that case it is straightforward to convince ourselves that the additional bc‑block‑validity rules are never an obstacle to producing a new bc‑block in $\mathcal{S}$:
  * The changes to the definition of contextual validity do not interfere with liveness, since they do not affect coinbase transactions, and therefore do not affect blocks in $\mathcal{S}$. That is, the bc‑block‑producer can always just omit non‑coinbase transactions that are contextually invalid.
  * The **Genesis rule** doesn't apply to new bc‑blocks.
  * The **Valid context rule** and **Extension rule** are always satisfiable by referencing the same context bft‑block as the parent bc‑block.
  * The **Finality depth rule** always allows the option of producing a safety block, and therefore does not affect blocks in $\mathcal{S}$.

The instructions to an honest bc‑block‑producer allow it to produce a block in $\mathcal{S}$. Therefore, $\Pi_{\mathrm{bc}}$ remains live under the same conditions as $\Pi_{\mathrm{origbc}}$.

The additional bft‑proposal‑validity, bft‑block‑validity, bft‑finality, and honest voting rules are also not an obstacle to making, voting for, or finalizing bft‑proposals:

* Because $\Pi_{\mathrm{bc}}$ is live, there will always be some point in time at which a fresh valid bc‑header chain that satisfies both the **Increasing score rule** and the **Tail confirmation rule** exists for use in the $P.\mathsf{headers\_bc}$ field.
* If no fresh valid bc‑header chain is available, the **Increasing score rule** and **Tail confirmation rule** allow an honest bft‑proposer to choose $\mathsf{headers\_bc}$ to be the same as in the previous bft‑block. So, if liveness of $\Pi_{\mathrm{origbft}}$ depends on an honest proposer always being able to make a proposal (as it does in adapted‑Streamlet for example), then this requirement will not be violated.
* The changes to voting are only requiring a vote to be for a proposal that could have been honestly proposed.
* The bft‑finality rules are unchanged from origbft‑finality.

Therefore, $\Pi_{\mathrm{bft}}$ remains live under the same conditions as in Snap‑and‑Chat applied to $\Pi_{\mathrm{origbft}}$.

The only other possibility for a liveness issue relative to Snap‑and‑Chat would be if the change to the construction of $\mathsf{LOG}_{\mathrm{fin}}$ could cause it to stall, even when $\Pi_{\mathrm{bft}}$ and $\Pi_{\mathrm{bc}}$ are both still live.

However, liveness of $\Pi_{\mathrm{bft}}$ and the **Increasing score rule** together imply that at each point in time, provided there are sufficient honest bft‑proposers/validators, eventually a new bft‑block with a higher-scoring snapshot will become final in the context of the longest bft‑valid‑chain. ==TODO make that more precise.==

Because of the **Extension rule**, this new bft‑block must be a descendent of the previous final bft‑block in the context visible to bc‑block‑producers. Therefore, the new finalized chain will extend the old finalized chain. It could be the case that all of the new transactions are sanitized out, but that would only happen if they double‑spend or use outputs that were nonexistent in the context computed by $\textsf{bda-ctx}$ at the point at which they are to be contextually checked.

Finally, we need to show that Safety Mode is only triggered when it should be; that is, when the assumptions needed for liveness of $\Pi_{\mathrm{bft}}$ are violated. Informally, that is the case because, as long as there are sufficient honest bc‑block‑producers *and* sufficient honest bft‑proposers/validators, the finalization point implied by the $\mathsf{context\_bft}$ field at the tip of the bc‑best chain in any node's view will advance fast enough for the finalization gap bound $L$ not to be hit. This depends on the value of $L$ relative to $\sigma$, the network delay, the hash rate of honest bc‑block‑producers, the number of honest bft‑proposers and the proportion of voting units they hold, and other details of the BFT protocol. ==TODO: more detailed argument needed, especially for the dependence on $L$.==

## Safety argument

### Discussion

The **Extension rule** ensures that, informally, if a given node $i$'s view of its bc‑best‑chain at a depth of $\sigma$ blocks does not roll back, then neither does its view of the bft‑final block referenced by its bc‑best‑chain, and therefore neither does its view of $\mathsf{LOG}_{\mathrm{fin},i}^t$.

This does *not* by itself imply that all nodes are seeing the "same" confirmed bc‑best‑chain (up to propagation timing), or the same $\mathsf{LOG}_{\mathrm{fin},i}^t$. If the network is partitioned *and* $\Pi_{\mathrm{bft}}$ is subverted, it could be that the nodes on each side of the partition follow a different fork, and the adversary arranges for each node's view of the last final bft‑block to be consistent with the fork it is on. It can potentially do this if it has more than one third of validators, because if the validators are partitioned in the same way as other nodes, it can vote with an additional one third of them on each side of the fork.

This is, if you think about it, unavoidable. $\Pi_{\mathrm{bc}}$ doesn't include the mechanisms needed to maintain finality under partition; it takes a different position on the CAP trilemma. In order to maintain finality under partition, we need $\Pi_{\mathrm{bft}}$ not to be subverted (and to actually work!)

So what is the strongest security property we can realistically get? It is stronger than what Snap‑and‑Chat provides. Snap‑and‑Chat is unsafe *even without a partition* if $\Pi_{\mathrm{bft}}$ is subverted. Ideally we would have a protocol with safety that is *only* limited by attacks "like" the unavoidable attack described above --- which also applies to $\Pi_{\mathrm{bc}}$ used on its own.

### Proof of safety for LOG<sub>fin</sub>

In order to capture the intuition that it is hard in practice to cause a consistent partition of the kind described in the previous section, we will need to assume that the [**Prefix Agreement**](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Safety-of-Pi_mathrmbc) safety property holds for the relevant executions of $\Pi_{\mathrm{bc}}$. The structural and consensus modifications to $\Pi_{\mathrm{bc}}$ relative to $\Pi_{\mathrm{origbc}}$ seem unlikely to have any significant effect on this property, given that we proved above that they do not affect liveness. ==TODO: that is a handwave; we should be able to do better, as we do for $\Pi_{\mathrm{bft}}$ below.== So, to the extent that it is reasonable to assume that **Prefix Agreement** holds for executions of $\Pi_{\mathrm{origbc}}$ under some conditions, it should also be reasonable to assume it holds for executions of $\Pi_{\mathrm{bc}}$ under the same conditions.

Recall that $\mathsf{LF}(H) := \textsf{bft-last-final}(H\mathsf{.context\_bft})$.

:::success
**Prefix Lemma:** If $H_1$, $H_2$ are bc‑valid blocks with $H_1 \preceq_{\mathrm{bc}} H_2$, then $\mathsf{LF}(H_1) \preceq_{\mathrm{bft}} \mathsf{LF}(H_2)$.

Proof: Using the **Extension rule**, by induction on the distance between $H_1$ and $H_2$.
:::

<!--
:::success
Lemma: In an execution of $\Pi_{\mathrm{bc}}$ that has **Prefix Consistency** at confirmation depth $\sigma$, for all times $t \leq t'$ and all nodes $i$, $j$ (potentially the same) such that $i$ is honest at time $t$ and $j$ is honest at time $t'$, we have that $\mathsf{LF}(\mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\sigma) \preceq_{\mathrm{bft}} \mathsf{LF}(\mathsf{ch}_j^{t'})$.
:::
-->

Using this lemma (once for each direction) we can transfer the [**Prefix Agreement**](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Safety-of-Pi_mathrmbc) property to the referenced bft‑blocks:

:::success
**Prefix Agreement Lemma:** In an execution of $\Pi_{\mathrm{bc}}$ that has **Prefix Agreement** at confirmation <span style="white-space: nowrap">depth $\sigma$,</span> <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> we have <span style="white-space: nowrap">$\mathsf{LF}(\mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\sigma) \preceq\hspace{-0.5em}\succeq_{\mathrm{bft}} \mathsf{LF}(\mathsf{ch}_j^{t'} \lceil_{\mathrm{bc}}^\sigma)$.</span>
:::

(The notation $B \preceq\hspace{-0.5em}\succeq_{\mathrm{*}} C$ means that <span style="white-space: nowrap">either $B \preceq_{\mathrm{*}} C$ or $C \preceq_{\mathrm{*}} B$.</span> That is, <span style="white-space: nowrap">"one of $B$ and $C$</span> is a prefix of the other".)

Recall that $$
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

Because $\mathsf{fin}$ takes the form <span style="white-space: nowrap">$\mathsf{fin}(H) := [f(X) \text{ for } X \preceq_{\mathrm{bft}} g(H)]$,</span> we have that <span style="white-space: nowrap">$g(H) \preceq_{\mathrm{bft}} g(H') \implies \mathsf{fin}(H) \preceq \mathsf{fin}(H')$.</span> (This would be true for any well‑typed <span style="white-space: nowrap">$f$ and $g$.)</span>

By this observation and the **Prefix Agreement Lemma**, we also have that, in an execution of Crosslink where $\Pi_{\mathrm{bc}}$ has the **Prefix Agreement** safety property at confirmation depth <span style="white-space: nowrap">$\sigma$,</span> <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> <span style="white-space: nowrap">$\mathsf{fin}(\mathsf{ch}_i^t) \preceq\hspace{-0.5em}\succeq \mathsf{fin}(\mathsf{ch}_j^{t'})$.</span>

Because $\mathsf{sanitize}$ only considers previous state, $\textsf{context-txns}$ ∘ $\textsf{san-ctx}$ must be a prefix-preserving map; that is, <span style="white-space: nowrap">if $S_1 \preceq S_2$ then $\textsf{context-txns}(\textsf{san-ctx}(S_1)) \preceq \textsf{context-txns}(\textsf{san-ctx}(S_2))$.</span> Therefore:

:::success
**LOG<sub>fin</sub> Safety theorem (from Prefix Agreement of Π<sub>bc</sub>):** In an execution of Crosslink where $\Pi_{\mathrm{bc}}$ has **Prefix Agreement** at confirmation depth $\sigma$, <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{fin},i}^t \preceq\hspace{-0.5em}\succeq \mathsf{LOG}_{\mathrm{fin},j}^{t'}\,$.</span>
:::

Notice that this does not depend on any safety property of $\Pi_{\mathrm{bft}}$, and is an elementary proof. ([[NTT2020](https://eprint.iacr.org/2020/1091.pdf), Theorem 2] is a much more complicated proof that takes nearly 3 pages, not counting the reliance on results from [[PS2017]](https://eprint.iacr.org/2016/918.pdf).)

*In addition,* just as in Snap‑and‑Chat, safety of $\mathsf{LOG}_{\mathrm{fin}}$ can be inferred from safety of <span style="white-space: nowrap">$\Pi_{\mathrm{bft}}$,</span> which follows from safety of <span style="white-space: nowrap">$\Pi_{\mathrm{origbft}}$.</span> We prove this based on the [**Final Agreement**](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Safety-of-Pi_mathrmbft) property for executions of <span style="white-space: nowrap">$\Pi_{\mathrm{origbft}}$:</span>

:::success
An execution of $\Pi_{\mathrm{origbft}}$ has the **Final Agreement** safety property iff for all origbft‑valid <span style="white-space: nowrap">blocks $C$</span> in honest view at <span style="white-space: nowrap">time $t$</span> and $C'$ in honest view at <span style="white-space: nowrap">time $t'$,</span> we have <span style="white-space: nowrap">$\textsf{origbft-last-final}(C) \preceq\hspace{-0.5em}\succeq_{\mathrm{origbft}} \textsf{origbft-last-final}(C')\,$.</span>
:::

The changes in $\Pi_{\mathrm{bft}}$ relative to $\Pi_{\mathrm{origbft}}$ only add structural components and tighten bft‑block‑validity and bft‑proposal‑validity rules. So for any legal execution of $\Pi_{\mathrm{bft}}$ there is a corresponding legal execution of $\Pi_{\mathrm{origbft}}$, with the structural additions erased and with the same nodes honest at any given time. A safety property, by definition, only asserts that executions not satisfying the property do not occur. Safety properties of $\Pi_{\mathrm{origbft}}$ necessarily do not refer to the added structural components in $\Pi_{\mathrm{bft}}$. Therefore, for any safety property of $\Pi_{\mathrm{origbft}}$, including **Final Agreement**, the corresponding safety property holds for $\Pi_{\mathrm{bft}}$.

By the definition of $\mathsf{fin}$ as above, in an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has [**Final Agreement**](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Safety-of-Pi_mathrmbft), <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> <span style="white-space: nowrap">$\mathsf{fin}(\mathsf{ch}_i^t) \preceq\hspace{-0.5em}\succeq \mathsf{fin}(\mathsf{ch}_j^{t'})\,$.</span> Therefore, by an argument similar to the one above using the fact that $\textsf{context-txns}$ ∘ $\textsf{san-ctx}$ is a prefix-preserving map:

:::success
**LOG<sub>fin</sub> Safety theorem (from Final Agreement of Π<sub>bft</sub> or Π<sub>origbft</sub>):** In an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has **Final Agreement**, <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{fin},i}^t \preceq\hspace{-0.5em}\succeq \mathsf{LOG}_{\mathrm{fin},j}^{t'}\,$.</span>
:::

### Proof of safety for LOG<sub>bda</sub>

From the two $\mathsf{LOG}_{\mathrm{fin}}$ Safety theorems and the [Ledger prefix property](#Definitions-of-LOGtfini-and-LOGtbdai%CE%BC), we immediately have:

:::success
**LOG<sub>bda</sub> does not roll back past the agreed LOG<sub>fin</sub>:** Let $\mu_i$ be an arbitrary choice of $\mathsf{LOG}_{\mathrm{bda}}$ confirmation depth for each node $i$. Consider an execution of Crosslink where either $\Pi_{\mathrm{bc}}$ has **Prefix Agreement** at confirmation depth $\sigma$ or $\Pi_{\mathrm{bft}}$ has **Final Agreement**.

In such an execution, <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> either $\mathsf{LOG}_{\mathrm{fin},i}^t \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{fin},j}^{t'} \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{bda},j,\mu_j}^{t'}$ or $\mathsf{LOG}_{\mathrm{fin},j}^{t'} \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{fin},i}^t \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{bda},i,\mu_i}^t$.

**Corollary:** Under the same conditions, if wlog $\mathsf{LOG}_{\mathrm{fin},i}^t \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{fin},j}^{t'}$, then $\mathsf{LOG}_{\mathrm{fin},i}^t \preceq_{\mathrm{bc}} \{ \mathsf{LOG}_{\mathrm{bda},i,\mu_i}^t, \mathsf{LOG}_{\mathrm{bda},j,\mu_j}^{t'} \}$.
:::

The above property is not as strong as we would like for practical uses of $\mathsf{LOG}_{\mathrm{bda}}$, because it does not say anything about rollbacks up to the finalization point, and such rollbacks may be of unbounded length. (Loosely speaking, the number of <span style="white-space: nowrap">non-Safety Mode bc‑blocks</span> after the consensus finalization point is bounded by <span style="white-space: nowrap">$L$,</span> but we have also not proven that so far.)

As documented in the [Model for BFT protocols](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Model-for-BFT-protocols-%CE%A0origbftbft) section of [The Crosslink Construction]([/JqENg--qSmyqRt_RqY7Whw](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view)):

> For each epoch, there is a fixed number of voting units distributed between the players, which they use to vote for a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal</span>. If, and only if, the votes cast for a <span style="white-space: nowrap">$\mathrm{*}$bft‑proposal</span> $P$ satisfy a notarization rule, then it is possible to obtain a valid <span style="white-space: nowrap">$\mathrm{*}$bft‑notarization-proof</span> <span style="white-space: nowrap">$\mathsf{proof}_P$.</span> The notarization rule must require at least a two-thirds absolute supermajority of voting units to have been cast for $P$. (It may also require other conditions.)
>
> A voting unit for an epoch is cast non‑honestly if:
> * it is cast other than by the holder of the unit (due to key compromise or any flaw in the voting protocol, for example); or
> * it is double‑cast (i.e. for distinct proposals); or
> * the holder of the unit following the conditions for honest voting in $\Pi_{\mathrm{*bft}}$, according to its view, should not have cast that vote.
>
> :::success
> An execution of $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property if at any epoch in the execution, strictly fewer than one third of the total voting units for that epoch are cast non‑honestly.
> :::

By a well known argument often used to prove safety of BFT protocols, in an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property (and assuming soundness of notarization proofs), any bft‑valid block for a given epoch in honest view must commit to the same proposal.

Proof (adapted from [[CS2020](https://eprint.iacr.org/2020/088.pdf), Lemma 1]): Suppose there are two bft‑proposals $P$ and $P'$, both for <span style="white-space: nowrap">epoch $e$,</span> such that <span style="white-space: nowrap">$P$ is</span> committed to by some bft‑block‑valid <span style="white-space: nowrap">block $B$,</span> and <span style="white-space: nowrap">$P'$ is</span> committed to by some bft‑block‑valid <span style="white-space: nowrap">block $B'$.</span> This implies that $B$ and $B'$ have valid notarization proofs. Let the number of voting units for <span style="white-space: nowrap">epoch $e$</span> <span style="white-space: nowrap">be $n_e$.</span> Assuming soundness of the notarization proofs, it must be that at least $2n_e/3$ voting units for <span style="white-space: nowrap">epoch $e$,</span> denoted as the <span style="white-space: nowrap">set $S$,</span> were cast <span style="white-space: nowrap">for $P$,</span> and at least $2n_e/3$ voting units for <span style="white-space: nowrap">epoch $e$,</span> denoted as the <span style="white-space: nowrap">set $S'$,</span> were cast <span style="white-space: nowrap">for $P'$.</span> Since there are $n_e$ voting units for <span style="white-space: nowrap">epoch $e$,</span> $S \cap S'$ must have size at least <span style="white-space: nowrap">$n_e/3$.</span> In an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property, $S \cap S'$ must therefore include at least one voting unit that was cast honestly. Since a voting unit for epoch $e$ that is cast honestly is not double-cast, it must be <span style="white-space: nowrap">that $P = P'$.</span>

:::info
In the case of a network partition, votes may not be seen on both/all sides of the partition. Therefore, it is not necessarily the case that honest nodes can directly see double‑voting. The above argument does not depend on being able to do so.
:::

Therefore, in an execution of Crosslink for which $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property, for each <span style="white-space: nowrap">epoch $e$</span> there will be at most one bft‑proposal‑valid <span style="white-space: nowrap">proposal $P_e$,</span> and at least one third of honestly cast voting units must have been cast for it. Let $\mathcal{I}_e$ be the (necessarily nonempty) set of nodes that cast these honest votes; then, $\mathsf{snapshot}(P_e) \preceq_{\mathrm{bc}} \mathsf{ch}_i^{t_{e,i}} \lceil_{\mathrm{bc}}^\sigma$ for <span style="white-space: nowrap">all $i \in \mathcal{I}_e$</span> at the <span style="white-space: nowrap">times $t_{e,i}$</span> of their votes in epoch $e$. <span style="white-space: nowrap">(For simplicity,</span> we assume that for each honest <span style="white-space: nowrap">node $i$</span> there is only one <span style="white-space: nowrap">time $t_{e,i}$</span> at which it obtains a successful check for the voting condition in <span style="white-space: nowrap">epoch $e$,</span> which it uses for any votes that it casts in that epoch.)

Let $B$ be any bft‑block for <span style="white-space: nowrap">epoch $e$</span> such that <span style="white-space: nowrap">$B \preceq_{\mathrm{bft}} \textsf{bft-last-final}(C)$,</span> where $C$ is some bft‑block‑valid block. <span style="white-space: nowrap">Since $B \preceq_{\mathrm{bft}} C$,</span> <span style="white-space: nowrap">$B$ is bft‑block‑valid.</span> So by the argument above, $B$ commits to the only bft‑proposal‑valid <span style="white-space: nowrap">proposal $P_e$</span> for <span style="white-space: nowrap">epoch $e$,</span> and $\mathsf{snapshot}(B) = \mathsf{snapshot}(P_e)$ was voted for in that epoch by a nonempty subset of honest <span style="white-space: nowrap">nodes $\mathcal{I}_e$.</span>

Let $H$ be any bc‑valid block. We have by definition: $$
\begin{array}{rcl}
\mathsf{fin}(H) &\!\!=\!\!& [\mathsf{snapshot}(B) \text{ for } B \preceq_{\mathrm{bft}} \mathsf{LF}(H \lceil_{\mathrm{bc}}^\sigma)] \\
&\!\!=\!\!& [\mathsf{snapshot}(B) \text{ for } B \preceq_{\mathrm{bft}} \textsf{bft-last-final}(H \lceil_{\mathrm{bc}}^\sigma\mathsf{.context\_bft})]
\end{array}
$$ So, taking $C = H \lceil_{\mathrm{bc}}^\sigma\mathsf{.context\_bft}$, each $\mathsf{snapshot}(B)$ for $B$ of epoch $e$ in the result of $\mathsf{fin}(H)$ satisfies $\mathsf{snapshot}(B) \preceq_{\mathrm{bc}} \mathsf{ch}_i^{t_{e,i}} \lceil_{\mathrm{bc}}^\sigma$ for all $i$ in some nonempty honest set of nodes $\mathcal{I}_e$.

For an execution of Crosslink in which $\Pi_{\mathrm{bc}}$ has the **Prefix Consistency** property at confirmation depth $\sigma$, for every epoch $e$, for every such $(i, t_{e,i})$, for every node $j$ that is honest at any time $t' \geq t_{e,i}$, we have $\mathsf{ch}_i^{t_{e,i}} \lceil_{\mathrm{bc}}^\sigma \preceq_{\mathrm{bc}} \mathsf{ch}_j^{t'}$. Let $t_e = \min \{ t_{e,i} : i \in \mathcal{I}_e \}$. Then, by transitivity of $\preceq_{\mathrm{bc}}$:

:::success
In an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property and $\Pi_{\mathrm{bc}}$ has the **Prefix Consistency** property at confirmation <span style="white-space: nowrap">depth $\sigma$,</span> every bc‑chain $\mathsf{snapshot}(B)$ in $\mathsf{fin}(\mathsf{ch}_i^t)$ (and therefore every snapshot that contributes to <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{fin},i}^t$)</span> is, <span style="white-space: nowrap">at any time $t' \geq t_e$</span>,</span> in the bc‑best‑chain of <span style="white-space: nowrap">every node $j$</span> that is honest <span style="white-space: nowrap">at time $t'$</span> (where $B$ commits to $P_e$ at epoch $e$ and $t_e$ is the time of the first honest vote <span style="white-space: nowrap">for $P_e$).</span>
:::

A similar (weaker) statement holds if we replace $t' \geq t_e$ with $t' \geq t$, since the time of the first honest vote for $P$ necessarily precedes the time at which the signed $(P, \mathsf{proof}_P)$ is submitted as a bft‑block, which necessarily <span style="white-space: nowrap">precedes $t$.</span> (Whether or not the notarization proof depends on the *first* honest vote for <span style="white-space: nowrap">$B$'s proposal $P_e$,</span> it must depend on some honest vote for that proposal that was not made earlier <span style="white-space: nowrap">than $t_e$.)</span>

Furthermore, we have $$
\begin{array}{rcl}
\textsf{bda-ctx}(H, \mu) &\!\!\!=\!\!\!& \textsf{san-ctx}(\mathsf{fin}(H) \,||\, [H \lceil_{\mathrm{bc}}^\mu]) \\
\mathsf{LOG}_{\mathrm{bda},i,\mu}^t &\!\!\!=\!\!\!& \textsf{context-txns}(\textsf{bda-ctx}(\mathsf{ch}_i^t, \mu))
\end{array}
$$

So in an execution of Crosslink where $\Pi_{\mathrm{bc}}$ has the **Prefix Consistency** property at confirmation <span style="white-space: nowrap">depth $\mu$,</span> <span style="white-space: nowrap">if node $i$</span> is honest <span style="white-space: nowrap">at time $t$</span> then $H \lceil_{\mathrm{bc}}^\mu$ is also, <span style="white-space: nowrap">at any time $t' \geq t$,</span> in the bc‑best‑chain of <span style="white-space: nowrap">every node $j$</span> that is honest <span style="white-space: nowrap">at time $t'$.</span>

If an execution of $\Pi_{\mathrm{bc}}$ has the **Prefix Consistency** property at confirmation <span style="white-space: nowrap">depth $\mu \leq \sigma$,</span> then it necessarily also has it at confirmation <span style="white-space: nowrap">depth $\sigma$.</span> Therefore we have:

:::success
In an execution of Crosslink where $\Pi_{\mathrm{bft}}$ has the **one‑third bound on non‑honest voting** property and $\Pi_{\mathrm{bc}}$ has the **Prefix Consistency** property at confirmation <span style="white-space: nowrap">depth $\mu \leq \sigma$,</span> every bc‑chain snapshot in $\mathsf{fin}(\mathsf{ch}_i^t) \,||\, [\mathsf{ch}_i^t \lceil_{\mathrm{bc}}^\mu]$ (and therefore every snapshot that contributes to <span style="white-space: nowrap">$\mathsf{LOG}_{\mathrm{bda},i,\mu}^t$)</span> is, <span style="white-space: nowrap">at any time $t' \geq t$,</span> in the bc‑best‑chain of <span style="white-space: nowrap">every node $j$</span> that is honest <span style="white-space: nowrap">at time $t'$.</span>
:::

Sketch: we also need the sequence of snapshots output from fin to only be extended in the view of any node. In that case we can infer that the node does not observe a rollback in LOG_bda.

Recall that in the proof of safety for $\mathsf{LOG}_{\mathrm{fin}}$, we showed that in an execution of Crosslink where $\Pi_{\mathrm{bft}}$ (or $\Pi_{\mathrm{origbft}}$) has [**Final Agreement**](https://hackmd.io/JqENg--qSmyqRt_RqY7Whw?view#Safety-of-Pi_mathrmbft), <span style="white-space: nowrap">for all times $t$, $t'$</span> and <span style="white-space: nowrap">all nodes $i$, $j$</span> (potentially the same) such that <span style="white-space: nowrap">$i$ is honest</span> at <span style="white-space: nowrap">time $t$</span> and <span style="white-space: nowrap">$j$ is honest</span> at <span style="white-space: nowrap">time $t'$,</span> <span style="white-space: nowrap">$\mathsf{fin}(\mathsf{ch}_i^t) \preceq\hspace{-0.5em}\succeq \mathsf{fin}(\mathsf{ch}_j^{t'})\,$.</span>

What we want to show is that, under some conditions on executions, ...

<!--
By definition, $\textsf{final-bft}(\mathsf{parent}_{\mathrm{bc}}^\sigma(\mathsf{ch}_i^t)) = \textsf{bft-last-final}(C)$ for $C = \mathsf{tip}(\mathsf{ch}_i^t)\mathsf{.context\_bft}$, and if $i$ is honest at time $t$ then $C$ is necessarily a bft‑valid block in honest view.

Therefore, in an execution where $\Pi_{\mathrm{bft}}$ has the **Final Agreement** property, for all times $t, t'$; all nodes $i$, $j$ such that $i$ that is honest at time $t$ and $j$ is honest at time $t'$; and all $B_i \preceq_{\mathrm{bft}} \textsf{final-bft}(\mathsf{parent}_{\mathrm{bc}}^\sigma(\mathsf{ch}_i^t))$ and $B_j \preceq_{\mathrm{bft}} \textsf{final-bft}(\mathsf{parent}_{\mathrm{bc}}^\sigma(\mathsf{ch}_j^{t'}))$, we have $B_i \preceq\hspace{-0.5em}\succeq_{\mathrm{bft}} B_j$. This implies that any particular ... -->



<!-- On the other hand, if an execution of Crosslink does *not* have the Prefix Consistency property, then ... -->

<!-- fixme false, need to make stronger assumptions


:::success
Let $\mu$ be an arbitrary choice of $\mathsf{LOG}_{\mathrm{bda}}$ confirmation depth. Consider an execution of Crosslink where both $\Pi_{\mathrm{bc}}$ has **Prefix Agreement** at confirmation depth $\mu$ and $\Pi_{\mathrm{bft}}$ has **Final Agreement**.

In such an execution, for all times $t$ and all nodes $i$, $j$ such that $i$ and $j$ are honest at time $t$, then either $\mathsf{LOG}_{\mathrm{bda},i,\mu}^t \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{bda},j,\mu}^t$ or $\mathsf{LOG}_{\mathrm{bda},j,\mu}^t \preceq_{\mathrm{bc}} \mathsf{LOG}_{\mathrm{bda},i,\mu}^t$.
:::

Proof: In an execution where $\Pi_{\mathrm{bft}}$ has **Final Agreement**, ==TODO==

==TODO we need to take account of accumulated work, in order to prevent an adversary from, e.g. building a $\sigma$‑block bc‑chain at low difficulty from $\mathcal{O}_{\mathrm{bc}}$, which will be accepted as valid if it has subverted the BFT protocol.==
-->

## Disadvantages of Crosslink

### More invasive changes

Unlike Snap‑and‑Chat, Crosslink requires structural and consensus rule changes to both $\Pi_{\mathrm{bc}}$ and $\Pi_{\mathrm{bft}}$. On the other hand, several of those changes are arguably necessary to fix a showstopper bug in Snap‑and‑Chat (not being able to spend some finalized outputs).

### Finalization latency

For a given choice of $\sigma$, the finalization latency is higher. The snapshot of the BFT chain used to obtain $\mathsf{LOG}_{\mathrm{fin},i,\mu}^t$ is obtained from the block at depth $\mu$ on node $i$'s best $\Pi_{\mathrm{bc}}$ chain, which will on average lead to a finalized view that is about $\mu + 1 + \sigma$ blocks back (in $\Pi_{\mathrm{bc}}$), rather than $\sigma_{\mathrm{sac}}$ blocks in Snap‑and‑Chat. This is essentially the cost of ensuring that safety is given by the stronger of the safety of $\Pi_{\mathrm{bc}}$ (at $\mu$ confirmations) and the safety of $\Pi_{\mathrm{bft}}$.

On the other hand, the relative increase in expected finalization latency is only $\frac{\mu + 1 + \sigma}{\sigma_{\mathrm{sac}}},$ i.e. at most slightly more than a factor of 2 for the case $\mu = \sigma = \sigma_{\mathrm{sac}}$.

### More involved liveness argument

See the Liveness section above.

## Every rule in Crosslink is individually necessary

:::warning
In order to show that Crosslink is at a *local* optimum in the security/complexity trade‑off space, for each rule we show attacks on safety and/or liveness that could be performed if that rule were omitted or simplified.
:::

Edit: some rules, e.g. the **Increasing Score rule**, only contribute heuristically to security in the analysis so far.
