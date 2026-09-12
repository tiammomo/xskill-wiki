# From session evidence to a task graph: Session, Atom, Task and Attempt

xskill organizes time-ordered assistant conversations into a graph of user goals and execution attempts. It preserves source evidence while distinguishing continuous intent segments, logical goals and individual executions. This makes resumed goals, retries, user corrections and resource usage independently traceable.

The task graph is a separate semantic processing branch. It reads Sessions and Atoms to build Tasks, Attempts and their relationships. It does not silently rewrite consumed Atoms during linking, and its existence does not mean the production Skill pipeline already consumes complete task-level inputs.

This reference describes object responsibilities, processing, persistence and current boundaries. Behavior was checked on September 12, 2026. Optional designs and incompletely supported cases are listed separately at the end.

## Why a task graph is needed

A single assistant session can contain several goals, while one goal can continue across sessions. A user may switch from goal A to goal B and later return to A. One goal may also involve failure, correction and another execution.

Grouping only by session mixes unrelated goals. Grouping only by messages or continuous segments cannot represent a goal resumed later. Keeping only a final summary loses the failed approach, execution relationships and the evidence behind an outcome.

The task graph preserves the timeline while adding two views: which evidence serves the same goal, and which execution attempt that evidence belongs to.

## Responsibilities of the four objects

| Object | Definition | Main purpose |
| --- | --- | --- |
| Session | A Harness conversation record and its source information | Preserve user interaction, assistant output and available execution facts in order |
| Atom | A continuous segment of a Session centered on an intent | Provide locatable, inspectable segmented evidence |
| Logical Task, or Task | A user goal and its supporting evidence associations | Represent a goal continuing across segments and sessions |
| Task Attempt, or Attempt | One execution or retry of a Task | Preserve execution continuity, corrections, outcomes and resource attribution |

A Harness is the tool or runtime that hosts the assistant. Different Harnesses may expose different execution identities, structured terminal states and usage information.

These objects do not have one-to-one relationships:

- One Session can contain multiple Atoms and Tasks.
- One Task can associate non-contiguous Atoms and continue across Sessions within an allowed scope.
- An Atom has at most one confirmed primary Task membership, while proposed relationships can coexist.
- One Task can contain multiple Attempts.
- One Attempt can reference several evidence segments; one Atom can also contain multiple locatable execution attempts.

`Session → Atom → Task → Attempt` is a useful reading order, but not a complete data model. Tasks and Attempts connect to evidence through separate references; they do not move the source content from layer to layer.

## An end-to-end example

A user asks the assistant to fix a timeout in an order API. The assistant first raises the timeout, but validation still fails. The user then asks it to inspect the connection pool. During the investigation, the user requests a translation before returning to the API problem.

This can produce four continuous segments: initial investigation, correction, translation and resumed investigation. They serve two primary goals: resolving the API timeout and completing the translation.

| Segment | Goal | Execution meaning |
| --- | --- | --- |
| Investigate and raise the timeout | Resolve the API timeout | Initial attempt |
| Correct the approach and inspect the pool | Resolve the API timeout | Corrected attempt |
| Translate a description | Complete the translation | Execution of an independent goal |
| Return to the pool problem and validate | Resolve the API timeout | Resume the goal; execution continuity is a separate question |

This example assumes the required evidence meets confirmation conditions. Similar wording alone does not guarantee automatic merging.

With a trustworthy stable run identity, the resumed investigation may remain part of the corrected Attempt. Without sufficient continuity evidence, a new Attempt and a proposed continuation relationship are retained. “Continue this problem” is a goal-continuation cue, not a complete execution identity.

Likewise, “test passed” in the record does not automatically establish verified Task success. The result must be attributable to the relevant goal, execution attempt and valid evidence.

## From source records to referenceable evidence

### Normalized conversations and metadata

