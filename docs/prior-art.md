# Prior Art and Adjacent Ecosystem References

This document collects public prior art, adjacent ecosystem projects, vocabulary, and key concepts that inform `protocol-as-code`.

> **Non-canon posture:** These are references for study and comparison only. They are **NOT** adopted canon for this repository. Nothing listed here is binding on `protocol-as-code` unless explicitly adopted through the repository's review and status process. See [`docs/definition.md`](definition.md) and [`docs/principles.md`](principles.md).

## Public Prior Art

These projects established the practice of describing interfaces, message shapes, and service contracts as reviewable source material.

### gRPC

- **What it does:** A high-performance, open-source universal RPC framework built on HTTP/2. Clients and servers communicate via defined service contracts and strongly typed messages.
- **Relevance to this repo:** Demonstrates how explicit, reviewable service contracts can drive both human review and machine execution across languages. The idea that a protocol is a first-class, versionable artifact aligns with `protocol-as-code`.
- **Docs:** https://grpc.io/docs/

### Protocol Buffers

- **What it does:** A language-neutral, platform-neutral extensible mechanism for serializing structured data. Defines message types in an IDL and generates code for many languages.
- **Relevance to this repo:** Core example of schema-first design: the `.proto` file is the canonical source, and everything else is derived. Models how a single source artifact can be reviewed, versioned, and tested.
- **Docs:** https://protobuf.dev/

### Apache Thrift

- **What it does:** A scalable cross-language service development framework. Defines data types and service interfaces in an IDL and generates client/server code for many languages.
- **Relevance to this repo:** Early and influential example of interface definition driving multi-language execution. Illustrates the trade-offs of bundling interface, transport, and serialization in one contract.
- **Docs:** https://thrift.apache.org/docs/

### JSON-RPC

- **What it does:** A stateless, lightweight remote procedure call protocol encoded in JSON. Defines a small, uniform envelope for requests, responses, and notifications.
- **Relevance to this repo:** A minimal, human-readable contract format. Shows how little ceremony is needed to define a callable protocol, useful as a contrast to richer IDL systems.
- **Docs:** https://www.jsonrpc.org/

### OpenAPI

- **What it does:** A specification for describing HTTP APIs. Defines endpoints, request/response schemas, authentication, and errors in a machine-readable document (YAML/JSON).
- **Relevance to this repo:** Strong example of contract-first API design with a rich ecosystem of tooling for validation, documentation, and code generation. Models how a single spec can drive review, testing, and client generation.
- **Docs:** https://swagger.io/specification/

### AsyncAPI

- **What it does:** A specification for describing event-driven and message-based APIs. Defines channels, messages, payloads, and bindings for brokers like Kafka, MQTT, and WebSocket.
- **Relevance to this repo:** Extends contract-first design to asynchronous, event-driven workflows. Relevant because many operational protocols are event- or message-driven rather than request/response.
- **Docs:** https://www.asyncapi.com/docs

### GraphQL SDL

- **What it does:** A type definition language for GraphQL schemas. Declares types, fields, queries, mutations, and subscriptions as a reviewable, language-neutral schema.
- **Relevance to this repo:** Demonstrates a compact, human-readable schema language that is both the contract and the source of truth for a system's surface area. Useful reference for how a small IDL can express rich structure.
- **Docs:** https://graphql.org/learn/schema/

## Adjacent Ecosystem

These projects address serialization, schema evolution, and interface definition from adjacent angles. They are related but not direct ancestors of `protocol-as-code`.

### Cap'n Proto

- **What it does:** A fast binary serialization protocol and RPC system. Uses a schema language with a strong focus on zero-copy reads and forward/backward compatibility.
- **Relevance to this repo:** Influential model for schema evolution and compatibility discipline. Its approach to evolving schemas without breaking older readers is directly relevant to versioning operational protocols.
- **Docs:** https://capnproto.org/

### FlatBuffers

- **What it does:** A cross-platform serialization library that prioritizes performance and zero-copy access. Schemas are defined in an IDL and compiled to typed accessors.
- **Relevance to this repo:** Another data point on schema-first, code-generated access to structured data. Relevant for the trade-off between inspection-friendliness and performance in protocol artifacts.
- **Docs:** https://flatbuffers.dev/

### MessagePack

- **What it does:** A binary serialization format that is compact and fast, while remaining readable across languages. It is format-only and does not prescribe a schema language.
- **Relevance to this repo:** A reference for schemaless serialization. Useful as a contrast to schema-first approaches and for thinking about where explicit contracts add value over raw encoding.
- **Docs:** https://msgpack.org/

### Apache Avro

- **What it does:** A data serialization system that relies on schemas defined in JSON. Schemas travel with the data, enabling rich schema evolution and resolution rules.
- **Relevance to this repo:** Strong model for schema evolution, resolution, and backward/forward compatibility. Its schema-resolution rules are a useful reference for evolving protocol definitions safely.
- **Docs:** https://avro.apache.org/docs/

### Bond

- **What it does:** A cross-platform framework for working with schematized data. Supports an IDL, code generation, and a pluggable serialization runtime.
- **Relevance to this repo:** Another industrial example of IDL-driven, code-generated data contracts. Relevant for how a single schema can target multiple runtimes and serialization formats.
- **Docs:** https://microsoft.github.io/bond/

### FIDL

- **What it does:** Fuchsia's Interface Definition Language. Defines protocols and data types for inter-process communication with an emphasis on versioning and ABI stability.
- **Relevance to this repo:** A modern, carefully versioned IDL designed for a microkernel OS. A strong reference for how interface definitions can encode compatibility and evolution as first-class concerns.
- **Docs:** https://fuchsia.dev/fuchsia-src/development/languages/fidl

## Vocabulary References

Terms used across this repository and the surrounding ecosystem. Definitions here are working notes, not authoritative canon.

- **protocol-as-code:** Treating repeatable workflows, checklists, runbooks, playbooks, and safety procedures as version-controlled, reviewable, testable, auditable, and agent-operable source material. See [`docs/definition.md`](definition.md).
- **schema-first design:** The practice of defining the shape and contract of data or behavior in an explicit schema before, and independently of, any implementation.
- **IDL (Interface Definition Language):** A language for declaring interfaces, message types, and service contracts in a way that is independent of any programming language.
- **serialization:** The process of converting in-memory data structures into a format that can be stored or transmitted and later reconstructed.
- **contract-first:** A design approach where the interface or protocol contract is defined and reviewed before implementations are written, so that the contract drives the system rather than the reverse.

## Key Concepts

Concepts that recur across the prior art above and that are relevant to `protocol-as-code`.

- **Interface definition:** Declaring the surface area of a system (operations, inputs, outputs, roles) in an explicit, reviewable form. Central to gRPC, Thrift, OpenAPI, AsyncAPI, GraphQL SDL, and FIDL.
- **Schema evolution:** The discipline of changing a schema over time without invalidating existing consumers. Central to Cap'n Proto, Avro, and FIDL's compatibility model.
- **Backward and forward compatibility:** Backward compatibility means newer code can read data produced by older code; forward compatibility means older code can read data produced by newer code. Both are first-class concerns in Cap'n Proto, Avro, Protobuf, and FIDL.
- **Code generation:** Producing typed client/server code, validators, or documentation from a schema or IDL. Common to gRPC/Protobuf, Thrift, OpenAPI, AsyncAPI, Cap'n Proto, FlatBuffers, Bond, and FIDL.

## Note on Status

This document is a reference collection, not an adoption. Items listed here are public projects and concepts that inform the design space of `protocol-as-code`. None of them are adopted canon for this repository unless explicitly marked and audited through the repository's review and status process.
