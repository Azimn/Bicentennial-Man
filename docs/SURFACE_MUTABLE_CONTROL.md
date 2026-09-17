# Surface-Mutable Control

The existing OpenEvolve wrapper experiment is the Surface-Mutable Control.

Its purpose is not to improve DUCK. Its purpose is to estimate how much apparent phenotype improvement can be obtained while DUCK remains unchanged.

The generated candidate receives two explicit phases from the trusted laboratory bridge. In the prepare phase it may rewrite the subject-facing text, add or remove elapsed ticks, and use its own persistent surface state. In the postprocess phase it may rewrite the raw DUCK response. Every turn records whether those channels were used and preserves the raw DUCK response for later audit.

Generated code is executed in a Docker container with no network, a read-only root filesystem, the candidate file mounted read-only, and one writable assigned surface-state directory. DUCK source, Bicentennial Man source, scenario files, evaluator code, sealed suites, and other candidates are not mounted. The trusted host process invokes DUCK separately through the JSON interaction interface.

The phenotype judge does not receive candidate instrumentation metadata. It sees only the observable conversational transcript. This prevents exploit labels or raw-response annotations from steering the judge.

Naturalness is not part of the early OpenEvolve optimization score. The combined score is recomputed by the laboratory from the non-naturalness phenotype dimensions.

A Surface-Mutable candidate is not evidence of organism improvement, even if it achieves a strong phenotype score. If its gain coincides with input rewriting, output rewriting, timing manipulation, or wrapper-owned state, record that result as benchmark exploitation.