Adapters handle tool-specific source formats, preserving normalized conversations and available actor, workspace, model, Harness, run identity, terminal state and usage information. Downstream task interpretation should not depend on every tool's internal file format.

Current processing reads normalized text, Atom files and source metadata. Display text may be truncated, and fields vary by source. A display view must not be treated as a lossless raw log. Missing terminal states, model versions and usage must not be invented.

### Identity, scope and content revision

Stable identity answers “which object is this?” A content digest answers “has this object's input changed?” Titles, summaries and local paths are unsuitable as durable task identities.

The graph distinguishes access, goal ownership and collection source:

| Scope | Purpose |
| --- | --- |
| TenantScope | Defines the permission and privacy boundary |
| TaskScope | Defines the semantic boundary for automatic linking; by default combines tenant, actor and workspace |
| SourceScope | Provides a stable namespace for a collection source |

Session and Atom references carry their scopes. Bare session or segment identifiers cannot be compared across sources as globally unique identities.

Sharing Skills within a team does not make similar requests from different members one Task. Access to the same material is not permission to group goals. Several sources can belong to a TaskScope, but cross-source continuation still requires evidence.

## Session to Atom: identifying continuous intent segments

### Semantic proposals and deterministic validation

The splitter starts with a line-numbered map of user queries, previous segments and the current resume position. The model reads source text as needed and submits segment start positions, intents and summaries. Deterministic code validates starts and derives ends.

User turns are candidate boundaries, not mandatory cuts. Several turns can share a continuous intent, and a single Atom can preserve retries or corrections for the Attempt layer to interpret later.

Code checks ranges, ordering, bounds, coverage and overlap for the current input. Summary quality needs separate evaluation: valid ranges do not establish a faithful summary.

### Evidence coordinates

Current Atom offsets are one-based line numbers, using a half-open interval that includes the start and excludes the end. `[7, 11)` covers lines 7 through 10.

The first complete split begins at line 1; the final segment ends at the total line count plus one. Incremental splitting covers the range after the current resume position. Neighbor references preserve segment order.

Evidence ranges also need a source revision and content digest. A file still existing does not mean the content behind an old reference remains valid.

### Consumed evidence and appended output

Once an Atom is persisted and consumed, routing and linking must not silently rewrite it without versioning. Re-splitting or appending facts requires an explicit relationship between old references and new content, with downstream invalidation.

Current incremental splitting primarily handles new user intents. Assistant-only or tool-only append operations still have coverage and attribution gaps. “No new user turn” must not be interpreted as “no new evidence.” The limitation and intended direction are listed below.

## Atom to Task: organizing a shared user goal

### Reusing unchanged memberships

Graph construction checks source and segment revisions and reuses unchanged confirmed memberships and stable identities. Rebuilding should not assign new identifiers to every historical task.

Segments requiring a new decision are scoped by TaskScope before task candidates are retrieved.

### Bounded candidates and linking rules

The default linker uses bounded inverted-index candidates and recent tasks from the same Session. Segment terms, candidate count and task-anchor size have limits. An anchor is a bounded feature set for retrieval and comparison, not an ever-growing full task prompt.

Explicit continuation, retry or correction cues still require candidate matching. An existing Task is reused automatically only when the best candidate meets the threshold and is sufficiently separated from the next candidate.

Content similarity alone does not establish goal identity. When ordinary similar segments cannot be confirmed, the linker can create an independent confirmed primary Task while retaining proposed relationships to similar older Tasks.

Default linking is not all-pairs model clustering and should not be described as already using vector retrieval or LLM adjudication by default.

### Confirmation and uncertainty

Relationship decisions distinguish confirmed, proposed, rejected and needs-review states. Primary membership and corresponding official statistics use confirmed facts; multiple candidates are not counted as independent confirmed memberships.

Heuristic retrieval scores are not calibrated probabilities. The system retains reasons and algorithm information rather than presenting a similarity score as a probability of correctness.

