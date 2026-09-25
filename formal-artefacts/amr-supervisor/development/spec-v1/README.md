# Draft v1 specification gap

These immutable snapshots preserve the first specification and the accepted source before the goal-stop repair. Both source and target satisfy its 1,824 abstract input checks, yet the runtime source reaches the goal without issuing Brake; the chosen Halted interface requires sustained effective Brake, so Finish is never enabled.

This is an observed mismatch between an inadequate authored contract and its physical completion interface, not an LLM generation failure or a source/target correspondence defect. The v1.1 contract explicitly adds goal braking without weakening Halted or collision evaluation.

Reproduce from any directory using `python reproduce.py --output <new-directory>`. The wrapper loads only these archived semantics and the original unchanged `amr-corridor` physical modules. The full failure run is stored in `failure-run/` and is kept separate from final v1.1 candidate counts and comparison episodes.
