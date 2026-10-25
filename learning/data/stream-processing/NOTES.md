# Stream Processing Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- No interview yet. The mission was written from the scope in issue #142, which named the arc's material (the stream-table duality, the DSL and topologies, state, windows, joins, exactly-once, scaling, testing, operating, and a judgment stage) but not the learner's reason for wanting it. The first interactive session should ask that reason and narrow the mission if the answer is narrower than "build and run Kafka Streams apps".
- Kafka Streams as the only engine came from the issue, not from a learner. If the learner already runs Flink, keep the Streams lessons and lean on lesson 18's comparison earlier rather than rewriting the arc.

## On the arc

The eight stages and twenty lessons are public, in `README.md`. The caveat on them belongs here: the whole arc was written upfront in one change, not one lesson per interactive session, and `learning-records/` is empty. Nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- No lesson has been run against a live broker. The `TopologyTestDriver` reps need only a JDK and the `kafka-streams-test-utils` artifact; the scaling, rebalancing and monitoring reps need a local cluster, which is the first thing to confirm with a learner.
- Defaults and protocol status were read from the Apache Kafka 4.3 documentation and the KIPs in October 2026. Recheck them before reusing a lesson's numbers on a later release.