Task relationships can also represent parent and child goals, dependencies or follow-up tasks. Having these relationship types does not imply reliable automatic inference from arbitrary conversations. Writes still validate scope, parent constraints and acyclicity.

## Task and Attempt: goal identity versus execution continuity

An Attempt belongs to one Task and connects to execution evidence through EvidenceRange references. A goal can be executed repeatedly; a later success must not overwrite an earlier failed execution.

Current grouping considers direct adjacency in the original timeline, a stable run id under the same Harness, explicit retry or correction cues, and previously confirmed Attempt boundaries.

| Situation | Handling |
| --- | --- |
| Same goal with execution-continuity evidence | May retain the same Attempt |
| Explicit retry | Create an Attempt with retry_of |
| Explicit correction of the earlier approach | Create an Attempt with correction_of |
| Same goal without execution-continuity evidence | Create an Attempt with proposed continuation_of |

Crossing a Session boundary does not necessarily start an Attempt; staying in one Session does not imply one Attempt. Compaction, recovery and retries must be interpreted from execution facts.

When a retry or correction is locatable within one Atom, its evidence can be split into execution ranges associated with separate Attempts without changing the Atom itself.

Previously confirmed execution boundaries take precedence over later automatic grouping. Rebuilding must not silently collapse existing Attempts. Confirmed Attempt relationships must stay within one Task and remain acyclic.

## Outcomes: completion, success, verification and user feedback

Task outcomes use separate dimensions rather than overloading one boolean.

| Dimension | Meaning |
| --- | --- |
| Lifecycle | Whether a Task is open, blocked or closed, or an Attempt is running or finished |
| Outcome | Observed success, partial success, failure, cancellation or unknown result |
| Verification | Verified, unverified, contradicted or conflicting evidence |
| User disposition | Accepted, rejected, corrected, cancelled or unknown feedback |

A finished execution does not establish goal completion. A failed execution does not establish that the Task cannot continue.

Automatic Attempt terminal inference currently relies primarily on structured Harness terminal information from a sole-Task Session. Source-reported success can finish an execution while verification remains unverified. Deriving a Task outcome requires the relevant outcome and verification evidence conditions.

For multi-goal Sessions, a session-wide success must not be copied to every Task. A final Attempt without structured terminal evidence may remain running with an unknown outcome. Conservative records are preferable to fabricated completion or success.

If evidence drifts or a terminal fact is withdrawn, affected automatic conclusions must become unknown or require review. Old decisions and their stale evidence remain auditable.

## Updating, persisting and recovering the graph

### Independent background processing

The graph uses a worker consuming a durable change queue. Versioned queue entries identify sources or scopes requiring processing so an older completion acknowledgement cannot clear updates that arrived during processing.

Initial enablement can backfill historical sources in batches. Algorithm or important parameter changes can schedule scope rebuilds. Pausing the graph must not delete source evidence, human decisions or raw usage facts.

### Immutable generations and query projections

A generation represents one complete graph result, stored as immutable manifests and content-addressed shards. Unchanged shards can be reused, and a small current pointer is switched atomically to publish the next version.

SQLite provides the query projection. Publication validates required facts, writes the graph contents, switches the pointer, updates the scope projection transactionally, then acknowledges the matching queue version.

File publication and a database update do not form a native cross-storage transaction. Recovery relies on the current pointer, generation identity, retained pending work and idempotent processing.

If the pointer changed but SQLite failed, work must not be acknowledged; the projection must be repaired later. If the projection completed but acknowledgement did not, repeated processing must not duplicate usage facts or renumber unchanged tasks.

### Human corrections

Confirmations, rejections, merges, splits and state changes are stored as ordered, identified override events, validated and rebuilt under a scope lock. Automatic processing must not overwrite recorded human decisions.

Merging retains a canonical Task and aliases or tombstones for old identities. Splitting and moving must preserve Attempt ownership and confirmed relationships. Current operations cannot arbitrarily cut an Attempt; finer execution-boundary editing requires additional design.

