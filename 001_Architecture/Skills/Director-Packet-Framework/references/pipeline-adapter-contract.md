# Pipeline Adapter Contract

The global Director's Packet skill remains independent of pipeline approval and generation. A future adapter may provide:

- `project_root`
- `packet_output_root`
- `style_guidance`
- `complexity_threshold`
- `required_components`
- `approval_mode`
- `provider_capabilities`
- `archive_root`

The adapter may call the framework to create, revise, validate, or assemble a packet. It may then decide whether to request human review or route the approved packet to a provider. The global skill must not make those decisions itself.