Human events must not silently disappear when a source is deleted. Invalid references remain as stale facts.

## Usage and cost attribution

xskill separates execution usage incurred by the original assistant completing user goals from xskill_processing usage incurred by splitting, linking and analysis. Each plane is recorded, presented and conserved separately; neither should be conflated into one model-execution cost.

Raw usage events have stable identities. Duplicate ingestion must have identical content. Unknown values remain null with reasons instead of becoming zero.

An event can be directly attributed, explicitly shared or left as an unattributed balance. Current shared allocation uses confirmed primary evidence line spans and the largest-remainder method to conserve integer Token totals.

The source total can be measured while an Attempt share remains a method-defined allocation, not a precise measurement of that execution. Session, Task and Attempt totals are different views of the same fact and must not be added again.

## Performance and complexity boundaries

Bounded candidates and anchors, source caching, stable membership reuse and content-shard reuse reduce repeated reads and comparisons. They do not imply that every operation touches only new segments.

Current construction still collects and sorts within a scope, and projections may be replaced at scope granularity. A local update can therefore still depend on historical scope size. Candidate bounds alone do not establish end-to-end complexity or a measured speedup.

Incremental performance evaluation should record source reads, candidate comparisons, model calls, database writes, new shard bytes, memory and end-to-end latency. Optimizations must retain deletion, restart, override-replay and consistency checks.

## Current boundaries and future directions

These boundaries affect use and integration and should remain visible to readers.

| Scenario | Current boundary | Direction |
| --- | --- | --- |
| Assistant-only or tool-only append | No new Atom may be produced, leaving stale ranges or later misattribution | Define append-evidence versions, ownership and downstream invalidation |
| Temporary source read failure | Exception classification can still confuse a read fault with a missing source | Distinguish deletion from retryable faults and retain affected work |
| External algorithm kernel | Task scheduling still has coupling to native-processing conditions | Let the graph's own switch and queue control scheduling |
| LLM-assisted linking | An optional unmerged extension, not default main-branch behavior | Bound candidates, calls and time; fall back on failure and evaluate quality separately |
| Native terminal state and Task success | Source fields and verifiable evidence vary; automatic inference is conservative | Improve source observability while separating execution completion from verified goal success |
| Task-grounded Skill learning | A graph does not mean production Skill learning fully consumes Tasks | Integrate through explicit evidence contracts, consumers and compatibility verification |

Update these boundaries with actual releases. Capability status must follow observable behavior and validation, not merely the existence of a type, configuration field or page.

## Frequently asked questions

### Why not summarize each Session directly into a Task?

Sessions can mix goals and execution attempts. An overall summary is useful for reading, but cannot replace scoped evidence, goal identity and execution relationships.

### Why retain Atoms?

Atoms provide continuous, referenceable upstream segments for independent splitting evaluation and evidence reuse. Tasks add non-contiguous goal semantics above them; the responsibilities differ.

### Why can one Task have multiple Attempts?

The goal can stay the same while an approach fails, is retried or is corrected by the user. Separate Attempts preserve those processes so outcomes and costs can be distinguished by execution.

### Why were similar segments not merged automatically?

Similarity is a retrieval signal. Scope, continuation evidence, separation between candidates and historical decisions also matter. Insufficient evidence leaves an independent primary membership and candidate relationships.

### Can the graph automatically establish success for every Task?

No. Automatic outcomes depend on structured terminal evidence, goal attribution and verification. Missing evidence remains unknown.

### Does rebuilding lose human corrections?

The design preserves them through a separate override log, versioned graph and recovery markers. Rebuilds must replay these facts rather than treat the query database as the only source of truth.

### Does a task graph mean every downstream feature operates on Tasks?

No. The graph provides goal and execution structure. Each consumer still needs explicit inputs, eligibility checks, version invalidation, deduplication and fallback behavior.
